import math
import os
import yaml
import unittest

class AdvancedAnticoagTraumaEngine:
    def __init__(self, tip_radius_microns: float, plt_count_uL: float, archive_config_path: str = "tests/voxel_settings.yaml"):
        """
        Calculates traumatic fluid cascades while computing platelet plug inhibition
        kinetics under pharmacological anticoagulation profiles.
        """
        self.r_tip_m = tip_radius_microns * 1e-6
        self.a_lesion_initial = math.pi * (self.r_tip_m ** 2)
        self.plt = max(1000.0, plt_count_uL)
        self.rho = 1060.0
        self.c_d = 0.65
        self.config_path = archive_config_path
        self.view_settings = self._load_voxel_view_yaml()

    def _load_voxel_view_yaml(self) -> dict:
        """Parses custom YAML properties to dynamically customize 3D rendering views."""
        if not os.path.exists(self.config_path):
            return {"view_parameters": {"default_elevation": 25.0, "total_rotation_steps": 12, "animation_fps": 8}}
        with open(self.config_path, "r") as stream:
            return yaml.safe_load(stream)

    def simulate_inhibited_hemorrhage(self, initial_p_mmHg: float, drug_inhibition_index: float, time_steps_sec: int) -> dict:
        """
        Models the dynamic bleeding volume rates cascading through a capsular breach,
        factoring in platelet plug inhibition vectors (I_drug).
        """
        i_drug = max(0.0, min(1.0, drug_inhibition_index)) # Bounds inhibition factor between [0.0, 1.0]
        p_vessel_pa = initial_p_mmHg * 133.322
        p_peritoneal_pa = 5.0 * 133.322
        
        cumulative_volume_lost_mL = 0.0
        current_clot_area_m2 = 0.0
        time_series_log = []
        
        k_clot = 1.8e-5
        lambda_pressure_decay = 0.0012

        for t in range(time_steps_sec):
            current_p_pa = p_vessel_pa * math.exp(-lambda_pressure_decay * cumulative_volume_lost_mL)
            delta_p_pa = current_p_pa - p_peritoneal_pa
            
            a_effective = max(0.0, self.a_lesion_initial - current_clot_area_m2)
            
            if delta_p_pa <= 0 or a_effective <= 0:
                leak_rate_mL_s = 0.0
            else:
                leak_rate_m3_s = self.c_d * a_effective * math.sqrt((2.0 * delta_p_pa) / self.rho)
                leak_rate_mL_s = leak_rate_m3_s * 1e6
                
                # Dynamic Thrombus Accumulation modified by the (1.0 - I_drug) pharmacodynamic factor
                d_clot_area = k_clot * (1.0 - i_drug) * (self.plt / 150000.0) * leak_rate_m3_s
                current_clot_area_m2 += d_clot_area
                
            cumulative_volume_lost_mL += leak_rate_mL_s
            
            time_series_log.append({
                "second": t,
                "vessel_pressure_mmHg": round(current_p_pa / 133.322, 1),
                "effective_orifice_area_um2": round(a_effective * 1e12, 2),
                "bleeding_rate_mL_s": round(leak_rate_mL_s, 4)
            })

        return {
            "clotting_suppression_active": i_drug > 0.5,
            "total_blood_loss_volume_mL": round(cumulative_volume_lost_mL, 3),
            "hemostasis_achieved_successfully": a_effective <= 0.0,
            "timeline_logs": time_series_log
        }

# =====================================================================
# SYSTEM STABILITY REPOSITORY VERIFICATIONS
# =====================================================================
class TestAnticoagulationTraumaLimits(unittest.TestCase):
    def test_heparin_bleeding_amplification(self):
        """VERIFICATION: Confirms high drug inhibition yields greater blood loss volumes."""
        # Patient 1: Control Group (0% Pathway Inhibition)
        control_engine = AdvancedAnticoagTraumaEngine(tip_radius_microns=5.0, plt_count_uL=250000.0)
        report_control = control_engine.simulate_inhibited_hemorrhage(initial_p_mmHg=90.0, drug_inhibition_index=0.0, time_steps_sec=15)
        
        # Patient 2: Heparin-Treated Group (85% Pathway Inhibition)
        heparin_engine = AdvancedAnticoagTraumaEngine(tip_radius_microns=5.0, plt_count_uL=250000.0)
        report_heparin = heparin_engine.simulate_inhibited_hemorrhage(initial_p_mmHg=90.0, drug_inhibition_index=0.85, time_steps_sec=15)
        
        self.assertLess(report_control["total_blood_loss_volume_mL"], report_heparin["total_blood_loss_volume_mL"])

if __name__ == "__main__":
    unittest.main()
