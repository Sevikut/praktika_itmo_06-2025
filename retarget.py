import pybullet as p
import os
import json
import numpy as np
from pathlib import Path

def resolve_urdf_path(urdf_path):
    if os.path.exists(urdf_path):
        return urdf_path
    
    script_dir = Path(__file__).parent
    relative_path = script_dir / urdf_path
    if relative_path.exists():
        return str(relative_path)
    downloads_path = Path.home() / "Downloads" / urdf_path

    if downloads_path.exists():
        return str(downloads_path)
    
    raise FileNotFoundError(f"no urdf in:\n"
                          f"- {urdf_path}\n"
                          f"- {relative_path}\n"
                          f"- {downloads_path}")

def load_robot_model(urdf_path):
    resolved_path = resolve_urdf_path(urdf_path)
    print(f"loading the urdf: {resolved_path}")
    if not os.access(resolved_path, os.R_OK):
        raise PermissionError(f"no -r permissions for: {resolved_path}")
    
    physics_client = p.connect(p.DIRECT)
    try:
        robot_id = p.loadURDF(
            resolved_path,
            basePosition=[0, 0, 0.5],
            baseOrientation=p.getQuaternionFromEuler([0, 0, 0]),
            useFixedBase=True,
            flags=p.URDF_USE_SELF_COLLISION
        )
        print(f"loaded robot with {p.getNumJoints(robot_id)} joints")
        return robot_id
    except p.error as e:
        p.disconnect()
        raise RuntimeError(f"fail to load urdf: {str(e)}\n"
                          f"file exists: {os.path.exists(resolved_path)}\n"
                          f"file size: {os.path.getsize(resolved_path) if os.path.exists(resolved_path) else 0} bytes")

def main():
    URDF_FILENAME = "anymal.urdf"
    HUMAN_MOTION_FILE = "human_dance_poses.json"
    OUTPUT_FILE = "robot_dance_poses.json"
    
    try:
        robot_id = load_robot_model(URDF_FILENAME)
        if not os.path.exists(HUMAN_MOTION_FILE):
            raise FileNotFoundError(f"no human dance poses at {HUMAN_MOTION_FILE}")
        
        with open(HUMAN_MOTION_FILE, 'r') as f:
            human_motion = json.load(f)

        num_joints = p.getNumJoints(robot_id)
        robot_motion = []
        
        for frame in human_motion:
            t = frame['time']
            base_angle = 0.5 * np.sin(t * 2 * np.pi)

            joint_positions = {
                p.getJointInfo(robot_id, i)[1].decode('utf-8'): float(base_angle * (i+1)/num_joints)
                for i in range(num_joints)
                if p.getJointInfo(robot_id, i)[2] != p.JOINT_FIXED
            }
            
            robot_motion.append({
                'time': t,
                'joints': joint_positions
            })
        

        with open(OUTPUT_FILE, 'w') as f:
            json.dump(robot_motion, f, indent=4)
        
        print(f"retargeted motion in {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"error: {str(e)}")
    finally:
        if 'p' in locals() and p.isConnected():
            p.disconnect()

if __name__ == "__main__":
    main()