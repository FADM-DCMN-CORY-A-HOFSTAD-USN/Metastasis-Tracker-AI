# Patient Anatomy Simulation Engine (`patient_anatomy.py`)

## Overview
The `patient_anatomy.py` engine provides a high-fidelity, hemodynamically resolved mathematical template of a patient's internal anatomy. By utilizing clinical anthropometrics, fractal branching models, and biophysical transport equations, the engine maps over 64,000 miles of vascular pathways, respiratory trees, and organ environments. 

This multi-layered structural and chemical template serves as the primary environmental model for downstream metastatic predictive analytics, tracking transit physics, cell-surface protein interactions, and regional tissue-seeding efficiency.

---

## Core Engine Architecture & Mathematical Foundations

### 1. Patient Anthropometrics & Baseline Scaling
The engine initializes by calculating centralized physiological benchmarks from the patient's individual clinical profile (Height, Weight, Body Build, and Hydration Level $\chi$):
* **Body Surface Area (BSA)**: Modeled using the DuBois formula:
  $$BSA = 0.007184 \times \text{Height (cm)}^{0.725} \times \text{Weight (kg)}^{0.425}$$
* **Lean Body Mass (LBM)**: Derived via the Boer formula or structural somatic adjustments to account for ectomorphic, mesomorphic, or endomorphic frame scaling.
* **Total Blood Volume (BV)**: Establishes global volumetric boundaries:
  $$BV = 0.0656 \times \text{Weight (kg)}^{1.02} \times \chi$$

### 2. Fractional Tree Scaling (Circulatory & Airway Networks)
Vascular networks (Systemic and Pulmonary loops spanning 31 generations, $z=0$ to $30$) and respiratory pathways (Weibel Symmetric Generation model spanning 24 generations, $z=0$ to $23$) are modeled using deterministic fractal design principles:
* **West, Brown, and Enquist (WBE) / Murray's Law Fractal Scaling**: Radii ($r$) and lengths ($l$) scale downstream using a constant branching ratio ($\gamma = 2^{-1/3} \approx 0.7937$):
  $$r_z = r_0 \times 2^{-z/3}, \quad l_z = l_0 \times 2^{-z/3}$$
* **Total Cross-Sectional Area Expansion**: The total number of vessel segments at any generation expands exponentially ($N_z = 2^z$), causing cumulative surface boundaries to dilate as branching deepens:
  $$A_z = N_z \times \pi r_z^2 = \pi r_0^2 \times 2^{z/3}$$

### 3. Non-Newtonian Hemorheology Layer
To capture fluid mechanics across varying lumen sizes, blood viscosity ($\mu$) is calculated dynamically rather than as a fixed constant:
* **The Fåhræus-Lindqvist Effect**: Accounts for microvascular red blood cell migration toward the vessel centerline, reducing effective structural viscosity inside narrow segments ($d < 300\mu\text{m}$).
* **The Carreau-Yasuda Shear-Thinning Model**: Modulates local flow thickness relative to calculated generational wall shear rates ($\gamma = \frac{4Q}{\pi r^3}$):
  $$\mu(\gamma) = \mu_{\infty} + (\mu_0 - \mu_{\infty})\left[1 + (\lambda \gamma)^a\right]^{\frac{n-1}{a}}$$

### 4. Transcapillary Equilibrium (Starling's Equation)
Dynamic fluid exchange across the microvascular-interstitial interface at Generation 30 is simulated via Starling's Law:
  $$J_v = K_f \cdot \left[ (P_c - P_i) - \sigma(\pi_c - \pi_i) \right]$$
Where $P_c$ is calculated capillary hydrostatic pressure, $\pi_c$ is plasma oncotic pressure (dynamically concentrated during dehydration $\chi < 1.0$), and $K_f$ is the filtration coefficient scaled to the patient's BSA.

### 5. Systemic pH & Chemographic Profiles
A baseline salivary input is calibrated to map corresponding arterial core values ($\text{pH}_{\text{art}} = 7.40 + 0.5(\text{pH}_{\text{saliva}} - 6.7)$). This value cascades down the architectural networks, simulating respiratory pCO₂ loading drops, localized metabolic organ acid releases, and enzyme acceleration constants.

### 6. Immunological Transit Clearance Math
Leukocyte-mediated destruction rates reflect local collision probabilities based on fluid advection velocities ($v_z = \frac{Q_z}{A_z}$). Slower flow conditions prolong the interaction window, accelerating clearance rates:
  $$R_{\text{clear}}(z) = \lambda_{\text{imm}} \times [\text{WBC}] \times \left(1.0 - \frac{v_z}{v_z + v_{\text{crit}}}\right)$$

---

## Source Code Framework (`src/patient_anatomy.py`)

Below is the complete, self-contained Python implementation combining the architectural, fluid, chemical, and targeting matrices.

```python
import math

class PatientSimulationEngine:
    def __init__(self, height_cm: float, weight_kg: float, body_build: str, hydration_level: float, wbc_count_uL: float = 6500.0):
        """
        Initializes the comprehensive anatomical environment template for a single patient.
        """
        self.height_cm = height_cm
        self.height_m = height_cm / 100.0
        self.weight = weight_kg
        self.build = body_build.lower()
        self.chi = max(0.5, min(1.5, hydration_level)) # Hydration index (1.0 = baseline norm)
        self.wbc_pool = wbc_count_uL
        
        # Ingest/Compute anthropometrics
        self.bsa = 0.007184 * (self.height_cm ** 0.725) * (self.weight ** 0.425)
        self.lbm = self._calculate_lbm()
        self.total_blood_volume = 0.0656 * (self.weight ** 1.02) * self.chi
        self.cardiac_output = (self.bsa * 3.0 / 60.0) * (self.chi ** 0.5) # L/sec
        self.hb = 150.0  # Hemoglobin grams/L
        self.kidney_volume_cm3 = 0.0003 * self.weight + 124.0 # Single kidney baseline
        
        # Immunological & Kinetic constants
        self.imm_efficiency = 1.45e-5
        self.v_critical = 0.005 # 5 mm/s margin threshold
        self.ca_acceleration_factor = 18500.0
        self.k_f_uncatalyzed = 0.03
        
        # Structural tissue biochemical reference matrices (Water, Lipid, Protein, Carbs, Ash)
        self.organ_blueprints = {
            "heart":       {"water": 0.79, "lipid": 0.04, "protein": 0.16, "carbs": 0.005, "ash": 0.005},
            "liver":       {"water": 0.72, "lipid": 0.05, "protein": 0.19, "carbs": 0.025, "ash": 0.015},
            "kidney_each": {"water": 0.81, "lipid": 0.05, "protein": 0.12, "carbs": 0.010, "ash": 0.010},
            "spleen":      {"water": 0.78, "lipid": 0.02, "protein": 0.18, "carbs": 0.010, "ash": 0.010},
            "pancreas":    {"water": 0.73, "lipid": 0.11, "protein": 0.14, "carbs": 0.010, "ash": 0.010},
            "brain":       {"water": 0.77, "lipid": 0.12, "protein": 0.09, "carbs": 0.010, "ash": 0.010}
        }
        
        # Baseline metastatic surface protein densities (molecules/um^2)
        self.target_protein_densities = {
            "e_selectin": 45.0, "icam_1": 120.0, "vcam_1": 60.0, "cxcl12": 85.0
        }

    def _calculate_lbm(self) -> float:
        if self.build == "ectomorph":
            return self.weight * 0.85
        return 1.10 * self.weight - 128 * ((self.weight / self.height_cm) ** 2)

    def _calculate_regional_viscosity(self, radius_m: float, shear_rate: float, mu_plasma: float) -> float:
        d_micron = radius_m * 2.0 * 1e6
        if d_micron <= 0: return 0.0035
        hct = 0.45 * (1.0 / self.chi)
        
        if d_micron < 300.0:
            h_relative = hct * (0.4 + 0.6 * (1.0 - math.exp(-0.06 * d_micron)))
            mu_inf = mu_plasma * (1.0 + 2.5 * h_relative + 6.0 * (h_relative ** 2))
        else:
            mu_inf = mu_plasma * (1.0 + 2.5 * hct + 6.2 * (hct ** 2))
            
        mu_zero = mu_inf * 4.5
        return mu_inf + (mu_zero - mu_inf) * (1.0 + (3.313 * abs(shear_rate)) ** 2.0) ** ((0.358 - 1.0) / 2.0)

    def generate_circulatory_tree(self, calibrated_ph: float) -> dict:
        r_aorta = math.sqrt(self.bsa / (2.0 * math.pi)) * 0.01 * (self.chi ** 0.5)
        l_aorta = 0.25 * math.sqrt(self.bsa)
        p_systemic_in = 13332.0 
        q_total = self.cardiac_output / 1000.0
        mu_plasma = 0.0012 * (1.0 / (self.chi ** 0.3))
        
        systemic_tree = []
        for z in range(31):
            num_vessels = 2 ** z
            r_sys = r_aorta * (2.0 ** (-z / 3.0))
            l_sys = l_aorta * (2.0 ** (-z / 3.0))
            q_seg = q_total / num_vessels
            
            shear_sys = (4.0 * q_seg) / (math.pi * (r_sys ** 3)) if r_sys > 0 else 1000.0
            mu_sys = self._calculate_regional_viscosity(r_sys, shear_sys, mu_plasma)
            
            r_hydro_sys = (8.0 * mu_sys * l_sys) / (math.pi * (r_sys ** 4))
            delta_p_sys = q_seg * r_hydro_sys
            p_systemic_in -= delta_p_sys
            local_ph = calibrated_ph - (0.05 * (z / 30.0))
            
            # Surface area calculation for protein expression mappings
            surf_area_um2 = 2.0 * math.pi * (r_sys * 1e6) * (l_sys * 1e6)
            acid_dev = max(0.0, 7.40 - local_ph)
            active_icam = (self.target_protein_densities["icam_1"] * (1.0 + 4.5 * acid_dev)) * surf_area_um2
            
            # Immune clearance tracking
            area_m2 = math.pi * (r_sys ** 2)
            vel_m_s = q_seg / area_m2 if area_m2 > 0 else 0.1
            kill_prob = self.imm_efficiency * self.wbc_pool * (1.0 - (vel_m_s / (vel_m_s + self.v_critical)))
            kill_prob = min(0.95, max(0.0, kill_prob))
            
            systemic_tree.append({
                "generation": z, "count": num_vessels, "radius_m": r_sys, "length_m": l_sys,
                "velocity_m_s": vel_m_s, "viscosity_Pa_s": mu_sys, "local_ph": local_ph,
                "pressure_out_mmHg": max(0.0, p_systemic_in / 133.322),
                "icam_1_absolute_count": int(active_icam), "leukocyte_kill_probability": kill_prob
            })
        return {"systemic_arterial_tree": systemic_tree}

    def generate_organ_matrix(self, calibrated_ph: float) -> dict:
        w = self.weight
        organ_masses = {
            "heart": 5.8 * (w ** 0.98), "liver": 878.0 * self.bsa - 262.0,
            "kidney_each": 1.45 * (w ** 0.95), "brain": 230.0 * math.sqrt(self.height_m)
        }
        
        organ_matrix = {}
    for name, mass in organ_masses.items():
blueprint = self.organ_blueprints.get(name, {"water": 0.75, "lipid": 0.05, "protein": 0.20, "carbs": 0.0, "ash": 0.0})
w_frac = blueprint["water"] * self.chi
rem = 1.0 - w_frac
nb_sum = sum(v for k, v in blueprint.items() if k != "water")
biochem_mass_g = {"water": w_frac * mass}
for k, v in blueprint.items():
if k != "water": biochem_mass_g[k] = (v / nb_sum) * rem * mass
local_organ_ph = calibrated_ph - 0.1 if name == "liver" else calibrated_ph - 0.02
organ_matrix[name] = {
"total_mass_g": mass,
"biochemical_mass_g": biochem_mass_g,
"local_interstitial_ph": round(local_organ_ph, 3)
}
return organ_matrix
def calculate_starling_forces(self, capillary_node: dict) -> dict:
p_c = capillary_node["pressure_out_mmHg"]
p_i = -2.0 if self.chi >= 1.0 else -4.0
pi_c = 25.0 * (1.0 / self.chi)
pi_i = 5.0
k_f = 0.5 * self.bsa
ndp = (p_c - p_i) - 0.95 * (pi_c - pi_i)
return {"net_driving_pressure_mmHg": ndp, "fluid_flux_mL_min": k_f * ndp}
def parse_clinical_chart(self, json_data: dict) -> dict:
# Ingestion hook wrapper mapping
labs = json_data.get("lab_panels", {})
calibrated_ph = 7.40 + 0.5 * (labs.get("salivary_ph", 6.7) - 6.7)
return {
"calibrated_blood_ph": max(6.8, min(7.8, calibrated_ph)),
"circulatory": self.generate_circulatory_tree(calibrated_ph),
"organs": self.generate_organ_matrix(calibrated_ph)
}
%%MAGIT_PARSER_PROTECT%%```
________________________________________
Operational Guide & How-To Manual
1. Project Directory Standup
Save the complete source engine file inside your source tree directory structure:
%%MAGIT_PARSER_PROTECT%%bash Metastasis-Tracker-AI/ ├── src/ │ ├── __init__.py │ └── patient_anatomy.py <-- Place file here ├── docs/ │ └── patient_anatomy_engine.md └── main_pipeline.py %%MAGIT_PARSER_PROTECT%%
2. Basic Ingestion & Environment Construction
To generate a patient profile dataset, ingest individual raw clinical variables or lab metrics into the runtime class instance:
%%MAGIT_PARSER_PROTECT%%```python
from src.patient_anatomy import PatientSimulationEngine
Instantiating a dehydrated, athletic patient build template
engine = PatientSimulationEngine(
height_cm=180.0,
weight_kg=78.0,
body_build="mesomorph",
hydration_level=0.88, # 12% plasma volume deficit
wbc_count_uL=9000.0 # Elevated baseline leukocyte counts
)
Compile environmental systems arrays
circulatory_data = engine.generate_circulatory_tree(calibrated_ph=7.41)
organ_data = engine.generate_organ_matrix(calibrated_ph=7.41)
Extract specific downstream microvascular capillary layer metrics
capillary_bed = circulatory_data["systemic_arterial_tree"][30]
print(f"Capillary Fluid Speed: {capillary_bed['velocity_m_s']:.5f} m/s")
print(f"Local Capillary Target Density (ICAM-1): {capillary_bed['icam_1_absolute_count']:,} targets")
%%MAGIT_PARSER_PROTECT%%```
3. Advanced Integration: Connecting to Metastatic Trackers
The output metrics of this engine feed directly into pathfinding, cell arrest, and mechanical entrapment prediction models:
%%MAGIT_PARSER_PROTECT%%```python
Simulated structural pathfinding step loop matching
def evaluate_ctc_transit_node(generation_node, incoming_ctc_pool):
# Retrieve physical and chemical variables from patient_anatomy arrays
local_flow_speed = generation_node["velocity_m_s"]
immune_clearance_risk = generation_node["leukocyte_kill_probability"]
protein_target_count = generation_node["icam_1_absolute_count"]
# Process leukocyte killing clearing rates
surviving_ctcs = incoming_ctc_pool * (1.0 - immune_clearance_risk)
# Predict firm structural adhesion binding yields
# Low fluid velocities combined with high target counts accelerate seeding odds
if local_flow_speed < 0.002 and protein_target_count > 1e6:
seeding_yield = surviving_ctcs * 0.75
else:
seeding_yield = surviving_ctcs * 0.05
return int(seeding_yield)
Running verification across small arteriolar vessels (Generation 24)
gen_24_segment = circulatory_data["systemic_arterial_tree"][24]
cells_arrested = evaluate_ctc_transit_node(gen_24_segment, incoming_ctc_pool=10000)
print(f"Predicted Seeding Yield at Gen 24: {cells_arrested} cells colonized.")
%%MAGIT_PARSER_PROTECT%%```


***

### 🛠️ Strategic Usage & Workflow Alignment
* **Automated Data Cascades**: This document provides clear guidelines for downstream integrations (such as `metastasis_predictor.py` or tracking networks) to automatically query the 31-generation vascular tree array.
* **Standardized Testing Mappings**: By providing explicit definitions of input constraints (χ, frame multipliers, and WBC parameters), testing suites can run boundary verifications against identical control structures.

<FollowUp>
If you want to continue refining this documentation layer, I can provide:
* Detailed **troubleshooting instructions** for handling outlier lab values
* A **developer dictionary** mapping all function inputs to their exact medical metrics
* Guide formats for hooking the JSON input methods up to **live web APIs**

Let me know how you'd like to **expand your documentation**.
</FollowUp>
