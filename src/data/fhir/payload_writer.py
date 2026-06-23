import json
import os

class FHIRPayloadWriter:
    @staticmethod
    def commit_clinical_fhir_payload(patient_id: str, platelet_count: float, heparin_inhibition: float):
        """
        Ingests runtime tracking metrics and outputs a production-grade 
        HL7 FHIR R4 JSON transaction bundle directly to the data directory.
        """
        output_filepath = "src/data/fhir/patient_hemostasis_payload.json"
        
        fhir_bundle = {
            "resourceType": "Bundle",
            "id": f"tx-bundle-{patient_id}-2026",
            "type": "transaction",
            "entry": [
                {
                    "fullUrl": f"urn:uuid:patient-{patient_id}",
                    "resource": {
                        "resourceType": "Patient",
                        "id": patient_id,
                        "active": True,
                        "name": [{"use": "official", "family": "Simulation_Cohort", "given": [f"Subject_{patient_id}"]}]
                    },
                    "request": {"method": "POST", "url": "Patient"}
                },
                {
                    "fullUrl": "urn:uuid:observation-coag-01",
                    "resource": {
                        "resourceType": "Observation",
                        "id": f"obs-{patient_id}-coag",
                        "status": "final",
                        "category": [{"coding": [{"system": "http://hl7.org", "code": "laboratory", "display": "Laboratory"}]}],
                        "code": {
                            "coding": [{"system": "http://loinc.org", "code": "26515-7", "display": "Platelets [#/volume] in Blood by Automated count"}],
                            "text": "Platelet Concentration count coupled to dynamic drug inhibition scaling matrix."
                        },
                        "subject": {"reference": f"urn:uuid:patient-{patient_id}"},
                        "effectiveDateTime": "2026-06-23T14:48:00Z",
                        "valueQuantity": {"value": platelet_count, "unit": "cells/uL", "system": "http://unitsofmeasure.org", "code": "/uL"},
                        "component": [
                            {
                                "code": {"coding": [{"system": "http://local-simulation-identifiers/codes", "code": "ANTICOAG_IDX", "display": "Heparin Inhibition Index (I_drug)"}]},
                                "valueQuantity": {"value": heparin_inhibition, "unit": "fraction", "system": "http://unitsofmeasure.org", "code": "1"}
                            }
                        ]
                    },
                    "request": {"method": "POST", "url": "Observation"}
                }
            ]
        }

        # Safe serialization check to ensure target directory tree pathways exist
        dir_name = os.path.dirname(output_filepath)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(output_filepath, "w") as file_stream:
            json.dump(fhir_bundle, file_stream, indent=2)
            
        print(f"[+] FHIR R4 Inoperability transaction successfully written to: {output_filepath}")

if __name__ == "__main__":
    # Sandbox operational test run
    FHIRPayloadWriter.commit_clinical_fhir_payload(
        patient_id="pat-tracker-03", 
        platelet_count=250000.0, 
        heparin_inhibition=0.85
    )
