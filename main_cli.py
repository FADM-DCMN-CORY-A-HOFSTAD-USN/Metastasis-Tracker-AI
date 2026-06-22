import numpy as np

# --- Core Metastasis Prediction Model ---

class MetastasisPredictor:
    """
    Simulates and predicts the hematogenous spread and lodging of cancer 
    (modeled conceptually as Pycnogonida) based on arterial geometry and flow dynamics.
    """
    
    def __init__(self, aorta_diameter_mm):
        """
        Initializes the model with the reference aortic diameter.
        :param aorta_diameter_mm: Diameter of the patient's aorta in millimeters.
        """
        self.AORTA_DIAMETER = aorta_diameter_mm
        self.TARGET_PROTEINS = {
            'Liver': ['P1', 'P2'],
            'Lung': ['P3', 'P4'],
            'Bone': ['P5', 'P6'],
            # ... Add organ-specific target proteins
        }

    def map_arterial_properties(self, arterial_diameter_mm):
        """
        Maps arterial diameter and calculates its percentage relative to the aorta.
        :param arterial_diameter_mm: Diameter of the arterial branch.
        :return: Tuple (arterial_percentage_of_aorta, is_smaller_than_aorta)
        """
        arterial_percentage_of_aorta = (arterial_diameter_mm / self.AORTA_DIAMETER) * 100
        return arterial_percentage_of_aorta, arterial_diameter_mm < self.AORTA_DIAMETER

    def calculate_pycnogonida_speed(self, pycnogonida_speed_mps, blood_flow_mps, against_flow=False):
        """
        Maps the net speed of the Pycnogonida (cancer cells) relative to the artery wall.
        :param pycnogonida_speed_mps: Intrinsic speed of the cell/Pycnogonida (m/s).
        :param blood_flow_mps: Local blood flow velocity (m/s).
        :param against_flow: True if traveling against the blood flow.
        :return: Net speed (m/s)
        """
        if against_flow:
            # Speed against blood flow
            net_speed = pycnogonida_speed_mps - blood_flow_mps
        else:
            # Speed with blood flow
            net_speed = pycnogonida_speed_mps + blood_flow_mps
            
        return net_speed

    def predict_lodging_and_growth(self, pycnogonida_size_mm, branch_diameter_mm):
        """
        Determines if a tumor lodges and grows based on size and vessel diameter.
        
        Rule: If pycnogonida size > diameter of arterial branch, Then Tumor exists.
        
        :param pycnogonida_size_mm: The effective size of the cancerous cell cluster.
        :param branch_diameter_mm: The local arterial branch diameter.
        :return: Boolean (True if lodging occurs)
        """
        if pycnogonida_size_mm > branch_diameter_mm:
            print("--- TUMOR LODGED: Pycnogonida size exceeds arterial diameter. ---")
            return True
        else:
            return False

    def measure_route_probability(self, available_branches, target_organ_proteins):
        """
        Measures the probability of a branch route based on diameter and target protein factors.
        
        Rule: Probability factored by largest diameter and target protein affinity.
        
        :param available_branches: A dictionary {branch_name: diameter_mm}.
        :param target_organ_proteins: List of proteins targeted by this specific cancer type.
        :return: The name of the most probable branch route.
        """
        # 1. Base probability on diameter (largest diameter is favored)
        if not available_branches:
            return None
            
        largest_branch = max(available_branches, key=available_branches.get)
        
        # 2. Factor in Target Protein Affinity (Simplified: count matches)
        # Assuming a dictionary where keys are organ/lymph and values are lists of proteins
        affinity_scores = {}
        
        for organ, required_proteins in self.TARGET_PROTEINS.items():
            # Calculate overlap between cancer targets and organ requirements
            match_count = len(set(target_organ_proteins) & set(required_proteins))
            affinity_scores[organ] = match_count
            
        # For simplicity, combine the largest diameter branch with the highest affinity organ
        # This logic would be a weighted average in a full model.
        
        print(f"\nTarget Protein Affinities: {affinity_scores}")
        
        # Simple selection: Choose the branch with the largest diameter
        return largest_branch

    def increment_and_locate_tumors(self, organ_arterial_flow, lymph_arterial_flow, bone_arterial_flow):
        """
        Increments through arterial flow data to determine tumor locations.
        """
        print("\n--- Determining Tumor Locations (Organ/Lymph/Bone) ---")
        
        # Increment Organs: General Tumor
        for organ, flow_data in organ_arterial_flow.items():
            print(f"Checking Organ Arterial Flow for: {organ}")
            # Logic here would involve iterating through vessels, calculating lodging probability,
            # and updating a risk score for the organ.
            
        # Increment Lymphs: Lymphoma
        for lymph, flow_data in lymph_arterial_flow.items():
            print(f"Checking Lymph Arterial Flow for: {lymph} (Lymphoma Risk)")
            
        # Increment Bone: Bone Cancer Infection
        for bone_region, flow_data in bone_arterial_flow.items():
            print(f"Checking Bone Arterial Flow for: {bone_region} (Bone Cancer Risk)")

# --- Example Usage ---

if __name__ == '__main__':
    # Initialize the predictor (Aorta Diameter: 30 mm)
    predictor = MetastasisPredictor(aorta_diameter_mm=30.0)

    # 1. Map Arterial Properties
    renal_artery_diameter = 6.0
    percent, is_smaller = predictor.map_arterial_properties(renal_artery_diameter)
    print(f"Renal Artery: {percent:.2f}% of Aorta. Is smaller: {is_smaller}") 

    # 2. Pycnogonida Dynamics
    blood_speed = 0.5 # m/s
    cell_intrinsic_speed = 0.05 # m/s
    speed_with = predictor.calculate_pycnogonida_speed(cell_intrinsic_speed, blood_speed, against_flow=False)
    speed_against = predictor.calculate_pycnogonida_speed(cell_intrinsic_speed, blood_speed, against_flow=True)
    print(f"Speed With Flow: {speed_with:.3f} m/s")
    print(f"Speed Against Flow: {speed_against:.3f} m/s") # Likely negative (pushed backward)

    # 3. Lodging Prediction
    cancer_cell_cluster_size = 0.4 # mm
    capillary_diameter = 0.008 # mm
    arteriole_diameter = 0.5 # mm

    lodges_in_arteriole = predictor.predict_lodging_and_growth(cancer_cell_cluster_size, arteriole_diameter)
    lodges_in_capillary = predictor.predict_lodging_and_growth(cancer_cell_cluster_size, capillary_diameter) 
    # Note: Lodging is predicted for the capillary, as 0.4 mm > 0.008 mm.

    # 4. Route Probability 
    available_routes = {'Pulmonary': 15.0, 'Hepatic': 10.0, 'Splenic': 7.0}
    # Assume this cancer type targets proteins P1 and P5
    cancer_targets = ['P1', 'P5', 'Unknown'] 
    
    best_route = predictor.measure_route_probability(available_routes, cancer_targets)
    print(f"Most Probable Initial Route (based on diameter): {best_route}")

    # 5. Tumor Location Increment
    predictor.increment_and_locate_tumors(
        organ_arterial_flow={'Liver': 'data...', 'Kidney': 'data...'},
        lymph_arterial_flow={'Thoracic Duct': 'data...'},
        bone_arterial_flow={'Femur': 'data...'}
    )
