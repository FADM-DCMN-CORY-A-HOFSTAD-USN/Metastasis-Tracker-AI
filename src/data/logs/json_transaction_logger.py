import json
import gzip
import os
from datetime import datetime, timezone

class JSONTransactionLogger:
    def __init__(self, target_directory: str = "src/data/logs"):
        """
        Manages high-density JSON serialization and GZIP compression 
        for tracking timeline execution diagnostic histories.
        """
        self.output_dir = target_directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def serialize_and_compress_log(self, step_records_list: list) -> str:
        """
        Converts array data structures into compressed JSON logs.
        Applies a .json.gz file footprint extension to release disk sectors.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"transaction_history_{timestamp}.json.gz"
        full_path = os.path.join(self.output_dir, filename)

        # Structure wrapper transaction envelope framework
        payload = {
            "schema_version": "2026.2.1",
            "transaction_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_records_packed": len(step_records_list),
            "telemetry_matrix": step_records_list
        }

        # Compress string bytes to disk using deep GZIP compression
        json_bytes = json.dumps(payload, indent=2).encode('utf-8')
        with gzip.open(full_path, 'wb') as gzf:
            gzf.write(json_bytes)

        print(f"[+] Compressed data transaction successfully written to: {full_path}")
        return full_path

    @staticmethod
    def read_compressed_json_log(filepath: str) -> dict:
        """Loads and unpacks a gzip compressed JSON transaction package."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Source file missing at: {filepath}")
        with gzip.open(filepath, 'rb') as gzf:
            return json.loads(gzf.read().decode('utf-8'))
