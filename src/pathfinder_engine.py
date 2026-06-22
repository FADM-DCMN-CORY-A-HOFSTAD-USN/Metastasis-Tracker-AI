import json
import math
from patient_anatomy import PatientSimulationEngine, AdvancedMetabolicEngine
from target_proteins import OncologicalTargetProteinEngine
from state_matrix import PycnogonidStateMatrix

class ParasitePathfinder:
    """
    Orchestrates the movement of a Pycnogonid variant species through the 
    vascular environment, driven by chemical gradients and pH-dependent enzymes.
    """
    def __init__(self, patient_config, agent_config, enzymes_filepath):
        # 1. Generate the Anatomical Environment
        self.anatomy = PatientSimulationEngine(**patient_config)
        self.metabolism = AdvancedMetabolicEngine(**patient_config)
        
        # Build the physical vascular tree
        self.circulatory_system = self.anatomy.generate_circulatory_tree()["systemic_arterial_tree"]
        
        # Calculate systemic pH mapping (assuming a baseline salivary pH of 6.8)
        self.ph_matrix = self.metabolism.generate_systemic_ph_matrix(salivary_ph=6.8)
        
        # 2. Initialize the Protein Targeting Engine
        self.target_engine = OncologicalTargetProteinEngine()
        
        # 3. Initialize the Parasite Agent and its Toxic Enzymes
        self.agent = PycnogonidStateMatrix(agent_config)
        
        with open(enzymes_filepath, 'r') as f:
            enzyme_data = json.load(f)
            self.salivary_enzymes = enzyme_data["pycnogonid_salivary_profile"]

    def _calculate_enzyme_efficiency(self, local_ph):
        """
        Calculates how effectively the parasite can digest host tissue 
        based on how close the local pH is to its enzymes' optimal pH.
        """
        efficiencies = {}
        for enzyme_name, profile in self.salivary_enzymes.items():
            optimal_ph = profile["optimal_ph"]
            # Gaussian drop-off: efficiency drops as pH deviates from optimal
            efficiency = math.exp(-((local_ph - optimal_ph) ** 2) / (2 * (0.5 ** 2)))
            efficiencies[enzyme_name] = round(efficiency * 100, 2)
        return efficiencies

    def simulate_infection_path(self, start_generation=0):
        print(f"--- INITIATING PYCNOGONID INFECTION PATHWAY ---")
        print(f"Agent ID: {self.agent.agent_id} | Initial State: {self.agent.current_state}\n")
        
        # Traverse the vascular tree generation by generation
        for vessel in self.circulatory_system[start_generation:]:
            gen = vessel["generation"]
            radius_m = vessel["radius_m"]
            
            # Fetch local pH from the pre-calculated anatomical matrix
            local_ph = self.ph_matrix["circulatory_paths"]["systemic_loop"][gen]["estimated_ph"]
            
            # 1. Map Target Proteins for this specific generation/pH
            protein_profile = self.target_engine.calculate_generational_protein_targets(
                generation=gen, 
                local_ph=local_ph, 
                vessel_radius_m=radius_m, 
                wall_length_m=vessel["length_m"]
            )
            
            # Simulate a chemokine gradient (CXCL12) pulling the parasite
            cxcl12_density = protein_profile["target_protein_profiles"]["cxcl12"]["surface_density_molecules_um2"]
            normalized_gradient = min(1.0, cxcl12_density / 300.0) # Normalize for the state matrix
            
            # 2. Construct the localized environment dictionary for the Agent
            env_context = {
                "temperature": 37.0, # Human body temp
                "ph": local_ph,
                "noise_level_db": 45.0, # Internal vascular fluid noise
                "chemical_gradient_delta_c": normalized_gradient
            }
            
            # Simulate physical lodging risk (parasite size vs vessel radius)
            penetration_chance = 0.8 if self.agent.leg_span > (radius_m * 1000) else 0.1
            
            telemetry = {
                "w_host": 6.0, # Host viability score
                "p_penetrate": penetration_chance, 
                "time_elapsed": gen * 2.5 # Arbitrary time scaling
            }
            
            # 3. Evaluate Agent State Matrix
            step_result = self.agent.evaluate_state_tick(env_context, telemetry)
            
            print(f"Gen {gen:02d} | Vessel Radius: {radius_m*1e6:.1f} um | Local pH: {local_ph:.2f}")
            print(f"   -> CXCL12 Gradient: {normalized_gradient:.2f} | HSI: {step_result['calculated_hsi']:.3f}")
            print(f"   -> Agent Action: {step_result['current_state']} (Velocity: {step_result['step_velocity_mm_sec']:.2f} mm/s)")
            
            # 4. Trigger Encystment & Digestion Logic
            if step_result['current_state'] == "ENCYSTED_FEEDING":
                print(f"\n[!] CRITICAL: Agent has lodged at Generation {gen}.")
                print(f"[!] Initiating Toxic Enzyme Release...")
                
                enzyme_performance = self._calculate_enzyme_efficiency(local_ph)
                for enzyme, efficiency in enzyme_performance.items():
                    print(f"   -> {enzyme} efficiency at local pH {local_ph}: {efficiency}%")
                
                print("\n--- INFECTION PATH CONCLUDED (VESICLE FORMATION BEGUN) ---")
                break 

if __name__ == "__main__":
    # Example Initialization
    patient_data = {
        "height_cm": 180.0, 
        "weight_kg": 80.0, 
        "body_build": "mesomorph", 
        "hydration_level": 0.95
    }
    
    agent_data = {
        "agent_id": "Pycnogonid_Alpha_01",
        "physical_properties": {
            "leg_span_mm": 2.5,  # 2.5 mm leg span
            "leg_ratio_r": 1.2
        }
    }
    
    # Run the engine
    tracker = ParasitePathfinder(
        patient_config=patient_data, 
        agent_config=agent_data, 
        enzymes_filepath="parasite_enzymes.json"
    )
    
    tracker.simulate_infection_path(start_generation=0)
