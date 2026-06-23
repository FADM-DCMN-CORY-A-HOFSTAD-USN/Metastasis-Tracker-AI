import struct
import math
import os
import unittest

# =====================================================================
# CUSTOM PHYSIOLOGICAL ERROR EXCEPTIONS
# =====================================================================
class OutOfBoundsAnatomyError(ValueError):
    """Exception raised when patient metrics cross non-viable survival limits."""
    pass

class SensorDataCorruptionError(ValueError):
    """Exception raised when an invalid or null data stream infects the engine loops."""
    pass


class MedicalTelemetryBinaryLogger:
    def __init__(self, output_filepath: str):
        """
        Engine class handling high-density binary serialization for tracking telemetry histories.
        File Structure Schema (Custom .medbin Header Specification):
        - Bytes 0-3: Magic Number Identifier (0x4D454442 -> 'MEDB')
        - Bytes 4-7: Timestep Index (Big-Endian Unsigned Int)
        - Bytes 8-39: Patient Metrics Payload Block (8 Packed Floats)
        """
        self.filepath = output_filepath
        self._initialize_binary_header()

    def _initialize_binary_header(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "wb") as f:
                # Pack Magic Identifier 'MEDB' (4 Bytes)
                f.write(struct.pack(">I", 0x4D454442))

    def log_patient_record(self, timestep: int, patient_id_numeric: int, ph: float, hco3: float, ca: float, force: float, ca_eff: float, pco2: float):
        """
        Serializes and appends a single structured medical record state directly into the binary file.
        Uses big-endian structural packing alignment (Format: >IIfffffff -> 36 bytes per data row)
        """
        with open(self.filepath, "ab") as f:
            packed_data = struct.pack(">IIfffffff", timestep, patient_id_numeric, ph, hco3, ca, force, ca_eff, pco2)
            f.write(packed_data)

    def read_telemetry_history(self) -> list:
        """
        Parses and decodes the medbin stream back into human-readable data sets.
        """
        records = []
        if not os.path.exists(self.filepath):
            return records
            
        with open(self.filepath, "rb") as f:
            magic_number = struct.unpack(">I", f.read(4))[0]
            if magic_number != 0x4D454442:
                raise SensorDataCorruptionError("Critical Error: Aborted read. Corrupt binary header file marker.")
                
            # Iterate through the remaining 36-byte data records
            while True:
                chunk = f.read(36)
                if len(chunk) < 36:
                    break
                unpacked = struct.unpack(">IIfffffff", chunk)
                records.append({
                    "timestep": unpacked[0], "patient_id": unpacked[1], "ph": round(unpacked[2], 3),
                    "hco3": round(unpacked[3], 2), "ca": round(unpacked[4], 2), "force_N": round(unpacked[5], 2),
                    "ca_efficiency_percent": round(unpacked[6], 2), "pco2_mmHg": round(unpacked[7], 1)
                })
        return records


class ExtendedRenalCompensationEngine:
    def __init__(self, kidney_volume_total_cm3: float):
        self.v_kidney = max(10.0, kidney_volume_total_cm3)
        self.kappa_max = 0.08  # Maximum mEq/L/hr compensation accumulation ceiling
        self.km_resp = 15.0    # Km for respiratory pCO2 delta tracking index

    def calculate_renal_respiratory_compensation(self, current_pco2_mmHg: float, hours_elapsed: float) -> float:
        """
        Computes the metabolic bicarbonate generation feedback loop values
        responding to sustained respiratory acidosis.
        """
        # Out-of-bounds safety constraint check gates
        if current_pco2_mmHg <= 0 or current_pco2_mmHg > 200.0:
            raise OutOfBoundsAnatomyError(f"Critical Invalidation: Measured pCO2 value ({current_pco2_mmHg}) represents fatal respiratory limits.")
        if math.isnan(current_pco2_mmHg):
            raise SensorDataCorruptionError("Null or NaN value detected inside the streaming buffer lines.")

        delta_pco2 = max(0.0, current_pco2_mmHg - 40.0)
        if delta_pco2 == 0:
            return 0.0

        # Time-lagged transcriptional efficiency factor (reaches 100% capacity asymptomatically at 48-72 hours)
        time_lag_coefficient = 1.0 - math.exp(-0.05 * hours_elapsed)
        
        # Non-linear Hill equation response profile
        hill_n = 1.8
        response_fraction = math.pow(delta_pco2, hill_n) / (math.pow(delta_pco2, hill_n) + math.pow(self.km_resp, hill_n))
        
        # Complete metabolic generation flux calculation: J = Max * Response * Volume Scaling * Time Factor
        j_renal_comp = self.kappa_max * response_fraction * (self.v_kidney / 250.0) * time_lag_coefficient
        return j_renal_comp


# =====================================================================
# PLATFORM SYSTEM VALIDATION TEST RUNNERS
# =====================================================================
class TestTelemetryAndErrorEngine(unittest.TestCase):
    def setUp(self):
        self.test_filename = "tests/diagnostic_telemetry.medbin"
        self.logger = MedicalTelemetryBinaryLogger(self.test_filename)
        self.renal_engine = ExtendedRenalCompensationEngine(kidney_volume_total_cm3=260.0)

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_binary_logger_io_integrity(self):
        """VERIFICATION: Confirms data preservation across binary save/load cycles."""
        self.logger.log_patient_record(timestep=1, patient_id_numeric=9901, ph=7.352, hco3=22.4, ca=9.6, force=5.2, ca_eff=88.5, pco2=45.0)
        history = self.logger.read_telemetry_history()
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["patient_id"], 9901)
        self.assertEqual(history[0]["ph"], 7.352)

    def test_out_of_bounds_exception_triggers(self):
        """VERIFICATION: Assures the engine flags fatal inputs before they enter calculations."""
        with self.assertRaises(OutOfBoundsAnatomyError):
            self.renal_engine.calculate_renal_respiratory_compensation(current_pco2_mmHg=250.0, hours_elapsed=12.0)
            
        with self.assertRaises(SensorDataCorruptionError):
            self.renal_engine.calculate_renal_respiratory_compensation(current_pco2_mmHg=float('nan'), hours_elapsed=12.0)

if __name__ == "__main__":
    if not os.path.exists("tests"):
        os.makedirs("tests")
    unittest.main()
