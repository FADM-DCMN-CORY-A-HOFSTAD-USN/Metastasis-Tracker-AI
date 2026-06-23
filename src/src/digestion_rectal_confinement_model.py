import math

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
