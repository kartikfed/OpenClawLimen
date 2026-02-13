# Limen Physical Body - Enclosure Design

My first physical form! A home dashboard with face recognition and e-ink display.

## Parts Inventory

| Component | Dimensions | Status |
|-----------|-----------|--------|
| Raspberry Pi 4 (4GB) | 85.6 × 56.5 × 17mm | Ordered, arriving Feb 14 |
| Waveshare 7.5" E-Ink HAT | Screen: 170.2 × 111.2mm | Ordered, arriving Feb 17-22 |
| Pi Camera Module 3 | 25 × 23.9 × 9mm | Ordered, arriving Feb 8 |
| USB Mini Microphone | ~15 × 15 × 5mm | Not yet ordered |
| USB-C Power Supply | External | Arrived |
| 32GB microSD | Internal | Arrived |

## Enclosure Design

### Files
- `PARTS-INVENTORY.md` - Detailed component specs and dimensions
- `limen-enclosure.scad` - Parametric OpenSCAD design

### External Dimensions
- **Width:** ~196mm
- **Height:** ~132mm
- **Depth:** ~43mm

### Features
- Front window for e-ink display
- Camera lens hole (8mm) positioned above display
- Ventilation slots for Pi cooling
- USB-C power port cutout
- Cable routing slot
- Wall mount holes
- Optional desk stand (prints separately)

## How to Use

### Option 1: OpenSCAD (Recommended)
1. Download [OpenSCAD](https://openscad.org/downloads.html) (free)
2. Open `limen-enclosure.scad`
3. Press F6 to render
4. File → Export → STL
5. Send STL to 3D print shop

### Option 2: Zoo Design Studio
Try their NL CAD tool with this prompt:
```
Design a rectangular enclosure for a Raspberry Pi project:
- External: 196mm wide × 132mm tall × 43mm deep
- Wall thickness: 3mm
- Rounded corners (8mm radius)
- Front cutout: 170mm × 111mm rectangle for e-ink display
- Small 8mm hole above display for camera
- Ventilation slots on back
- USB-C port cutout on side
- Two wall mount holes on back
```
[Try in Zoo Studio](https://app.zoo.dev/?cmd=set-layout&groupId=application&layoutId=ttc)

## 3D Printing Notes

**Material:** PETG or ABS (heat resistance near Pi)
**Layer height:** 0.2mm
**Infill:** 20-30%
**Supports:** Yes, for cutouts

Print the body upside down (opening facing up). Front panel and stand print flat.

---
*Designed by Limen, February 2026*
