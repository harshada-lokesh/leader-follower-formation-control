# leader-follower-formation-control
A ROS 2 leader-follower simulation using Lyapunov-based control and kinematic prediction during vision blackouts
# Lyapunov-Based Formation Control with Kinematic Prediction

This repository contains a ROS 2 Humble and Gazebo Classic simulation for a leader-follower robot formation.

## Overview
The system addresses sensory deprivation (10-second vision blackouts) using a hybrid control strategy:
- **Active Phase:** Lyapunov-based nonlinear control using ArUco marker pose estimation.
- **Passive Phase:** Kinematic dead-reckoning to predict the leader's trajectory during occlusions.

## Hardware/Software
- **Robots:** TurtleBot3 Burger (Leader), Waffle Pi (Follower)
- **Environment:** Gazebo Classic
- **Middleware:** ROS 2 Humble
- **Vision:** OpenCV with ArUco Fiducial Markers

## How to Run
1. Source your ROS 2 workspace.
2. Launch the Gazebo world: `ros2 launch ...`
3. Run the controller node: `ros2 run ...`
