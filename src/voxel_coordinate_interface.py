import os
import numpy as np
import matplotlib.pyplot as plt

class OcularVoxelStructuralInterface:
    def __init__(self, grid_resolution: int = 32):
        """
        Models and visualizes raw spatial tracking coordinates directly as 
        discrete, multi-dimensional 3D voxel density arrays.
        """
        self.res = grid_resolution
        # Initialize an empty 3D grid matrix mapping boundaries
        self.voxel_grid = np.zeros((self.res, self.res, self.res), dtype=bool)

    def inject_tracking_coordinate_node(self, x_normalized: float, y_normalized: float, z_normalized: float):
        """
        Maps normalized anatomical coordinates (0.0 to 1.0) into discrete voxel grid matrix cells.
        """
        # Convert floating coordinates vectors directly into integer indices
        idx_x = int(max(0.0, min(1.0, x_normalized)) * (self.res - 1))
        idx_y = int(max(0.0, min(1.0, y_normalized)) * (self.res - 1))
        idx_z = int(max(0.0, min(1.0, z_normalized)) * (self.res - 1))
        
        self.voxel_grid[idx_x, idx_y, idx_z] = True

    def render_voxel_diagnostic_plot(self, output_img_path: str = "docs/voxel_spatial_map.png"):
        """
        Renders a volumetric 3D voxel grid visualization layout mapping spatial densities.
        """
        if not np.any(self.voxel_grid):
            print("[-] Render warning: Grid matrix contains zero active coordinates nodes.")
            return False

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Draw active volumetric voxels sequentially across grid structures
        ax.voxels(self.voxel_grid, facecolors='crimson', edgecolors='black', alpha=0.8)
        
        ax.set_title("3D SPATIAL ANATOMICAL VOXEL GRID TRACKING MATRIX", fontsize=12, fontweight='bold')
        ax.set_xlabel("X-Axis Spatial Vector (Lateral Alignment)")
        ax.set_ylabel("Y-Axis Spatial Vector (Anteroposterior)")
        ax.set_zlabel("Z-Axis Spatial Vector (Axial Height Column)")
        
        output_dir = os.path.dirname(output_img_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        plt.savefig(output_img_path, dpi=150)
        plt.close()
        print(f"[+] Spatial 3D Voxel array successfully plotted at: {output_img_path}")
        return True

if __name__ == "__main__":
    # Generate mock coordinates along a trajectory curve path vector
    voxel_mapper = OcularVoxelStructuralInterface(grid_resolution=24)
    
    print("Simulating spatial structural trajectory tracking vectors...")
    for step in range(15):
        # Maps a rising helix path curve vector mimicking axial vertebral routing columns
        t_factor = step / 15.0
        voxel_mapper.inject_tracking_coordinate_node(
            x_normalized=0.5 + 0.2 * math.sin(t_factor * math.pi * 2),
            y_normalized=0.5 + 0.2 * math.cos(t_factor * math.pi * 2),
            z_normalized=t_factor
        )
        
    voxel_mapper.render_voxel_diagnostic_plot()
