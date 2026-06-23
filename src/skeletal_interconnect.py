import math

class SkeletalInterconnectEngine:
    def __init__(self, patient_height_cm: float, patient_weight_kg: float, hydration_level: float):
        """
        Calculates connectivity, filtration parameters, and ingress feasibility 
        across the 4 functional entry portals leading into the bone marrow compartments.
        """
        self.height_m = patient_height_cm / 100.0
        self.weight = patient_weight_kg
        self.chi = max(0.5, min(1.5, hydration_level))
        
        # Pull standard skeletal markers from your dynamic engine formulas
        self.lbm = 1.10 * self.weight - 128 * ((self.weight / patient_height_cm) ** 2)
        self.total_marrow_volume_cm3 = (0.15 * math.pow(self.lbm, 0.95) * 1000.0 / 1.92) * 0.18 * self.chi

    def evaluate_marrow_ingress_portals(self, particle_diameter_um: float, abdominal_pressure_mmHg: float) -> dict:
        """
        Evaluates the entry mechanics, size boundaries, and operational limits 
        for a particle trying to enter the bone marrow via the 4 defined routes.
        """
        # --- PORTAL A: CIRCULATORY SINUSOIDAL POROSITY ---
        sinusoid_pore_limit_um = 5.5
        portal_a_allowed = particle_diameter_um <= sinusoid_pore_limit_um
        
        # --- PORTAL B: VALVELESS RETROGRADE SHUNT (BATSON'S) ---
        # Shunt activates if pelvic abdominal strain overrides systemic baseline venous columns
        portal_b_active = abdominal_pressure_mmHg > 25.0
        portal_b_allowed = portal_b_active and (particle_diameter_um <= 15.0) # Larger caliber vein channels

        # --- PORTAL C: PERIAPICAL DENTAL PATH (TEETH GATE) ---
        # Root apex apical foramen average diameter constraint (adult baseline)
        apical_foramen_limit_um = 400.0
        portal_c_allowed = particle_diameter_um <= apical_foramen_limit_um

        # --- PORTAL D: CRIBRIFORM SIEVE (SINUS / AIRWAY GATE) ---
        cribriform_perforation_limit_um = 10.0
        portal_d_allowed = particle_diameter_um <= cribriform_perforation_limit_um

        return {
            "total_host_marrow_volume_reservoir_cm3": round(self.total_marrow_volume_cm3, 2),
            "portal_a_circulatory_sinusoid": {
                "max_pore_threshold_microns": sinusoid_pore_limit_um,
                "ingress_allowed": portal_a_allowed,
                "resolution": "Sinusoidal Filtration Engaged" if portal_a_allowed else "Excludes Macro-Particles"
            },
            "portal_b_batsons_axial_shunt": {
                "shunt_pressure_override_active": portal_b_active,
                "ingress_allowed": portal_b_allowed,
                "resolution": "Retrograde Pelvic-to-Spine Advection Enabled" if portal_b_allowed else "Stagnant or Size Blocked"
            },
            "portal_c_periapical_dental_pulp": {
                "max_apical_foramen_microns": apical_foramen_limit_um,
                "ingress_allowed": portal_c_allowed,
                "resolution": "Direct Internal Jaw Access Feasible" if portal_c_allowed else "Exceeds Root Canal Geometry"
            },
            "portal_d_cribriform_airway_interface": {
                "max_bone_perforation_microns": cribriform_perforation_limit_um,
                "ingress_allowed": portal_d_allowed,
                "resolution": "Direct Skull Base Marrow Infiltration Feasible" if portal_d_allowed else "Blocked at Cribriform Sieve Line"
            }
        }

# =====================================================================
# Operational Verification Pipeline Runner
# =====================================================================
if __name__ == "__main__":
    # Initialize the interconnected mapping loop for a standard patient template
    interconnect = SkeletalInterconnectEngine(height_cm=180.0, weight_kg=78.0, hydration_level=1.0)
    
    print("=========================================================================")
    print("BONE MARROW INTERCONNECTIVITY PORTAL GATE ANALYSIS")
    print("=========================================================================\n")
    
    # Trace a micro-particle (4.5 microns) under high coughing/straining stress (32 mmHg)
    print("--- SCENARIO 1: MICROSCOPIC COMPARTMENT TRANSIT ( 4.5 Micron Particle ) ---")
    report_micro = interconnect.evaluate_marrow_ingress_portals(particle_diameter_um=4.5, abdominal_pressure_mmHg=32.0)
    
    print(f" Route A (Circulatory) -> Ingress Allowed: {report_micro['portal_a_circulatory_sinusoid']['ingress_allowed']} ({report_micro['portal_a_circulatory_sinusoid']['resolution']})")
    print(f" Route B (Pelvic Shunt)-> Ingress Allowed: {report_micro['portal_b_batsons_axial_shunt']['ingress_allowed']} ({report_micro['portal_b_batsons_axial_shunt']['resolution']})")
    print(f" Route C (Dental Pulp) -> Ingress Allowed: {report_micro['portal_c_periapical_dental_pulp']['ingress_allowed']} ({report_micro['portal_c_periapical_dental_pulp']['resolution']})")
    print(f" Route D (Sinus Sieve) -> Ingress Allowed: {report_micro['portal_d_cribriform_airway_interface']['ingress_allowed']} ({report_micro['portal_d_cribriform_airway_interface']['resolution']})\n")

    # Trace a larger particle (25.0 microns) under the same somatic stress conditions
    print("--- SCENARIO 2: MACROSCOPIC COMPARTMENT TRANSIT ( 25.0 Micron Particle ) ---")
    report_macro = interconnect.evaluate_marrow_ingress_portals(particle_diameter_um=25.0, abdominal_pressure_mmHg=32.0)
    
    print(f" Route A (Circulatory) -> Ingress Allowed: {report_macro['portal_a_circulatory_sinusoid']['ingress_allowed']} ({report_macro['portal_a_circulatory_sinusoid']['resolution']})")
    print(f" Route B (Pelvic Shunt)-> Ingress Allowed: {report_macro['portal_b_batsons_axial_shunt']['ingress_allowed']} ({report_macro['portal_b_batsons_axial_shunt']['resolution']})")
    print(f" Route C (Dental Pulp) -> Ingress Allowed: {report_macro['portal_c_periapical_dental_pulp']['ingress_allowed']} ({report_macro['portal_c_periapical_dental_pulp']['resolution']})")
    print(f" Route D (Sinus Sieve) -> Ingress Allowed: {report_macro['portal_d_cribriform_airway_interface']['ingress_allowed']} ({report_macro['portal_d_cribriform_airway_interface']['resolution']})")
