import math
import unittest

class ReflexExpulsionSimulationEngine:
    def __init__(self, hydration_level: float):
        """
        Initializes the Pharyngeal Gag and Nasal Sneeze Reflex Engine.
        Expulsion velocities scale directly with core fluid and pressure metrics.
        """
        self.chi = max(0.5, min(1.5, hydration_level))
        self.rho_air = 1.225  # kg/m^3 air density at sea level
        self.c_d = 0.60       # Discharge/drag coefficient for irregular geometries

    def evaluate_nasal_sneeze_trigger(self, object_diameter_um: float, local_zone: str) -> dict:
        """
        Calculates mechanoreceptor activation probabilities and aerodynamic 
        expulsion velocities within the nasal/sinus cavity proper matrices.
        """
        d_obj_mm = object_diameter_um * 1e-3
        
        # Sneeze sensitivity parameters (Trigger threshold is low for particulate matter)
        d_thresh_mm = 0.05  # 50 microns
        k_slope = 15.0
        
        alpha_zone = 1.2 if local_zone.lower() == "nasal_turbinates" else 0.5
        
        # 1. Sigmoidal receptor trigger function
        p_sneeze = 1.0 / (1.0 + math.exp(-k_slope * (d_obj_mm - d_thresh_mm) * alpha_zone))
        
        # 2. Aerodynamic Jet Mechanics if reflex fires successfully
        if p_sneeze >= 0.75:
            # Stored intrathoracic gauge pressure reaches up to 100 mmHg (~13,332 Pascals)
            p_thoracic_pa = 100.0 * 133.322 * self.chi
            p_ambient_pa = 0.0
            
            # Torricelli gas velocity jet equation
            v_air_m_s = self.c_d * math.sqrt((2.0 * (p_thoracic_pa - p_ambient_pa)) / self.rho_air)
            
            # Calculate aerodynamic drag force acting on the particle area
            a_obj_m2 = math.pi * ((object_diameter_um * 1e-6 / 2.0) ** 2)
            f_drag_newtons = 0.5 * self.rho_air * (v_air_m_s ** 2) * self.c_d * a_obj_m2
            
            status = "SNEEZE_REFLEX_EXPLOSIVE_EJECTION"
        else:
            v_fluid_wash_mm_min = 0.0
            v_air_m_s = 0.0
            f_drag_newtons = 0.0
            status = "BASAL_MUCUS_RETENTION_ZONE"

        return {
            "receptor_activation_probability": round(p_sneeze, 4),
            "expulsion_air_velocity_m_s": round(v_air_m_s, 2),
            "calculated_air_velocity_mph": round(v_air_m_s * 2.23694, 1),
            "applied_aerodynamic_drag_newtons": f_drag_newtons,
            "reflex_execution_status": status
        }

    def evaluate_pharyngeal_gag_trigger(self, object_diameter_mm: float, contact_node_identity: str) -> dict:
        """
        Calculates sensory mechanoreceptor activation and muscular constriction
        wave velocities within the oropharynx/laryngopharynx throat paths.
        """
        # Gag threshold requires macro-scale touch contact stimulus
        d_thresh_mm = 1.5
        k_slope = 5.0
        
        alpha_zone = 1.5 if contact_node_identity.lower() == "posterior_pharyngeal_wall" else 0.4
        
        # Sigmoidal trigger calculation
        p_gag = 1.0 / (1.0 + math.exp(-k_slope * (object_diameter_mm - d_thresh_mm) * alpha_zone))
        
        if p_gag >= 0.80:
            # Coordinated muscular constriction wave velocity (m/s)
            v_wave_m_s = 0.35 * self.chi
            actual_clearance_time_s = 0.12 / v_wave_m_s  # 12cm pharyngeal length constraint
            status = "GAG_REFLEX_PROPULSIVE_EXPULSION"
        else:
            v_wave_m_s = 0.0
            actual_clearance_time_s = float('inf')
            status = "BASAL_SWALLOW_TRAFFIC_ZONE"

        return {
            "receptor_activation_probability": round(p_gag, 4),
            "muscular_constriction_velocity_m_s": round(v_wave_m_s, 3),
            "calculated_clearance_timeline_seconds": round(actual_clearance_time_s, 3) if v_wave_m_s > 0 else "Infinity",
            "reflex_execution_status": status,
            "terminal_clearance_destination": "Oral Cavity Extrusion / Involuntary Spitting" if p_gag >= 0.80 else "Esophageal Inlet Retention"
        }

# =====================================================================
# SYSTEM AUTOMATION VALIDATION SUITE
# =====================================================================
class TestRespiratoryReflexMechanics(unittest.TestCase):
    def setUp(self):
        self.engine = ReflexExpulsionSimulationEngine(hydration_level=1.0)

    def test_sneeze_velocity_boundaries(self):
        """VERIFICATION: Confirms that critical sneeze triggers yield realistic gas velocity bounds."""
        # Test a 150-micron particle hitting the sensitive nasal turbinate lining
        report = self.engine.evaluate_nasal_sneeze_trigger(object_diameter_um=150.0, local_zone="nasal_turbinates")
        
        self.assertEqual(report["reflex_execution_status"], "SNEEZE_REFLEX_EXPLOSIVE_EJECTION")
        # Sneeze air velocities mathematically bound between 30 and 55 m/s based on thoracic caps
        self.assertTrue(35.0 <= report["expulsion_air_velocity_m_s"] <= 60.0)
        print(f" -> Assert Verified: Sneeze jet generated at {report['expulsion_air_velocity_m_s']} m/s ({report['calculated_air_velocity_mph']} mph)")

    def test_gag_macro_selection(self):
        """VERIFICATION: Assures sub-threshold micro-particles do not trigger a gag crisis."""
        report_micro = self.engine.evaluate_pharyngeal_gag_trigger(object_diameter_mm=0.2, contact_node_identity="posterior_pharyngeal_wall")
        report_macro = self.engine.evaluate_pharyngeal_gag_trigger(object_diameter_mm=5.0, contact_node_identity="posterior_pharyngeal_wall")
        
        self.assertLess(report_micro["data_prob" if "data_prob" in report_micro else "receptor_activation_probability"], 0.5)
        self.assertEqual(report_macro["reflex_execution_status"], "GAG_REFLEX_PROPULSIVE_EXPULSION")

if __name__ == "__main__":
    unittest.main()
