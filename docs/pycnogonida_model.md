This is the comprehensive architectural documentation for the complete, multi-threaded Pycnogonida Physics and Bioenergetic Model developed across our workspace.

Save this file as `docs/PYCNOGONIDA_MODEL_REFERENCE.md` to serve as the master technical specification for your software engineers, system designers, and automated testing pipelines.

* * * * *

🕷️ Headless Pycnogonida Bioenergetic & Physics Subsystem
---------------------------------------------------------

1\. System Overview
-------------------

The Pycnogonida Subsystem is an optimized, multi-threaded, headless computational engine designed to model the morphology, physics-driven locomotion, extraintestinal digestion, and reproduction loops of diverse marine pycnogonid (sea spider) classes.

The architecture decouples heavy biochemical calculations from frame-rate-dependent rendering routines, allowing it to compile cleanly via the command-line toolchain for high-throughput automation pipelines.

```
       [ Game Loop Thread ]                       [ Physics Thread ]
  (Biomass / Digestion Loops)                 (Sub-stepping Callbacks)
              │                                           │
              ▼                                           ▼
   [ Biomass Engine Matrix ]                       [ Rigid Body Node ]
              │                                           │
              └───► [ Thread-Safe Data Bridge ] ──────────┘
                  (Lock-Free Double Buffering)

```

* * * * *

2\. Component and File Architecture
-----------------------------------

The subsystem splits definitions and compiled compilation steps into explicit source structures to align with strict build tool patterns:

```
Metastasis-Tracker-AI/
├── src/
│   ├── MetastasisTrackerAI.Build.cs        # Module build definitions & dependency maps
│   ├── state_matrix.py                      # Individual agent behavioral state loops
│   ├── population_engine.py                 # Lefkovitch matrix demographic projector
│   ├── biomass_scaler.py                    # Real-time condition factor calculations
│   ├── parse_reports.py                     # Automation report parsing utility
│   ├── objects/
│   │   ├── public/
│   │   │   └── PycnogonidBiomassPayload.h  # Thread-safe atomic data payloads
│   │   └── private/
│   │       └── [Implementation links]
│   └── data/
│       ├── parasite_enzymes.json            # Salivary protease/metalloproteinase constants
│       ├── target_proteins.json             # Marine protein substrate configurations
│       └── pycnogonid_thermal_profiles.json # Degree-day thresholds per species class
└── docs/
    ├── DATA_SCHEMAS.md                      # JSON profile layouts
    ├── MATHEMATICAL_MODELS.md               # Raw math reference library
    ├── UNIT_TESTING_REFERENCE.md            # Boundary condition validation matrix
    └── PYCNOGONIDA_MODEL_REFERENCE.md       # Master system architecture (This File)

```

* * * * *

3\. Mathematical Execution Pipelines
------------------------------------

A. Dynamic Morphology (Thick vs. Skinny)
----------------------------------------

Agents scale dynamically using a structural condition factor ($C_f$). The engine processes leg segments as concentric cylinders where the hollow interior space acts as a storage reservoir for reproductive products:

$$r_{\text{leg}}(t) = r_{\text{baseline}} \cdot C_f$$\
$$V_{\text{cavity}} = \sum_{i=1}^{8} \pi \cdot \left(r_{\text{leg}, i} \cdot \beta_{\text{wall}}\right)^2 \cdot L_{\text{femur}, i}$$

-   Skinny Variants ($C_f < 1.0$): Tightens internal storage, limiting maximum offspring production.
-   Thick Variants ($C_f > 1.2$): Expands available volume, allowing for massive physical egg output blocks.

B. Extraintestinal Multi-Substrate Digestion
--------------------------------------------

Salivary secretions melt tissue layers through multi-substrate Michaelis-Menten mechanics, factoring in substrate packing densities ($\rho$) as a competitive-like diffusion inhibitor:

$$R_{\text{liq}} = \sum_{e=1}^{E} \left( \frac{V_{\max, e} \cdot [S]}{K_{m, e} \cdot (1 + \rho_{\text{tissue}}) + [S]} \right) \cdot \alpha_{e, S}$$

C. Low-Reynolds Hadamars-Rybczynski Microscopic Drag
----------------------------------------------------

For newly emerged *protonymphon* larvae under 200 micrometers, standard Newtonian drag functions bypass to use the micro-capsule fluid-drag corrector to account for high-viscosity ambient media ($\mu$) and dense internal lipid-yolk cores ($\mu_{\text{internal}}$):

$$F_{\text{drag}} = 4\pi \cdot \mu \cdot r_{\text{larva}} \cdot v_{\text{larva}} \cdot \left( \frac{1 + \frac{2\mu}{3\mu_{\text{internal}}}}{1 + \frac{\mu}{\mu_{\text{internal}}}} \right)$$

* * * * *

4\. Multi-Threaded Memory Bridge
--------------------------------

To avoid blocking threads or triggering race conditions when writing to asynchronous physics simulation threads, the system uses a lock-free atomic buffer class implemented in `PycnogonidBiomassPayload.h`.

```
// Serialized packet passed across threads
struct FPycnogonidBiomassPayload {
    float ConditionFactor;
    float CurrentMassMg;
    float TotalCavityVolumeMm3;
    int32 AvailableEggCount;
};

```

-   Game Loop Thread: Writes live metabolic adjustments to the payload using release-memory order sequences (`std::memory_order_release`).
-   Physics Thread Callback: Evaluates an acquire-memory check (`std::memory_order_acquire`) inside the sub-stepping loop to adjust mass values, scales, and constraints without interrupting synchronous tick frames.

* * * * *

5\. Environmental Constraint Matrices
-------------------------------------

Long-term lifecycle and generation steps loop via a Lefkovitch matrix engine. Survival parameters compress or expand based on real-time environmental context inputs:

1.  Thermal Multiplier: Modeled via an Arrhenius $Q_{10}$ loop.
2.  Turbulence Interruption: Scales fertilization down based on wave-action power-law penalties.
3.  pH Structural Stress: Uses a tight Gaussian tolerance curve. If local pH parameters drift sharply from marine homeostasis (`8.1`), larval cuticle hardening fails, driving survival rates to `0.0`.

* * * * *

6\. Automation and Testing Pipeline
-----------------------------------

The model includes built-in verification support for automated continuous integration (CI) environments via a chained toolchain execution framework:

```
# 1. Run headless compile checks via shell wrappers
./Engine/Build/BatchFiles/RunUBT.sh MetastasisTrackerAI Linux Development -NoHotReload

# 2. Trigger async headless automation tests bypassing display requirements
./Engine/Build/BatchFiles/RunUAT.sh RunUnreal -nullrhi -ExecCmds="Automation RunTests Pycnogonid; Quit"

# 3. Parse JSON results directly to stdout via Python
python3 src/parse_reports.py Saved/AutomationReports/index.json

```

The script monitors all boundary test blocks (e.g., division-by-zero checks when fluid viscosity reaches absolute zero, or density saturation limits when initial carrying capacities are overrun) and terminates with strict exit codes to prevent broken builds from deploying.

* * * * *
