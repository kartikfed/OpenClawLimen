# Limen Home Brain - Parts Inventory & Dimensions

## Component List

### 1. Raspberry Pi 4 Model B (4GB)
- **Dimensions:** 85.6mm × 56.5mm × 17mm (board only, no heatsink)
- **Mounting holes:** 58mm × 49mm pattern, M2.5
- **Ports:** USB-C power, 2× micro-HDMI, 2× USB 3.0, 2× USB 2.0, Ethernet, 3.5mm audio
- **Notes:** Main compute unit, sits at bottom of enclosure

### 2. Waveshare 7.5" E-Ink HAT (V2)
- **Driver Board:** 65.0mm × 30.2mm
- **Display Area:** 163.2mm × 97.92mm
- **Raw Panel:** 170.2mm × 111.2mm × 1.18mm
- **Full Screen (with bezel):** 177.2mm × 118.2mm
- **Resolution:** 800 × 480 pixels
- **Notes:** Connects via 40-pin GPIO, display is the "face"

### 3. Raspberry Pi Camera Module 3
- **Board Dimensions:** 25mm × 23.9mm × 9mm (approx)
- **Lens protrusion:** ~5mm additional
- **Cable:** 15-pin FFC ribbon cable to CSI port
- **Notes:** Needs viewing hole in enclosure, ideally near display center

### 4. USB Mini Microphone
- **Dimensions:** ~15mm × 15mm × 5mm (typical)
- **Connection:** USB-A
- **Notes:** Small, can be mounted internally or externally

### 5. Power Supply
- **Connection:** USB-C (external, not enclosed)

---

## Enclosure Design Requirements

### Overall Dimensions (estimated)
- **Width:** ~190mm (to accommodate 177mm screen + margins)
- **Height:** ~130mm (to accommodate 118mm screen + Pi depth)
- **Depth:** ~40mm (Pi + HAT stack + camera)

### Key Features Needed
1. **Front window** for e-ink display (170mm × 111mm cutout)
2. **Camera hole** - small circle, ~8mm diameter, positioned for face detection
3. **Ventilation slots** on back/sides for Pi cooling
4. **Cable routing** for power (USB-C) and potentially HDMI
5. **Mounting points** for all components
6. **Stand/easel** option for desk placement OR wall-mount holes

### Component Stack (front to back)
1. E-ink display (front-facing)
2. HAT driver board
3. Raspberry Pi 4
4. Camera module (angled or front-mounted)
5. Back cover

### Design Style
- Clean, minimal aesthetic
- Rounded corners
- Matte finish preferred
- Color: Black or dark gray to complement e-ink
