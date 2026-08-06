# BD-927 Droid URDF

URDF description package for the BD-927 Droid — a bipedal robot built with Unitree GO-M8010-6 actuators. This package provides the robot model, 3D meshes, and launch files for visualization and simulation in ROS.

## Robot Overview

The BD-927 Droid is a bipedal platform with **16 revolute joints** across the body, legs, head, and antennas.

### Legs (×2 — left/right, 5 DOF each)

| Joint | Type | Axis | Range (rad) |
|---|---|---|---|
| `hip_yaw` | revolute | Z | ±0.3 |
| `hip_roll` | revolute | X | ±0.25 |
| `hip_pitch` | revolute | Y | 0 to 1.9 |
| `knee_pitch` | revolute | Y | −1.95 to 0 |
| `ankle_pitch` | revolute | Y | −1.8 to 1 |

### Head & Neck (4 DOF)

| Joint | Type | Axis | Range (rad) |
|---|---|---|---|
| `neck_pitch` | revolute | Y | 0 to 1.4 |
| `head_pitch` | revolute | Y | −1.75 to 0 |
| `head_yaw` | revolute | tilted | ±1 |
| `head_roll` | revolute | tilted | ±0.3 |

### Antennas (×2 — left/right)

| Joint | Type | Axis | Range (rad) |
|---|---|---|---|
| `antenna_pitch_l` | revolute | Y | ±1 |
| `antenna_pitch_r` | revolute | Y | ±1 |

### Sensors

- **IMU** — fixed link (`imu_link`) attached to `base_link` (HiPNUC HI13)

## Model Details

- **Total links:** 20 (including `base_link` and `imu_link`)
- **Total joints:** 16 revolute + 1 fixed
- **Actuators:** Unitree GO-M8010-6

## License

This project is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

**You are free to:**
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

**Under the following terms:**
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial** — You may not use the material for commercial purposes.
- **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license.
