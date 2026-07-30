#!/usr/bin/env python3
import rclpy, requests, re, json, time
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration

JOINT_NAMES = ["shoulder_pan_joint","shoulder_lift_joint","elbow_joint","wrist_1_joint","wrist_2_joint","wrist_3_joint"]

WAYPOINTS = {
    "home":         [0.0,  -1.57, 0.0, -1.57,  0.0,  0.0],
    "red_box":      [1.2,  -1.2,  1.0, -1.4,  -1.57, 0.0],
    "pick_height":  [1.2,  -0.8,  1.4, -2.1,  -1.57, 0.0],
    "blue_square":  [-1.2, -1.2,  1.0, -1.4,  -1.57, 0.0],
    "place_height": [-1.2, -0.8,  1.4, -2.1,  -1.57, 0.0],
    "observe":      [0.0,  -2.0,  1.5, -1.0,  -1.57, 0.0],
}

SYSTEM_PROMPT = (
    "You control a UR5e robot arm. Given a natural language command, "
    "output a JSON array of waypoint names to execute in order.\n\n"
    "Available waypoints:\n"
    "- home: safe resting position\n"
    "- red_box: positioned above the red box\n"
    "- pick_height: lowered to grasp level at red box\n"
    "- blue_square: positioned above the blue square\n"
    "- place_height: lowered to place level at blue square\n"
    "- observe: raised to look at the scene\n\n"
    "Rules:\n"
    "- Output ONLY a valid JSON array, nothing else.\n"
    "- Example: [\"home\", \"red_box\", \"pick_height\", \"blue_square\", \"place_height\"]\n"
    "- If the command makes no sense for a robot arm, output: [\"NONE\"]\n"
    "- Never add explanation outside the JSON array"
)

def llm_call(user_text):
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "gemma4:e4b",
        "prompt": user_text,
        "stream": False,
        "system": SYSTEM_PROMPT,
        "options": {"temperature": 0.0, "num_ctx": 512}
    }, timeout=120)
    r.raise_for_status()
    raw = r.json()["response"]
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    return raw.strip()

def resolve_sequence(user_text):
    raw = llm_call(user_text)
    print(f"  [LLM raw]: {raw}")
    match = re.search(r"\[.*?\]", raw, re.DOTALL)
    if not match:
        return None
    try:
        sequence = json.loads(match.group())
    except json.JSONDecodeError:
        return None
    if sequence == ["NONE"] or not sequence:
        return None
    for wp in sequence:
        if wp not in WAYPOINTS:
            print(f"  ! Invalid waypoint: {wp}")
            return None
    return sequence

class WaypointMover(Node):
    def __init__(self):
        super().__init__("waypoint_mover")
        self._client = ActionClient(self, FollowJointTrajectory,
            "/joint_trajectory_controller/follow_joint_trajectory")

    def move_to(self, positions, duration_sec=3.0):
        self._client.wait_for_server()
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = JOINT_NAMES
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=int(duration_sec))
        goal.trajectory.points = [point]
        return self._client.send_goal_async(goal)

def main():
    rclpy.init()
    mover = WaypointMover()
    print("\nUR5e LLM Controller")
    print(f"Waypoints: {list(WAYPOINTS.keys())}\n")

    while True:
        try:
            user_text = input("Command: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_text.lower() in ("quit","exit","q"):
            break
        if not user_text:
            continue

        print("  Thinking...")
        sequence = resolve_sequence(user_text)

        if sequence is None:
            print(f"  X Not recognized: {user_text}\n")
            continue

        print(f"  Sequence: {sequence}")
        for i, wp in enumerate(sequence):
            print(f"  [{i+1}/{len(sequence)}] -> {wp}")
            future = mover.move_to(WAYPOINTS[wp])
            rclpy.spin_until_future_complete(mover, future)
            time.sleep(0.8)

        print("  Complete.\n")

    mover.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
