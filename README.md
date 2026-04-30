# Leader-Follower Tracking for a Nonholonomic Robot under Intermittent Vision Feedback

This repository implements a robust leader-follower formation for mobile robots using **ROS 2 Humble** and **Gazebo Classic**. The system is designed to maintain formation stability even during 10-second vision blackouts using a hybrid control strategy.

## 🚀 Overview
The project solves the problem of leader-tracking for nonholonomic unicycle robots. When the Follower (Waffle Pi) loses sight of the Leader (Burger) due to sensory deprivation, it switches from vision-based tracking to dead-reckoning prediction to maintain the formation.

### Key Features:
*   **Nonlinear Control:** Lyapunov-based controller utilizing LaSalle’s Invariance Theorem to guarantee asymptotic stability.
*   **Fiducial Vision:** Real-time pose estimation using **OpenCV** and **Fiducial markers**.
*   **Trajectory Prediction:** Kinematic dead-reckoning applied during 10-second occlusion windows.
*   **Simulation:** Custom Gazebo environment with integrated hardware-in-the-loop logic.

## 🛠 Hardware & Software
*   **Robots:** TurtleBot3 Burger (Leader), TurtleBot3 Waffle Pi (Follower).
*   **Middleware:** ROS 2 Humble.
*   **Simulator:** Gazebo Classic for motion simulation and RViz for kinematics and workspace visualization.
*   **Languages:** Python for technical development and control logic, with C++ for performance-critical nodes.

## 📂 Repository Structure
```text
leader-follower-formation-control/
├── src/
│   ├── controller/          # ROS 2 Package (Control & Prediction Logic)
│   │   ├── controller/      # Lyapunov and Kinematic nodes
│   │   ├── launch/          # Simulation launch files
│   │   ├── package.xml
│   │   └── setup.py
│   └── models/              # Custom Gazebo Assets
│       ├── turtlebot3_burger/ # Modified SDF with ArUco Marker
│       └── marker0/         # ArUco Marker textures and SDF
└── README.md


### ⚙️Setup Instructions
1. Create a Workspace
   mkdir -p ~/robot_ws/src
   cd ~/robot_ws/src

2. Clone the Repository
   git clone https://github.com/harshada-lokesh/leader-follower-formation-control.git

3. Configure Custom Models
   # Create the local model directory
   mkdir -p ~/turtlebot3_ws/src/

   # Copy the models from the repo to your local model path
   cp -r ~/robot_ws/src/leader-follower-formation-control/src/models/* ~/turtlebot3_ws/src/

4. Build the Package
   cd ~/robot_ws
   colcon build --packages-select controller
   source install/setup.bash


### 🏁 How to Run
1. Launch the Simulation (Terminal 1)
   ros2 launch controller simulation.launch.py

2. Start the Formation Controller (Terminal 2)
   cd ~/robot_ws/src/controller/controller
   python3 follower_predict_controller.py

3. Run the 3 different trajectories (Terminal 3)
   a) Straight Path:
   ros2 topic pub /leader/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.25, y: 0.0, z: 0.0}, angular: {z: 0.0}}"
   b) Curved Path:
   ros2 topic pub /leader/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {z: 0.1}}"
   b) S-shaped Path:
   cd ~/robot_ws/src/controller/controller
   python3 leader_controller.py s
