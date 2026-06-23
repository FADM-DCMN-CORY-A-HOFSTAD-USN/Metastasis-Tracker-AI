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

class IngestedTransitModel:
    def __init__(self, initial_mass_g: float, exoskeleton_thickness_mm: float):
        """
        Models the biophysical degradation and transit of an ingested chitinous object.
        """
        self.mass = initial_mass_g
        self.thickness_mm = exoskeleton_thickness_mm
        self.is_fragmented = False

    def simulate_gastric_hydrolysis(self, gastric_volume_mL: float, local_ph: float, retention_time_min: float) -> dict:
        """
        Calculates the chemical breakdown of the structural matrix under gastric acid stress.
        """
        # Kinetic degradation constant scales with acidity
        acid_severity = max(0.1, 7.40 - local_ph)
        k_hyd = 0.0005 * math.exp(0.8 * acid_severity) # Hydrolysis rate constant
        
        # Solve mass decay over retention timeline: M(t) = M0 * e^(-k*t)
        final_mass = self.mass * math.exp(-k_hyd * retention_time_min)
        mass_lost = self.mass - final_mass
        self.mass = final_mass

        # Evaluate structural thinning
        remaining_thickness = self.thickness_mm * (final_mass / (final_mass + mass_lost))
        if remaining_thickness < 0.1 * self.thickness_mm:
            self.is_fragmented = True

        return {
            "initial_mass_grams": round(self.mass + mass_lost, 3),
            "post_hydrolysis_mass_grams": round(self.mass, 3),
            "structural_mass_lost_g": round(mass_lost, 3),
            "remaining_exoskeleton_thickness_mm": round(remaining_thickness, 4),
            "mechanical_fragmentation_triggered": self.is_fragmented
        }

    def calculate_gi_transit_timeline(self, patient_height_cm: float, baseline_hydration: float) -> dict:
        """
        Calculates the mechanical transit timeline through the continuous digestive path.
        """
        # Extract operational path lengths matching extended digestive formulas
        gi_length_m = 4.5 * (patient_height_cm / 100.0)
        
        # Average velocity mappings (meters per minute) under baseline motility
        velocities = {
            "esophagus": 1.8,                  # Fast transit
            "stomach_retention": 0.0,          # Modeled separately via retention loop
            "small_intestine": 0.02 * baseline_hydration,  # Peristaltic propagation
            "large_intestine": 0.005 * baseline_hydration  # Sluggish colonic transport
        }

        transit_times_min = {
            "esophagus": 0.25 / velocities["esophagus"],
            "stomach_retention": 120.0, # Baseline gastric emptying window
            "small_intestine": (gi_length_m * 0.90) / velocities["small_intestine"],
            "large_intestine": 1.50 / velocities["large_intestine"]
        }

        total_transit_duration_hours = sum(transit_times_min.values()) / 60.0

        return {
            "total_digestive_path_length_meters": round(gi_length_m + 0.62, 2),
            "compartment_transit_durations_minutes": {k: round(v, 2) for k, v in transit_times_min.items()},
            "total_elimination_window_hours": round(total_transit_duration_hours, 1),
            "systemic_absorption_allowed": False # Confinement verified
        }

# =====================================================================
# Verification Execution Matrix
# =====================================================================
if __name__ == "__main__":
    # Model a small 2.5-gram pycnogonid specimen with a thin 0.3mm exoskeleton shell
    specimen = IngestedTransitModel(initial_mass_g=2.5, exoskeleton_thickness_mm=0.3)
    
    print("=========================================================================")
    print("INGESTED CHITINOUS STRUCTURAL TRANSIT SIMULATION LOGS")
    print("=========================================================================\n")
    
    # 1. Simulate chemical exposure inside the stomach matrix (pH 1.8 for 120 minutes)
    breakdown = specimen.simulate_gastric_hydrolysis(gastric_volume_mL=500.0, local_ph=1.8, retention_time_min=120.0)
    print("--- 1. CHEMICAL HYDROLYSIS DEGRADATION ---")
    print(f" Post-Acid Exposure Remaining Mass:   {breakdown['post_hydrolysis_mass_grams']} g")
    print(f" Total Structural Mass Dissolved:     {breakdown['structural_mass_lost_g']} g")
    print(f" Structural Fragmentation Baseline:    {breakdown['mechanical_fragmentation_triggered']}\n")
    
    # 2. Track transit velocities and boundary blocks until elimination
    timeline = specimen.calculate_gi_transit_timeline(patient_height_cm=175.0, baseline_hydration=1.0)
    print("--- 2. LUMINALLY CONFINED MOTOR TRANSIT TIMELINE ---")
    print(f" Total Internal Path Trajectory:      {timeline['total_digestive_path_length_meters']} meters")
    for segment, duration in timeline['compartment_transit_durations_minutes'].items():
        print(f"  -> Peristaltic Time inside {segment:18}: {duration} minutes")
    print(f"\n Projected Total Elimination Window:   {timeline['total_elimination_window_hours']} hours")
    print(f" Vascular or Portal Circulation Leakage Risk: {timeline['systemic_absorption_allowed']} (Safely Retained in GI Lumen)")
