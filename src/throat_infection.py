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

class PharyngealInteractionModel:
    def __init__(self, object_length_mm: float, has_anchoring_appendages: bool = False):
        """
        Models the biophysical transport constraints and reflex clearing
        mechanics of a foreign object lodged within the pharyngeal lumen.
        """
        self.obj_length = object_length_mm
        self.has_anchors = has_anchoring_appendages
        self.pharynx_length_cm = 12.0 # Total length from upper nasopharynx to esophagus entry

    def evaluate_reflex_trigger(self) -> dict:
        """
        Calculates the probability of triggering an involuntary somatic 
        clearance reflex based on object size metrics.
        """
        # Objects larger than 1.0 mm routinely activate pharyngeal mechanoreceptors
        if self.obj_length > 1.0:
            gag_reflex_probability = 0.99
            swallow_reflex_velocity_m_s = 0.45  # High-speed muscular constriction wave
        else:
            gag_reflex_probability = 0.15
            swallow_reflex_velocity_m_s = 0.10

        return {
            "mechanoreceptor_activation": self.obj_length > 1.0,
            "involuntary_clearance_reflex_probability": gag_reflex_probability,
            "swallow_propulsion_wave_velocity_m_s": swallow_reflex_velocity_m_s
        }

    def simulate_clearance_timeline(self, hydration_level: float) -> dict:
        """
        Calculates the maximum survival duration of the object in the throat 
        before reflex advection forces it down into gastric acid sinks.
        """
        reflex = self.evaluate_reflex_trigger()
        
        # Basal salivary downward wash speed (converted to meters per second)
        v_saliva_m_s = (1.5 / 100.0) / 60.0 * hydration_level
        
        # Calculate time to clear the 12cm pharyngeal tract under basal wash alone
        basal_clearance_seconds = (self.pharynx_length_cm / 100.0) / v_saliva_m_s if v_saliva_m_s > 0 else 3600.0
        
        # If reflex is highly active, actual clearance takes fractions of a second
        if reflex["mechanoreceptor_activation"]:
            actual_clearance_seconds = (self.pharynx_length_cm / 100.0) / reflex["swallow_propulsion_wave_velocity_m_s"]
            evacuation_mechanism = "Involuntary Somatic Swallow Reflex"
        else:
            actual_clearance_seconds = basal_clearance_seconds
            evacuation_mechanism = "Basal Salivary Hydrodynamic Wash"

        return {
            "pharyngeal_pathway_length_cm": self.pharynx_length_cm,
            "active_evacuation_mechanism": evacuation_mechanism,
            "calculated_retention_window_seconds": round(actual_clearance_seconds, 3),
            "terminal_confinement_sink": "Esophageal Entry -> Gastric Acid Dissolution Loop"
        }

# =====================================================================
# Verification Execution Matrix
# =====================================================================
if __name__ == "__main__":
    # Model an unchewed object measuring 6.0 mm entering the throat lumen
    organism_segment = PharyngealInteractionModel(object_length_mm=6.0, has_anchoring_appendages=False)
    
    print("=========================================================================")
    print("PHARYNGEAL LUMEN TRANSPORT AND REFLEX CLEARANCE LOGS")
    print("=========================================================================\n")
    
    # 1. Run reflex threshold checks
    reflex_report = organism_segment.evaluate_reflex_trigger()
    print("--- 1. SOMATIC NEURO-REFLEX ACTIVATION REGISTER ---")
    print(f" Sensory Mechanoreceptor Structural Trigger: {reflex_report['mechanoreceptor_activation']}")
    print(f" Involuntary Swallow Reflex Probability:    {reflex_report['involuntary_clearance_reflex_probability'] * 100.0}%")
    print(f" Propulsive Constriction Wave Velocity:    {reflex_report['swallow_propulsion_wave_velocity_m_s']} m/s\n")
    
    # 2. Compute dynamic clearance timeline vector
    timeline_report = organism_segment.simulate_clearance_timeline(hydration_level=1.0)
    print("--- 2. HYDRODYNAMIC AND MECHANICAL EVACUATION TIMELINE ---")
    print(f" Dominant Clearing Mechanism:             {timeline_report['active_evacuation_mechanism']}")
    print(f" Calculated Retention Timeline Window:    {timeline_report['calculated_retention_window_seconds']} seconds")
    print(f" Terminal Isolation Endpoint Location:     {timeline_report['terminal_confinement_sink']}")
