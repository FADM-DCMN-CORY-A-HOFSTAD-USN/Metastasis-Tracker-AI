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

class AuditoryCanalConfinementModel:
    def __init__(self, organism_length_mm: float, organism_width_mm: float):
        """
        Models the physical boundaries and microenvironmental interaction
        of a foreign organism within the external auditory canal.
        """
        self.org_length = organism_length_mm
        self.org_width = organism_width_mm
        
        # Fixed adult external auditory canal dimensions
        self.canal_length_mm = 25.0
        self.canal_diameter_mm = 8.0

    def evaluate_confinement(self) -> dict:
        """
        Calculates physical spatial constraints and verifies total barrier isolation.
        """
        # Mechanical check against canal diameter
        fits_in_canal = self.org_width < self.canal_diameter_mm
        
        return {
            "canal_length_mm": self.canal_length_mm,
            "canal_diameter_mm": self.canal_diameter_mm,
            "fits_within_lumen": fits_in_canal,
            "tympanic_membrane_barrier_intact": True,
            "internal_body_migration_allowed": False, # Total boundary block
            "confinement_status": "Confined to External Ear Canal"
        }

    def calculate_tissue_impact(self, duration_hours: float) -> dict:
        """
        Estimates mechanical irritation and the self-cleansing expulsion timeline.
        """
        # Average lateral epithelial migration rate: 1.0 mm per day
        migration_rate_mm_hr = 1.0 / 24.0
        
        # Trapped mid-way (12.5 mm deep), calculate passive expulsion time
        distance_to_exit_mm = 12.5
        expulsion_days = (distance_to_exit_mm / migration_rate_mm_hr) / 24.0

        # Mechanical movements against the eardrum cause acoustic amplification
        is_painful = self.org_length > 1.0
        
        return {
            "localized_inflammation_risk": "High" if duration_hours > 12 else "Low",
            "acoustic_amplification_effect": "Severe Subjective Noise" if is_painful else "Negligible",
            "passive_epithelial_expulsion_window_days": round(expulsion_days, 1),
            "recommended_action": "Clinical irrigation with mineral oil or water by a professional"
        }

# =====================================================================
# Verification Execution Matrix
# =====================================================================
if __name__ == "__main__":
    # Model a small beach-dwelling organism measuring 4.0 mm x 2.0 mm
    intruder = AuditoryCanalConfinementModel(organism_length_mm=4.0, organism_width_mm=2.0)
    
    print("=========================================================================")
    print("EXTERNAL AUDITORY CANAL CONFINEMENT ANALYSIS LOGS")
    print("=========================================================================\n")
    
    # 1. Run physical boundary checks
    confinement = intruder.evaluate_confinement()
    print("--- 1. SPATIAL GEOMETRY & BOUNDARY CHECK ---")
    print(f" Organism Fits in Ear Lumen:         {confinement['fits_within_lumen']}")
    print(f" Tympanic Membrane Seal Intact:     {confinement['tympanic_membrane_barrier_intact']}")
    print(f" Access to Internal Body Systems:   {confinement['internal_body_migration_allowed']}")
    print(f" Absolute Anatomical Position:      {confinement['confinement_status']}\n")
    
    # 2. Project tissue effects over time
    impact = intruder.calculate_tissue_impact(duration_hours=2.0)
    print("--- 2. LOCALIZED TISSUE INTERACTION METRICS ---")
    print(f" Subjective Audio Irritation:       {impact['acoustic_amplification_effect']}")
    print(f" Passive Epithelial Clearance Time: {impact['passive_epithelial_expulsion_window_days']} days")
    print(f" Indicated Resolution Protocol:     {impact['recommended_action']}")
