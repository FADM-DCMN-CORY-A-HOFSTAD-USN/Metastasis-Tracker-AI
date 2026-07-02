## Metastasis-Tracker-AI / Tumor-Virus-Vesicle Usage Guide
This document defines the runtime instructions, environment parameters, and multi-modal pipeline configuration needed to execute the automated tracking, filtering, and reporting software matrix.
------------------------------
## 💻 Environment Setup & Initialization
Before orchestrating the pipeline data streams, build a dedicated virtual python workspace and verify that your system architecture maps all parallelization libraries cleanly.

# 1. Clone the master tracking branch
git clone https://github.com
cd TUMOR-Defined-As-Virus-Vesicle-WITH-IMAGES-VIDEO
# 2. Build and insulate virtual environment layers
python3 -m venv venv
source venv/bin/activate
# 3. Provision core imaging and mathematical processing dependencies
pip install --upgrade pip
pip install numpy scipy pydicom pytest
# 4. (Optional) Install PyCUDA drivers if system hardware contains an active NVIDIA GPU# Ensure your system PATH maps nvcc paths before executing
pip install pycuda

------------------------------
## 🛠️ Folder Hierarchy Provisioning
To construct the required structural paths, JSON configurations, baseline test structures, and bedside medical sheets automatically across your local machine in one pass, fire the root repository automation engine:

# Execute the single-pass directory builder script
python build_repo.py

This operation instantly structures your directory fields as follows:

* config/config_matrices.json — Stores hardware calibration attributes.
* src/ — Active Python logic modules (Aggregator, Core Engine, Filter, Loader, App).
* tests/ — Automated verification matrices.
* docs/bedside_containment_charting_model.md — Checklist log spreadsheet layout.
* reports/ — Staging ground for runtime diagnostic support file outputs.

------------------------------
## 🔄 Live Processing Pipeline Execution
The system automatically handles configuration checks, cross-sectional directory sorting, edge-preserving spatial filtering, multi-planar finite difference mathematics, and diagnostic support reporting via a centralized entry runner loop.
## 📐 Running the Complete Orchestration Engine
Ensure your local project paths are registered properly before initializing:

# Map source utilities straight into your active python environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
# Fire the central data processing coordinator pipeline
python src/main.py

## 🔬 Expected Operational Flow Metrics
When src/main.py is invoked, the data engine coordinates these continuous execution phases:

   1. Ingestion: Reads hardware phase drops and Hounsfield offsets via config_loader.py.
   2. Aggregation: dicom_series_aggregator.py reads dicom_input_series/, sorts individual slices by spatial ImagePositionPatient coordinate tags, and compiles a normalized 3D array matrix.
   3. Registration: core_registration_engine.py applies a 4x4 affine transform to register and warp coordinates.
   4. Scrubbing: anisotropic_filter.py deploys a 3D Perona-Malik diffusion loop (via PyCUDA or vectorized CPU fallbacks) to clean high-frequency scanner noise while keeping edge parameters sharp.
   5. Section 10 Dynamics: skeletal_dynamics.py calculates multi-planar gradients and 3D Laplacian flux vectors to quantify long-term marrow mineral leaching and tissue density variations.
   6. AI Report Support: ai_diagnostic_app.py reads guidelines stored in docs/, checks threshold bounds against processed arrays, and exports a structured diagnostic support file directly to your reports/ folder.

------------------------------
## 🧪 Automated Testing & Precision Verification
To verify that your coordinate transforms, file aggregation sorting matrices, and Section 10 multi-planar math profiles match strict analytical targets, run the automated verification routines:

# Run the entire test suite simultaneously via pytest engine triggers
pytest tests/ -v

------------------------------
## 📚 Trusted Official Resources

* PubMed Central (PMC) Clinical Archive: Full-text repository used to establish verified baselines for desmoplastic reactions and tissue encapsulation profiles.
* NOAA Ocean Exploration Portal: Federal taxonomic repository used to verify Pycnogonida structural appendicular matrices and morphologic characteristics.
* Naval Medical Research Directory: Department of the Navy medical archive defining standard operational PPE thickness controls and environmental engineering limits.
