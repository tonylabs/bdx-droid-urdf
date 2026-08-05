# BDX Droid URDF

[English](README.md) | 中文

BDX Droid 的 URDF 描述包 —— 一款基于 Unitree GO-M8010-6 电机的双足机器人。本包提供机器人模型、3D 网格文件以及用于 ROS 可视化和仿真的 Launch 文件。

## 机器人概览

BDX Droid 是一款双足平台，全身共 **17 个旋转关节**，分布在躯干、双腿、头部和天线。

### 腿部（左右各 1 条，每条 5 自由度）

| 关节 | 类型 | 轴向 | 范围 (rad) |
|---|---|---|---|
| `hip_yaw` | 旋转 | Z | ±0.3 |
| `hip_roll` | 旋转 | X | ±0.25 |
| `hip_pitch` | 旋转 | Y | 0 ~ 1.9 |
| `knee_pitch` | 旋转 | Y | −1.95 ~ 0 |
| `ankle_pitch` | 旋转 | Y | −1.8 ~ 1 |

### 头部与颈部（4 自由度）

| 关节 | 类型 | 轴向 | 范围 (rad) |
|---|---|---|---|
| `neck_pitch` | 旋转 | Y | 0 ~ 1.4 |
| `head_pitch` | 旋转 | Y | −1.75 ~ 0 |
| `head_yaw` | 旋转 | 倾斜 | ±1 |
| `head_roll` | 旋转 | 倾斜 | ±0.3 |

### 天线（左右各 1 根）

| 关节 | 类型 | 轴向 | 范围 (rad) |
|---|---|---|---|
| `antenna_pitch_l` | 旋转 | Y | ±1 |
| `antenna_pitch_r` | 旋转 | Y | ±1 |

### 传感器

- **IMU** — 固定连杆（`imu_link`），安装在 `base_link` 上（HiPNUC HI13）

## 包目录结构

```
bdx-droid-urdf/
├── CMakeLists.txt          # Catkin 构建配置
├── package.xml             # ROS 包描述文件
├── config/
│   └── joint_names_bdx.yaml
├── launch/
│   ├── display.launch      # RViz 可视化
│   └── gazebo.launch       # Gazebo 仿真
├── meshes/
│   └── *.STL               # 23 个网格文件（视觉 + 碰撞）
└── urdf/
    ├── bdx.urdf            # 机器人描述文件
    └── bdx.csv             # 完整连杆/关节导出数据
```

## 前置依赖

- **ROS**（已测试 Noetic）
- `robot_state_publisher`
- `joint_state_publisher_gui`
- `rviz`
- `gazebo_ros`（仿真用）

## 使用方法

### 在 RViz 中可视化

```bash
roslaunch bdx display.launch
```

### 在 Gazebo 中仿真

```bash
roslaunch bdx gazebo.launch
```

## 模型参数

- **连杆总数：** 20（含 `base_link` 和 `imu_link`）
- **关节总数：** 17 个旋转关节 + 1 个固定关节
- **电机型号：** Unitree GO-M8010-6
- **URDF 来源：** 由 SolidWorks 通过 [sw_urdf_exporter](http://wiki.ros.org/sw_urdf_exporter)（v1.6.0）自动导出

## 许可证

本项目采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可协议。

**您可以：**
- **共享** — 在任何媒介以任何形式复制、发行本作品
- **演绎** — 修改、转换或以本作品为基础进行创作

**惟须遵守下列条件：**
- **署名** — 您必须给出适当的署名，提供指向本许可协议的链接，同时标明是否对原始作品作了修改。
- **非商业性使用** — 您不得将本作品用于商业目的。
- **相同方式共享** — 如果您修改、转换或以本作品为基础进行创作，您必须基于与原先许可协议相同的许可协议分发您贡献的作品。
