# 🤖 LLM-Controlled UR5e Robotic Arm in Gazebo

[![ROS 2](https://img.shields.io/badge/ROS_2-Lyrical-blue.svg)](https://docs.ros.org/en/lyrical/)
[![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic-orange.svg)](https://gazebosim.org/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue?logo=docker)](https://www.docker.com/)

A demonstration of integrating Large Language Models (LLMs) with ROS 2 and Gazebo to control a Universal Robots UR5e arm. The project translates natural language into predefined joint configurations to command the robot through ROS 2 action calls.

## 🚀 Features
- **LLM Integration**: Uses `gemma2:4b` (via Ollama) to process natural language waypoints.
- **Gazebo Harmonic Simulation**: Highly realistic simulation of a UR5e manipulator.
- **Dockerized Environment**: fully plug-and-play setup for effortless deployment.
- **ROS 2 Action Servers**: Efficient and robust command execution via `/joint_trajectory_controller`.

## 📦 Plug-and-Play Installation (Docker)
The easiest way to run this project is using Docker. You only need Docker, Docker Compose, and the NVIDIA Container Toolkit installed.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/ur5e-llm-simulation.git
   cd ur5e-llm-simulation
   ```

2. **Allow X11 Forwarding (for the Gazebo GUI):**
   ```bash
   xhost +local:docker
   ```

3. **Launch the Simulation:**
   ```bash
   docker-compose up
   ```
   *(Note: The first run will download the ROS 2 environment and build the workspace automatically).*

## 🎮 Usage

Once the Gazebo simulation is running, open a new terminal to start the LLM waypoint mover script:

```bash
docker exec -it ur5e-sim python3 /workspace/waypoint_mover.py
```

Provide your text commands, and watch the UR5e arm move to the desired locations!

---

*This project was developed for a robotics showcase, bridging the gap between cutting-edge AI language models and classical robotic control architectures.*
