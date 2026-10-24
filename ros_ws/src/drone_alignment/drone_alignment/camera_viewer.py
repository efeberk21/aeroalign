import rclpy
import cv2
from cv_bridge import CvBridge, CvBridgeError
from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy.qos import qos_profile_sensor_data
from pathlib import Path

class CameraViewer(Node):
  def __init__ (self):
    super().__init__('camera_viewer')

    self.frame_count = 0
    self.bridge = CvBridge()

    self.snapshot_path = (
        Path.home() / 'projects/aeroalign/reports/raw/camera_check.png'
    )
    self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)

    self.subscription = self.create_subscription(
      Image,
      '/camera/image_raw',
      self.image_callback,
      qos_profile_sensor_data,
    )
    self.get_logger().info('Camera node has been started')

  def image_callback(self,msg):
    try:
      frame = self.bridge.imgmsg_to_cv2(
        msg,
        desired_encoding = 'bgr8',
      )
    except CvBridgeError as error:
      self.get_logger().error(f'Goruntu donusum hatasi: {error}')
      return

    cv2.imshow('AeroAlign - Kamera', frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        saved = cv2.imwrite(str(self.snapshot_path), frame)

        if saved:
            self.get_logger().info(
                f'Goruntu kaydedildi: {self.snapshot_path}'
            )
        else:
            self.get_logger().error('Goruntu kaydedilemedi.')

    self.frame_count += 1
    if self.frame_count % 30 == 0:
      self.get_logger().info(
        f'(Goruntu: {msg.width} x {msg.height},)'
        f'{msg.encoding} | Toplam kare: {self.frame_count}'
      )

def main(args=None):
  rclpy.init(args=args)
  node = CameraViewer()

  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    pass
  finally:
    node.destroy_node()
    cv2.destroyAllWindows()
    if rclpy.ok():
      rclpy.shutdown()

if __name__ == '__main__':
  main()
