import json
import matplotlib.pyplot as plt
import os
import sys

def generate_heatmap():
    data_file = "heatmap_data.json"
    output_file = "heatmap.png"
    
    if not os.path.exists(data_file):
        print("No data file found.")
        return False

    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
            
        points = data.get("points", [])
        if not points:
            print("No points to plot.")
            return False
            
        x = [p['x'] for p in points]
        z = [p['z'] for p in points]
        
        # DayZ Chernarus Map Size approx 15360x15360
        plt.figure(figsize=(10, 10), facecolor='#2f3136')
        ax = plt.gca()
        ax.set_facecolor('#2f3136')
        
        # Plot points
        # Invert Z axis because DayZ map coordinates (0,0) is bottom-left but image logic might differ
        # Usually DayZ maps are plotted with X horizontal and Z vertical.
        # Let's assume standard plotting.
        
        plt.scatter(x, z, c='red', alpha=0.5, s=10, edgecolors='none')
        
        plt.xlim(0, 15360)
        plt.ylim(0, 15360)
        plt.axis('off') # Hide axis
        
        # Add title
        plt.title("BigodeTexas - PvP Heatmap", color='white', fontsize=20)
        
        plt.tight_layout()
        plt.savefig(output_file, facecolor='#2f3136')
        plt.close()
        
        print(f"Heatmap saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error generating heatmap: {e}")
        return False

if __name__ == "__main__":
    generate_heatmap()
