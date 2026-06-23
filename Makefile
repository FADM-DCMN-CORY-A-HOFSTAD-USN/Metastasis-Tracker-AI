# Append these lines to your existing root Makefile mapping core target shortcuts
# Append these validation targets to your repository root Makefile mapping configuration
.PHONY: plot config-archive animate test-bounds compile-gif test-anticoag test-schema export-fhir compile-csv test-fhir-pipeline test-reflexes export-reflex-fhir test-local-workflow print-h5-schema parse-h5 test-hdf5-compliance visualize-pulmonary

test-local-workflow:
	@echo "Launching complete local validation testing workflow suite..."
	chmod +x tests/run_local_workflow.sh
	./tests/run_local_workflow.sh

visualize-pulmonary:
	@echo "Extracting telemetry arrays to render diagnostic pulmonary compliance line charts..."
	python3 -c "from src.pulmonary_hdf5_core import HDF5TelemetryPipelineEngine; e=HDF5TelemetryPipelineEngine('tests/pipeline_telemetry.h5'); e.write_mock_hdf5_telemetry_file(8809, 1.0, 8); from src.pulmonary_visualizer import HDF5PulmonaryVisualizer; v=HDF5PulmonaryVisualizer('tests/pipeline_telemetry.h5'); v.load_and_render_trends()"

parse-h5:
	@echo "Parsing high-density HDF5 data logs into human-readable console rows..."
	python3 -c "from src.pulmonary_hdf5_core import HDF5TelemetryPipelineEngine; e=HDF5TelemetryPipelineEngine('tests/pipeline_telemetry.h5'); e.write_mock_hdf5_telemetry_file(8809, 1.0, 5); e.execute_terminal_parser_stream()"

test-hdf5-compliance:
	@echo "Executing continuous integration HDF5 container format verifications..."
	python3 src/pulmonary_hdf5_core.py

print-h5-schema:
	@echo "Displaying multi-dimensional HDF5 database logging layout schemas..."
	python3 -c "from src.pulmonary_collapse_engine import PulmonaryCollapseSimulationEngine; print(PulmonaryCollapseSimulationEngine.get_hdf5_logging_schema_template())"

test-reflexes:
	@echo "Executing aerodynamic gas jet and somatic muscular reflex unit verifications..."
	python3 src/respiratory_reflex_engine.py

export-reflex-fhir:
	@echo "Processing respiratory reflex metrics into HL7 FHIR R4 JSON observation structures..."
	python3 -c "from src.respiratory_reflex_engine import IntegratedRespiratoryReflexEngine; e=IntegratedRespiratoryReflexEngine(175,72,1.0); r=e.evaluate_lower_airway_cough(0,4.5,7.4); e.commit_fhir_observation_record('pat-09', r)"

parse-reflex-fhir:
	@echo "Unpacking nested FHIR JSON observation payloads into human-readable text blocks..."
	python3 src/data/fhir/parse_reflex_payload.py

compile-csv:
	@echo "Flattening individual timestamped JSON logs into a unified flat CSV spreadsheet..."
	chmod +x src/data/fhir/compile_csv.sh
	./src/data/fhir/compile_csv.sh

test-fhir-pipeline:
	@echo "Executing schema rule checking runs and testing fhir stream integrations..."
	python3 src/data/fhir/fhir_pipeline.py

export-fhir:
	@echo "Serializing runtime hemostasis values down to HL7 FHIR R4 compliant schemas..."
	python3 src/data/fhir/payload_writer.py

test-schema:
	@echo "Executing continuous schema verification loops against YAML profiles..."
	python3 src/fibrinolysis_verifier_core.py

compile-gif:
	@echo "Executing frame compression and compiling animated .gif payload packages..."
	chmod +x src/compile_gif.sh
	./src/compile_gif.sh

test-anticoag:
	@echo "Running dynamic clotting inhibition system unit verifications..."
	python3 src/trauma_anticoag_core.py

animate:
	@echo "Compiling animated spatial tracking rotation path sequences..."
	python3 -c "from src.voxel_coordinate_interface import OcularVoxelStructuralInterface; v=OcularVoxelStructuralInterface(); [v.inject_tracking_coordinate_node(0.5,0.5,i/10.0) for i in range(10)]; v.render_animated_rotation_sequence()"

test-bounds:
	@echo "Running programmatic unit boundary checks against 3D voxel input channels..."
	python3 -m unittest tests/test_voxel_boundaries.py


plot:
	@echo "Processing packed tracking spatial coordinates arrays into 3D Voxel models..."
	python3 src/voxel_coordinate_interface.py

config-archive:
	@echo "Parsing YAML retention thresholds to execute automated configuration archiving..."
	python3 src/archive_config_wrapper.py

# Default target executes complete continuous validation bounds
all: validate test

validate:
	@echo "Executing continuous integration diagnostic drivers..."
	./run_pipeline.sh

test:
	@echo "Running end-to-end multi-module pipeline validation assertions..."
	python3 -m unittest tests/test_integration_pipeline.py

run-ui:
	@echo "Launching real-time command-line bioenergetic dashboard panel..."
	python3 src/metabolic_dashboard_engine.py

parse:
	@echo "Decoding compressed .medbin streams to raw console layout text..."
	python3 src/medbin_terminal_parser.py

archive:
	@echo "Initiating file compression on historical binary telemetry trees..."
	python3 src/telemetry_archiver.py

local-webhook:
	@echo "Launching local test loop server to catch outbound alert JSON streams..."
	chmod +x tests/test_local_webhook.sh
	./tests/test_local_webhook.sh

help:
	@echo "========================================================================="
	@echo "  METASTASIS-TRACKER-AI CONTROL SYSTEM MAKEFILE INTERFACE"
	@echo "========================================================================="
	@echo "  make validate        - Executes the main shell pipeline driver checking permissions"
	@echo "  make test            - Runs the synchronized end-to-end integration test suites"
	@echo "  make run-ui          - Launches the real-time live terminal patient telemetry table"
	@echo "  make parse           - Decodes medbin files directly to text rows on the screen"
	@echo "  make archive         - Compresses historical data files into zipped packages"
	@echo "  make local-webhook   - Tests JSON notification hooks using background listeners"
	@echo "========================================================================="
