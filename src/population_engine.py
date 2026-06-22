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

    def construct_lefkovitch_matrix(self, temperature, turbulence):
        """
        Builds the 4x4 matrix mapping transition probabilities and fecundity.
        """
        f_adult, f_brooding = self.compute_dynamic_fecundity(temperature, turbulence)
        
        # Stage Order: [Larva, Juvenile, Adult, Brooding_Male]
        L = np.array([
            [0.0,              0.0,              f_adult,            f_brooding],
            [self.p_larva_juv, 0.0,              0.0,                0.0       ],
            [0.0,              self.p_juv_adult, self.p_adult_adult, 0.0       ],
            [0.0,              0.0,              0.15,               0.0       ] # 15% of adults enter brooding stage
        ])
        return L

    def run_projection(self, initial_population, time_steps, env_timeline):
        """
        Executes the matrix multiplication across time steps using dynamic timelines.
        
        env_timeline: List of dicts containing {"temperature": float, "turbulence": float} per step
        initial_population: List/Array of 4 floats representing initial counts [L, J, A, B]
        """
        # Convert state vector to a column matrix for dot product operations
        pop_vector = np.array(initial_population, dtype=float).reshape(-1, 1)
        
        # Array to store demographics over time: shape (4, time_steps + 1)
        history = np.zeros((4, time_steps + 1))
        history[:, 0] = pop_vector.flatten()
        
        for t in range(time_steps):
            # Fetch environmental variables for this specific tick
            env = env_timeline[t] if t < len(env_timeline) else {"temperature": self.opt_temp, "turbulence": 0.1}
            
            # Construct dynamic matrix step
            L_t = self.construct_lefkovitch_matrix(env["temperature"], env["turbulence"])
            
            # Linear Algebra Matrix Multiplication: N_(t+1) = L_t . N_t
            pop_vector = np.dot(L_t, pop_vector)
            
            # Save demographic vector
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
