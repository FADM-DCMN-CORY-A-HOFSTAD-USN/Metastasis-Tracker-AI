import os
import unittest
import matplotlib.pyplot as plt
from src.pulmonary_visualizer import HDF5PulmonaryVisualizer

class TestMatplotlibLayoutAnomalies(unittest.TestCase):
    def setUp(self):
        self.mock_h5 = "tests/pipeline_telemetry.h5"
        self.out_png = "docs/pulmonary_trends.png"
        
        # Ensure a template file context is present to execute layout parses
        if not os.path.exists("tests"): os.makedirs("tests")
        with open(self.mock_h5 + ".mockjson", "w") as f:
            f.write('{"data": [[0,7.4,1,1,2,150],[1,7.3,1.2,0.9,7,550]]}')
            
        self.visualizer = HDF5PulmonaryVisualizer(self.mock_h5, self.out_png)

    def test_graphic_layout_overlap_boundaries(self):
        """
        AUTOMATED SCHEMA VALIDATION: Renders the figure canvas, extracts 
        the physical bounding box coordinates, and verifies zero label overlaps.
        """
        # Render plot elements into memory
        self.visualizer.load_and_render_trends()
        self.assertTrue(os.path.exists(self.out_png), "Visualizer failed to emit graphic asset.")

        # Re-verify layout using current plot figure handles
        fig = plt.figure(1) 
        renderer = fig.canvas.get_renderer()
        
        bboxes = []
        for ax in fig.axes:
            # Extract bounding boxes for titles, x-labels, and y-labels
            if ax.title.get_text():
                bboxes.append(ax.title.get_window_extent(renderer))
            if ax.xaxis.get_label().get_text():
                bboxes.append(ax.xaxis.get_label().get_window_extent(renderer))
            if ax.yaxis.get_label().get_text():
                bboxes.append(ax.yaxis.get_label().get_window_extent(renderer))

        # Check all bounding boxes combinations for physical intersection
        overlap_detected = False
        for i in range(len(bboxes)):
            for j in range(i + 1, len(bboxes)):
                # If box 'i' intersects box 'j', matplotlib bounding boxes overlap
                if bboxes[i].intersects(bboxes[j]):
                    overlap_detected = True
                    break
                    
        self.assertFalse(overlap_detected, "Graphic Layout Error: Text overlaps detected on output chart panel layout.")
        print("[+] Automated Layout Validation Passed: Zero rendering collisions detected.")

if __name__ == "__main__":
    unittest.main()
