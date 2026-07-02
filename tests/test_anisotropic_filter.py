"""
Metastasis-Tracker-AI: Anisotropic Filter Verification Module
Filename: tests/test_anisotropic_filter.py
"""

import pytest
import numpy as np
from src.anisotropic_filter import AnisotropicFilterEngine

def test_anisotropic_filter_reduces_variance_while_preserving_edges():
    """
    Verifies that the anisotropic diffusion engine actively scrubs flat-field 
    noise variations while leaving high-density edge boundaries intact.
    """
    shape = (10, 10, 10)
    engine = AnisotropicFilterEngine(shape)
    
    # 1. Synthesize a clean step edge feature array
    clean_volume = np.full(shape, 100.0, dtype=np.float32)
    clean_volume[5:, :, :] = 400.0  # Sharp physical density split along the Z-axis
    
    # 2. Inject high-frequency noise variance
    np.random.seed(42)  # Lock randomness for test reproducibility
    noisy_volume = clean_volume + np.random.normal(0.0, 10.0, shape).astype(np.float32)
    
    initial_flat_variance = np.var(noisy_volume[:4, :, :])
    
    # 3. Execute edge-preserving calculation loop
    filtered_volume = engine.execute_filter(noisy_volume, iterations=5, lambda_val=0.15, k_val=25.0)
    final_flat_variance = np.var(filtered_volume[:4, :, :])
    
    # Assert background noise has been suppressed cleanly (final variance < initial variance)
    assert final_flat_variance < initial_flat_variance
    
    # Assert structural step boundaries are preserved without collapsing into muddy blurs
    # Step edge transition contrast (Index 4 to Index 5) must remain distinct
    mean_lower_tier = np.mean(filtered_volume[4, :, :])
    mean_upper_tier = np.mean(filtered_volume[5, :, :])
    assert (mean_upper_tier - mean_lower_tier) > 200.0
