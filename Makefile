# Append these lines to your existing root Makefile mapping core target shortcuts
# Append these validation targets to your repository root Makefile mapping configuration
.PHONY: plot config-archive animate test-bounds compile-gif test-anticoag


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
