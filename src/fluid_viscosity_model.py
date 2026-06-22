import math

class BodyFluidViscosityModel:
    def __init__(self, baseline_hydration: float, base_hct: float = 0.45):
        """
        Calculates localized fluid viscosities across distinct anatomical compartments.
        :param baseline_hydration: Patient hydration factor \chi (1.0 = normal, 0.85 = dehydrated)
        :param base_hct: Baseline systemic hematocrit fraction (normal range: 0.40 - 0.50)
        """
        self.chi = baseline_hydration
        
        # Hematocrit scales inversely with plasma volume (hydration factor)
        # Dehydration concentrates the cellular fraction of the blood
        self.hct = base_hct * (1.0 / self.chi)
        
        # Viscosity of pure plasma at 37°C (Pascal-seconds, Pa·s)
        # Normal plasma is ~0.0012 Pa·s; increases as hydration drops
        self.mu_plasma = 0.0012 * (1.0 / (self.chi ** 0.6))
        
        # Viscosity of pure water/CSF at 37°C baseline
        self.mu_water = 0.00069 

    def calculate_vascular_viscosity(self, radius_m: float, mean_velocity_m_s: float) -> float:
        """
        Calculates dynamic blood viscosity using non-Newtonian Casson rheology
        and the Fåhræus-Lindqvist effect for small vessels/capillaries.
        Returns viscosity in Pascal-seconds (Pa·s).
        """
        diameter_um = radius_m * 2.0 * 1e6
        
        # 1. Prevent mathematical singularities for extremely small simulated vessels
        if diameter_um < 3.0:
            diameter_um = 3.0
            
        # 2. Compute Shear Rate (\dot{\gamma} = 4v/r)
        if mean_velocity_m_s <= 0:
            # Prevent division by zero in stasis conditions (minimum background shear)
            shear_rate = 0.1 
        else:
            shear_rate = (4.0 * mean_velocity_m_s) / radius_m

        # 3. Fåhræus-Lindqvist Effect: Microvascular hematocrit drops in vessels under 300 um
        if diameter_um < 300.0:
            # Empirical Pries et al. formulation for relative discharge hematocrit
            hct_local = self.hct * (0.048 + 0.952 * (1.0 + 1.24 * (math.exp(-0.047 * diameter_um)) - 0.24 * (math.exp(-0.006 * diameter_um))))
        else:
            hct_local = self.hct

        # 4. Casson Model for non-Newtonian Yield Stress at low shear rates
        # Yield stress (\tau_y) spikes drastically with higher hematocrit and dehydration
        if hct_local > 0:
            yield_stress = 0.005 * ((hct_local / (1.0 - hct_local)) ** 3) * (1.0 / self.chi)
        else:
            yield_stress = 0.0
            
        # 5. Core Apparent Viscosity Calculation
        if shear_rate > 0 and hct_local > 0:
            # Casson formulation equation
            root_mu_casson = math.sqrt(self.mu_plasma / (1.0 - hct_local)) + math.sqrt(yield_stress / shear_rate)
            mu_apparent = root_mu_casson ** 2
        else:
            mu_apparent = self.mu_plasma / (1.0 - hct_local)

        # Cap minimum viscosity to plasma and max out at severe stasis hyperviscosity
        return max(self.mu_plasma, min(mu_apparent, 0.025))

    def calculate_airway_mucus_viscosity(self, generation: int) -> float:
        """
        Models the non-Newtonian viscoelasticity of the airway surface liquid (ASL).
        Upper airways (trachea) have thick, gel-like mucins; deeper alveoli use low-viscosity surfactant.
        """
        # Dehydration thickens mucus layer exponentially due to water reabsorption
        mucus_hydration_penalty = 1.0 / (self.chi ** 2)
        
        if generation == 0:
            # Trachea / Main Bronchi: High gel layer composition (~2.0 Pa·s baseline)
            return 2.0 * mucus_hydration_penalty
        elif generation <= 10:
            # Conducting bronchi: Transitioning thickness
            return (2.0 - (0.15 * generation)) * mucus_hydration_penalty
        elif generation <= 16:
            # Terminal Bronchioles: Dominated by sol-phase periciliary fluid
            return 0.05 * mucus_hydration_penalty
        else:
            # Generations 17-23 (Respiratory/Alveolar Zone): Pulmonary Surfactant film
            # Fluid behavior approaches near-aqueous conditions
            return 0.002 * (1.0 / self.chi)

    def calculate_interstitial_fluid_viscosity(self) -> float:
        """
        Returns the viscosity of the extracellular interstitial matrix.
        Influenced by protein transudation and glycosaminoglycan concentration.
        """
        # Baseline interstitial fluid is ~30% more viscous than water due to hyaluronan matrix
        base_interstitial = self.mu_water * 1.3
        # Dehydration decreases fluid volume, consolidating extracellular matrix polymers
        return base_interstitial * (1.0 / (self.chi ** 1.5))

    def calculate_cerebrospinal_fluid_viscosity(self) -> float:
        """
        Returns the viscosity of CSF inside the cerebral ventricular compartments.
        Protected by the Blood-Brain Barrier; highly resistant to sharp hydration shifts.
        """
        # CSF mimics pure water closely (~0.0007 Pa·s), scales minorly under extreme dehydration
        return self.mu_water * (1.0 / (self.chi ** 0.2))
