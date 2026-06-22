import numpy as np


class PycnogonidPopulationEngine:
    def __init__(self, config):
        """
        Initializes the stage-structured Lefkovitch population model.
        """
        self.config = config["breeding_matrix_config"]
        
        # Extract base coefficients
        coefs = self.config["leslie_matrix_coefficients"]
        self.base_f_adult = coefs["fecundity_adult_f"]
        self.base_f_brooding = coefs["fecundity_brooding_f"]
        self.p_larva_juv = coefs["survival_larva_to_juv"]
        self.p_juv_adult = coefs["survival_juv_to_adult"]
        self.p_adult_adult = coefs["adult_retention_rate"]
        
        # Environmental constants
        env = self.config["environmental_sensitivities"]
        self.opt_temp = env["optimal_breeding_temp_c"]
        self.q10 = env["thermal_exponential_limit_q10"]
        self.turb_exponent = env["turbulence_fertilization_penalty_exponent"]
        
        # New pH Optima and Tolerance Span
        self.opt_ph = env.get("optimal_ph", 8.1)
        self.sigma_ph = env.get("ph_tolerance_sigma", 0.35)  # Determines how sharp the survival drop is
        
        # Environmental Carrying Capacity (To ground the exponential growth model)
        self.carrying_capacity = env.get("carrying_capacity", 5000.0)

    def calculate_environmental_scalars(self, temperature, turbulence, ph):
        """
        Computes the reproductive and survival scalars based on climate context.
        """
        # 1. Thermal exponential scaling (Q10 Rule)
        thermal_scalar = self.q10 ** ((temperature - self.opt_temp) / 10.0)
        
        # 2. Turbulence mating penalty
        fertilization_success = max(0.01, 1.0 - (turbulence ** self.turb_exponent))
        
        # 3. pH Stress Curve (Gaussian bell-curve representing physiological tolerance)
        # Drops sharply as pH drifts far from standard ocean chemistry (8.1)
        ph_scalar = np.exp(-((ph - self.opt_ph) ** 2) / (2 * (self.sigma_ph ** 2)))
        
        # Calculate composite values
        # pH suppresses both breeding capability and larval survival rates
        scaled_f_adult = self.base_f_adult * thermal_scalar * fertilization_success * ph_scalar
        scaled_f_brooding = self.base_f_brooding * thermal_scalar * fertilization_success * ph_scalar
        scaled_p_larva = self.base_p_larva_juv * ph_scalar
        
        return scaled_f_adult, scaled_f_brooding, scaled_p_larva, ph_scalar

    def compute_dynamic_fecundity(self, temperature, turbulence):
        """
        Calculates environmental scaling on fertilization and hatching rates.
        Uses an exponential Q10 thermal rule and a power-law turbulence penalty.
        """
        # 1. Thermal exponential scaling (Arrhenius/Q10 approximation)
        thermal_scalar = self.q10 ** ((temperature - self.opt_temp) / 10.0)
        
        # 2. Turbulence fertilization penalty (reduces mating contact efficiency)
        # Turbulence ranges from 0.0 (still water) to 1.0 (heavy storm/surf wave break)
        fertilization_success = max(0.01, 1.0 - (turbulence ** self.turb_exponent))
        
        # Composite fecundity terms
        scaled_f_adult = self.base_f_adult * thermal_scalar * fertilization_success
        scaled_f_brooding = self.base_f_brooding * thermal_scalar * fertilization_success
        
        return scaled_f_adult, scaled_f_brooding

    def construct_lefkovitch_matrix(self, temperature, turbulence, ph):
        """
        Builds the dynamic 4x4 matrix mapping transitions and environmental strain.
        """
        f_adult, f_brooding, p_larva_juv, _ = self.calculate_environmental_scalars(temperature, turbulence, ph)
        
        # Stage Matrix Setup: [Larva, Juvenile, Adult, Brooding_Male]
        L = np.array([
            [0.0,         0.0,              f_adult,            f_brooding],
            [p_larva_juv, 0.0,              0.0,                0.0       ],
            [0.0,         self.p_juv_adult, self.p_adult_adult, 0.0       ],
            [0.0,         0.0,              0.15,               0.0       ]
        ])
        return L

    def run_projection(self, initial_population, time_steps, env_timeline):
        """
        Executes the matrix multiplication while accounting for pH surges and carrying capacity.
        """
        pop_vector = np.array(initial_population, dtype=float).reshape(-1, 1)
        history = np.zeros((4, time_steps + 1))
        history[:, 0] = pop_vector.flatten()
        
        for t in range(time_steps):
            # Fallback environment context if timeline runs short
            env = env_timeline[t] if t < len(env_timeline) else {"temperature": 14.0, "turbulence": 0.1, "ph": 8.1}
            
            # Construct matrix step with real-time pH parameter
            L_t = self.construct_lefkovitch_matrix(env["temperature"], env["turbulence"], env["ph"])
            
            # 1. Standard Linear Projection step
            next_pop_vector = np.dot(L_t, pop_vector)
            
            # 2. Apply a density-dependent saturation penalty (Logistic Carrying Capacity filter)
            total_pop = np.sum(next_pop_vector)
            if total_pop > self.carrying_capacity:
                saturation_factor = self.carrying_capacity / total_pop
                next_pop_vector *= saturation_factor
                
            pop_vector = next_pop_vector
            history[:, t + 1] = pop_vector.flatten()
            
        return history

# ==============================================================================
# Execution Example & Verification Loop
# ==============================================================================
if __name__ == "__main__":
    # Mock Config Setup mapping directly to the JSON format provided previously
    mock_config = {
      "breeding_matrix_config": {
        "leslie_matrix_coefficients": {
          "fecundity_adult_f": 12.5,       # Number of viable larvae added per step per adult
          "fecundity_brooding_f": 35.0,    # Brooding males protect/release higher clusters
          "survival_larva_to_juv": 0.12,   # 12% survival rate
          "survival_juv_to_adult": 0.55,   # 55% maturation rate
          "adult_retention_rate": 0.90     # 90% adult survival per step
        },
        "environmental_sensitivities": {
          "optimal_breeding_temp_c": 14.0,
          "thermal_exponential_limit_q10": 2.2,
          "turbulence_fertilization_penalty_exponent": 1.5
        }
      }
    }
    
    engine = PycnogonidPopulationEngine(mock_config)
    
    # Starting setup: 100 Larvae, 10 Juveniles, 5 Adults, 0 Brooding Males
    starting_pop = [100, 10, 5, 0]
    total_steps = 5
    
    # Simulate a dynamic scenario: Temperature increases, turbulence peaks at step 3
    mock_timeline = [
        {"temperature": 12.0, "turbulence": 0.0}, # Cold, calm
        {"temperature": 14.0, "turbulence": 0.1}, # Optimal peak
        {"temperature": 15.5, "turbulence": 0.2}, # Warm, light waves
        {"temperature": 14.0, "turbulence": 0.8}, # Storm surge (high penalty)
        {"temperature": 11.0, "turbulence": 0.1}  # Cold drop
    ]
    
    results = engine.run_projection(starting_pop, total_steps, mock_timeline)
    
    # Clean output tracking across generations
    print(f"--- Demographic Tracking Over {total_steps} Iterations ---")
    stages = ["Larvae", "Juveniles", "Adults", "Brooding"]
    for idx, stage in enumerate(stages):
        row_str = " -> ".join([f"{val:.1f}" for val in results[idx, :]])
        print(f"{stage:<10}: {row_str}")
