import math

class CentralNervousSystemEngine:
    def __init__(self, height_cm: float, weight_kg: float, hydration_level: float):
        """
        Initializes the brain structural engine and its fluid pathways.
        Dimensions adapt dynamically to baseline patient metrics.
        """
        self.height_cm = height_cm
        self.height_m = height_cm / 100.0
        self.weight = weight_kg
        self.chi = max(0.5, min(1.5, hydration_level)) # Hydration vector factor

        # Compute core metrics matching repository specifications
        self.bsa = 0.007184 * (self.height_cm ** 0.725) * (self.weight ** 0.425)
        self.brain_mass_g = 230.0 * math.sqrt(self.height_m)
        self.icv_mL = (self.brain_mass_g / 1.03) / 0.85 # Total Intracranial Volume mapping

    def generate_brain_compartment_matrix(self) -> dict:
        """
        Partitions the internal intracranial volume into neural tissue,
        ventricular cerebrospinal fluid pools, and blood compartments.
        """
        total_icv = self.icv_mL
        
        # Volumetric partition fractions
        v_parenchyma = total_icv * 0.85
        v_blood = total_icv * 0.05
        v_intracranial_csf = total_icv * 0.10

        # Spinal cord length approximation derived from axial tracking column metrics
        spinal_length_cm = 0.35 * self.height_cm
        v_spinal_csf = 0.45 * spinal_length_cm * self.chi

        return {
            "total_intracranial_volume_mL": round(total_icv, 1),
            "neural_parenchyma_volume_cm3": round(v_parenchyma, 1),
            "intracranial_blood_volume_mL": round(v_blood, 1),
            "cerebrospinal_fluid_system": {
                "intracranial_csf_volume_mL": round(v_intracranial_csf, 1),
                "spinal_subarachnoid_csf_volume_mL": round(v_spinal_csf, 1),
                "total_systemic_csf_pool_mL": round(v_intracranial_csf + v_spinal_csf, 1),
                "basal_csf_production_rate_mL_min": round(0.35 * self.chi, 3)
            }
        }

    def calculate_cranial_sinus_interface(self, particle_diameter_um: float, current_icp_mmHg: float) -> dict:
        """
        Models the clearance gating mechanics at the dural venous sinuses, 
        where the brain fluid loop interfaces directly with paranasal/nasal matrices.
        """
        # Healthy resting intracranial pressure (ICP) standard: 7 to 15 mmHg
        icp = max(2.0, min(50.0, current_icp_mmHg))
        
        # Max clearance threshold of the arachnoid villi drainage ports
        arachnoid_gate_limit_um = 2.0
        
        # Mechanical size filtration gate check
        is_size_excluded = particle_diameter_um > arachnoid_gate_limit_um
        
        # Hydrodynamic fluid clearance velocity out into the dural sinuses:
        # Flow rates accelerate if ICP increases (pressure-driven drainage)
        v_drainage_mm_min = 0.12 * (icp / 10.0) * self.chi if not is_size_excluded else 0.0

        return {
            "monitored_intracranial_pressure_mmHg": icp,
            "target_particle_diameter_microns": particle_diameter_um,
            "arachnoid_villi_gate_limit_microns": arachnoid_gate_limit_um,
            "mechanical_clearance_allowed": not is_size_excluded,
            "glymphatic_drainage_velocity_mm_min": round(v_drainage_mm_min, 4),
            "barrier_structural_status": "BLOCKED / TRAPPED IN VENTRICLES" if is_size_excluded else "CLEARANCE THROUGH DURAL SINUSES ACTIVE"
        }

# =====================================================================
# Operational Verification Matrix
# =====================================================================
if __name__ == "__main__":
    # Simulate an average adult patient context
    engine = CentralNervousSystemEngine(height_cm=175.0, weight_kg=72.0, hydration_level=1.0)
    
    print("=========================================================================")
    print("CNS FLUID PATHWAYS & CRANIAL SINUS INTERFACE LOGS")
    print("=========================================================================\n")
    
    # 1. Verify internal brain and spinal cord fluid tracking allocations
    cns_matrix = engine.generate_brain_compartment_matrix()
    print("--- 1. INTRACRANIAL & SPINAL FLUID VOLUMETRIC PARTITIONING ---")
    print(f" Calculated Total Brain Mass:    {engine.brain_mass_g:.1f} grams")
    print(f" Intracranial Parenchyma Volume: {cns_matrix['neural_parenchyma_volume_cm3']} cm³")
    print(f" Ventricular Intracranial CSF:   {cns_matrix['cerebrospinal_fluid_system']['intracranial_csf_volume_mL']} mL")
    print(f" Spinal Cord Subarachnoid CSF:   {cns_matrix['cerebrospinal_fluid_system']['spinal_subarachnoid_csf_volume_mL']} mL")
    print(f" Continuous Systemic CSF Pool:   {cns_matrix['cerebrospinal_fluid_system']['total_systemic_csf_pool_mL']} mL\n")

    # 2. Test the cranial-sinus interface mechanics for two particle profiles
    # Test Node A: A large 25-micron particle inside the cerebrospinal space
    macro_report = engine.calculate_cranial_sinus_interface(particle_diameter_um=25.0, current_icp_mmHg=12.0)
    print("--- 2. SCENARIO A: MACROSCOPIC PARTICLE CEREBRAL TRAPPING ---")
    print(f" Mechanical Gate Allowance:      {macro_report['mechanical_clearance_allowed']}")
    print(f" Glymphatic Clearing Velocity:   {macro_report['glymphatic_drainage_velocity_mm_min']} mm/min")
    print(f" Interface Structural Status:    {macro_report['barrier_structural_status']}\n")

    # Test Node B: A small 0.5-micron micro-particle under elevated ICP stress
    micro_report = engine.calculate_cranial_sinus_interface(particle_diameter_um=0.5, current_icp_mmHg=25.0)
    print("--- 3. SCENARIO B: MICROSCOPIC GLYMPHATIC SINUS CLEARANCE ---")
    print(f" Mechanical Gate Allowance:      {micro_report['mechanical_clearance_allowed']}")
    print(f" Glymphatic Clearing Velocity:   {micro_report['glymphatic_drainage_velocity_mm_min']} mm/min (Pressure Accelerated)")
    print(f" Interface Structural Status:    {micro_report['barrier_structural_status']}")
