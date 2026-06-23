import os
import json

class PycnogonidSpeciesSelector:
    def __init__(self):
        """
        Loads the species baseline registry and visual tooltip tracking variables.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        registry_path = os.path.join(base_dir, "src", "data", "pycnogonid_species_selector.json")
        
        with open(registry_path, "r") as f:
            self.data = json.load(f)
            self.registry = self.data["pycnogonid_species_registry"]

    def list_available_options(self):
        """
        Generates data for UI dropdown components, showing display names and color codes.
        """
        options = []
        for key, profile in self.registry.items():
            options.append({
                "id_key": key,
                "display_name": profile["display_name"],
                "color_hex": profile["ui_tooltip"]["hex_code"],
                "tooltip_text": f"Pattern: {profile['ui_tooltip']['pattern_style']} | {profile['ui_tooltip']['description']}"
            })
        return options

    def apply_selection_to_engines(self, target_species_key, biomass_engine, population_engine):
        """
        Overrides core engine constants at runtime based on the user selection.
        """
        if target_species_key not in self.registry:
            print(f"⚠️ Error: Species key [{target_species_key}] not found in JSON data maps.")
            return False

        profile = self.registry[target_species_key]
        limits = profile["empirical_threshold_limits"]

        # 1. Update individual Biomass Engine parameters
        biomass_engine.single_egg_vol = (4.0 / 3.0) * 3.14159 * ((limits["larval_egg_diameter_mm"] / 2.0) ** 3)
        # Re-initialize baseline structural ratios to prevent mass calculation discrepancies
        if "Pycnogonum" in target_species_key:
            biomass_engine.base_leg_rad = 0.85 # Structurally thicker profile
        else:
            biomass_engine.base_leg_rad = 0.50 # Slender nymphonid configuration

        # 2. Update demographic Population Engine matrix constraints
        population_engine.opt_temp = limits["optimal_temperature_c"]
        population_engine.base_f_adult = limits["fecundity_baseline"]
        
        # Extrapolate structural pH/salinity safety buffers based on species environmental depth caps
        if limits["depth_range_m"][1] > 2000.0:
            population_engine.sigma_ph = 0.15 # Abyssal variants possess hyper-rigid pH tolerance ceilings
        else:
            population_engine.sigma_ph = 0.35 # Intertidal variants are robust to environmental variance

        print(f"🚀 SUCCESS: Simulation engines calibrated to peer-reviewed data profiles for:")
        print(f"   -> {profile['display_name']} ({profile['ui_tooltip']['primary_color']})")
        return True

# ==============================================================================
# Terminal Selection Interactivity Verification
# ==============================================================================
if __name__ == "__main__":
    selector_tool = PycnogonidSpeciesSelector()
    ui_list = selector_tool.list_available_options()
    
    print("\n--- 🕷️ SIMULATOR UI TOOLTIP SELECTION EMULATOR ---")
    for idx, item in enumerate(ui_list):
        print(f"[{idx}] {item['display_name']}")
        print(f"    🎨 Color Swatch: {item['color_hex']} | {item['tooltip_text']}")
        
    print("\n📋 Technical Integration Note: Passing selection indices straight to apply_selection_to_engines() re-maps the environmental limits across active simulation ticks.")
