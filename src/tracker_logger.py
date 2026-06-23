#!/usr/bin/env python3
import os
import json
from datetime import datetime

class TrackerDiagnosticLogger:
    def __init__(self, filename_prefix="tracker_diagnostics"):
        """
        Manages the generation of standardized JSON telemetry records.
        """
        # Resolve path boundaries to ensure file generation drops into outbound/
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.outbound_dir = os.path.join(self.base_dir, "outbound")
        
        # Proactively ensure the output directory exists
        os.makedirs(self.outbound_dir, exist_ok=True)
        
        # Generate a unique timestamped file name for this simulation run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(self.outbound_dir, f"{filename_prefix}_{timestamp}.json")
        
        # Initialize an empty array structure inside the runtime file
        self.initialize_log_file()

    def initialize_log_file(self):
        """
        Sets up the baseline JSON structure with metadata blocks.
        """
        initial_payload = {
            "simulation_metadata": {
                "engine_version": "1.4.2-Headless",
                "execution_timestamp": datetime.now().isoformat(),
                "record_format": "Standardized-Diagnostic-v2"
            },
            "telemetry_steps": []
        }
        with open(self.log_file_path, "w", encoding="utf-8") as f:
            json.dump(initial_payload, f, indent=2)

    def log_step(self, location_id, local_env, report_output, internal_metrics):
        """
        Appends a discrete, standardized step entry into the active JSON file.
        """
        # Formulate a clean, standardized data dictionary payload
        step_record = {
            "timestamp_offset_iso": datetime.now().isoformat(),
            "tracking_node": location_id,
            "environmental_context": {
                "temperature_c": local_env.get("temperature", 14.0),
                "turbulence_factor": local_env.get("turbulence", 0.0),
                "ph_level": local_env.get("ph", 8.1)
            },
            "engine_status": report_output.get("status", "UNKNOWN"),
            "biomass_metrics": {
                "accumulated_protein_vol_mm3": internal_metrics.get("protein_vol", 0.0),
                "current_condition_factor": internal_metrics.get("condition_factor", 1.0)
            },
            "generation_yield_vector": report_output.get("larval_pool_generation", [0.0, 0.0, 0.0, 0.0])
        }

        # Thread-safe read/write modification cycle
        try:
            with open(self.log_file_path, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data["telemetry_steps"].append(step_record)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
        except IOError as e:
            print(f"⚠️  Logging Warning: Could not write step diagnostic record to disk: {e}")
