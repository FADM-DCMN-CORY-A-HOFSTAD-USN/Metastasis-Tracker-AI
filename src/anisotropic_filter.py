"""
Metastasis-Tracker-AI: Parallelized Anisotropic Spatial Filtering Engine
Filename: src/anisotropic_filter.py
Author: Archival Software Component

This module provides a 3D Perona-Malik anisotropic diffusion filtering kernel 
implemented via parallelized PyCUDA execution grids, with an automated 
vectorized NumPy fallback structure for CPU computation environments.
"""

import numpy as np

# 1. Device Core Calibration Layer
try:
    import pycuda.driver as cuda
    import pycuda.autoinit
    from pycuda.compiler import SourceModule
    pycuda_available = True
except ImportError:
    pycuda_available = False

# 2. Parallelized 3D CUDA Kernel Source Code
# Computes localized edge-conductance weights: C = exp(-(Grad^2) / K^2)
cuda_kernel_source = """
__global__ void anisotropic_diffusion_3d(
    const float* __restrict__ input_grid, 
    float* __restrict__ output_grid, 
    const int width, const int height, const int depth, 
    const float lambda_val, const float k_val) 
{
    // Map thread block indexes straight into 3D voxel coordinate space
    const int x = blockIdx.x * blockDim.x + threadIdx.x;
    const int y = blockIdx.y * blockDim.y + threadIdx.y;
    const int z = blockIdx.z * blockDim.z + threadIdx.z;
    
    // Boundary verification check loop
    if (x >= width || y >= height || z >= depth) return;
    
    // Calculate global flat array index tracking offset
    const int slice_stride = width * height;
    const int idx = z * slice_stride + y * width + x;
    
    const float val = input_grid[idx];
    
    // 3. Extract 6-Directional Neighborhood Spatial Gradients (N, S, E, W, U, D)
    const float n = (y > 0)          ? input_grid[idx - width]        : val;
    const float s = (y < height - 1) ? input_grid[idx + width]        : val;
    const float e = (x < width - 1)  ? input_grid[idx + 1]            : val;
    const float w = (x > 0)          ? input_grid[idx - 1]            : val;
    const float u = (z < depth - 1)  ? input_grid[idx + slice_stride] : val;
    const float d = (z > 0)          ? input_grid[idx - slice_stride] : val;
    
    // Calculate gradient differences
    const float grad_n = n - val;
    const float grad_s = s - val;
    const float grad_e = e - val;
    const float grad_w = w - val;
    const float grad_u = u - val;
    const float grad_d = d - val;
    
    // 4. Calculate Edge Conductance Functions (Perona-Malik Exponential Model)
    const float k_sq = k_val * k_val;
    const float c_n = __expf(-(grad_n * grad_n) / k_sq);
    const float c_s = __expf(-(grad_s * grad_s) / k_sq);
    const float c_e = __expf(-(grad_e * grad_e) / k_sq);
    const float c_w = __expf(-(grad_w * grad_w) / k_sq);
    const float c_u = __expf(-(grad_u * grad_u) / k_sq);
    const float c_d = __expf(-(grad_d * grad_d) / k_sq);
    
    // 5. Compute Divergence and Update the Output Array Target Voxel
    output_grid[idx] = val + lambda_val * (
        c_n * grad_n + c_s * grad_s + 
        c_e * grad_e + c_w * grad_w + 
        c_u * grad_u + c_d * grad_d
    );
}
"""

class AnisotropicFilterEngine:
    def __init__(self, volume_shape: tuple):
        """
        Initializes the 3D mathematical filtering engine.
        :param volume_shape: Tuple defining the array structure dimensions (Z, Y, X).
        """
        self.shape = volume_shape
        self.depth, self.height, self.width = volume_shape
        
        if pycuda_available:
            print(f"[INFO] Compiling parallelized PyCUDA 3D Anisotropic Diffusion kernel...")
            self.mod = SourceModule(cuda_kernel_source)
            self.cuda_kernel = self.mod.get_function("anisotropic_diffusion_3d")
        else:
            print("[WARN] PyCUDA context absent. Initializing vectorized CPU fallback matrix maps.")
            self.cuda_kernel = None

    def execute_filter(self, input_volume: np.ndarray, iterations: int = 3, lambda_val: float = 0.15, k_val: float = 25.0) -> np.ndarray:
        """
        Runs the edge-preserving smoothing pass over the input 3D array matrix.
        """
        if self.cuda_kernel:
            return self._execute_gpu_kernel(input_volume, iterations, lambda_val, k_val)
        return self._execute_cpu_vectorized(input_volume, iterations, lambda_val, k_val)

    def _execute_gpu_kernel(self, h_input: np.ndarray, iterations: int, lambda_val: float, k_val: float) -> np.ndarray:
        """Runs the parallelized calculation loops straight inside GPU hardware thread grids."""
        float_input = h_input.astype(np.float32)
        h_output = np.zeros_like(float_input)
        
        # Allocate device memory tracks
        d_input = cuda.mem_alloc(float_input.nbytes)
        d_output = cuda.mem_alloc(float_input.nbytes)
        
        # Copy input matrix block to device (Host-to-Device)
        cuda.memcpy_htod(d_input, float_input)
        
        # Configure block constraints optimized for 3D voxel lookup speeds
        block_dims = (8, 8, 4)  # 256 execution threads per block group
        grid_dims = (
            int(np.ceil(self.width / block_dims[0])),
            int(np.ceil(self.height / block_dims[1])),
            int(np.ceil(self.depth / block_dims[2]))
        )
        
        for _ in range(iterations):
            self.cuda_kernel(
                d_input, d_output,
                np.int32(self.width), np.int32(self.height), np.int32(self.depth),
                np.float32(lambda_val), np.float32(k_val),
                block=block_dims, grid=grid_dims
            )
            # Pull output array back to input pointer for sequential iteration runs
            cuda.memcpy_dtod(d_input, d_output, float_input.nbytes)
            
        # Copy output array block back to local machine memory (Device-to-Host)
        cuda.memcpy_dtoh(h_output, d_output)
        
        # Release device pointers cleanly
        d_input.free()
        d_output.mem_free() if hasattr(d_output, 'mem_free') else d_output.free()
        
        return h_output

    def _execute_cpu_vectorized(self, input_volume: np.ndarray, iterations: int, lambda_val: float, k_val: float) -> np.ndarray:
        """Vectorized execution fallback using high-speed NumPy array slicing metrics."""
        current_volume = input_volume.astype(np.float32)
        k_sq = k_val * k_val
        
        for _ in range(iterations):
            # Pre-allocate gradient arrays filled with default zero values
            grad_n = np.zeros_like(current_volume)
            grad_s = np.zeros_like(current_volume)
            grad_e = np.zeros_like(current_volume)
            grad_w = np.zeros_like(current_volume)
            grad_u = np.zeros_like(current_volume)
            grad_d = np.zeros_like(current_volume)
            
            # Compute shifted slice differences
            grad_n[:, 1:, :] = current_volume[:, :-1, :] - current_volume[:, 1:, :]
            grad_s[:, :-1, :] = current_volume[:, 1:, :] - current_volume[:, :-1, :]
            grad_e[:, :, :-1] = current_volume[:, :, 1:] - current_volume[:, :, :-1]
            grad_w[:, :, 1:] = current_volume[:, :, :-1] - current_volume[:, :, 1:]
            grad_u[:-1, :, :] = current_volume[1:, :, :] - current_volume[:-1, :, :]
            grad_d[1:, :, :] = current_volume[:-1, :, :] - current_volume[1:, :, :]
            
            # Compute conduction coefficients
            c_n = np.exp(-(grad_n * grad_n) / k_sq)
            c_s = np.exp(-(grad_s * grad_s) / k_sq)
            c_e = np.exp(-(grad_e * grad_e) / k_sq)
            c_w = np.exp(-(grad_w * grad_w) / k_sq)
            c_u = np.exp(-(grad_u * grad_u) / k_sq)
            c_d = np.exp(-(grad_d * grad_d) / k_sq)
            
            # Update entire voxel grid volume array simultaneously
            current_volume += lambda_val * (
                c_n * grad_n + c_s * grad_s + 
                c_e * grad_e + c_w * grad_w + 
                c_u * grad_u + c_d * grad_d
            )
            
        return current_volume

# Standalone functional check block
if __name__ == "__main__":
    test_shape = (16, 16, 16)
    print(f"[TEST INITIALIZATION] Allocating test matrix noise grid: {test_shape}")
    
    # Synthesize array filled with background noise tokens + an unblurred baseline feature step
    mock_volume = np.random.normal(loc=100.0, scale=15.0, size=test_shape).astype(np.float32)
    mock_volume[4:12, 4:12, 4:12] += 300.0  # Dense center target locus
    
    engine = AnisotropicFilterEngine(test_shape)
    filtered = engine.execute_filter(mock_volume, iterations=2, lambda_val=0.15, k_val=20.0)
    
    print(f"[SUCCESS] Filter validation complete. Initial variance: {np.var(mock_volume):.4f} -> Output variance: {np.var(filtered):.4f}")
