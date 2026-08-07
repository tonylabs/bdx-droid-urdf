#!/usr/bin/env python3
"""Open MuJoCo viewer with the robot lifted above ground in a neutral pose."""

import mujoco
import mujoco.viewer

MODEL = "world.xml"
LIFT_HEIGHT = 0.5  # meters above ground

# Load model
m = mujoco.MjModel.from_xml_path(MODEL)
d = mujoco.MjData(m)

# Reset to keyframe if available, otherwise use defaults
if m.nkey > 0:
    mujoco.mj_resetDataKeyframe(m, d, 0)
else:
    mujoco.mj_resetData(m, d)

# Lift the free body above ground
d.qpos[2] = LIFT_HEIGHT  # z-position of the free joint

# Forward kinematics to update body positions
mujoco.mj_forward(m, d)

# Disable gravity so the robot stays in place
m.opt.disableflags |= mujoco.mjtDisableBit.mjDSBL_GRAVITY

# Launch viewer
print(f"Robot lifted to z={LIFT_HEIGHT}m, gravity disabled.")
print("Press SPACE to toggle pause, ESC to exit.")
with mujoco.viewer.launch_passive(m, d) as viewer:
    # Show site frames (XYZ axes at IMU)
    viewer.opt.frame = mujoco.mjtFrame.mjFRAME_SITE
    viewer.sync()
    while viewer.is_running():
        mujoco.mj_step(m, d)
        viewer.sync()
