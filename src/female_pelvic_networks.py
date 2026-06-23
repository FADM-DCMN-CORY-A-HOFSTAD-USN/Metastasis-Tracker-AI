import math

class FemalePelvicSimulationEngine:
    def __init__(self, height_cm: float, weight_kg: float, hydration_level: float):
        """
        Initializes the female reproductive and urinary system templates.
        Dimensions scale directly from central patient biometrics.
        """
        self.height_cm = height_cm
        self.height_m = height_cm / 100.0
        self.weight = weight_kg
        self.chi = max(0.5, min(1.5, hydration_level)) # Hydration scaling constant
        
        # Base anthropometrics matching repository protocols
        self.bsa = 0.007184 * (self.height_cm ** 0.725) * (self.weight ** 0.425)
        self.cardiac_output_L_min = self.bsa * 3.0 * math.sqrt(self.chi)

    def generate_reproductive_network(self) -> dict:
        """
        Generates dimensions and structural tracking boundaries for the 
        continuous female reproductive tree down to the bilateral ovaries.
        """
        # Base mass configuration scaling relative to total body size
        w = self.weight
        base_ovary_mass_g = 1.45 * math.sqrt(w) # Reference standard human weight

        reproductive_tree = {
            "vaginal_canal": {
                "length_cm": 8.2, "resting_diameter_cm": 3.0, 
                "local_ph": round(4.15 * (1.0 / self.chi), 2), # Acidic defensive envelope
                "epithelium_class": "Stratified Squamous"
            },
            "uterine_cavity": {
                "length_cm": 7.5, "interstitial_volume_cm3": 35.0 * self.chi,
                "myometrial_mass_g": round(65.0 * (w / 70.0), 1),
                "local_ph": 7.10
            },
            "fallopian_tubes_bilateral": {
                "length_cm": 11.0, "mean_lumen_diameter_mm": 2.0,
                "ciliary_outward_velocity_mm_min": 1.5, # Direct fluid protection current
                "continuity_status": "Patent Conduit"
            },
            "bilateral_ovaries": {
                "left_ovary": {
                    "mass_g": round(base_ovary_mass_g * 1.02, 2),
                    "dimensions_cm": {"length": 4.0, "width": 2.0, "depth": 1.5},
                    "venous_drainage_sink": "Left Renal Vein (90-degree hydrostatic drop)"
                },
                "right_ovary": {
                    "mass_g": round(base_ovary_mass_g * 0.98, 2),
                    "dimensions_cm": {"length": 3.8, "width": 1.9, "depth": 1.4},
                    "venous_drainage_sink": "Inferior Vena Cava (Direct Confluence)"
                }
            }
        }
        return reproductive_tree

    def generate_urinary_network(self) -> dict:
        """
        Calculates structural values and filtration capacities for the 
        female urinary tract from the meatus up to the kidneys.
        """
        w = self.weight
        kidney_mass_base = 1.45 * (w ** 0.95)
        
        total_renal_volume_cm3 = ((kidney_mass_base * 1.05) + (kidney_mass_base * 0.98)) / 1.05
        gfr_mL_min = 0.00055 * total_renal_volume_cm3 * 1000.0

        return {
            "urethra": {
                "length_cm": 3.9, "diameter_cm": 0.6,
                "flush_peak_velocity_m_s": 0.35, # Dynamic clearance force
            },
            "urinary_bladder": {
                "maximum_capacity_mL": round(450.0 * self.chi, 1),
                "resting_wall_thickness_cm": 0.45
            },
            "ureters_bilateral": {
                "length_cm": 29.0, "lumen_diameter_cm": 0.35,
                "peristaltic_frequency_per_min": 3.0
            },
            "kidney_filtration_matrix": {
                "left_kidney_mass_g": round(kidney_mass_base * 1.05, 2),
                "right_kidney_mass_g": round(kidney_mass_base * 0.98, 2),
                "calculated_gfr_mL_min": round(gfr_mL_min, 2),
                "allocated_renal_blood_flow_L_min": round(self.cardiac_output_L_min * 0.22, 3)
            }
        }

    def build_pelvic_dataset(self) -> dict:
        return {
            "patient_pelvic_metrics": {
                "calculated_bsa_m2": self.bsa,
                "cardiac_output_L_min": self.cardiac_output_L_min
            },
            "reproductive_system_matrix": self.generate_reproductive_network(),
            "urinary_system_matrix": self.generate_urinary_network()
        }

# =====================================================================
# Execution & Sample Output Verification
# =====================================================================
if __name__ == "__main__":
    # Simulate a female patient (Height: 168cm, Weight: 62kg, Hydration: 1.0)
    engine = FemalePelvicSimulationEngine(height_cm=168.0, weight_kg=62.0, hydration_level=1.0)
    dataset = engine.build_pelvic_dataset()
    
    print("=========================================================================")
    print("FEMALE PELVIC SYSTEM GEOMETRY & FLOW VERIFICATION LOGS")
    print("=========================================================================\n")
    
    # 1. Inspect Reproductive Properties
    repro = dataset["reproductive_system_matrix"]
    print("--- 1. REPRODUCTIVE MATRIX PATHWAYS ---")
    print(f" Vaginal Canal Base Environment:  pH {repro['vaginal_canal']['local_ph']} | Epithelium: {repro['vaginal_canal']['epithelium_class']}")
    print(f" Fallopian Conduit Clearance:    Ciliary Outflow Speed = {repro['fallopian_tubes_bilateral']['ciliary_outward_velocity_mm_min']} mm/min")
    print(f" Left Ovary Drainage Hub:        {repro['bilateral_ovaries']['left_ovary']['venous_drainage_sink']}")
    print(f" Right Ovary Mass Calculation:    {repro['bilateral_ovaries']['right_ovary']['mass_g']} grams\n")
    
    # 2. Inspect Urinary Properties
    urinary = dataset["urinary_system_matrix"]
    print("--- 2. URINARY FILTRATION & OUTFLOW CHANNELS ---")
    print(f" Female Urethra Dimensions:      Length = {urinary['urethra']['length_cm']} cm | Diameter = {urinary['urethra']['diameter_cm']} cm")
    print(f" Bladder Capacity (Hydrated):    {urinary['urinary_bladder']['maximum_capacity_mL']} mL")
    print(f" Systemic GFR Baseline:          {urinary['kidney_filtration_matrix']['calculated_gfr_mL_min']} mL/min")
    print(f" Total Perfusion Target RBF:     {urinary['kidney_filtration_matrix']['allocated_renal_blood_flow_L_min']:.3f} L/min")
