#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math
import sys

class LeaderController(Node):
    def __init__(self, mode='s'):
        super().__init__('leader_controller')
        self.publisher_ = self.create_publisher(Twist, '/leader/cmd_vel', 10)
        self.timer_period = 0.1  # 10Hz
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.start_time = self.get_clock().now().nanoseconds / 1e9
        self.mode = mode
        
        self.get_logger().info(f"LEADER STARTED: Testing {mode.upper()} path for error analysis.")

    def timer_callback(self):
        now = self.get_clock().now().nanoseconds / 1e9
        t = now - self.start_time
        msg = Twist()

        if self.mode == 's':
            # --- PROFESSIONAL S-CURVE (Sweeping Sine) ---
            # Constant forward velocity
            msg.linear.x = 0.22 #0.18
            # 0.25 = gentle turn intensity
            # 0.4 = slow frequency (one full wave every ~30 seconds)
            # This prevents the leader from "zipping" out of view
            msg.angular.z = 0.3 * math.sin(0.5 * t)

        elif self.mode == 'circle':
            # --- STABLE CIRCLE (Control Case) ---
            msg.linear.x = 0.15
            msg.angular.z = 0.25

        else:
            # --- FIGURE-8 ---
            msg.linear.x = 0.12 
            msg.angular.z = 0.4 * math.cos(0.2 * t)

        self.publisher_.publish(msg)

def main():
    # Use 's' for your primary analysis, 'circle' for baseline
    mode_choice = 's'
    if len(sys.argv) > 1:
        mode_choice = sys.argv[1]

    rclpy.init()
    node = LeaderController(mode=mode_choice)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.publisher_.publish(Twist())
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()
