import os
import math
import matplotlib.pyplot as plt

# Defensive library checking for cross-module reliability
try:
    import h5py
    H5PY_AVAILABLE = True
except ImportError:
    H5PY_AVAILABLE = False
    import json # Fallback parsing mechanism if h5py is missing in raw test loops

class HDF5PulmonaryVisualizer:
    def __init__(self, h5_filepath: str = "tests/pipeline_telemetry.h5", output_img_path: str = "docs/pulmonary_trends.png"):
        """
        Parses multi-dimensional HDF5 simulation datasets and auto-generates
        diagnostic timeline charts tracking lung compliance decay.
        """
        self.h5_path = h5_filepath
        self.out_path = output_img_path

    def load_and_render_trends(self) -> bool:
        timesteps = []
        fluid_loss = []
        compliance = []
        vent_rate = []

        # 1. Extraction Pipeline Layer
        if not H5PY_AVAILABLE:
            mock_json = self.h5_path + ".mockjson"
            if not os.path.exists(mock_json): return False
            with open(mock_json, "r") as f:
                records = json.load(f)["data"]
        else:
            if not os.path.exists(self.h5_path): return False
            with h5py.File(self.h5_path, "r") as h5f:
                records = h5f["time_series_log"][:]

        # 2. Map raw array columns to physiological metrics
        # Baseline reference parameters for compliance/vent calculation loops
        c_base = 100.0
        rr_base = 12.0
        
        for row in records:
            t = row[0]
            # Use Column 5 (Collapse Pressure) as a proxy for alveolar fluid flooding volume metrics
            v_fluid_mL = row[5] * 0.25 
            
            # Compliance non-linear decay: C = C_base * e^(-0.001 * V)
            c_lung = c_base * math.exp(-0.0015 * v_fluid_mL)
            # Vent adaptation: RR = RR_base + 0.35 * (C_base - C_lung)
            rr_vent = rr_base + 0.35 * (c_base - c_lung)

            timesteps.append(t)
            fluid_loss.append(v_fluid_mL)
            compliance.append(c_lung)
            vent_rate.append(rr_vent)

        # 3. Matplotlib Layout Compilation Matrix
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
        fig.suptitle("PULMONARY TISSUE COMPLIANCE & VENTILATION FEEDBACK TRAJECTORY", fontsize=12, fontweight='bold')

        # Subplot 1: Accumulating Fluid Flooding Volume
        ax1.plot(timesteps, fluid_loss, color='navy', marker='o', linestyle='-', linewidth=2)
        ax1.set_ylabel("Fluid Transudation (mL)")
        ax1.grid(True, linestyle=':')

        # Subplot 2: Lung Compliance Decay Curve
        ax2.plot(timesteps, compliance, color='crimson', marker='s', linestyle='--', linewidth=2)
        ax2.axhline(y=20.0, color='darkorange', linestyle=':', label='ARDS Crisis Threshold')
        ax2.set_ylabel("Compliance (mL/cmH2O)")
        ax2.grid(True, linestyle=':')
        ax2.legend(loc="upper right")

        # Subplot 3: Ventilator Adaptive Respiratory Rate Response
        ax3.plot(timesteps, vent_rate, color='teal', marker='^', linestyle='-', linewidth=2)
        ax3.set_ylabel("Vent Rate (breaths/min)")
        ax3.set_xlabel("Simulation Timeline Steps (seconds)")
        ax3.grid(True, linestyle=':')

        plt.tight_layout()
        
        # Verify destination path folders are available before committing sectors
        out_dir = os.path.dirname(self.out_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        plt.savefig(self.out_path, dpi=150)
        plt.close()
        print(f"[+] Multi-panel trend visualization chart rendered successfully at: {self.out_path}")
        return True

if __name__ == "__main__":
    # Ingest baseline file parameters for standalone diagnostic execution checks
    visualizer = HDF5PulmonaryVisualizer()
    visualizer.load_and_render_trends()
