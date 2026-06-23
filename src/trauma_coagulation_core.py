import math
import unittest

class AdvancedCoagulationHemorrhageEngine:
    def __init__(self, tip_radius_microns: float, plt_count_uL: float, clotting_factor_index: float = 1.0):
        """
        Initializes the dynamic fluid hemorrhage engine coupled to 
        biochemical platelet aggregation and clotting profiles.
        """
        self.r_tip_m = tip_radius_microns * 1e-6
        self.a_lesion_initial = math.pi * (self.r_tip_m ** 2)
        self.plt = max(1000.0, plt_count_uL)       # Clinical normal: 150k - 450k
        self.alpha_factor = clotting_factor_index   # 1.0 = normal, 0.0 = hemophilia/heparin
        self.rho = 1060.0                           # kg/m^3 blood density
        self.c_d = 0.62                             # Orifice coefficient

    def simulate_clotted_hemorrhage(self, initial_p_vessel_mmHg: float, time_steps_sec: int) -> dict:
        """
        Simulates active bleeding while calculating real-time platelet plug growth,
        effective area reduction, and systemic leakage cessation profiles.
        """
        p_vessel_pa = initial_p_vessel_mmHg * 133.322
        p_int_pa = 5.0 * 133.322 # Baseline interstitial counterpressure
        
        cumulative_volume_lost_mL = 0.0
        current_clot_area_m2 = 0.0
        time_series_log = []
        
        # Kinetic parameters for platelet deposition scaling
        k_clot = 1.8e-5 
        lambda_pressure_decay = 0.0012

        for t in range(time_steps_sec):
            # 1. Calculate pressure decay due to fluid exit
            current_p_pa = p_vessel_pa * math.exp(-lambda_pressure_decay * cumulative_volume_lost_mL)
            delta_p_pa = current_p_pa - p_int_pa
            
            # 2. Derive effective hole size left open by the aggregating clot matrix
            a_effective = max(0.0, self.a_lesion_initial - current_clot_area_m2)
            
            if delta_p_pa <= 0 or a_effective <= 0:
                leak_rate_mL_s = 0.0
                current_p_pa = p_int_pa
            else:
                # Torricelli flow velocity applied to the shrinking orifice geometry
                leak_rate_m3_s = self.c_d * a_effective * math.sqrt((2.0 * delta_p_pa) / self.rho)
                leak_rate_mL_s = leak_rate_m3_s * 1e6
                
                # 3. Dynamic Clot Growth Differential equation loop
                # Growth scales with current flow payload, platelet concentration, and factor integrity
                d_clot_area = k_clot * self.alpha_factor * (self.plt / 150000.0) * leak_rate_m3_s
                current_clot_area_m2 += d_clot_area
                
            cumulative_volume_lost_mL += leak_rate_mL_s
            
            time_series_log.append({
                "second": t,
                "vessel_pressure_mmHg": round(current_p_pa / 133.322, 1),
                "effective_orifice_area_um2": round(a_effective * 1e12, 2),
                "bleeding_rate_mL_s": round(leak_rate_mL_s, 4)
            })

        return {
            "initial_lesion_area_um2": round(self.a_lesion_initial * 1e12, 2),
            "final_plugged_area_um2": round(min(self.a_lesion_initial, current_clot_area_m2) * 1e12, 2),
            "total_blood_loss_volume_mL": round(cumulative_volume_lost_mL, 3),
            "clotting_achieved_successfully": a_effective <= 0.0,
            "timeline_logs": time_series_log
        }

# =====================================================================
# SYSTEM AUTOMATION TESTS FRAMEWORK
# =====================================================================
class TestCoagulationClottingBoundaries(unittest.TestCase):
    def test_thrombus_hemostasis_efficiency(self):
        """
        VERIFICATION: Ensures a healthy high-platelet profile seals 
        wounds significantly faster than a low-platelet profile.
        """
        # Patient A: Healthy clotting status
        healthy_patient = AdvancedCoagulationHemorrhageEngine(tip_radius_microns=4.0, plt_count_uL=350000.0, clotting_factor_index=1.0)
        report_healthy = healthy_patient.simulate_clotted_hemorrhage(initial_p_vessel_mmHg=100.0, time_steps_sec=20)
        
        # Patient B: Thrombocytopenic (critical bleeding deficit)
        bleeding_patient = AdvancedCoagulationHemorrhageEngine(tip_radius_microns=4.0, plt_count_uL=20000.0, clotting_factor_index=1.0)
        report_bleeding = bleeding_patient.simulate_clotted_hemorrhage(initial_p_vessel_mmHg=100.0, time_steps_sec=20)
        
        # Assertion validation: Healthy patient should lose strictly less blood volume due to clotting
        self.assertLess(report_healthy["total_blood_loss_volume_mL"], report_bleeding["total_blood_loss_volume_mL"])
        print(f" -> Assert Verified: Healthy lost {report_healthy['total_blood_loss_volume_mL']}mL vs Thrombocytopenic {report_bleeding['total_blood_loss_volume_mL']}mL")

if __name__ == "__main__":
    unittest.main()
