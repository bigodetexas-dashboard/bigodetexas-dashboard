import json
import os
import time
import subprocess

# 1. Create dummy data
data = {
    "points": [
        {"x": 7500, "z": 7500, "timestamp": time.time()},
        {"x": 8000, "z": 8000, "timestamp": time.time()},
        {"x": 2000, "z": 14000, "timestamp": time.time()}, # NWAF approx
        {"x": 13000, "z": 3000, "timestamp": time.time()}  # Electro approx
    ]
}

with open("heatmap_data.json", "w") as f:
    json.dump(data, f)

print("Created dummy heatmap_data.json")

# 2. Run generation script
print("Running generate_heatmap.py...")
result = subprocess.run(["python", "generate_heatmap.py"], capture_output=True, text=True)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)

# 3. Check output
if os.path.exists("heatmap.png"):
    print("SUCCESS: heatmap.png generated.")
else:
    print("FAILURE: heatmap.png not found.")
