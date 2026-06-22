import json
from patient_anatomy import AdvancedClinicalImmunoEngine
from pathfinder_engine import ParasitePathfinder
from population_engine import PycnogonidPopulationEngine

class OncologyPredictionPipeline:
    """
    Unified clinical orchestrator. Ingests EHR data, simulates the metastasis 
    vector, determines the lodging site, and projects tumor genesis (population growth).
    """
    def __init__(self, ehr_filepath: str, agent_config: dict, breeding_config_filepath: str, enzymes_filepath: str):
        print("--- INITIALIZING METASTASIS PREDICTION SUITE ---")
        
        # 1. Ingest Clinical Chart
        with open(ehr_filepath, 'r') as f:
            ehr_data = json.load(f)
            
        self.patient_config = AdvancedClinicalImmunoEngine.ingest_clinical_chart_profile(ehr_data)
        print(f"[*] EHR Ingested: Height {self.patient_config['engine_ready_height_cm']}cm, " 
              f"Hydration Index: {self.patient_config['derived_hydration_factor']}")
        
        # 2. Setup the Pathfinding Engine
        # Maps the patient's specific vascular tree and target proteins
        self.pathfinder = ParasitePathfinder(
            patient_config={
                "height_cm": self.patient_config["engine_ready_height_cm"],
                "weight_kg": self.patient_config["engine_ready_weight_kg"],
                "body_build": self.patient_config["engine_ready_build"],
                "hydration_level": self.patient_config["derived_hydration_factor"]
            },
            agent_config=agent_config,
            enzymes_filepath=enzymes_filepath
        )
        
        # 3. Setup the Tumor Staging Engine (Population Growth)
        with open(breeding_config_filepath, 'r') as f:
            breeding_config = json.load(f)
        self.population_engine = PycnogonidPopulationEngine(breeding_config)

    def run_clinical_assessment(self, simulation_months: int = 6):
        """
        Executes the full end-to-end clinical tracking and staging simulation.
        """
        # PHASE 1: INFECTION & SPREAD
        print("\n[PHASE 1: VASCULAR PATHFINDING]")
        lodging_data = self.pathfinder.simulate_infection_path(start_generation=0)
        
        if not lodging_data or lodging_data['state'] != "ENCYSTED_FEEDING":
            print("[!] Vector remained in systemic circulation or was destroyed. No tumor genesis detected.")
            return
            
        # PHASE 2: VESICLE FORMATION & TUMOR GENESIS
        print("\n[PHASE 2: TUMOR GENESIS & CALCIFICATION]")
        print(f"[*] Lodging confirmed at Vascular Generation {lodging_data['generation']}.")
        print(f"[*] Local Microenvironment: pH {lodging_data['local_ph']:.2f}")
        
        # Set up the micro-environment timeline for the population engine
        # Assuming body temperature is roughly homeostatic around 37C (98.6F), 
        # and vascular turbulence at the blockage site is highly restricted (near 0.0)
        env_timeline = [
            {
                "temperature": 37.0, 
                "turbulence": 0.05, 
                "ph": lodging_data['local_ph']
            } for _ in range(simulation_months)
        ]
        
        # Initialize the variant species starting cluster (e.g., 2 adults, 10 larvae)
        initial_cluster = [10.0, 5.0, 2.0, 0.0] 
        
        print(f"\n[PHASE 3: TUMOR STAGING PROJECTION ({simulation_months} MONTHS)]")
        population_history = self.population_engine.run_projection(
            initial_population=initial_cluster, 
            time_steps=simulation_months, 
            env_timeline=env_timeline
        )
        
        self._generate_clinical_report(lodging_data, population_history, simulation_months)

    def _generate_clinical_report(self, lodging_data, population_history, months):
        """
        Formats the output into a standardized medical summary.
        """
        print("\n=======================================================")
        print("          PREDICTIVE ONCOLOGY METASTASIS REPORT        ")
        print("=======================================================")
        print(f"Vector Classification: Marine Variant Species")
        print(f"Primary Blockage Site: Systemic Generation {lodging_data['generation']}")
        print(f"Host Tissue pH:        {lodging_data['local_ph']:.2f}")
        print("-------------------------------------------------------")
        print("Tumor Mass Projection (Variant Species Population Density):")
        
        stages = ["Larval Pool", "Juvenile", "Adult (Active)", "Brooding (Calcifying)"]
        for idx, stage in enumerate(stages):
            # Extract the final month's population count
            final_count = population_history[idx, -1]
            print(f"  - {stage:<22}: {final_count:,.0f} units")
            
        total_mass = sum(population_history[:, -1])
        
        # Basic staging logic based on population density/calcified shells
        clinical_stage = "Stage I"
        if total_mass > 500: clinical_stage = "Stage II"
        if total_mass > 2500: clinical_stage = "Stage III"
        if total_mass > 8000: clinical_stage = "Stage IV (Systemic Overload)"
            
        print("-------------------------------------------------------")
        print(f"Predicted Clinical Stage at {months} Months: {clinical_stage}")
        print("=======================================================\n")

if __name__ == "__main__":
    # Example execution for a clinical technician
    agent_params = {
        "agent_id": "Clinical_Variant_01",
        "physical_properties": {
            "leg_span_mm": 2.5,
            "leg_ratio_r": 1.2
        }
    }
    
    # In a real environment, this would point to a patient's exported JSON file
    pipeline = OncologyPredictionPipeline(
        ehr_filepath="sample_patient_ehr.json",
        agent_config=agent_params,
        breeding_config_filepath="breeding_matrix.json",
        enzymes_filepath="parasite_enzymes.json"
    )
    
    pipeline.run_clinical_assessment(simulation_months=6)
