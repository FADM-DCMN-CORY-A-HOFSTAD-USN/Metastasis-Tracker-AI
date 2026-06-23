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

class NasalSinusExclusionEngine:
    def __init__(self, object_max_diameter_mm: float, is_motile: bool = False):
        """
        Models the physical entry parameters and mucociliary clearance timelines 
        of a foreign object within the paranasal sinus networks.
        """
        self.object_diameter = object_max_diameter_mm
        self.is_motile = is_motile # Non-native organisms lack compatible motility in mammalian mucus

    def evaluate_sinus_entry(self) -> dict:
        """
        Calculates mechanical entry allowances across the paranasal ostia metrics.
        """
        ostia_diameters = {
            "maxillary_sinus": 2.5,
            "frontal_sinus": 1.5,
            "sphenoid_sinus": 1.8,
            "ethmoid_cells": 1.0
        }

        entry_results = {}
        for sinus, ostium_d in ostia_diameters.items():
            # Structural mechanical check
            can_enter = self.object_diameter < ostium_d
            entry_results[sinus] = {
                "ostium_aperture_mm": ostium_d,
                "mechanical_entry_allowed": can_enter,
                "status": "Blocked by Bone Boundary" if not can_enter else "Passage Dimensionally Feasible"
            }
        return entry_results

    def calculate_clearance_timeline(self, nasal_path_length_cm: float = 8.0) -> dict:
        """
        Calculates the time required for the mucociliary escalator to expel 
        the object from the nasal cavity into the digestive tract.
        """
        # Baseline physiological mucus transport speed: 6.5 mm per minute
        v_mucus_mm_min = 6.5
        path_length_mm = nasal_path_length_cm * 10.0

        # Non-motile objects are moved strictly at the rate of the escalator vector
        if not self.is_motile:
            clearance_time_min = path_length_mm / v_mucus_mm_min
        else:
            clearance_time_min = path_length_mm / v_mucus_mm_min # Fallback standard physics

        return {
            "nasal_transit_distance_mm": path_length_mm,
            "mucociliary_velocity_mm_min": v_mucus_mm_min,
            "calculated_clearance_time_minutes": round(clearance_time_min, 2),
            "terminal_destination": "Oropharynx / Swallowed to Stomach Acid Sinks"
        }

# =====================================================================
# Operational Verification Loop
# =====================================================================
if __name__ == "__main__":
    # Model an unchewed seafood fragment or small appendage measuring 5.0 mm in diameter
    ingested_fragment = NasalSinusExclusionEngine(object_max_diameter_mm=5.0, is_motile=False)
    
    print("=========================================================================")
    print("PARANASAL SINUS MECHANICAL EXCLUSION & TRANSIT LOGS")
    print("=========================================================================\n")
    
    # 1. Run size checking simulation against paranasal boundaries
    exclusion_report = ingested_fragment.evaluate_sinus_entry()
    print("--- 1. PARANASAL OSTIA MECHANICAL SELECTION MATRIX ---")
    for sinus, reporting in exclusion_report.items():
        print(f" - {sinus.upper():16} -> Ostium: {reporting['ostium_aperture_mm']} mm | Access: {reporting['mechanical_entry_allowed']} ({reporting['status']})")
        
    # 2. Evaluate transit expulsion speeds along the nasal mucosa
    clearance_report = ingested_fragment.calculate_clearance_timeline(nasal_path_length_cm=8.0)
    print("\n--- 2. MUCOCILIARY EXPULSION TIMELINE TRACING ---")
    print(f" Total Transport Path Distance: {clearance_report['nasal_transit_distance_mm']} mm")
    print(f" Calculated Retention Window:  {clearance_report['calculated_clearance_time_minutes']} minutes until evacuation.")
    print(f" Final Particle Destination:    {clearance_report['terminal_destination']} (Confinement Confirmed)")
