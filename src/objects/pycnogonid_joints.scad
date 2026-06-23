// ==============================================================================
// 🕷️ BIOMECHANICALLY PROPORTIONED PYCNOGONID COMPONENT ENGINE
// ==============================================================================
$fn = 32;

// Target Export: "BODY_SEGMENT", "PALP_SEGMENT", "OVIGER_SEGMENT"
part_type = "BODY_SEGMENT"; 

// Anatomical Scales
base_r = 1.0;
lat_process_len = 2.2;
palp_joint_len = 1.8;
oviger_joint_len = 1.4;

module joint_socket() {
    sphere(r = base_r * 1.25);
}

module joint_ball(distance) {
    translate([0, distance, 0])
        sphere(r = base_r * 1.05);
}

// 1. Central Body Node with Pronounced Lateral Extenders
if (part_type == "BODY_SEGMENT") {
    difference() {
        union() {
            // Main spine cross-section
            cylinder(h = 3.5, r = base_r * 1.8, center = true);
            // Lateral process arms pointing outward
            rotate([90, 0, 0]) 
                cylinder(h = lat_process_len * 2 + 3.0, r1 = base_r * 1.4, r2 = base_r * 1.1, center = true);
        }
        // Deep sockets at the tips of the lateral processes for Coxa 1 connection
        translate([0, (lat_process_len + 1.5), 0]) joint_socket();
        translate([0, -(lat_process_len + 1.5), 0]) joint_socket();
    }
}

// 2. Slender, Highly Articulated Palp Segment (Sensory Appendages)
if (part_type == "PALP_SEGMENT") {
    difference() {
        union() {
            rotate([0, 90, 0])
                cylinder(h = palp_joint_len, r1 = base_r * 0.4, r2 = base_r * 0.3, center = false);
            translate([palp_joint_len, 0, 0]) sphere(r = base_r * 0.35);
        }
        rotate([0, 90, 0]) joint_socket();
    }
}

// 3. Curved Oviger Node (Egg-Carrying Appendage)
if (part_type == "OVIGER_SEGMENT") {
    difference() {
        union() {
            // Curving individual segments slightly to mimic the natural oviger hook
            rotate([5, 90, 0])
                cylinder(h = oviger_joint_len, r1 = base_r * 0.5, r2 = base_r * 0.38, center = false);
            translate([oviger_joint_len, 0, 0]) sphere(r = base_r * 0.42);
        }
        rotate([5, 90, 0]) joint_socket();
    }
}
