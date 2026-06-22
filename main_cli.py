#!/usr/bin/env parser
import numpy as np
import argparse
import json
import os
import sys
from datetime import datetime
from src.clinical_pipeline import OncologyPredictionPipeline

def generate_fhir_bundle(lodging_data, final_mass_projection, clinical_stage, patient_id="EHR-2026-9904"):
    """
    Compiles the clinical simulation results into a valid HL7/FHIR R4 Transaction Bundle.
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    fhir_bundle = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
          {
            "fullUrl": "urn:uuid:diagnostic-report-metastasis-01",
            "resource": {
              "resourceType": "DiagnosticReport",
              "status": "final",
              "category": [
                {
                  "coding": [
                    {
                      "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                      "code": "LAB",
                      "display": "Laboratory"
                    }
                  ]
                }
              ],
              "code": {
                "coding": [
                  {
                    "system": "http://loinc.org",
                    "code": "60568-3",
                    "display": "Pathology Synoptic report"
                  }
                ],
                "text": "Predictive Oncology Metastasis Report"
              },
              "subject": {
                "reference": f"Patient/{patient_id}"
              },
              "effectiveDateTime": timestamp,
              "conclusion": f"Predicted Clinical Stage: {clinical_stage}",
              "result": [
                { "reference": "urn:uuid:obs-vector-class" },
                { "reference": "urn:uuid:obs-blockage-site" },
                { "reference": "urn:uuid:obs-tissue-ph" },
                { "reference": "urn:uuid:obs-pop-total" }
              ]
            },
            "request": {
              "method": "POST",
              "url": "DiagnosticReport"
            }
          },
          {
            "fullUrl": "urn:uuid:obs-vector-class",
            "resource": {
              "resourceType": "Observation",
              "status": "final",
              "code": {
                "text": "Vector Classification"
              },
              "subject": {
                "reference": f"Patient/{patient_id}"
              },
              "valueString": "Marine Variant Species"
            },
            "request": {
              "method": "POST",
              "url": "Observation"
            }
          },
          {
            "fullUrl": "urn:uuid:obs-blockage-site",
            "resource": {
              "resourceType": "Observation",
              "status": "final",
              "code": {
                "coding": [
                  {
                    "system": "http://snomed.info/sct",
                    "code": "361083003",
                    "display": "Normal anatomy"
                  }
                ],
                "text": "Primary Blockage Site"
              },
              "subject": {
                "reference": f"Patient/{patient_id}"
              },
              "valueString": f"Systemic Generation {lodging_data.get('generation', 'Unknown')}"
            },
            "request": {
              "method": "POST",
              "url": "Observation"
            }
          },
          {
            "fullUrl": "urn:uuid:obs-tissue-ph",
            "resource": {
              "resourceType": "Observation",
              "status": "final",
              "code": {
                "coding": [
                  {
                    "system": "http://loinc.org",
                    "code": "2744-1",
                    "display": "pH of Tissue"
                  }
                ],
                "text": "Host Tissue pH"
              },
              "subject": {
                "reference": f"Patient/{patient_id}"
              },
              "valueQuantity": {
                "value": lodging_data.get('local_ph', 7.4),
                "unit": "pH",
                "system": "http://unitsofmeasure.org",
                "code": "[pH]"
              }
            },
            "request": {
              "method": "POST",
              "url": "Observation"
            }
          },
          {
            "fullUrl": "urn:uuid:obs-pop-total",
            "resource": {
              "resourceType": "Observation",
              "status": "final",
              "code": {
                "text": "Tumor Mass Projection: Total Variant Species Density"
              },
              "subject": {
                "reference": f"Patient/{patient_id}"
              },
              "valueQuantity": {
                "value": int(final_mass_projection),
                "unit": "units"
              }
            },
            "request": {
              "method": "POST",
              "url": "Observation"
            }
          }
        ]
    }
    return fhir_bundle

def main():
    parser = argparse.ArgumentParser(
        description="Clinical CLI Command Center for Metastasis-Tracker-AI Engine."
    )
    
    # Required Clinical Inputs
    parser.add_argument("--ehr", required=True, help="Path to the patient's ingested EHR JSON profile.")
    parser.add_argument("--enzymes", default="src/parasite_enzymes.json", help="Path to parasite enzyme profiles.")
    parser.add_argument("--breeding", default="src/breeding_matrix.json", help="Path to the population matrix rules.")
    
    # Simulation Constraints
    parser.add_argument("--months", type=int, default=6, help="Staging projection timeline window (months).")
    parser.add_argument("--agent_id", default="Vect_Alpha_Prod", help="Unique tracker ID assigned to the tracking instance.")
    
    # Outbound Router Destinations
    parser.add_argument("--export-fhir", help="Output filepath to drop the compliant FHIR JSON payload.")
    
    args = parser.parse_args()

    # Validate structural dependencies
    for path in [args.ehr, args.enzymes, args.breeding]:
        if not os.path.exists(path):
            print(f"[-] Critical Error: Required file dependency missing -> {path}")
            sys.exit(1)

    # Hardcoded baseline parameters for the physical vector configuration
    agent_config = {
        "agent_id": args.agent_id,
        "physical_properties": {
            "leg_span_mm": 2.5,
            "leg_ratio_r": 1.2
        }
    }

    try:
        # Initialize the underlying enterprise pipeline
        pipeline = OncologyPredictionPipeline(
            ehr_filepath=args.ehr,
            agent_config=agent_config,
            breeding_config_filepath=args.breeding,
            enzymes_filepath=args.enzymes
        )
        
        print("\n[*] Initializing Automated Clinical Assessment Pipeline...")
        # Note: Modified pipeline workflow back-returns localized metrics upon completion
        lodging_data, population_history, clinical_stage = pipeline.run_clinical_assessment(
            simulation_months=args.months
        )
        
        # Compile total systemic mass density from final generation tracking matrix
        total_final_mass = sum(population_history[:, -1]) if population_history is not None else 0

        # Handle outbound FHIR compilation if flag is checked
        if args.export_fhir:
            print(f"\n[*] Generating HL7/FHIR R4 Transaction Bundle...")
            fhir_payload = generate_fhir_bundle(
                lodging_data=lodging_data,
                final_mass_projection=total_final_mass,
                clinical_stage=clinical_stage,
                patient_id=os.path.basename(args.ehr).split('_')[0]
            )
            
            with open(args.export_fhir, 'w') as fhir_out:
                json.dump(fhir_payload, fhir_out, indent=2)
            print(f"[+] FHIR bundle successfully generated and written to: {args.export_fhir}")
            print(f"[!] Ready for outbound secure gateway transmission.")

    except Exception as e:
        print(f"[-] Execution halted due to pipeline processing anomaly: {str(e)}")
        sys.exit(1)

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

if __name__ == "__main__":
    main()
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
