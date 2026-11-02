"""
Capture dataset images from a scripted downward camera instead of a flight.

A headless Gazebo server loads one platform world without the drone and adds a
gravity-free camera with the Iris gimbal camera's image settings. Before each
image the camera, the platform and the distractors are moved with one
set_pose_vector call. Images are written with the recorder's write_record, so
manifests have the same columns; exact poses go to capture_poses.csv.

Run it as a file, like dataset_recorder.py:

    python ros_ws/src/drone_alignment/drone_alignment/scene_capture.py \
        --world platform_world_sand_low --scene-id scene02 --seed 2
"""

import argparse
import csv
from datetime import datetime
import json
import math
import os
from pathlib import Path
import random
import signal
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET

import cv2
from cv_bridge import CvBridge
from dataset_recorder import MANIFEST_FIELDS, write_record
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


PROJECT_ROOT = Path(__file__).resolve().parents[4]
WORLDS = PROJECT_ROOT / 'sim' / 'worlds'
VENDOR_ROOT = Path(os.environ.get(
    'ALIGN_GZ_ROOT', Path.home() / 'projects/drone_alignment_vendor/ardupilot_gazebo'
))
WORLD_NAME = 'iris_runway'
IMAGE_TOPIC = '/aeroalign/capture/image'
CAMERA_PROFILE = 'rig_nadir_640x480_hfov2'
HFOV = 2.0
ASPECT = 480 / 640
PLATFORM_TOP_M = 0.128

PLATFORMS = {
    'orange': ('delivery_platform', 'orange_h_v1'),
    'blue': ('delivery_platform_blue', 'blue_ring_v1'),
}
# Rough half-size of each distractor's footprint, used to keep them apart.
DISTRACTORS = {
    'distractor_crate': 0.75,
    'distractor_dark_mat': 1.45,
    'distractor_hazard_stripes': 1.6,
    'distractor_orange_barrel': 0.35,
}
PARKED = {
    'delivery_platform': (-45.0, 40.0),
    'delivery_platform_blue': (-40.0, 40.0),
    'distractor_crate': (-35.0, 40.0),
    'distractor_dark_mat': (-30.0, 40.0),
    'distractor_hazard_stripes': (-25.0, 40.0),
    'distractor_orange_barrel': (-20.0, 40.0),
}
POSE_FIELDS = [
    'image_id', 'kind', 'camera_x', 'camera_y', 'camera_z', 'camera_yaw',
    'platform_model', 'platform_x', 'platform_y', 'platform_yaw', 'distractors',
]

CAMERA_MODEL = f"""
<model name="capture_camera">
  <pose>0 0 10 0 1.5707963267948966 0</pose>
  <link name="camera_link">
    <gravity>false</gravity>
    <inertial><mass>0.1</mass></inertial>
    <sensor name="camera" type="camera">
      <always_on>true</always_on>
      <update_rate>10</update_rate>
      <topic>{IMAGE_TOPIC}</topic>
      <camera>
        <horizontal_fov>{HFOV}</horizontal_fov>
        <image><width>640</width><height>480</height><format>R8G8B8</format></image>
        <clip><near>0.05</near><far>200</far></clip>
      </camera>
    </sensor>
  </link>
</model>
"""


def scene_variants(world):
    """Return (ground_variant, light_variant) for a world name."""
    variants = json.loads((WORLDS / 'scene_variants.json').read_text())
    if world == 'platform_world':
        ground, light = variants['base']['ground'], variants['base']['light']
    else:
        ground, _, light = world.removeprefix('platform_world_').partition('_')
    return variants['grounds'][ground]['variant'], variants['lights'][light]['variant']


def capture_world(world, folder):
    """Write the world without the drone and with the capture camera."""
    tree = ET.parse(WORLDS / f'{world}.sdf')
    root = tree.getroot().find('world')
    for include in root.findall('include'):
        if include.findtext('uri') == 'model://iris_with_gimbal':
            root.remove(include)
    root.append(ET.fromstring(CAMERA_MODEL))
    path = Path(folder) / f'{world}_capture.sdf'
    tree.write(path, encoding='utf-8', xml_declaration=True)
    return path


def quaternion(roll, pitch, yaw):
    """Return (x, y, z, w) for fixed-axis roll, pitch, yaw."""
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def pose_text(name, x, y, z, roll=0.0, pitch=0.0, yaw=0.0):
    """Return one gz.msgs.Pose entry in protobuf text format."""
    qx, qy, qz, qw = quaternion(roll, pitch, yaw)
    return (
        f'pose {{ name: "{name}" position {{ x: {x:.4f} y: {y:.4f} z: {z:.4f} }} '
        f'orientation {{ x: {qx:.6f} y: {qy:.6f} z: {qz:.6f} w: {qw:.6f} }} }}'
    )


class Layout:
    """Sample object positions inside the camera footprint."""

    def __init__(self, rng, height):
        self.rng = rng
        distance = height - PLATFORM_TOP_M
        self.half_u = distance * math.tan(HFOV / 2)
        self.half_v = self.half_u * ASPECT

    def place(self, camera, margin):
        """Return a ground point whose image position keeps `margin` from the edge."""
        cx, cy, yaw = camera
        u = self.rng.uniform(-1, 1) * max(self.half_u - margin, 0.0)
        v = self.rng.uniform(-1, 1) * max(self.half_v - margin, 0.0)
        # Image right is (sin yaw, -cos yaw) and image up is (cos yaw, sin yaw).
        return (
            cx + u * math.sin(yaw) + v * math.cos(yaw),
            cy - u * math.cos(yaw) + v * math.sin(yaw),
        )

    def sample(self, platform_model, count_range):
        """Return camera, platform and distractor poses for one image."""
        rng = self.rng
        camera = (rng.uniform(-3, 3), rng.uniform(-3, 3), rng.uniform(0, 2 * math.pi))
        taken = []
        platform = None
        if platform_model is not None:
            # Mostly fully visible; about one in seven may cross the image edge.
            # The centre stays inside the image, so at least a corner remains visible.
            margin = 0.3 if rng.random() < 0.15 else 1.45
            x, y = self.place(camera, margin)
            platform = (platform_model, x, y, rng.uniform(0, 2 * math.pi))
            taken.append((x, y, 1.45))

        distractors = []
        names = rng.sample(sorted(DISTRACTORS), rng.randint(*count_range))
        for name in names:
            radius = DISTRACTORS[name]
            for _ in range(50):
                x, y = self.place(camera, radius)
                if all(math.dist((x, y), (tx, ty)) > radius + tr + 0.4
                       for tx, ty, tr in taken):
                    distractors.append((name, x, y, rng.uniform(0, 2 * math.pi)))
                    taken.append((x, y, radius))
                    break
        return camera, platform, distractors


class CaptureNode(Node):
    """Keep the latest capture-camera image."""

    def __init__(self):
        super().__init__('scene_capture')
        self.latest = None
        self.create_subscription(
            Image, IMAGE_TOPIC, self.on_image, qos_profile_sensor_data
        )

    def on_image(self, msg):
        self.latest = msg

    def wait_for_image(self, min_stamp_ns, timeout_s):
        """Spin until an image at or after min_stamp_ns arrives."""
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)
            if self.latest is not None and stamp_ns(self.latest) >= min_stamp_ns:
                return self.latest
        raise TimeoutError(f'{IMAGE_TOPIC}: no image within {timeout_s} s')


def stamp_ns(msg):
    return msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec


def set_poses(env, entries):
    """Move several models in one set_pose_vector request."""
    result = subprocess.run(
        ['gz', 'service', '-s', f'/world/{WORLD_NAME}/set_pose_vector',
         '--reqtype', 'gz.msgs.Pose_V', '--reptype', 'gz.msgs.Boolean',
         '--timeout', '5000', '--req', ' '.join(entries)],
        env=env, capture_output=True, text=True, check=False,
    )
    if 'data: true' not in result.stdout:
        raise RuntimeError(f'set_pose_vector failed: {result.stdout} {result.stderr}')


def record_session(node, env, args, height, variants, rng):
    """Capture one height session and return its folder."""
    session_id = f'rig_h{height:02.0f}_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    session_dir = Path(args.output_dir).expanduser() / args.scene_id / session_id
    session_dir.mkdir(parents=True, exist_ok=False)
    manifest_path = session_dir / 'manifest.csv'
    with manifest_path.open('x', newline='', encoding='utf-8') as stream:
        csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS).writeheader()
    poses_path = session_dir / 'capture_poses.csv'
    with poses_path.open('x', newline='', encoding='utf-8') as stream:
        csv.DictWriter(stream, fieldnames=POSE_FIELDS).writeheader()

    platform_model, platform_variant = PLATFORMS[args.platform]
    kinds = ['pos'] * args.positives + ['neg'] * args.negatives
    rng.shuffle(kinds)
    layout = Layout(rng, height)
    bridge = CvBridge()

    empty_used = False
    for index, kind in enumerate(kinds, start=1):
        if kind == 'pos':
            camera, platform, distractors = layout.sample(platform_model, (0, 2))
        else:
            # Empty frames of a flat-coloured ground are pixel-identical, so
            # allow only one empty negative per session.
            camera, platform, distractors = layout.sample(
                None, (1 if empty_used else 0, 3)
            )
            empty_used = empty_used or not distractors

        entries = [pose_text('capture_camera', camera[0], camera[1], height,
                             pitch=math.pi / 2, yaw=camera[2])]
        placed = {}
        if platform is not None:
            placed[platform[0]] = platform[1:]
        for name, x, y, yaw in distractors:
            placed[name] = (x, y, yaw)
        for name, (px, py) in PARKED.items():
            x, y, yaw = placed.get(name, (px, py, 0.0))
            entries.append(pose_text(name, x, y, 0.0, yaw=yaw))

        before = stamp_ns(node.latest)
        set_poses(env, entries)
        # Several 10 Hz frames later, the new poses are certainly rendered.
        msg = node.wait_for_image(before + int(args.settle_s * 1e9), timeout_s=30)
        frame = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        # A plain-ground negative may be nearly uniform; all black means no render.
        if frame.max() == 0:
            raise RuntimeError('Rendered image is black; is the scene loaded?')
        encoded_ok, encoded = cv2.imencode('.png', frame)
        if not encoded_ok:
            raise RuntimeError('PNG encoding failed.')

        image_id = f'{args.scene_id}_{session_id}_frame{index:06d}'
        image_path = session_dir / f'{image_id}.png'
        write_record(image_path, manifest_path, encoded.tobytes(), {
            'image_id': image_id,
            'scene_id': args.scene_id,
            'session_id': session_id,
            'image_path': image_path.name,
            'source_stamp_ns': stamp_ns(msg),
            'width': msg.width,
            'height': msg.height,
            'platform_variant': platform_variant if platform else 'none',
            'ground_variant': variants[0],
            'light_variant': variants[1],
            'nominal_height_m': height,
            'notes': f'rig_capture world={args.world} seed={args.seed}',
            'camera_profile': CAMERA_PROFILE,
        })
        with poses_path.open('a', newline='', encoding='utf-8') as stream:
            csv.DictWriter(stream, fieldnames=POSE_FIELDS).writerow({
                'image_id': image_id,
                'kind': kind,
                'camera_x': f'{camera[0]:.4f}',
                'camera_y': f'{camera[1]:.4f}',
                'camera_z': f'{height:.4f}',
                'camera_yaw': f'{camera[2]:.6f}',
                'platform_model': platform[0] if platform else '',
                'platform_x': f'{platform[1]:.4f}' if platform else '',
                'platform_y': f'{platform[2]:.4f}' if platform else '',
                'platform_yaw': f'{platform[3]:.6f}' if platform else '',
                'distractors': ';'.join(
                    f'{n}@{x:.3f},{y:.3f},{yaw:.4f}' for n, x, y, yaw in distractors
                ),
            })
        node.get_logger().info(f'[{index}/{len(kinds)}] {kind} {image_path.name}')
    return session_dir


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument('--world', required=True, help='sim/worlds/<world>.sdf')
    parser.add_argument('--scene-id', required=True)
    parser.add_argument('--platform', choices=sorted(PLATFORMS), default='orange')
    parser.add_argument('--heights', type=float, nargs='+', default=[5.0, 8.0, 10.0])
    parser.add_argument('--positives', type=int, default=12)
    parser.add_argument('--negatives', type=int, default=3)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--settle-s', type=float, default=0.45)
    parser.add_argument(
        '--output-dir', default=str(PROJECT_ROOT / 'datasets' / 'platform')
    )
    return parser.parse_args()


def main():
    args = parse_args()
    variants = scene_variants(args.world)
    rng = random.Random(args.seed)

    env = os.environ.copy()
    env['GZ_PARTITION'] = f'aeroalign_capture_{os.getpid()}'
    env['GZ_SIM_RESOURCE_PATH'] = os.pathsep.join(filter(None, [
        str(PROJECT_ROOT / 'sim' / 'models'), str(VENDOR_ROOT / 'models'),
        env.get('GZ_SIM_RESOURCE_PATH'),
    ]))

    processes = []
    with tempfile.TemporaryDirectory() as folder:
        world_path = capture_world(args.world, folder)
        try:
            for command in (
                ['gz', 'sim', '-s', '-r', str(world_path), '--render-engine', 'ogre',
                 '-v', '1'],
                ['ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
                 f'{IMAGE_TOPIC}@sensor_msgs/msg/Image[gz.msgs.Image'],
            ):
                processes.append(subprocess.Popen(
                    command, env=env, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, start_new_session=True,
                ))
            rclpy.init()
            node = CaptureNode()
            first = node.wait_for_image(0, timeout_s=90)
            node.wait_for_image(stamp_ns(first) + 2_000_000_000, timeout_s=30)
            for height in args.heights:
                session_dir = record_session(node, env, args, height, variants, rng)
                print(session_dir, flush=True)
            node.destroy_node()
        finally:
            if rclpy.ok():
                rclpy.shutdown()
            for process in processes:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGINT)
            for process in processes:
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)


if __name__ == '__main__':
    main()
