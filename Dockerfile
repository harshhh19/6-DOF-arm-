FROM osrf/ros:lyrical-desktop

ENV DEBIAN_FRONTEND=noninteractive
ENV QT_X11_NO_MITSHM=1

# Install Gazebo Harmonic
RUN apt-get update && apt-get install -y \
    curl gnupg lsb-release mesa-utils libgl1 libglx-mesa0 libglvnd0 libx11-6 \
    && curl -sSL https://packages.osrfoundation.org/gazebo.gpg -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -sc) main" > /etc/apt/sources.list.d/gazebo-stable.list \
    && apt-get update && apt-get install -y gz-harmonic ros-lyrical-ros-gz \
    && rm -rf /var/lib/apt/lists/*

# Install required tools
RUN apt-get update && apt-get install -y \
    python3-pip python3-colcon-common-extensions \
    ros-lyrical-ur-description \
    ros-lyrical-ur-robot-driver \
    ros-lyrical-controller-manager \
    ros-lyrical-joint-state-broadcaster \
    ros-lyrical-joint-trajectory-controller \
    && rm -rf /var/lib/apt/lists/*

# Set up the workspace
WORKDIR /workspace
COPY src /workspace/src
COPY waypoint_mover.py /workspace/

# Build the workspace
RUN /bin/bash -c "source /opt/ros/lyrical/setup.bash && colcon build --symlink-install"

# Source the workspace in .bashrc
RUN echo "source /opt/ros/lyrical/setup.bash" >> ~/.bashrc \
    && echo "source /workspace/install/setup.bash" >> ~/.bashrc

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
