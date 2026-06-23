import math

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
