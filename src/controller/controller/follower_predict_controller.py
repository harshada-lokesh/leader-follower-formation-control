#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist, Point  # Point is for the image_error topic
from cv_bridge import CvBridge
import cv2
import math
import numpy as np

class LyapunovVisionFollower(Node):
    def __init__(self):
        super().__init__('lyapunov_vision_follower')
        self.subscription = self.create_subscription(Image, '/follower/camera/image_raw', self.image_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/follower/cmd_vel', 10)
        
        # Publisher for Image Error Tracking
        self.error_pub = self.create_publisher(Point, '/follower/image_error', 10)
        
        self.bridge = CvBridge()
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters()

        # Gains & State
        self.kx, self.ky, self.kt = 0.008, 0.008, 0.4 
        self.target_width_px = 150.0 
        self.deadzone_px = 5.0
        self.last_v, self.last_w = 0.0, 0.0
        self.xe, self.ye = 0.0, 0.0
        self.ids = None

        # Experiment Timing
        self.experiment_triggered = False
        self.experiment_start_clock = None
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info("ROBUST SYSTEM READY - Logging to /follower/image_error")

    def image_callback(self, msg):
        try:
            full_frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            is_blackout = False
            if self.experiment_triggered:
                elapsed = (self.get_clock().now() - self.experiment_start_clock).nanoseconds / 1e9
                if 10.0 <= elapsed < 20.0:
                    is_blackout = True

            if is_blackout:
                display_frame = np.zeros_like(full_frame)
                status_text = "BLACKOUT - PREDICTING"
                color = (0, 0, 255)
                self.ids = None 
            else:
                display_frame = full_frame
                corners, ids, _ = cv2.aruco.detectMarkers(display_frame, self.aruco_dict, parameters=self.parameters)
                self.ids = ids
                
                if ids is not None and 0 in ids:
                    idx = np.where(ids == 0)[0][0]
                    c = corners[idx][0]
                    center_x = (c[0][0] + c[1][0] + c[2][0] + c[3][0]) / 4
                    current_width = abs(c[0][0] - c[1][0])
                    self.xe = self.target_width_px - current_width
                    self.ye = 320 - center_x
                    
                    # --- PUBLISH DATA TO ROS ---
                    error_msg = Point()
                    error_msg.x = float(self.xe) # Distance error
                    error_msg.y = float(self.ye) # Centering error
                    self.error_pub.publish(error_msg)
                    
                    cv2.aruco.drawDetectedMarkers(display_frame, corners, ids)
                    status_text = "LYAPUNOV ACTIVE"
                    color = (0, 255, 0)
                else:
                    status_text = "TARGET LOST"
                    color = (0, 255, 255)

            cv2.putText(display_frame, f"STATUS: {status_text}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.imshow("Follower Vision", display_frame)
            cv2.waitKey(1)
        except Exception as e:
            self.get_logger().error(f"Vision Error: {e}")

    def control_loop(self):
        elapsed = 0.0
        if self.experiment_triggered:
            elapsed = (self.get_clock().now() - self.experiment_start_clock).nanoseconds / 1e9

        is_blackout = 10.0 <= elapsed < 20.0
        cmd = Twist()

        if is_blackout:
            cmd.linear.x = self.last_v
            cmd.angular.z = self.last_w
        else:
            if self.ids is not None and 0 in self.ids:
                theta_e = math.atan2(self.ye, self.target_width_px)
                v_calc = max(min(float(self.kx * self.xe), 0.4), -0.1) 
                w_calc = max(min(float(self.ky * self.ye + self.kt * math.sin(theta_e)), 0.8), -0.8)
                
                cmd.linear.x, cmd.angular.z = v_calc, w_calc
                self.last_v, self.last_w = cmd.linear.x, cmd.angular.z

                if not self.experiment_triggered and v_calc > 0.12:
                    self.experiment_triggered = True
                    self.experiment_start_clock = self.get_clock().now()
                    self.get_logger().info(">>>> MISSION START <<<<")
            else:
                cmd.linear.x, cmd.angular.z = 0.0, 0.0

        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = LyapunovVisionFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
