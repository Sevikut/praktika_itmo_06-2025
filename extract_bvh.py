from bvh import Bvh
import json
import numpy as np
import os

bvh_file = "/home/ubuntu/Documents/isaac/ubisoft-laforge-animation-dataset/output/BVH/dance1_subject1.bvh"

if not os.path.exists(bvh_file):
    raise FileNotFoundError(f"no bvh at: {bvh_file}")

with open(bvh_file, "r") as f:
    mocap = Bvh(f.read())

frames = mocap.frames
joint_names = mocap.get_joints_names()
frame_time = mocap.frame_time
motion_data = []

frames_array = np.array(frames)

for i, frame in enumerate(frames_array):
    time = i * frame_time
    frame_dict = {}
    
    for j, name in enumerate(joint_names):
        start_idx = j * 3
        frame_dict[name] = frame[start_idx:start_idx+3].tolist()
    
    motion_data.append({
        "time": round(time, 4),
        "joints": frame_dict
    })

output_file = "human_dance_poses.json"
with open(output_file, "w") as f:
    json.dump(motion_data, f, indent=4)

print(f"converted bvh to json here {output_file}")