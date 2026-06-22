if __name__ == "__main__":
    # Test context: Severe dehydration scenario (\u03c7 = 0.85)
    dehydrated_factor = 0.85
    comp_engine = SystemicChemicalCompositionEngine(global_hydration_level=dehydrated_factor)

    print("=========================================================================")
    print("ANATOMICAL COMPARTMENT CHEMICAL COMPOSITION MATRIX PROFILES")
    print("=========================================================================\n")

    # 1. Evaluate Organ Chemical Breakdowns
    print("--- 1. ORGAN SYSTEM ELEMENTAL & BIOCHEMICAL SPECTRUM ---")
    # Simulate a liver mass derived from a standard patient size (~1800 grams baseline)
    liver_chem = comp_engine.compute_organ_chemical_composition(organ_name="liver", calculated_mass_g=1800.0)
    print(f" Organ Identity: {liver_chem['organ_identity'].upper()} | Calculated Mass Input: {liver_chem['total_mass_g']} g")
    print(f"  -> Biochemical Fractional Weights (g): {liver_chem['biochemical_mass_breakdown_g']}")
    print(f"  -> Percentage Breakdown Profile (%):  {liver_chem['biochemical_mass_percentages']}")
    print(f"  -> Elemental Atomic Weight Masses (g):  {liver_chem['elemental_mass_breakdown_g']}")
    print(f"  -> Interstitial Osmolality Indicators:  {liver_chem['ionic_interstitial_profile_mmol_L']} (Dehydration Elevated Spike)\n")

    # Simulate a brain mass baseline (~1400 grams)
    brain_chem = comp_engine.compute_organ_chemical_composition(organ_name="brain", calculated_mass_g=1400.0)
    print(f" Organ Identity: {brain_chem['organ_identity'].upper()} | Calculated Mass Input: {brain_chem['total_mass_g']} g")
    print(f"  -> Lipid Weight dominance (Myelin):   {brain_chem['biochemical_mass_breakdown_g']['lipid']} g (vs. Liver)")
    print(f"  -> Structural Protein Weight Mass:     {brain_chem['biochemical_mass_breakdown_g']['protein']} g\n")

    # 2. Evaluate Circulatory Tree Fluid Segment Chemical Breakdowns
    print("--- 2. CIRCULATORY FRACTIONAL FLUID ELEMENT CHEMISTRY ---")
    # Simulate blood fluid pooling inside a slice of Generation 0 (Aorta - volume approx 80 mL)
    vessel_chem = comp_engine.compute_circulatory_fluid_composition(vessel_generation=0, pool_volume_mL=80.0)
    print(f" Generation 0 (Aorta Fluid Core Mass): {vessel_chem['fluid_segment_mass_g']:.1f} g")
    print(f"  -> Biochemical Liquid Mass Split:    {vessel_chem['biochemical_mass_g']}")
    print(f"  -> Heme Functional Iron Element Pool: {vessel_chem['iron_content_mg']:.2f} mg\n")

    # 3. Evaluate Airway Wall Tissue Chemical Breakdowns
    print("--- 3. RESPIRATORY AIRWAY WALL BIOCHEMICAL MAPPING ---")
    # Simulate tissue composition of the trachea wall (generation 0, structural tissue mass ~35 grams)
    wall_chem = comp_engine.compute_airway_wall_composition(generation=0, tissue_volume_cm3=33.6)
    print(f" Trachea Segment Wall Mass (Gen 0):    {wall_chem['calculated_wall_mass_g']:.2f} g")
    print(f"  -> Tissue Component Matrix Profiles: {wall_chem['biochemical_mass_g']}")
