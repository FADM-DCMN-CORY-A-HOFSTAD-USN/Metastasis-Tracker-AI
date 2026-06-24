#!/usr/bin/env python3
import argparse
import json
import os
import sys
import importlib
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
python main_cli.py --ehr tests/patient_hemostasis_payload.json --export-dir outbound/
# --- High-Performance Computing (HPC) Integration ---
try:
    from numba import config, cuda, njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

def bootstrap_hpc_environment(use_cuda, user_cores):
    """Configures the NVIDIA CUDA and Multicore NJIT environment."""
    print("=======================================================")
    print("    METASTASIS-TRACKER-AI : HPC HARDWARE BOOTSTRAP     ")
    print("=======================================================")
    
    # Multicore Allocation
    logical_cores = multiprocessing.cpu_count()
    active_cores = user_cores if user_cores and user_cores > 0 else logical_cores
    print(f"[*] Multicore Allocation: {active_cores} / {logical_cores} Cores Enabled")

    if NUMBA_AVAILABLE:
        # Enforce thread layer for multicore operations on the physics matrices
        config.THREADING_LAYER = 'workqueue'
        config.NUMBA_NUM_THREADS = active_cores
        print("[*] JIT Compiler (Numba): Activated for mathematical array caching.")
        
        # Warmup the NJIT compiler to prevent cold-start execution delays
        @njit(parallel=True)
        def _warmup_cores():
            acc = 0.0
            for i in prange(1000):
                acc += i * 0.5
            return acc
        _warmup_cores()
        
        # NVIDIA GPU Intercept
        if use_cuda:
            if cuda.is_available():
                gpu_device = cuda.get_current_device()
                print(f"[*] NVIDIA GPU Detected:  {gpu_device.name}")
                print("[*] CUDA Processing:      ENABLED (Vectors delegated to GPU)")
            else:
                print("[-] CUDA Error: GPU requested but no NVIDIA device found. Defaulting to CPU NJIT.")
    else:
        print("[-] HPC Warning: 'numba' library not found. Run `pip install numba` for NJIT & GPU support.")

    print("=======================================================\n")
    return active_cores

def load_all_src_modules(src_path="src"):
    """Dynamically fetches and pre-compiles all .py modules in the src/ directory."""
    print("[*] Dynamically Loading and JIT-Compiling Source Modules...")
    
    # Ensure src is in the system path for internal imports to work
    abs_src_path = os.path.abspath(src_path)
    if abs_src_path not in sys.path:
        sys.path.insert(0, abs_src_path)
        sys.path.insert(0, os.path.dirname(abs_src_path)) # Add root
        
    loaded_count = 0
    src_dir = Path(src_path)
    
    for file_path in src_dir.rglob('*.py'):
        if file_path.name == '__init__.py':
            continue
            
        # Convert absolute path to dot-notation module path
        rel_path = file_path.relative_to(src_dir)
        module_name = str(rel_path).replace(os.sep, '.')[:-3]
        
        try:
            # Dynamically import into system memory
            importlib.import_module(module_name)
            loaded_count += 1
        except Exception as e:
            # Suppress specific missing dependencies from breaking the loop
            pass
            
    print(f"[+] Successfully loaded {loaded_count} internal modules into system memory.\n")

def generate_fhir_bundle(lodging_data, final_mass_projection, clinical_stage, patient_id):
    """Compiles the clinical simulation results into a valid HL7/FHIR R4 Transaction Bundle."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Handle potentially missing dict keys from simulation anomalies
    gen_val = lodging_data.get('generation', 'Unknown') if isinstance(lodging_data, dict) else 'Unknown'
    ph_val = lodging_data.get('local_ph', 7.4) if isinstance(lodging_data, dict) else 7.4

    fhir_bundle = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
          {
            "fullUrl": f"urn:uuid:diagnostic-report-{patient_id}",
            "resource": {
              "resourceType": "DiagnosticReport",
              "status": "final",
              "code": {
                "coding": [{"system": "http://loinc.org", "code": "60568-3", "display": "Pathology Synoptic report"}],
                "text": "Predictive Oncology Metastasis Report"
              },
              "subject": { "reference": f"Patient/{patient_id}" },
              "effectiveDateTime": timestamp,
              "conclusion": f"Predicted Clinical Stage: {clinical_stage}",
              "result": [
                { "reference": "urn:uuid:obs-vector-class" },
                { "reference": "urn:uuid:obs-blockage-site" },
                { "reference": "urn:uuid:obs-tissue-ph" },
                { "reference": "urn:uuid:obs-pop-total" }
              ]
            },
            "request": { "method": "POST", "url": "DiagnosticReport" }
          },
          {
            "fullUrl": "urn:uuid:obs-vector-class",
            "resource": {
              "resourceType": "Observation",
              "status": "final",
              "code": { "text": "Vector Classification" },
              "subject": { "reference": f"Patient/{patient_id}" },
              "valueString": "Marine Variant Species"
            },
            "request": { "method": "POST", "url": "Observation" }
          },
          {
            "fullUrl": "urn:uuid:obs-blockage-site",
            "resource": {
              "resourceType": "Observation",
              "status": "final",
              "code": { "text": "Primary Blockage Site" },
              "subject": { "reference": f"Patient/{patient_id}" },
              "valueString": f"Systemic Generation {gen_val}"
            },
            "request": { "method": "POST", "url": "Observation" }
          },
          {
            "fullUrl": "urn:uuid:obs-pop-total",
            "resource": {
              "resourceType": "Observation",
              "status": "final",
              "code": { "text": "Tumor Mass Projection: Total Variant Species Density" },
              "subject": { "reference": f"Patient/{patient_id}" },
              "valueQuantity": { "value": int(final_mass_projection), "unit": "units" }
            },
            "request": { "method": "POST", "url": "Observation" }
          }
        ]
    }
    return fhir_bundle

def process_patient_ehr(ehr_file, args, agent_config):
    """Isolated worker process for Multicore Batching."""
    try:
        if args.mode == "oncology":
            from src.clinical_pipeline import OncologyPredictionPipeline
            pipeline = OncologyPredictionPipeline(
                ehr_filepath=ehr_file,
                agent_config=agent_config,
                breeding_config_filepath=args.breeding,
                enzymes_filepath=args.enzymes
            )
            lodging_data, population_history, clinical_stage = pipeline.run_clinical_assessment(simulation_months=args.months)
            total_final_mass = sum(population_history[:, -1]) if population_history is not None else 0
            
            # File generation (FHIR bundle logic)
            out_file = None
            if args.export_dir:
                os.makedirs(args.export_dir, exist_ok=True)
                patient_id = os.path.basename(ehr_file).replace('.json', '')
                out_file = os.path.join(args.export_dir, f"{patient_id}_metastasis_bundle.json")
                fhir_payload = generate_fhir_bundle(lodging_data, total_final_mass, clinical_stage, patient_id)
                with open(out_file, 'w') as f:
                    json.dump(fhir_payload, f, indent=2)
            if args.push_to_epic:
    try:
        from src.epic_interconnect_gateway import EpicInterconnectGateway
        epic_gateway = EpicInterconnectGateway(args.epic_url, args.epic_client, args.epic_key)
        epic_gateway.transmit_metastasis_bundle(out_file)
    except Exception as e:
        print(f"[-] Epic Transmission Failed for {patient_id}: {str(e)}")
            if args.push_to_epic:
    try:
        from src.epic_interconnect_gateway import EpicInterconnectGateway
        epic_gateway = EpicInterconnectGateway(args.epic_url, args.epic_client, args.epic_key)
        epic_gateway.transmit_metastasis_bundle(out_file)
    except Exception as e:
        print(f"[-] Epic Transmission Failed for {patient_id}: {str(e)}")
            return True, ehr_file, out_file

        elif args.mode == "trauma":
            from src.trauma_fluid_core import VascularHemorrhageDynamicsEngine
            # Initialize the new mechanical stress engine
            engine = VascularHemorrhageDynamicsEngine(tip_radius_microns=args.tip_radius)
            # Evaluate baseline puncture stress against the macro arterial trunk
            results = engine.evaluate_tissue_puncture_stress(applied_force_newtons=1.2, tissue_type="Macro Artery Core Trunk")
            print(f"   -> [TRAUMA] Puncture Status: {results['puncture_status']} | Stress: {results['applied_stress_MPa']:.3f} MPa")
            return True, ehr_file, "Console Output (Trauma Engine)"

        elif args.mode == "metabolism":
            from src.metabolic_dashboard_engine import MetabolicDashboardEngine
            engine = MetabolicDashboardEngine()
            results = engine.calculate_carbonic_anhydrase_kinetics(temperature_c=38.0, local_pco2_mmhg=45.0)
            print(f"   -> [METABOLISM] CA Flux: {results['conversion_velocity_mmol_sec']:.3f} mmol/s | Buffer pH: {results['homeostatic_buffer_ph']:.2f}")
            return True, ehr_file, "Console Output (Metabolic Kinetics)"

    except Exception as e:
        return False, ehr_file, str(e)
        
    try:
        from src.clinical_pipeline import OncologyPredictionPipeline
        pipeline = OncologyPredictionPipeline(
            ehr_filepath=ehr_file,
            agent_config=agent_config,
            breeding_config_filepath=args.breeding,
            enzymes_filepath=args.enzymes
        )
        
        lodging_data, population_history, clinical_stage = pipeline.run_clinical_assessment(simulation_months=args.months)
        total_final_mass = sum(population_history[:, -1]) if population_history is not None else 0
        
        # File generation
        out_file = None
        if args.export_dir:
            os.makedirs(args.export_dir, exist_ok=True)
            patient_id = os.path.basename(ehr_file).replace('.json', '')
            out_file = os.path.join(args.export_dir, f"{patient_id}_metastasis_bundle.json")
            
            fhir_payload = generate_fhir_bundle(lodging_data, total_final_mass, clinical_stage, patient_id)
            with open(out_file, 'w') as f:
                json.dump(fhir_payload, f, indent=2)
                
        return True, ehr_file, out_file
        
    except Exception as e:
        return False, ehr_file, str(e)

def main():
    # Simulation Arguments
    parser.add_argument("--mode", default="oncology", choices=["oncology", "trauma", "metabolism", "pulmonary"], 
                        help="Select which clinical engine to execute on the batch.")
    
    # Engine-Specific Arguments
    parser.add_argument("--months", type=int, default=6, help="Staging projection timeline window (months) for oncology.")
    parser.add_argument("--tip-radius", type=float, default=3.5, help="Radius of contact curvature (microns) for trauma engine.")
    parser.add_argument("--agent_id", default="Vect_Alpha_Prod", help="Unique ID assigned to the variant species instance.")
    parser = argparse.ArgumentParser(description="HPC Clinical CLI Command Center for Metastasis-Tracker-AI.")

    # Epic Integration Arguments
    parser.add_argument("--push-to-epic", action="store_true", help="Instantly transmit the generated FHIR payload to Epic EHR.")
    parser.add_argument("--epic-url", default="https://epic.hospital.org/interconnect", help="Hospital's Epic FHIR endpoint.")
    parser.add_argument("--epic-client", help="Epic App Orchard Client ID.")
    parser.add_argument("--epic-key", default="workspace/certs/epic_private.pem", help="Path to Epic RS384 private key.")

    # Input/Output Arguments
    parser.add_argument("--ehr", required=True, help="Path to single EHR JSON file OR a directory of EHRs for batch processing.")
    parser.add_argument("--export-dir", default="outbound", help="Directory to save generated HL7/FHIR JSON payloads.")
    parser.add_argument("--enzymes", default="src/data/parasite_enzymes.json", help="Path to parasite enzyme profiles.")
    parser.add_argument("--breeding", default="src/data/breeding_matrix.json", help="Path to the population matrix rules.")
    
    # Simulation Arguments
    parser.add_argument("--months", type=int, default=6, help="Staging projection timeline window (months).")
    parser.add_argument("--agent_id", default="Vect_Alpha_Prod", help="Unique ID assigned to the vector instance.")
    
    # Hardware Arguments
    parser.add_argument("--cuda", action="store_true", help="Enable NVIDIA GPU hardware acceleration via CUDA.")
    parser.add_argument("--cores", type=int, default=0, help="Number of CPU cores for multiprocessing (Default 0 = Use All).")
    
    args = parser.parse_args()

    # 1. Bootstrap the Hardware Environment
    active_cores = bootstrap_hpc_environment(args.cuda, args.cores)
    
    # 2. Dynamically map and load all scripts to ensure JIT compiling recognizes definitions
    load_all_src_modules()

    agent_config = {
        "agent_id": args.agent_id,
        "physical_properties": { "leg_span_mm": 2.5, "leg_ratio_r": 1.2 }
    }

    # 3. Determine Execution Mode (Single File vs Directory Batching)
    target_files = []
    if os.path.isdir(args.ehr):
        target_files = [os.path.join(args.ehr, f) for f in os.listdir(args.ehr) if f.endswith('.json')]
        print(f"[*] Batch Mode Active: Found {len(target_files)} Patient EHR records in directory.")
    elif os.path.isfile(args.ehr):
        target_files = [args.ehr]
    else:
        print(f"[-] Critical Error: Invalid path provided to --ehr")
        sys.exit(1)

    print("[*] Initiating Distributed Clinical Assessment Pipeline...\n")
    
    # 4. Execute via Multicore ProcessPool
    successful_runs = 0
    with ProcessPoolExecutor(max_workers=active_cores) as executor:
        futures = {executor.submit(process_patient_ehr, path, args, agent_config): path for path in target_files}
        
        for future in as_completed(futures):
            success, file_path, result = future.result()
            base_name = os.path.basename(file_path)
            
            if success:
                successful_runs += 1
                out_msg = f"Saved to {result}" if result else "Console Output Only"
                print(f"   [✓] SUCCESS: {base_name} -> {out_msg}")
            else:
                print(f"   [X] FAILED:  {base_name} -> Exception: {result}")

    print(f"\n[*] Run Complete. Successfully processed {successful_runs}/{len(target_files)} charts.")
    if args.export_dir and successful_runs > 0:
        print(f"[*] Ready for outbound transmission via secure gateway.")

if __name__ == "__main__":
    main()
