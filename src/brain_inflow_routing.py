import math

class BrainInflowRoutingPipeline:
    def __init__(self, height_cm: float, weight_kg: float, hydration_level: float, wbc_count_uL: float):
        """
        Consolidates and solves transport mechanics across all 4 anatomical 
        inflow pathways leading directly to the brain matrix.
        """
        self.height_cm = height_cm
        self.weight = weight_kg
        self.chi = max(0.5, min(1.5, hydration_level))
        self.wbc = wbc_count_uL
        
        # Geometrical references matching core architecture logs
        self.bsa = 0.007184 * (self.height_cm ** 0.725) * (self.weight ** 0.425)
        self.cardiac_output_m3_s = ((self.bsa * 3.0 * math.sqrt(self.chi)) / 1000.0) / 60.0
        self.spinal_length_cm = 0.35 * self.height_cm

    def evaluate_all_routes(self, particle_diameter_um: float, intra_abdominal_pressure_mmHg: float) -> dict:
        """
        Runs simultaneous fluid, structural, and mechanical filtration gates 
        across the four complete brain inflow pathways.
        """
        # --- ROUTE A: ARTERIAL ADVECTION LOGIC ---
        # Cerebral perfusion accounts for approx 15% of arterial resting flow
        q_cerebral = self.cardiac_output_m3_s * 0.15
        # Generation 12 cerebral capillary typical combined radius proxy
        r_capillary_m = 4.5e-6
        area_capillary_m2 = math.pi * (r_capillary_m ** 2)
        v_arterial_m_s = q_cerebral / (area_capillary_m2 * 1e6) # Distributed flow velocity
        
        # Blood-brain barrier molecular/size crossing rules
        arterial_gate_passed = particle_diameter_um < 0.005 # Extensively limited to sub-nanometer compounds
        
        # --- ROUTE B: AXIAL VALVELESS SHUNT (BATSON'S PLEXUS) ---
        # Retrograde upward velocity vector triggers if abdominal pressure overrides systemic venous columns
        if intra_abdominal_pressure_mmHg > 25.0:
            v_batson_m_s = 0.015 * (intra_abdominal_pressure_mmHg / 25.0)
            batson_transit_seconds = (self.spinal_length_cm / 100.0) / v_batson_m_s
            batson_accessible = True
        else:
            v_batson_m_s = 0.0
            batson_transit_seconds = float('inf')
            batson_accessible = False

        # --- ROUTE C: VENTRICULAR-SPINAL CSF COLUMN ---
        v_csf_flow_m_s = (0.35 / 1e6) / 60.0 * self.chi # Extremely slow bulk advection drift
        csf_transit_seconds = (self.spinal_length_cm / 100.0) / v_csf_flow_m_s if v_csf_flow_m_s > 0 else float('inf')

        # --- ROUTE D: CRANIAL-SINUS PERIVASCULAR INTERFACE ---
        # Mechanical selection limits set to 2.0 microns at the cribriform gate line
        glymphatic_gate_passed = particle_diameter_um <= 2.0

        return {
            "patient_anthropometric_bsa_m2": round(self.bsa, 2),
            "pathway_a_arterial_loop": {
                "calculated_capillary_velocity_m_s": round(v_arterial_m_s, 5),
                "blood_brain_barrier_clearance": arterial_gate_passed,
                "status": "Accessible (Compound Size Modulated)" if arterial_gate_passed else "Blocked at Blood-Brain Barrier Endothelium"
            },
            "pathway_b_batson_valveless_shunt": {
                "axial_retrograde_velocity_m_s": round(v_batson_m_s, 4),
                "spinal_to_dural_transit_time_seconds": round(batson_transit_seconds, 2) if batson_accessible else "Infinity (No Pressure Drive)",
                "status": "ACTIVE UPPER ADVECTION" if batson_accessible else "STAGNANT / INACTIVE"
            },
            "pathway_c_spinal_csf_column": {
                "basal_csf_advection_velocity_m_s": v_csf_flow_m_s,
                "lumbar_to_ventricle_transit_hours": round((csf_transit_seconds / 3600.0), 1),
                "status": "Continuous Passive Drift Column"
            },
            "pathway_d_cranial_sinus_interface": {
                "particle_size_microns": particle_diameter_um,
                "cribriform_sieve_limit_microns": 2.0,
                "mechanical_gate_clearance": glymphatic_gate_passed,
                "status": "PASSAGE SCHEMATICALLY FEASIBLE" if glymphatic_gate_passed else "CRITICAL SIZE EXCLUSION (Blocked at Skull Base Bone)"
            }
        }

# =====================================================================
# Operational Verification Execution Matrix
# =====================================================================
if __name__ == "__main__":
    # Test context: Standard initialized patient engine properties
    pipeline = BrainInflowRoutingPipeline(height_cm=175.0, weight_kg=72.0, hydration_level=1.0, wbc_count_uL=6500.0)
    
    print("=========================================================================")
    print("COMPREHENSIVE BRAIN INFLOW ROUTING NETWORK ANALYSIS")
    print("=========================================================================\n")
    
    # Analyze a sub-micron particle (0.5 microns) under high intra-abdominal strain (coughing fit)
    analysis_report = pipeline.evaluate_all_routes(particle_diameter_um=0.5, intra_abdominal_pressure_mmHg=35.0)
    
    print("--- 1. PATHWAY A: ARTERIAL SYSTEMIC GENERATION PERFUSION ---")
    print(f" Capillary Flow Velocity: {analysis_report['pathway_a_arterial_loop']['calculated_capillary_velocity_m_s']} m/s")
    print(f" Barrier Gating Status:   {analysis_report['pathway_a_arterial_loop']['status']}\n")
    
    print("--- 2. PATHWAY B: AXIAL VALVELESS SHUNT (BATSON'S PLEXUS) ---")
    print(f" Retrograde Spinal Speed: {analysis_report['pathway_b_batson_valveless_shunt']['axial_retrograde_velocity_m_s']} m/s")
    print(f" Time-of-Flight to Brain: {analysis_report['pathway_b_batson_valveless_shunt']['spinal_to_dural_transit_time_seconds']} seconds (High-Pressure Override Active)\n")
    
    print("--- 3. PATHWAY C: VENTRICULAR-SPINAL SUBARACHNOID FLUID ---")
    print(f" Lumbar-to-Cranial Bulk Drift Time: {analysis_report['pathway_c_spinal_csf_column']['lumbar_to_ventricle_transit_hours']} hours\n")
    
    print("--- 4. PATHWAY D: CRANIAL-SINUS GLYMPHATIC PERIVASCULAR INTERFACE ---")
    print(f" Particle Sizing Vector:  {analysis_report['pathway_d_cranial_sinus_interface']['particle_size_microns']} um (Ceiling Limit: {analysis_report['pathway_d_cranial_sinus_interface']['cribriform_sieve_limit_microns']} um)")
    print(f" Entry Gate Evaluation:   {analysis_report['pathway_d_cranial_sinus_interface']['status']}")
