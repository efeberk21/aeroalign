"""Save sampled camera images and a separate manifest for each session."""

import csv
from datetime import datetime
import math
from pathlib import Path
import re

import cv2
from cv_bridge import CvBridge, CvBridgeError
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


MANIFEST_FIELDS = [
    'image_id', 'scene_id', 'session_id', 'image_path',
    'source_stamp_ns', 'width', 'height', 'platform_variant',
    'ground_variant', 'light_variant', 'nominal_height_m',
    'notes', 'camera_profile',
]


def write_record(image_path, manifest_path, png_bytes, row):
    """Write a new PNG and roll back a failed CSV append."""
    image_created = False
    try:
        with image_path.open('xb') as image_file:
            image_created = True
            image_file.write(png_bytes)

        with manifest_path.open('r+', newline='', encoding='utf-8') as stream:
            stream.seek(0, 2)
            checkpoint = stream.tell()
            try:
                csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS).writerow(row)
                stream.flush()
            except Exception:
                stream.seek(checkpoint)
                stream.truncate()
                stream.flush()
                raise
    except Exception:
        if image_created:
            image_path.unlink()
        raise


class DatasetRecorder(Node):
    """Record camera images with operator-supplied scene metadata."""

    def __init__(self):
        super().__init__('dataset_recorder')

        defaults = {
            'output_dir': str(
                Path.home() / 'projects/aeroalign/datasets/platform'
            ),
            'scene_id': 'scene01',
            'session_id': datetime.now().strftime('session_%Y%m%d_%H%M%S_%f'),
            'save_interval_s': 1.0,
            'nominal_height_m': -1.0,
            'platform_variant': 'orange_h_v1',
            'ground_variant': 'matte_gray_v1',
            'light_variant': 'sun_default_v1',
            'camera_profile': 'iris_wide_640x480_hfov2_zoom1',
            'notes': '',
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

        self.output_dir = Path(
            self.get_parameter('output_dir').value
        ).expanduser()
        self.scene_id = self.get_parameter('scene_id').value
        self.session_id = self.get_parameter('session_id').value
        self.save_interval_s = self.get_parameter('save_interval_s').value
        nominal_height = self.get_parameter('nominal_height_m').value

        if not math.isfinite(self.save_interval_s) or self.save_interval_s <= 0:
            raise ValueError('save_interval_s pozitif ve sonlu olmali.')
        if not math.isfinite(nominal_height) or (
            nominal_height < 0 and nominal_height != -1.0
        ):
            raise ValueError('Yukseklik sifir/pozitif veya bilinmiyorsa -1.0 olmali.')

        for name, value in (
            ('scene_id', self.scene_id),
            ('session_id', self.session_id),
        ):
            if re.fullmatch(r'[A-Za-z0-9_-]+', value) is None:
                raise ValueError(f'{name}: yalnizca harf, rakam, _ ve - kullan.')

        self.metadata = {
            name: self.get_parameter(name).value
            for name in (
                'platform_variant', 'ground_variant', 'light_variant',
                'camera_profile', 'notes',
            )
        }
        self.metadata['nominal_height_m'] = (
            '' if nominal_height == -1.0 else nominal_height
        )

        self.bridge = CvBridge()
        self.frame_count = 0
        self.saved_count = 0
        self.last_saved_stamp_ns = None

        self.session_dir = self.output_dir / self.scene_id / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=False)
        self.manifest_path = self.session_dir / 'manifest.csv'
        with self.manifest_path.open('x', newline='', encoding='utf-8') as stream:
            csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS).writeheader()

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            qos_profile_sensor_data,
        )
        self.get_logger().info(f'Kayit klasoru: {self.session_dir}')
        self.get_logger().info(f'Manifest: {self.manifest_path}')
        self.get_logger().info(
            f'Aralik: {self.save_interval_s} simulasyon saniyesi | '
            f'Nominal yukseklik: {self.metadata["nominal_height_m"]} m'
        )

    def image_callback(self, msg):
        """Sample by source timestamp and save matching image/CSV records."""
        self.frame_count += 1
        if self.frame_count == 1:
            self.get_logger().info(
                f'Ilk goruntu: {msg.width} x {msg.height} ({msg.encoding})'
            )

        stamp_ns = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
        if self.last_saved_stamp_ns is not None:
            elapsed_s = (stamp_ns - self.last_saved_stamp_ns) / 1_000_000_000
            if 0 <= elapsed_s < self.save_interval_s:
                return

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            encoded_ok, encoded = cv2.imencode('.png', frame)
        except (CvBridgeError, cv2.error) as error:
            self.get_logger().error(f'Goruntu donusum hatasi: {error}')
            return
        if not encoded_ok:
            raise RuntimeError('PNG kodlamasi basarisiz.')

        image_id = (
            f'{self.scene_id}_{self.session_id}_'
            f'frame{self.saved_count + 1:06d}'
        )
        image_path = self.session_dir / f'{image_id}.png'
        row = {
            'image_id': image_id,
            'scene_id': self.scene_id,
            'session_id': self.session_id,
            'image_path': image_path.name,
            'source_stamp_ns': stamp_ns,
            'width': msg.width,
            'height': msg.height,
            **self.metadata,
        }
        write_record(image_path, self.manifest_path, encoded.tobytes(), row)

        self.saved_count += 1
        self.last_saved_stamp_ns = stamp_ns
        self.get_logger().info(
            f'PNG + CSV kaydedildi [{self.saved_count}]: {image_path.name}'
        )


def main(args=None):
    """Run the recorder until interrupted."""
    rclpy.init(args=args)
    node = None
    try:
        node = DatasetRecorder()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
