import math
# ==============================================================================
# 🪝 PYCNOGONID BIOENERGETIC ENGINE INTEGRATION HOOK
# ==============================================================================
import os
import json
from src.biomass_scaler import PycnogonidBiomassEngine
from src.population_engine import PycnogonidPopulationEngine
from src.tracker_bridge import TrackerBiomassOrchestrator

# 1. Resolve relative directory paths for standard data files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTEIN_DATA_PATH = os.path.join(BASE_DIR, "src", "data", "target_proteins.json")
THERMAL_DATA_PATH = os.path.join(BASE_DIR, "src", "data", "pycnogonid_thermal_profiles.json")

# 2. Safely parse JSON parameter files
with open(PROTEIN_DATA_PATH, "r") as pf:
    protein_configuration = json.load(pf)
with open(THERMAL_DATA_PATH, "r") as tf:
    thermal_profiles = json.load(tf)

# 3. Instantiate the sub-calculation blocks
# Baseline morphology: 8.0mm femur, 0.5mm baseline leg radius
biomass_calculation_core = PycnogonidBiomassEngine({
    "base_femur_length_mm": 8.0, 
    "base_leg_radius_mm": 0.5
})

# Extract target species profile constants for the Lefkovitch population tensor
species_key = "Pycnogonidae_shallow_profile"
population_config_wrapper = {
    "breeding_matrix_config": thermal_profiles["pycnogonid_thermal_development_matrix"][species_key]
}
population_calculation_core = PycnogonidPopulationEngine(population_config_wrapper)

# 4. Initialize the communication orchestrator bridge
biomass_tracker_orchestrator = TrackerBiomassOrchestrator(
    biomass_engine=biomass_calculation_core,
    population_engine=population_calculation_core,
    protein_config=protein_configuration
)

# 5. Pre-seed the agent's internal nutrient pool to enable reproduction calculations
# Adjust this value (in mm3) depending on the initial state of the tracker agent
biomass_calculation_core.accumulated_protein_vol = 6.20 

print("✅ Pycnogonid bioenergetic engine successfully hooked into tracking routing.")

# ==============================================================================
# 🔄 INNER LOOP INTEGRATION EXAMPLE (Insert inside your path navigation loops)
# ==============================================================================
# Inside your tracking loops where the agent jumps between nodes, paste this step block:

# Target Tracking Variables Mock (Ensure these match your live tracking outputs)
current_tracking_node_id = "cerebral_capillary_bed_alpha" # Live node ID string
time_delta_this_step = 1.0 # Duration spent at this coordinates node (seconds)

# Live climate context variables query
live_environment_context = {
    "temperature": 14.0, 
    "turbulence": 0.0, 
    "ph": 8.1
}

# RUNTIME EXECUTION CALL
biomass_step_report = biomass_tracker_orchestrator.process_tracker_location_step(
    location_id=current_tracking_node_id,
    local_env_context=live_environment_context,
    delta_time=time_delta_this_step
)

# Parse output telemetry results for automated diagnostic tracking
if biomass_step_report["status"] == "REPRODUCTION_CYCLING":
    print(f"🔥 ALERT: Gonopore activation confirmed at node [{current_tracking_node_id}].")
    print(f"   New generational output vector: {biomass_step_report['larval_pool_generation']}")
else:
    residual_reserves = biomass_step_report["protein_reserves_remaining"]
    print(f"🔹 Absorbing nutrients at node [{current_tracking_node_id}]. Current internal pool: {residual_reserves:.4f} mm3")
# ==============================================================================

# Insert this updated pattern inside your execution tracking scripts:

from src.biomass_scaler import PycnogonidBiomassEngine
from src.population_engine import PycnogonidPopulationEngine
from src.tracker_bridge import TrackerBiomassOrchestrator
from src.tracker_logger import TrackerDiagnosticLogger

# 1. Initialize core engines and communication paths
bio_eng = PycnogonidBiomassEngine({"base_femur_length_mm": 8.0, "base_leg_radius_mm": 0.5})
pop_eng = PycnogonidPopulationEngine({"breeding_matrix_config": {
    "leslie_matrix_coefficients": {"fecundity_adult_f": 15.0, "fecundity_brooding_f": 40.0, "survival_larva_to_juv": 0.25, "survival_juv_to_adult": 0.60, "adult_retention_rate": 0.92},
    "environmental_sensitivities": {"optimal_breeding_temp_c": 14.0, "thermal_exponential_limit_q10": 2.0, "turbulence_fertilization_penalty_exponent": 1.5, "optimal_ph": 8.1, "ph_tolerance_sigma": 0.35}
}})
orchestrator = TrackerBiomassOrchestrator(bio_eng, pop_eng, {})

# 2. Instantiate the new diagnostic logger module
diagnostic_logger = TrackerDiagnosticLogger(filename_prefix="cerebral_path_run")

# --- Inside your active node navigation loop ---
current_node = "cerebral_capillary_bed_alpha"
env_context = {"temperature": 14.2, "turbulence": 0.0, "ph": 8.1}

# Execute the bioenergetic tensor calculation step
step_report = orchestrator.process_tracker_location_step(
    location_id=current_node,
    local_env_context=env_context,
    delta_time=1.0
)

# Extract internal parameters to ensure total visibility inside the JSON file
current_cf = 1.3 if bio_eng.accumulated_protein_vol > 5.0 else 1.0
internal_telemetry = {
    "protein_vol": bio_eng.accumulated_protein_vol,
    "condition_factor": current_cf
}

# 3. Log the step payload seamlessly into outbound/
diagnostic_logger.log_step(
    location_id=current_node,
    local_env=env_context,
    report_output=step_report,
    internal_metrics=internal_telemetry
)

class MaternalFetalTransportEngine:
    def __init__(self, maternal_hydration: float, fetal_mass_kg: float):
        """
        Models the prenatal gestational transport network connecting maternal 
        organs to a developing fetal anatomy template.
        """
        self.chi_mat = max(0.5, min(1.5, maternal_hydration))
        self.fetal_mass = fetal_mass_kg
        
        # Fetal physiological baselines (scaled to gestational size)
        # Umbilical vein radius averages approx 2.5 mm near term
        self.r_umbilical_m = 0.0025 
        self.fetal_cardiac_output_L_min = 0.22 * self.fetal_mass # ~220 mL/min/kg baseline

        # Absolute structural gating limit of the placental syncytiotrophoblast barrier
        self.placental_pore_cutoff_microns = 1.0 

    def evaluate_placental_filtration_gate(self, particle_diameter_um: float) -> dict:
        """
        Applies mechanical size-exclusion sorting to check if a structural mass matrix 
        can cross the placental tissue barrier into the child's bloodstream.
        """
        is_excluded = particle_diameter_um > self.placental_pore_cutoff_microns
        
        return {
            "input_particle_diameter_microns": particle_diameter_um,
            "barrier_pore_ceiling_microns": self.placental_pore_cutoff_microns,
            "mechanical_crossing_allowed": not is_excluded,
            "gating_status": "BLOCKED / SIZE EXCLUSION" if is_excluded else "PASSAGE SCHEMATICALLY FEASIBLE"
        }

    def calculate_fetal_delivery_velocity(self) -> dict:
        """
        Solves the forward fluid advection velocity driving allowed micro-particles 
        along the umbilical vein toward the child's central organs.
        """
        # Convert fetal flow rate from Liters/minute to m^3/second
        q_fetal_m3_s = (self.fetal_cardiac_output_L_min / 1000.0) / 60.0
        
        # Umbilical vein cross-sectional flow area
        area_m2 = math.pi * (self.r_umbilical_m ** 2)
        
        # Advection speed profile: v = Q / A
        v_advection_m_s = q_fetal_m3_s / area_m2
        
        # Average umbilical cord length tracking parameter: 50 cm (0.50 meters)
        cord_length_m = 0.50
        time_of_flight_seconds = cord_length_m / v_advection_m_s

        return {
            "fetal_umbilical_flow_rate_L_min": round(self.fetal_cardiac_output_L_min, 3),
            "umbilical_vein_velocity_m_s": round(v_advection_m_s, 4),
            "transit_time_across_cord_seconds": round(time_of_flight_seconds, 2),
            "primary_fetal_delivery_sink": "Ductus Venosus -> Right Atrium -> Systemic Scaling Tree"
        }

    def execute_maternal_fetal_pipeline(self, particle_diameter_um: float) -> dict:
        """
        Runs the full structural mapping loop combining the filtration filter 
        and fluid transport timelines.
        """
        gate = self.evaluate_placental_filtration_gate(particle_diameter_um)
        
        if gate["mechanical_crossing_allowed"]:
            transit = self.calculate_fetal_delivery_velocity()
            resolution = f"Successful delivery to child via Umbilical Vein in {transit['transit_time_across_cord_seconds']}s"
        else:
            transit = {}
            resolution = "Transport aborted at Placental Wall: " + gate["gating_status"]

        return {
            "filtration_gate_metrics": gate,
            "hydrodynamic_transit_metrics": transit,
            "terminal_simulation_outcome": resolution
        }

# =====================================================================
# Operational Verification Pipeline Loop
# =====================================================================
if __name__ == "__main__":
    # Simulate a third-trimester fetal template context (Mass: 3.0 kg)
    pipeline = MaternalFetalTransportEngine(maternal_hydration=1.0, fetal_mass_kg=3.0)
    
    print("=========================================================================")
    print("MATERNAL-TO-CHILD GESTATIONAL TRANSIT SIMULATION LOGS")
    print("=========================================================================\n")
    
    # Test Node A: A macroscopic 15-micron fragment trying to navigate the vascular loop
    macro_test = pipeline.execute_maternal_fetal_pipeline(particle_diameter_um=15.0)
    print("--- SCENARIO A: MACROSCOPIC PARTICLE TRANSIT ---")
    print(f" Mechanical Gate Allowance: {macro_test['filtration_gate_metrics']['mechanical_crossing_allowed']}")
    print(f" Simulation Terminal Fate:  {macro_test['terminal_simulation_outcome']}\n")

    # Test Node B: A sub-micron 0.2-micron (200 nm) particle navigating the loop
    micro_test = pipeline.execute_maternal_fetal_pipeline(particle_diameter_um=0.2)
    print("--- SCENARIO B: SUB-MICRON PARTICULATE TRANSIT ---")
    print(f" Mechanical Gate Allowance: {micro_test['filtration_gate_metrics']['mechanical_crossing_allowed']}")
    print(f" Fluid Speed in Umbilical Core: {micro_test['hydrodynamic_transit_metrics']['umbilical_vein_velocity_m_s']} m/s")
    print(f" Cord Flight Vector Time:       {micro_test['hydrodynamic_transit_metrics']['transit_time_across_cord_seconds']} seconds")
    print(f" Child Distribution Target Sink: {micro_test['hydrodynamic_transit_metrics']['primary_fetal_delivery_sink']}")
    print(f" Simulation Terminal Fate:       {micro_test['terminal_simulation_outcome']}")
