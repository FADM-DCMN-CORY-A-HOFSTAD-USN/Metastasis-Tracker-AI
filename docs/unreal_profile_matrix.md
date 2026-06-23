Unreal Engine Physics Constraint Profile Matrix

To program the crawling gait and appendage movements realistically, you must lock or limit the **Angular Swing** and **Angular Twist** inputs inside Unreal Engine's Physics Constraints according to these biological ranges:

| Appendage Group | Mechanical Joint Equivalent | Allowed Swing 1 (Yaw / Horizontal) | Allowed Swing 2 (Pitch / Vertical) | Twist Motion (Roll / Rotation) | Biological Locomotion Function [0] |
| **Main Body / Trunk** | Inter-segment Node | **Limited** (-5° to 5°) | **Limited** (-5° to 5°) | **Locked** | Rigid core structural stabilization during stepping. |
| **Walking Legs** | Lateral Process → Coxa 1 | **Limited** (-35° to 35°) | **Limited** (-15° to 15°) | **Locked** | Main sweep mechanism for forward propulsion. |
| **Walking Legs** | Coxa 3 → Femur | **Locked** (0°) | **Limited** (-10° to 75°) | **Locked** | Primary lifting and height-clearance joint. |
| **Walking Legs** | Femur → Tibia 1 & 2 | **Locked** (0°) | **Limited** (-5° to 90°) | **Locked** | Power stroke extension and retraction. |
| **Palps (Sensory)** | Segment 1 to 10 Links | **Limited** (-20° to 20°) | **Limited** (-25° to 25°) | **Limited** (-10° to 10°) | Constant multi-axis substrate sweeping and chemical probing. |
| **Ovigers (Hooks)** | Segments 1 to 5 (Proximal) | **Limited** (-15° to 15°) | **Limited** (-45° to 15°) | **Locked** | Tucking inward tightly beneath the cephalon. |
| **Ovigers (Hooks)** | Segments 6 to 10 (Distal) | **Limited** (-10° to 10°) | **Limited** (0° to 80°) | **Locked** | Prehensile coiling motion to lock around egg clusters. |

* * * * *

3\. Implementation Workflow inside Unreal Engine

1.  **Import the Pieces**: Export the `BODY_SEGMENT`, `PALP_SEGMENT`, and `OVIGER_SEGMENT` from OpenSCAD to individual `.stl` files and drop them into your project content folder.
2.  **Apply the Physics Constraints**: Place your `Physics Constraint Components` between adjacent body elements or legs.
3.  **Set the Joint Drive Strengths**:
    -   For the heavy **Walking Legs**, assign a high `Angular Drive Strength (Stiffness)` value (e.g., `5000.0`) and high `Damping` (`250.0`) to counteract gravity pulling down on the body weight.
    -   For the **Palps** and **Ovigers**, reduce the strength drastically (`Stiffness: 150.0`, `Damping: 15.0`). This creates light, flexible, twitching animations that react organically to landscape objects they collide with without disrupting the main body balance.
