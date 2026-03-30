# Coaxial-Quard-Copter-for-Chimney-Inspection

# 🚁 PX4 Offboard Control + Camera + ROS2 + Gazebo (GZ) Setup Guide

## 📌 Overview

This project sets up:

* PX4 SITL drone simulation
* ROS2 (Humble)
* Offboard control using Python
* Gazebo (GZ) simulation
* Camera streaming from drone to ROS2
* Foundation for AI-based autonomous navigation

---

## 🧰 Prerequisites

* Ubuntu 22.04
* ROS2 Humble
* PX4 Autopilot
* Gazebo (GZ / Garden or Harmonic)

---

# ⚙️ 1. Workspace Setup

```bash
mkdir -p ~/drone_ws/src
cd ~/drone_ws
colcon build
```

---

# 📦 2. Create ROS2 Package

```bash
cd ~/drone_ws/src
ros2 pkg create px4_offboard_control --build-type ament_python
```

---

# 📁 3. Add Python Script

Place your file:

```
offboard_control.py
```

Inside:

```
~/drone_ws/src/px4_offboard_control/px4_offboard_control/
```

---

# 🛠️ 4. Modify setup.py

```python
entry_points={
    'console_scripts': [
        'offboard_control = px4_offboard_control.offboard_control:main',
    ],
},
```

---

# 🔨 5. Build Workspace

```bash
cd ~/drone_ws
colcon build
```

---

# 🔁 6. Source Environment

```bash
source /opt/ros/humble/setup.bash
source ~/drone_ws/install/setup.bash
```

---

# 🚀 7. Run Offboard Control

```bash
ros2 run px4_offboard_control offboard_control
```

---

# ✈️ 8. Drone Behavior

* Arms automatically
* Takes off
* Moves to a setpoint (x, y, z)

---

# ⚠️ Common Issues

## ❌ ModuleNotFoundError: px4_msgs

### Fix:

```bash
cd ~/drone_ws/src
git clone https://github.com/PX4/px4_msgs.git
cd ~/drone_ws
colcon build
```

---

## ❌ ros2: command not found

### Fix:

```bash
source /opt/ros/humble/setup.bash
```

Permanent fix:

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "source ~/drone_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## ❌ ROS2 Broken Installation

### Fix:

```bash
sudo apt remove ros-humble-*
sudo apt autoremove
sudo apt update
sudo apt install ros-humble-desktop
```

---

# 📷 9. Camera Integration (Gazebo → ROS2)

## 🔍 Check Camera Topic (Gazebo)

```bash
gz topic -l | grep camera
```

---

## 🔎 Check Camera Type

```bash
gz topic -i -t /camera
```

Expected:

```
gz.msgs.Image
```

---

# 🔗 10. Bridge Gazebo Camera to ROS2

## Install Bridge

```bash
sudo apt install ros-humble-ros-gz-bridge
sudo apt install ros-humble-ros-gz-image
```

---

## Run Bridge

```bash
ros2 run ros_gz_bridge parameter_bridge \
/camera@sensor_msgs/msg/Image@gz.msgs.Image
```

---

# 📡 11. Verify Camera in ROS2

```bash
ros2 topic list | grep camera
```

---

## View Image

```bash
rqt_image_view
```

Select:

```
/camera
```

---

# 🚨 Major Issue Faced

## ❌ Unknown message type [9]

### Cause:

* Conflict between:

  * ❌ Ignition (ign)
  * ❌ Gazebo Classic
  * ✅ New Gazebo (gz)

### Fix:

```bash
sudo apt remove 'ros-humble-ros-ign-*'
sudo apt remove 'libignition-*'
sudo apt autoremove
```

Then reinstall:

```bash
sudo apt install ros-humble-ros-gz-bridge
```

---

# 🧠 Key Learnings

* PX4 uses **GZ (new Gazebo)**
* ROS bridge must match GZ version
* Mixing `ign` and `gz` causes failures
* ROS must be sourced in every terminal

---

# 🔄 System Architecture

```
PX4 SITL
   ↓
Gazebo (GZ)
   ↓
Camera (/camera)
   ↓
ros_gz_bridge
   ↓
ROS2 topic (/camera)
   ↓
OpenCV / AI
   ↓
Offboard Control
   ↓
Drone movement
```

---

# 🚀 Next Steps

* Subscribe to `/camera` using OpenCV
* Apply AI model (YOLO / CNN)
* Detect objects (chimney, pipes, etc.)
* Send movement commands to drone

---

# 🔥 Final Goal

👉 Fully autonomous inspection drone
(Camera + AI + Offboard Control)

---

# 👨‍💻 Author

Gopi Krishnan
AI + Robotics Enthusiast 🚀

---

# ✅ Status

✔ Offboard control working
✔ Drone takeoff successful
✔ Camera streaming working (Gazebo)
✔ ROS2 bridge configured

🚧 Next: AI integration
