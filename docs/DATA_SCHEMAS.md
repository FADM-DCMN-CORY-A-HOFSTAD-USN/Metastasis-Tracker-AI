📄 Pycnogonid Simulation Subsystem: Data Schema Documentation

This document describes the structure, validation criteria, and mathematical intent of the configuration files used to drive the pycnogonid behavioral, enzymatic, and reproductive tracking modules.

* * * * *

🗺️ 1. State Matrix Configuration (`state_matrix.json`)

Purpose

Defines the individual behavioral state machine (\(S_t \to S_{t+1}\)), physical attributes, and environmental switch thresholds for active agents.

Key Fields & Validation Rules

-   `current_state`: Validates agent state constraints (`FREE_SWIMMING`, `HOST_SEEKING`, `ENCYSTED_FEEDING`, `INTERNAL_FREE_MOVING`, `FREE_LIVING_ADULT`, `DEAD`).
-   `leg_ratio_r`: Normalized structural segment ratio (\(\frac{L_{femur}}{L_{tibia1}+L_{tibia2}}\)). Used to calculate the mechanical damping coefficient (b) inside tissue.
-   `flow_regime_exponent_n`: Swaps physics equations depending on fluid medium context:
    -   `0.5`: High-Reynolds open-water turbulent flow.
    -   `1.0`: Low-Reynolds highly viscous creeping flow (Stokes regime).

Complete Schema & Example File

json

```
{
  "agent_id": "pyc_larva_0842",
  "current_state": "HOST_SEEKING",
  "physical_properties": {
    "leg_span_mm": 1.25,
    "proboscis_length_mm": 0.31,
    "leg_ratio_r": 0.45,
    "surface_area_mm2": 2.14,
    "mass_mg": 0.08,
    "thrust_force_f": 0.012
  },
  "environmental_context": {
    "fluid_viscosity_pas": 0.00108,
    "chemical_gradient_delta_c": 0.85,
    "habitat_suitability_hsi": 0.92
  },
  "state_transitions": [
    {
      "from_state": "HOST_SEEKING",
      "to_state": "ENCYSTED_FEEDING",
      "trigger_condition": {
        "variable": "p_penetrate",
        "operator": ">=",
        "threshold": 0.75
      },
      "physics_modifier_update": {
        "flow_regime_exponent_n": 1.0
      }
    },
    {
      "from_state": "HOST_SEEKING",
      "to_state": "FREE_SWIMMING",
      "trigger_condition": {
        "variable": "hsi",
        "operator": "<",
        "threshold": 0.20
      },
      "physics_modifier_update": {
        "flow_regime_exponent_n": 0.5
      }
    }
  ]
}

```

Use code with caution.

* * * * *

🧪 2. Parasite Enzymes Configuration (`parasite_enzymes.json`)

Purpose

Stores the Michaelis-Menten kinetic data for extraintestinal (pre-oral) saliva profiles. This feeds directly into the tissue liquefaction engine (\(R_{liq}\)).

Mathematical Integration

The parameters map to the multi-substrate digestion formula:\
\(R_{liq}=\sum _{e=1}^{E}\left(\frac{V_{max,e}\cdot [S]}{K_{m,e}\cdot (1+\rho _{tissue})+[S]}\right)\cdot \alpha _{e,S}\)

File Structure

json

```
{
  "pycnogonid_salivary_profile": {
    "exopeptidase_alpha": {
      "enzyme_class": "Protease",
      "optimal_ph": 7.8,
      "v_max_moles_sec_mg": 3.4e-6,
      "k_m_molar": 0.012,
      "target_affinities": {
        "actinoporin_complex": 0.90,
        "mesogleal_collagen_type_i": 0.45,
        "mucinous_glycoprotein_3": 0.15
      }
    },
    "collagenase_beta": {
      "enzyme_class": "Metalloproteinase",
      "optimal_ph": 8.2,
      "v_max_moles_sec_mg": 5.8e-6,
      "k_m_molar": 0.005,
      "target_affinities": {
        "actinoporin_complex": 0.20,
        "mesogleal_collagen_type_i": 0.95,
        "mucinous_glycoprotein_3": 0.10
      }
    }
  }
}

```

Use code with caution.

* * * * *

🥚 3. Breeding Matrix Configuration (`breeding_matrix.json`)

Purpose

Feeds demographic projection constants, carrying capacities, and environmental tolerance variables directly into the stage-structured Lefkovitch population tensor.

System Behaviors Configured

1.  **Thermal Fecundity Scaling**: Uses an Arrhenius Q₁₀ multiplier to exponentially boost breeding outputs when ambient conditions approach `optimal_breeding_temp_c`.
2.  **Turbulence Mating Interruption**: Multiplies fertilization rates by a power-law penalty (\(1.0 - \text{Turbulence}^{1.5}\)) to model wave-action disruption of egg transfer to male ovigers.
3.  **pH Collapse Threshold**: Implements a Gaussian standard deviation (`ph_tolerance_sigma`) around the `optimal_ph` target. When pH drifts away from `8.1`, larval survivability and fecundity compress to zero.

File Structure

json

```
{
  "breeding_matrix_config": {
    "species": "Pycnogonum_littorale_profile",
    "morphological_constraints": {
      "functional_gonopores": 6,
      "mean_egg_diameter_mm": 0.08,
      "femur_volume_mm3": 1.45
    },
    "leslie_matrix_coefficients": {
      "fecundity_adult_f": 15.0,
      "fecundity_brooding_f": 40.0,
      "survival_larva_to_juv": 0.25,
      "survival_juv_to_adult": 0.60,
      "adult_retention_rate": 0.92
    },
    "environmental_sensitivities": {
      "optimal_breeding_temp_c": 14.0,
      "thermal_exponential_limit_q10": 2.0,
      "turbulence_fertilization_penalty_exponent": 1.5,
      "optimal_ph": 8.1,
      "ph_tolerance_sigma": 0.35,
      "carrying_capacity": 10000.0
    }
  }
}

```
