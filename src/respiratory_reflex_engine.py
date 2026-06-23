import math
import json
import os
import unittest
from datetime import datetime, timezone

class IntegratedRespiratoryReflexEngine:
    def __init__(self, height_cm: float, weight_kg: float, hydration_level: float):
        """
        Engine module calculating the fluid dynamics, physics forces, and 
        EHR clinical reporting logs for respiratory clearance reflexes.
        """
        self.height_m = height_cm / 100.0
        self.weight = weight_kg
        self.chi = max(0.5, min(1.5, hydration_level))
        
        # Fundamental fluid constants
        self.rho_air = 1.225  # kg/m^3 air density at sea level
        self.c_d = 0.60       # Discharge and aerodynamic drag coefficient

        # Generate base tracheal dimensions (Gen 0 reference) matching Weibel specs
        self.r_trachea_m = 0.006 * self.height_m

    def evaluate_lower_airway_cough(self, generation: int, object_diameter_mm: float, local_ph: float) -> dict:
        """
        Tracks lower conducting airway zones (Generations 0 to 10).
        Calculates cough trigger odds, air velocities, and drag force extraction.
        """
        z = max(0, min(10, generation))
        
        # 1. Compute dynamic localized lumen diameter threshold
        r_z_m = self.r_trachea_m * (2.0 ** (-z / 3.0))
        d_lumen_mm = r_z_m * 2.0 * 1000.0
        d_min_threshold_mm = d_lumen_mm * 0.05  # Trigger requires 5% lumen occlusion
        
        # 2. Evaluate sensory trigger probability via a sigmoidal step curve
        k_tuss = 12.0
        eta_ph = 1.0 if local_ph >= 7.35 else max(0.1, 1.0 - 3.5 * (7.35 - local_ph))
        p_cough = (1.0 / (1.0 + math.exp(-k_tuss * (object_diameter_mm - d_min_threshold_mm)))) * eta_ph

        if p_cough >= 0.80:
            # Active compression pressure drive (120 mmHg transformed to Pascals)
            delta_p_pa = 120.0 * 133.322 * self.chi
            v_air_m_s = self.c_d * math.sqrt((2.0 * delta_p_pa) / self.rho_air)
            
            # 3. Calculate aerodynamic drag force vector
            r_obj_m = (object_diameter_mm / 2.0) * 1e-3
            a_obj_m2 = math.pi * (r_obj_m ** 2)
            f_drag_newtons = 0.5 * self.rho_air * (v_air_m_s ** 2) * self.c_d * a_obj_m2
            
            # Adhesion restriction boundary check
            sigma_mucus_adhesion = 0.012  # Newtons
            clearance_active = f_drag_newtons > sigma_mucus_adhesion
            status = "COUGH_EXPLOSIVE_CLEARANCE_ACTIVE" if clearance_active else "PARTICLE_RETAINED_HIGH_MUCUS_ADHESION"
        else:
            v_air_m_s = 0.0
            f_drag_newtons = 0.0
            status = "BASAL_CONDUCTING_FLOW_ZONE"

        return {
            "vessel_generation": z,
            "local_lumen_diameter_mm": round(d_lumen_mm, 3),
            "receptor_activation_probability": round(p_cough, 4),
            "expulsion_air_velocity_m_s": round(v_air_m_s, 2),
            "applied_aerodynamic_drag_newtons": round(f_drag_newtons, 6),
            "reflex_execution_status": status
        }

    def evaluate_upper_airway_reflex_gate(self, object_diameter_mm: float, anatomical_node: str) -> dict:
        """
        Tracks Upper Respiratory Zones: Gag Reflex (Throat/Pharynx) 
        and Sneeze Reflex (Nasal/Sinus Matrix Cavities).
        """
        node_key = anatomical_node.lower()
        
        if "sinus" in node_key or "nasal" in node_key:
            # Nasal Sneeze Reflex Core Math
            d_thresh_mm = 0.05  # Trigger requires only 50-micron stimulus particle matter
            p_sneeze = 1.0 / (1.0 + math.exp(-25.0 * (object_diameter_mm - d_thresh_mm)))
            
            if p_sneeze >= 0.85:
                delta_p_sneeze = 100.0 * 133.322 * self.chi
                v_air_m_s = self.c_d * math.sqrt((2.0 * delta_p_sneeze) / self.rho_air)
                status = "SNEEZE_EXPLOSIVE_EJECTION"
            else:
                v_air_m_s = 0.0
                status = "BASAL_SINUS_RETENTION"
                
            return {
                "reflex_type": "NASAL_SNEEZE_REFLEX", "trigger_probability": round(p_sneeze, 4),
                "expulsion_velocity_m_s": round(v_air_m_s, 2), "execution_status": status,
                "destination": "External Environment Dislodgement" if v_air_m_s > 0 else "Nasal Lumen Trapped"
            }
            
        else:
            # Pharyngeal Gag Reflex Core Math
            d_thresh_mm = 1.5  # Requires macroscopic mechanical mass contact
            p_gag = 1.0 / (1.0 + math.exp(-5.0 * (object_diameter_mm - d_thresh_mm)))
            
            if p_gag >= 0.80:
                v_wave_m_s = 0.35 * self.chi
                status = "GAG_REFLEX_PROPULSIVE_EXPULSION"
            else:
                v_wave_m_s = 0.0
                status = "BASAL_PHARYNGEAL_TRAFFIC"
                
            return {
                "reflex_type": "PHARYNGEAL_GAG_REFLEX", "trigger_probability": round(p_gag, 4),
                "expulsion_velocity_m_s": round(v_wave_m_s, 3), "execution_status": status,
                "destination": "Oral Cavity Extrusion / Spitting" if v_wave_m_s > 0 else "Esophageal Inlet Cascade"
            }

    def commit_fhir_observation_record(self, patient_id: str, reflex_report: dict, output_path: str = "src/data/fhir/reflex_observation.json") -> str:
        """
        Constructs and writes a verified HL7 FHIR R4 Observation resource payload
        logging the respiratory clearance activation event metrics.
        """
        iso_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        fhir_observation = {
            "resourceType": "Observation",
            "id": f"obs-reflex-{patient_id}",
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://hl7.org",
                    "code": "procedure",
                    "display": "Procedure"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "9279-1",
                    "display": "Respiratory rate Respiratory system"
                }],
                "text": f"Somatic Respiratory Clearance Reflex Execution Trigger: {reflex_report.get('reflex_type', 'COUGH_REFLEX')}"
            },
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": iso_ts,
            "valueString": reflex_report["execution_status"] if "execution_status" in reflex_report else reflex_report["reflex_execution_status"],
            "component": [
                {
                    "code": {"coding": [{"system": "http://local-simulation-identifiers/codes", "code": "EXP_VEL", "display": "Exiting Air Fluid Velocity"}]},
                    "valueQuantity": {"value": reflex_report.get("expulsion_air_velocity_m_s", reflex_report.get("expulsion_velocity_m_s", 0.0)), "unit": "m/s"}
                },
                {
                    "code": {"coding": [{"system": "http://local-simulation-identifiers/codes", "code": "TRIG_PROB", "display": "Sensory Receptor Trigger Probability"}]},
                    "valueQuantity": {"value": reflex_report.get("receptor_activation_probability", reflex_report.get("trigger_probability", 0.0)), "unit": "fraction"}
                }
            ]
        }

        dir_name = os.path.dirname(output_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(output_path, "w") as f:
            json.dump(fhir_observation, f, indent=2)
        return output_path


# =====================================================================
# CONTINUOUS INTEGRATION VERIFICATION SUITE
# =====================================================================
class TestRespiratoryTraumaReflexes(unittest.TestCase):
    def setUp(self):
        self.engine = IntegratedRespiratoryReflexEngine(height_cm=175.0, weight_kg=72.0, hydration_level=1.0)
        self.test_json_path = "src/data/fhir/test_reflex.json"

    def tearDown(self):
        if os.path.exists(self.test_json_path):
            os.remove(self.test_json_path)

    def test_cough_aerodynamic_bounds(self):
        """VERIFICATION: Confirms lower airway branches trigger high-priority gas velocities."""
        report = self.engine.evaluate_lower_airway_cough(generation=3, object_diameter_mm=2.5, local_ph=7.40)
        self.assertEqual(report["reflex_execution_status"], "COUGH_EXPLOSIVE_CLEARANCE_ACTIVE")
        self.assertTrue(35.0 <= report["expulsion_air_velocity_m_s"] <= 60.0)

    def test_fhir_logging_persistence(self):
        """VERIFICATION: Validates error-free serialization of clinical observation resource models."""
        report = self.engine.evaluate_upper_airway_reflex_gate(object_diameter_mm=5.0, anatomical_node="pharyngeal_throat")
        written_path = self.engine.commit_fhir_observation_record(patient_id="pat-09", reflex_report=report, output_path=self.test_json_path)
        
        self.assertTrue(os.path.exists(written_path))
        with open(written_path, "r") as f:
            data = json.load(f)
        self.assertEqual(data["resourceType"], "Observation")
        self.assertEqual(data["valueString"], "GAG_REFLEX_PROPULSIVE_EXPULSION")

if __name__ == "__main__":
    unittest.main()
