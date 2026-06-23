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

class RectalConfinementModel:
    def __init__(self, initial_specimen_mass_g: float, fractional_survival: float = 0.01):
        """
        Models the final transit, retention, and elimination of structural 
        remnants arriving in the rectum after full gastrointestinal transit.
        """
        # Calculate surviving mass based on upstream attrition equations
        self.arriving_mass_g = initial_specimen_mass_g * fractional_survival
        self.rectum_length_cm = 13.5
        self.is_viable = False # Biomatter is non-viable post-gastric acid loop

    def calculate_rectal_state(self, hydration_level: float) -> dict:
        """
        Computes the physical dimensions and retention states within the rectal vault.
        """
        # Rectal holding capacity scales with the patient's hydration coefficient
        rectal_resting_volume_cm3 = 120.0 * hydration_level
        
        # Microbe-driven decomposition rate constant (fermentation of organic matter)
        k_decomp = 0.002 # per minute
        
        # Assume an average fecal retention window in the rectal vault of 480 minutes (8 hours)
        retention_time_min = 480.0
        final_mass_g = self.arriving_mass_g * math.exp(-k_decomp * retention_time_min)

        return {
            "rectal_vault_length_cm": self.rectum_length_cm,
            "calculated_resting_volume_cm3": round(rectal_resting_volume_cm3, 1),
            "arriving_structural_mass_g": round(self.arriving_mass_g, 4),
            "post_retention_decomposed_mass_g": round(final_mass_g, 4),
            "organism_viability_status": "NON-VIABLE / DEGRADED BIOMATTER"
        }

    def simulate_defecation_clearance(self, wbc_pool_uL: float) -> dict:
        """
        Models the mechanical clearance of the remaining fragments via defecation.
        """
        # The rectal vault triggers mechanoreceptors when stool mass exerts wall pressure
        rectal_wall_pressure_mmHg = 45.0
        
        # Defecation applies high mechanical shearing forces to evacuate the lumen
        evacuation_efficiency_percent = 99.9
        
        # Local immune tracking: Mucosal IgA and leukocytes respond to foreign matter inflammation
        local_immune_response_index = 1.0 + (0.0001 * wbc_pool_uL)

        return {
            "defecation_reflex_trigger_status": "ACTIVE / TRIGGERED" if rectal_wall_pressure_mmHg > 15.0 else "STANDBY",
            "mechanical_lumen_clearance_efficiency_percent": evacuation_efficiency_percent,
            "mucosal_immune_activation_multiplier": round(local_immune_response_index, 2),
            "terminal_environmental_fate": "EXCRETION / COMPLETE ELIMINATION FROM HOST"
        }

# =====================================================================
# Verification Execution Matrix
# =====================================================================
if __name__ == "__main__":
    # Simulate a 2.5-gram unchewed object where only 1% of degraded fragments reach the rectum
    rectal_node = RectalConfinementModel(initial_specimen_mass_g=2.5, fractional_survival=0.01)
    
    print("=========================================================================")
    print("TERMINAL RECTAL VALUT CONFINEMENT & ELIMINATION LOGS")
    print("=========================================================================\n")
    
    # 1. Evaluate holding state and organic decomposition
    state = rectal_node.calculate_rectal_state(hydration_level=0.95)
    print("--- 1. RECTAL VAULT CAVITY RETENTION STATES ---")
    print(f" Organism Viability Index:      {state['organism_viability_status']}")
    print(f" Mass Arriving in Rectum:       {state['arriving_structural_mass_g']} grams")
    print(f" Decomposed Mass Post-Holding:  {state['post_retention_decomposed_mass_g']} grams\n")
    
    # 2. Execute mechanical elimination loops
    clearance = rectal_node.simulate_defecation_clearance(wbc_pool_uL=7500.0)
    print("--- 2. MECHANICAL EVACUATION AND FLUID DISCHARGE ---")
    print(f" Defecation Reflex Vector:      {clearance['defecation_reflex_trigger_status']}")
    print(f" Lumen Clearance Efficiency:    {clearance['mechanical_lumen_clearance_efficiency_percent']}%")
    print(f" Mucosal Immune Index Scaling:  {clearance['mucosal_immune_activation_multiplier']}x base")
    print(f" Terminal Simulation Endpoint:  {clearance['terminal_environmental_fate']}")
