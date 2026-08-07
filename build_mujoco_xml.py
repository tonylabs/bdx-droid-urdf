#!/usr/bin/env python3
"""Convert BDX URDF -> a MuJoCo body-tree include (bdx.xml).

Emits a ``<mujocoinclude>`` holding ONLY the robot body tree (base_link free body +
the two leg chains), meant to be pulled into a world with
``<include file="dreambo_asymmetry.xml"/>`` inside <worldbody>. The rest of the model
— compiler + mesh assets (dependencies.xml), scene/floor/lights (scene.xml),
actuators + sensors (world.xml) — lives in the sibling include files.

What this adds beyond a raw MuJoCo URDF compile:

  1. a real ``base_link`` BODY with a <freejoint> (the raw import welds the root link
     into worldbody, so there's no floating base / no body named base_link),
  2. base_link inertial recovered from the URDF (the weld drops it),
  3. an "imu" site at the pose of the URDF "imu" fixed joint (imu_link mount) so the
     gyro/accelerometer frames (declared in world.xml) match training,
  4. per-joint <joint armature=...> (reflected rotor inertia; policy is sensitive to
     it on the ankle),
  5. collision geoms set contype=1 conaffinity=0 -> robot geoms collide with the floor
     (conaffinity=1 in scene.xml) but never each other (convex-hull STLs interpenetrate
     at the bent-knee pose); visual geoms (group 1) stay non-colliding.

Joint names / axes / limits / link poses all come from bdx.urdf.
Re-run after any URDF change.
"""

import math
import os
import xml.etree.ElementTree as ET
import mujoco

# run from this script's directory so the paths below stay relative & portable
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

URDF = os.path.join("bdx.urdf")
OUT = os.path.join("bdx.xml")

SPAWN_Z = 0.33  # init_state.pos[2]; default home height of the free base

# name-suffix -> armature (reflected rotor inertia).

ARMATURE = [
    ("hip_yaw",     0.02),
    ("hip_roll",    0.02),
    ("hip_pitch",   0.02),
    ("knee_pitch",  0.02),
    ("ankle_pitch", 0.0042),
    ("ankle_roll",  0.0042),
    ("neck_pitch",  0.02),
    ("head_pitch",  0.005),
    ("head_yaw",    0.005),
    ("head_roll",   0.005),
    ("antenna_l",   0.001),
    ("antenna_r",   0.001),
]


def armature_for(joint_name):
    for suffix, arm in ARMATURE:
        if joint_name.startswith(suffix):
            return arm
    raise KeyError(joint_name)


def rpy_to_quat(roll, pitch, yaw):
    """URDF extrinsic-XYZ rpy -> MuJoCo (w, x, y, z) quaternion string."""
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    return f"{w:g} {x:g} {y:g} {z:g}"


# --- 1. raw URDF -> MJCF via MuJoCo's compiler (gives bodies/joints/inertias/geoms) ---
# MuJoCo's URDF compiler accepts a <mujoco> child inside <robot> for compiler options.
# We parse the URDF, inject the element properly, and compile from string.
meshdir = os.path.abspath(ROOT).replace("\\", "/")
urdf_tree = ET.parse(URDF)
urdf_root = urdf_tree.getroot()
# Add <mujoco><compiler> as a child of <robot>
mujoco_elem = ET.SubElement(urdf_root, "mujoco")
ET.SubElement(mujoco_elem, "compiler", {
    "meshdir": meshdir,
    "balanceinertia": "true",
    "discardvisual": "false",
})
urdf_str = ET.tostring(urdf_root, encoding="unicode")
m = mujoco.MjModel.from_xml_string(urdf_str)
raw = os.path.join(ROOT, "_raw.mjcf")
mujoco.mj_saveLastXML(raw, m)

tree = ET.parse(raw)
root = tree.getroot()
os.remove(raw)

# --- 2. restructure worldbody: weld-base -> base_link body + freejoint ---
# The raw import welds base_link (and its fixed-joint child imu_link) into worldbody,
# so its geoms sit as direct children of <worldbody> and the leg chains are separate
# <body> subtrees. Re-parent all of it under a floating base_link body.
wb = root.find("worldbody")
base_geoms = list(wb.findall("geom"))          # base_link + imu_link visual geoms
# All direct child bodies of base_link: legs + neck/head/antenna chain
child_bodies = [b for b in wb.findall("body")
                if b.get("name") in ("hip_yaw_l_link", "hip_yaw_r_link", "neck_pitch_link")]

base = ET.Element("body", {"name": "base_link", "pos": f"0 0 {SPAWN_Z}"})
ET.SubElement(base, "freejoint", {"name": "floating_base"})

# base_link inertial straight from the URDF (the weld drops it from the import).
urdf_tree = ET.parse(URDF)
urdf_root = urdf_tree.getroot()
blink = next(l for l in urdf_root.findall("link") if l.get("name") == "base_link")
bi = blink.find("inertial")
bpos = bi.find("origin").get("xyz")
mass = float(bi.find("mass").get("value"))
inr = bi.find("inertia")
ixx, iyy, izz = (float(inr.get(k)) for k in ("ixx", "iyy", "izz"))
ixy, ixz, iyz = (float(inr.get(k)) for k in ("ixy", "ixz", "iyz"))
# MuJoCo fullinertia order: ixx iyy izz ixy ixz iyz
ET.SubElement(base, "inertial", {
    "pos": bpos,
    "mass": f"{mass:g}",
    "fullinertia": f"{ixx:g} {iyy:g} {izz:g} {ixy:g} {ixz:g} {iyz:g}",
})

# IMU mount: read pose from the URDF "imu" fixed joint (imu_link is rigidly fixed to
# base_link). The gyro/accelerometer (declared in world.xml) report in this site
# frame, so it must match the IMU mount used in training.
imu_joint = next(j for j in urdf_root.findall("joint") if j.get("name") == "imu")
imu_org = imu_joint.find("origin")
imu_pos = imu_org.get("xyz", "0 0 0") if imu_org is not None else "0 0 0"
imu_rpy = [float(v) for v in
           (imu_org.get("rpy", "0 0 0") if imu_org is not None else "0 0 0").split()]
ET.SubElement(base, "site", {
    "name": "imu", "pos": imu_pos, "quat": rpy_to_quat(*imu_rpy), "size": "0.01",
})

for g in base_geoms:
    wb.remove(g)
    base.append(g)
for b in child_bodies:
    wb.remove(b)
    base.append(b)

# --- 3. per-joint armature ---
for jnt in base.iter("joint"):
    name = jnt.get("name") or ""
    if name.endswith("_joint"):
        jnt.set("armature", f"{armature_for(name):g}")

# --- 4. collision filtering: self-collision OFF, robot<->floor ON ---
# The compile marks visual geoms (group 1) contype=0 conaffinity=0 already. Give the
# collision geoms (no contype set) contype=1 conaffinity=0: they collide with the
# scene.xml floor (conaffinity=1) but, sharing conaffinity=0, never with each other.
for g in base.iter("geom"):
    if g.get("contype") is None:
        g.set("contype", "1")
        g.set("conaffinity", "0")

# --- 5. emit a <mujocoinclude> body-tree ---
out_root = ET.Element("mujocoinclude")
out_root.append(base)
out_tree = ET.ElementTree(out_root)
ET.indent(out_tree, space="    ")
out_tree.write(OUT, encoding="unicode", xml_declaration=False)
print("wrote", OUT)
