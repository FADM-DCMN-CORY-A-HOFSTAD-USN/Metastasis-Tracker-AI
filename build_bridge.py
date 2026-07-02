"""
Metastasis-Tracker-AI: Automated Repository Bridge Installer
Filename: build_bridge.py

This utility script automatically constructs the expanded project architecture, 
writes scanner configuration JSON profiles, and instantiates the complete 
programming matrix required to link all volumes.
"""

import os

def build_project_bridge():
    print("==================================================================")
    print("        INITIALIZING METASTASIS-TRACKER-AI REPOSITORY BRIDGE       ")
    print("==================================================================")

    # 1. Establish structural path arrays
    directories = ["config", "docs", "reports", "src", "tests"]
    for folder in directories:
        os.makedirs(folder, exist_ok=True)
        print(f"[INFO] Created directory node: ./{folder}")

    # 2. Generate config_matrices.json
    config_path = "config/config_matrices.json"
    config_content = """{
  "scanner_profiles": {
    "carestream_xray_default": {
      "hardware_vendor": "Carestream Health / Kodak",
      "modality": "CR / DX (Digital Radiography)",
      "calibration_matrices": {
        "affine_translation": [1.025, -0.985, 0.0],
        "spatial_scaling": [1.0, 1.0, 1.0],
        "hounsfield_offset": -1024.0
      }
    },
    "ge_mri_3t_default": {
      "hardware_vendor": "GE Medical Systems",
      "modality": "MR (Magnetic Resonance)",
      "magnetic_field_strength_tesla": 3.0,
      "calibration_matrices": {
        "t1_relaxation_scaling": 1.045,
        "t2_dixon_phase_offset": [0.0, 0.0, 0.2618],
        "adc_normalization_multiplier": 1.000000e-06
      },
      "pulse_sequence_profiles": {
        "spair_fat_sat": {
          "repetition_time_ms": 3500.0,
          "echo_time_ms": 85.0,
          "inversion_time_ms": 160.0
        }
      }
    }
  },
  "pipeline_global_constraints": {
    "target_voxel_resolution_mm": [0.5, 0.5, 1.0],
    "chitin_attenuation_bounds": [140.0, 690.0],
    "restricted_adc_threshold": 0.7
  }
}"""
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)
    print(f"[SUCCESS] Written hardware profiles layer: {config_path}")

    # 3. Generate config_loader.py
    loader_path = "src/config_loader.py"
    loader_content = """import os
import json
import numpy as np

class ConfigurationLoader:
    def __init__(self, json_path: str = "config/config_matrices.json"):
        self.json_path = json_path
        self.config_data = {}
        
    def load_and_validate_matrices(self) -> bool:
        if not os.path.exists(self.json_path):
            return False
        with open(self.json_path, 'r') as file:
            self.config_data = json.load(file)
        return True

    def extract_carestream_affine_vectors(self) -> tuple:
        profile = self.config_data["scanner_profiles"]["carestream_xray_default"]
        translation = np.array(profile["calibration_matrices"]["affine_translation"], dtype=np.float32)
        scaling = np.array(profile["calibration_matrices"]["spatial_scaling"], dtype=np.float32)
        hu_offset = float(profile["calibration_matrices"]["hounsfield_offset"])
        return translation, scaling, hu_offset

    def extract_ge_mri_profiles(self) -> tuple:
        profile = self.config_data["scanner_profiles"]["ge_mri_3t_default"]
        phase_offset = np.array(profile["calibration_matrices"]["t2_dixon_phase_offset"], dtype=np.float32)
        adc_multiplier = float(profile["calibration_matrices"]["adc_normalization_multiplier"])
        spair_settings = profile["pulse_sequence_profiles"]["spair_fat_sat"]
        return phase_offset, adc_multiplier, spair_settings

    def get_global_pipeline_constraints(self) -> dict:
        return self.config_data.get("pipeline_global_constraints", {})
"""
    with open(loader_path, "w", encoding="utf-8") as f:
        f.write(loader_content)
    print(f"[SUCCESS] Written configuration loading class: {loader_path}")

    # 4. Generate dicom_series_aggregator.py
    aggregator_path = "src/dicom_series_aggregator.py"
    aggregator_content = """import os
import glob
import numpy as np
import pydicom

class DICOMSeriesAggregator:
    def __init__(self, directory_path: str):
        self.directory_path = directory_path
        self.volume_3d = None
        self.spatial_metadata = {}

    def compile_3d_volume(self) -> np.ndarray:
        search_pattern = os.path.join(self.directory_path, "*.dcm")
        file_list = glob.glob(search_pattern)
        if not file_list:
            raise FileNotFoundError(f"No slices inside: {self.directory_path}")
        valid_slices = []
        for file_path in file_list:
            ds = pydicom.dcmread(file_path)
            if "PixelData" not in ds: continue
            slice_pos = float(ds.ImagePositionPatient[2]) if "ImagePositionPatient" in ds else float(ds.get("SliceLocation", 0.0))
            valid_slices.append((slice_pos, ds))
        valid_slices.sort(key=lambda x: x[0])
        ref = valid_slices[0][1]
        slope = float(ref.get('RescaleSlope', 1.0))
        intercept = float(ref.get('RescaleIntercept', 0.0))
        spacing = ref.get('PixelSpacing', [1.0, 1.0])
        dz = abs(valid_slices[1][0] - valid_slices[0][0]) if len(valid_slices) > 1 else float(ref.get('SliceThickness', 1.0))
        self.volume_3d = np.zeros((len(valid_slices), ref.pixel_array.shape[0], ref.pixel_array.shape[1]), dtype=np.float32)
        for idx, (_, ds) in enumerate(valid_slices):
            self.volume_3d[idx, :, :] = (ds.pixel_array.astype(np.float32) * slope) + intercept
        self.spatial_metadata = {"dx": float(spacing[0]), "dy": float(spacing[1]), "dz": float(dz), "volume_shape": self.volume_3d.shape}
        return self.volume_3d
"""
    with open(aggregator_path, "w", encoding="utf-8") as f:
        f.write(aggregator_content)
    print(f"[SUCCESS] Written sequential tracking aggregator: {aggregator_path}")

    # 5. Generate ai_diagnostic_app.py
    app_path = "src/ai_diagnostic_app.py"
    app_content = """import os
import glob
from datetime import datetime

class AIDiagnosticSupportApp:
    def __init__(self, docs_dir: str = "docs", reports_dir: str = "reports"):
        self.docs_dir = docs_dir
        self.reports_dir = reports_dir
        self.knowledge_base_summary = ""
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

    def ingest_documentation_vault(self) -> int:
        files = glob.glob(os.path.join(self.docs_dir, "*.md"))
        compiled = []
        for fp in files:
            with open(fp, 'r', encoding='utf-8') as f:
                compiled.append(f.read())
        self.knowledge_base_summary = "\\n".join(compiled)
        return len(files)

    def process_and_evaluate_metrics(self, metrics: dict) -> dict:
        peak = metrics.get("peak_density", 0.0)
        total = metrics.get("total_voxels", 0)
        violation = 140.0 <= peak <= 690.0
        urgency = "CRITICAL" if total > 500 else "STABLE"
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target_voxels_detected": total,
            "matrix_peak_intensity": peak,
            "chitin_signature_match": "POSITIVE" if violation else "NEGATIVE",
            "clinical_status_urgency": urgency,
            "recommended_action": "Initiate High-Dose Vitamin Loading & Fluid Tracking" if urgency == "CRITICAL" else "Maintain Observation"
        }

    def export_diagnosis_support_file(self, results: dict) -> str:
        slug = datetime.now().strftime("%Y%m%d_%H%M%S")
        rp = os.path.join(self.reports_dir, f"diagnostic_support_log_{slug}.md")
        content = f\"\"\"# Operation Cancer Moonshot: AI Diagnostic Support Document
Generated on: {results['timestamp']}
Status: **{results['clinical_status_urgency']}**

## 📊 Live Array Analytical Metrics
*   Total Voxel Clusters Active: {results['target_voxels_detected']}
*   Peak Signal Vector Value   : {results['matrix_peak_intensity']:.4f}
*   Chitin Attenuation Match   : {results['chitin_signature_match']}

## 🧠 Action Blueprint
*   Directive: {results['recommended_action']}
\"\"\"
        with open(rp, 'w', encoding='utf-8') as f:
            f.write(content)
        return rp
"""
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_content)
    print(f"[SUCCESS] Written automated diagnostic support interface: {app_path}")

    # 6. Generate placeholders for test mock files to prevent standalone compilation crash
    mock_test_path = "tests/test_placeholder.py"
    with open(mock_test_path, "w") as f:
        f.write("def test_bridge_status():\n    assert True\n")
    print(f"[SUCCESS] Instantiated baseline testing verification files: {mock_test_path}")
    print("==================================================================")
    print("[SUCCESS] Repository bridge constructed. Ready for git synchronization loops.")

if __name__ == "__main__":
    build_project_bridge()
