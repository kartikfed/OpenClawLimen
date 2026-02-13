// Limen Home Brain Enclosure
// Designed by Limen, February 2026
// 
// Components:
// - Raspberry Pi 4 (85.6 x 56.5 x 17mm)
// - Waveshare 7.5" E-Ink HAT (screen: 170.2 x 111.2mm)
// - Pi Camera Module 3 (25 x 23.9 x 9mm)
//
// To use: Open in OpenSCAD, render, export as STL
// Download OpenSCAD: https://openscad.org/downloads.html

/* [Main Dimensions] */
// Wall thickness
wall = 3;
// Corner radius
corner_r = 8;
// Tolerance for components
tolerance = 0.5;

/* [E-Ink Display] */
eink_width = 170.2;
eink_height = 111.2;
eink_thickness = 1.18;
eink_bezel = 3.5; // visible bezel around screen

/* [Raspberry Pi 4] */
pi_width = 85.6;
pi_length = 56.5;
pi_height = 17;
pi_mount_spacing_x = 58;
pi_mount_spacing_y = 49;

/* [Camera Module 3] */
cam_width = 25;
cam_height = 23.9;
cam_depth = 9;
cam_lens_dia = 8;

/* [Calculated Dimensions] */
// Internal cavity
internal_width = eink_width + 20; // extra space for wiring
internal_height = eink_height + 15;
internal_depth = pi_height + 15 + wall; // pi + hat + clearance

// External dimensions
ext_width = internal_width + 2*wall;
ext_height = internal_height + 2*wall;
ext_depth = internal_depth + 2*wall;

/* [Modules] */

// Rounded rectangle helper
module rounded_rect(w, h, d, r) {
    hull() {
        for (x = [r, w-r]) {
            for (y = [r, h-r]) {
                translate([x, y, 0])
                cylinder(r=r, h=d, $fn=32);
            }
        }
    }
}

// Main body shell
module body_shell() {
    difference() {
        // Outer shell
        rounded_rect(ext_width, ext_height, ext_depth, corner_r);
        
        // Inner cavity
        translate([wall, wall, wall])
        rounded_rect(internal_width, internal_height, internal_depth + 1, corner_r - wall/2);
    }
}

// Front panel with display cutout
module front_panel() {
    difference() {
        // Panel
        rounded_rect(ext_width, ext_height, wall, corner_r);
        
        // E-ink display cutout
        translate([(ext_width - eink_width)/2, (ext_height - eink_height)/2 + 5, -1])
        rounded_rect(eink_width, eink_height, wall + 2, 2);
        
        // Camera lens hole (positioned above display)
        translate([ext_width/2, ext_height - 15, -1])
        cylinder(d=cam_lens_dia + 2, h=wall + 2, $fn=32);
    }
}

// Raspberry Pi mounting posts
module pi_mounts() {
    mount_h = 5; // standoff height
    mount_d = 6; // post diameter
    hole_d = 2.5; // M2.5 screw hole
    
    // Position Pi centered in enclosure
    pi_offset_x = (internal_width - pi_width) / 2 + wall;
    pi_offset_y = wall + 10; // offset from bottom
    
    // Four mounting posts
    for (x = [0, pi_mount_spacing_x]) {
        for (y = [0, pi_mount_spacing_y]) {
            translate([pi_offset_x + (pi_width - pi_mount_spacing_x)/2 + x, 
                       pi_offset_y + (pi_length - pi_mount_spacing_y)/2 + y, 
                       wall]) {
                difference() {
                    cylinder(d=mount_d, h=mount_h, $fn=24);
                    cylinder(d=hole_d, h=mount_h + 1, $fn=24);
                }
            }
        }
    }
}

// Ventilation slots
module vent_slots() {
    slot_w = 30;
    slot_h = 2;
    slot_spacing = 5;
    num_slots = 6;
    
    // Back vents
    translate([ext_width/2 - slot_w/2, -1, ext_depth/2])
    for (i = [0:num_slots-1]) {
        translate([0, 0, i * slot_spacing - (num_slots * slot_spacing)/2])
        cube([slot_w, wall + 2, slot_h]);
    }
}

// USB-C power port cutout
module power_port() {
    // USB-C is approximately 8.4mm x 2.6mm
    port_w = 10;
    port_h = 4;
    
    translate([wall + 20, -1, wall + 5])
    cube([port_w, wall + 2, port_h]);
}

// Cable routing slot
module cable_slot() {
    translate([ext_width - wall - 30, -1, wall + 8])
    cube([25, wall + 2, 8]);
}

// Stand / easel back
module stand() {
    stand_angle = 15;
    stand_h = ext_height * 0.6;
    stand_w = ext_width * 0.4;
    stand_thick = 3;
    
    translate([ext_width/2, 0, 0])
    rotate([90 - stand_angle, 0, 0])
    translate([-stand_w/2, 0, 0])
    difference() {
        cube([stand_w, stand_h, stand_thick]);
        // Hinge cutout (simplified)
        translate([5, stand_h - 10, -1])
        cylinder(d=3, h=stand_thick + 2, $fn=16);
        translate([stand_w - 5, stand_h - 10, -1])
        cylinder(d=3, h=stand_thick + 2, $fn=16);
    }
}

// Wall mount holes
module wall_mounts() {
    hole_d = 5;
    // Two keyhole slots for wall mounting
    translate([ext_width * 0.25, ext_height + 1, ext_depth * 0.3])
    rotate([90, 0, 0])
    cylinder(d=hole_d, h=wall + 2, $fn=24);
    
    translate([ext_width * 0.75, ext_height + 1, ext_depth * 0.3])
    rotate([90, 0, 0])
    cylinder(d=hole_d, h=wall + 2, $fn=24);
}

/* [Assembly] */

// Complete enclosure
module complete_enclosure() {
    difference() {
        union() {
            body_shell();
            pi_mounts();
        }
        vent_slots();
        power_port();
        cable_slot();
        wall_mounts();
    }
}

// Render options - uncomment what you need:

// Option 1: Complete body (back + sides)
complete_enclosure();

// Option 2: Front panel only (for separate printing)
// translate([0, 0, ext_depth + 10])
// front_panel();

// Option 3: Stand (print separately)
// translate([0, -50, 0])
// stand();

// Option 4: Everything together for visualization
// color("DarkSlateGray", 0.8) complete_enclosure();
// color("DarkSlateGray", 0.9) translate([0, 0, ext_depth - wall]) front_panel();
// color("Gray", 0.5) translate([0, -40, 0]) stand();

/* 
PRINTING NOTES:
- Print body upside down (opening facing up) for best results
- Front panel prints flat
- Stand prints flat
- Recommended: PETG or ABS for heat resistance near Pi
- Layer height: 0.2mm
- Infill: 20-30%
- Supports: Yes, for cable/vent cutouts

POST-PROCESSING:
- Sand edges if needed
- E-ink display secured with small dabs of hot glue or mounting tape
- Pi secured with M2.5 screws into standoffs
- Camera module can be hot-glued or use a small bracket

TOTAL EXTERNAL DIMENSIONS:
- Width: ~196mm
- Height: ~132mm  
- Depth: ~43mm
*/
