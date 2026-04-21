# RoboSort - Vision-Based Robotic Sorting via Instance Segmentation & 6D Pose Estimation

<p align="center">
  <img src="https://img.shields.io/badge/Status-In%20Progress-orange?style=flat-square" />
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/PyTorch-2.x-red?style=flat-square&logo=pytorch" />
  <img src="https://img.shields.io/badge/YOLOv11-Ultralytics-purple?style=flat-square" />
  <img src="https://img.shields.io/badge/Open3D-0.18-teal?style=flat-square" />
  <img src="https://img.shields.io/badge/RealSense-D435-lightgray?style=flat-square" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

---

## Overview

This project builds a complete **vision-based robotic sorting system** capable of identifying common household objects and determining their precise 3D orientation — enabling a robotic gripper to know *how* to pick each object up, not just *where* it is.

The system combines state-of-the-art **instance segmentation** (YOLOv11) with **6D pose estimation** via point cloud alignment (FPFH + ICP), operating on RGB-D data from an Intel RealSense D435 depth camera. The end goal is a real-time inference pipeline deployable on a mobile robotic platform.

**Why this matters:** Most robotic pick-and-place systems either rely on expensive structured-light scanners or are limited to pre-programmed, fixed object positions. This project demonstrates a low-cost, learning-based approach that generalizes to arbitrary object placements and orientations — a fundamental challenge in service robotics.

---

## Table of Contents

- [Project Architecture](#project-architecture)
- [Technical Stack](#technical-stack)
- [Development Roadmap](#development-roadmap)
  - [Phase 1 — Environment Setup](#phase-1--environment-setup)
  - [Phase 2 — Data Collection & Annotation](#phase-2--data-collection--annotation)
  - [Phase 3 — 2D Instance Segmentation](#phase-3--2d-instance-segmentation)
  - [Phase 4 — 3D Point Cloud Processing](#phase-4--3d-point-cloud-processing)
  - [Phase 5 — 6D Pose Estimation](#phase-5--6d-pose-estimation)
  - [Phase 6 — Integration & Evaluation](#phase-6--integration--evaluation)
- [Key Metrics & Results](#key-metrics--results)
- [Repository Structure](#repository-structure)
- [Setup & Installation](#setup--installation)
- [Current Limitations & Future Work](#current-limitations--future-work)
- [References](#references)

---

## Project Architecture

```
RGB-D Camera (RealSense D435)
         │
         ▼
 ┌───────────────────┐
 │  Aligned RGB+D    │  ← Depth aligned to color frame via camera intrinsics
 │  Frame Capture    │
 └────────┬──────────┘
          │
          ▼
 ┌───────────────────┐
 │  YOLOv11-seg      │  ← Per-instance pixel masks + class labels
 │  Segmentation     │
 └────────┬──────────┘
          │  (mask per object)
          ▼
 ┌───────────────────┐
 │  Point Cloud      │  ← Back-projection using camera intrinsics
 │  Extraction       │     Voxel downsampling + outlier removal
 └────────┬──────────┘
          │
          ▼
 ┌───────────────────┐
 │  FPFH Feature     │  ← Coarse global registration (RANSAC)
 │  Matching + ICP   │     Fine-grained point-to-plane ICP alignment
 └────────┬──────────┘
          │  (4×4 transformation matrix)
          ▼
 ┌───────────────────┐
 │  6D Pose Output   │  ← Translation (x, y, z) + Rotation (roll, pitch, yaw)
 │  + Gripper Cmd    │     Approach vector for gripper trajectory planning
 └───────────────────┘
```

---

## Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Depth Camera | Intel RealSense D435 | RGB-D frame acquisition |
| Segmentation | YOLOv11-seg (Ultralytics) | Per-instance pixel mask generation |
| Deep Learning | PyTorch 2.x + CUDA | Model training and inference |
| 3D Processing | Open3D 0.18 | Point cloud operations, ICP, visualization |
| Feature Matching | FPFH + RANSAC | Coarse pose initialization |
| Fine Alignment | Point-to-Plane ICP | 6D pose refinement |
| Annotation | LabelMe | Polygon-level instance annotation |
| Experiment Tracking | Weights & Biases | Training metrics and run comparison |
| Language | Python 3.12 | End-to-end implementation |

---

## Development Roadmap

The project is organized into six sequential phases. Each phase has defined deliverables and completion criteria. Status indicators reflect current progress.

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Environment Setup | ✅ Complete |
| 2 | Data Collection & Annotation | 🔄 In Progress |
| 3 | 2D Instance Segmentation | 🔄 In Progress |
| 4 | 3D Point Cloud Processing | ⏳ Planned |
| 5 | 6D Pose Estimation | ⏳ Planned |
| 6 | Integration & Evaluation | ⏳ Planned |

---

### Phase 1 — Environment Setup
**Status: ✅ Complete**

Established the full development environment including GPU-accelerated PyTorch, Intel RealSense SDK, Open3D for point cloud processing, and all supporting libraries. Verified end-to-end import chain and CUDA availability.

**Deliverables completed:**
- Python 3.12 virtual environment with pinned dependencies (`requirements.txt`)
- CUDA 11.8 + cuDNN installation and verification
- Intel RealSense SDK (`pyrealsense2`) configured and camera handshake verified
- Repository structure scaffolded with separation of raw data, processed data, models, source, and results
- `test_env.py` — environment validation script confirming all imports and GPU access

**Key decisions:**
- Using Python virtual environments (not Conda) for portability across lab machines
- Pinning Open3D to 0.18.x due to API stability considerations for ICP pipelines
- YOLOv11 via Ultralytics unified API to simplify the train/eval/export workflow

---

### Phase 2 — Data Collection & Annotation
**Status: 🔄 In Progress**

Building a custom RGB-D dataset of common household objects using the Intel RealSense D435. The dataset prioritizes **within-class pose diversity** — each object is captured from multiple angles, positions, and lighting conditions to ensure the model generalizes to unseen orientations.

**Target object classes:** `mug`, `pen`, `box`, `stapler`, `spray_bottle`

**Dataset targets:**
- 300–500 RGB-D frame pairs (aligned color + depth)
- Minimum 60 frames per object class
- Coverage: 4+ orientations, 3 lighting conditions, varied table positions

**Deliverables completed:**
- `src/capture.py` — RealSense acquisition script with depth alignment, frame timestamping, and depth scale export
- `src/annotate_helper.py` — LabelMe-to-YOLO-segmentation format converter with automatic train/val split (80/20)
- `data/processed/dataset.yaml` — YOLO dataset configuration file

**In progress:**
- Completing polygon-level annotation of 300 collected frames in LabelMe
- Verifying annotation consistency (class name normalization, minimum polygon vertex count)
- Generating depth colormap visualizations for sanity-checking alignment quality

**Annotation approach:** Polygon segmentation (not bounding boxes) using LabelMe. Each annotated polygon traces the exact visible silhouette of the object instance, enabling precise mask supervision during training.

**Known challenges:**
- Transparent objects (glass) produce invalid depth readings — excluded from dataset
- RealSense minimum depth range (~20 cm) constrains table setup distance
- Requires USB 3.0 connection; USB 2.0 produces corrupted depth streams

---

### Phase 3 — 2D Instance Segmentation
**Status: 🔄 In Progress**

Training a YOLOv11 instance segmentation model on the custom dataset. The model produces per-instance binary masks and class labels, which downstream modules use to isolate individual object point clouds from the full scene depth map.

**Model variants under evaluation:**

| Variant | Parameters | Target Latency | Target mAP50 |
|---------|-----------|---------------|--------------|
| YOLOv11-nano | ~2.9M | < 10 ms | > 0.72 |
| YOLOv11-small | ~9.4M | < 25 ms | > 0.80 |
| YOLOv11-medium | ~20.1M | < 50 ms | > 0.85 |

**Deliverables completed:**
- `src/train_segmentation.py` — full training script with augmentation config, early stopping, W&B logging, and automatic best-weight export
- Training run initialized on YOLOv11-nano for baseline benchmarking

**In progress:**
- Running full training sweep across nano/small/medium variants
- Generating per-class mAP breakdown to identify underperforming object categories
- Confusion matrix analysis for class-level annotation quality audit

**Evaluation criteria:**
- Primary: **mAP50** (segmentation, IoU threshold = 0.5) ≥ 0.80
- Secondary: **mAP50-95** ≥ 0.55
- Latency: mean inference < 30 ms on RTX 2070 (target real-time at 30 fps)

**Training configuration:**
```
Optimizer:     AdamW
LR:            1e-3 (cosine decay)
Epochs:        100 (early stopping, patience=30)
Image size:    640×640
Augmentation:  HSV jitter, horizontal flip, mosaic, ±10° rotation
```

---

### Phase 4 — 3D Point Cloud Processing
**Status: ⏳ Planned**

Converting segmented RGB-D regions into clean 3D point clouds for use in pose estimation. This phase bridges the 2D segmentation output and the 3D pose estimation pipeline by implementing the standard back-projection pipeline and Open3D-based preprocessing.

**Planned deliverables:**
- `src/pose_estimation.py: RGBDProcessor` — class implementing:
  - Intrinsic-based back-projection (depth → XYZ)
  - Masked point cloud extraction (object region only, via segmentation mask)
  - Voxel downsampling (target voxel size: 2 mm)
  - Statistical outlier removal (k=20 neighbors, 2σ threshold)
  - Surface normal estimation for ICP compatibility
- Template capture workflow — protocol for recording canonical object point clouds in known poses
- `data/templates/` — one `.pcd` template file per object class

**Key technical decisions (planned):**
- Voxel size of 2 mm selected to balance point density with ICP speed at object scales of 5–20 cm
- Normal estimation uses a 1 cm hybrid search radius (radius + k-NN) as recommended by Open3D for downstream ICP stability
- Templates will be captured with the object flat on a contrasting surface to minimize background contamination

**Dependencies:** Phase 3 complete (segmentation masks required as input)

---

### Phase 5 — 6D Pose Estimation
**Status: ⏳ Planned**

Estimating the full 6 degrees-of-freedom pose (3D position + 3D orientation) of each detected object by aligning its observed point cloud to a pre-captured template using FPFH feature matching followed by ICP refinement.

**Planned deliverables:**
- `src/pose_estimation.py: PoseEstimator` — class implementing:
  - FPFH (Fast Point Feature Histograms) feature extraction
  - RANSAC-based coarse global registration
  - Point-to-Plane ICP fine alignment
  - Euler angle decomposition (ZYX convention) from 4×4 transformation matrix
  - `compute_add_metric()` — ADD (Average Distance of Model Points) scorer
- `_compute_gripper_command()` — converts 6D pose to approach vector + grasp position for downstream robot controller integration

**Pose representation:**

The output transformation matrix **T** encodes full 6D pose:

```
T = | R₁₁  R₁₂  R₁₃ | tx |
    | R₂₁  R₂₂  R₂₃ | ty |
    | R₃₁  R₃₂  R₃₃ | tz |
    |  0    0    0   |  1 |
```

Where **R** (3×3) is the rotation matrix and **t** (3×1) is the translation vector in camera coordinates.

**Evaluation metric — ADD (Average Distance of Model Points):**

A pose estimate is considered correct if:

```
ADD = mean‖ T_pred · p_i − T_gt · p_i ‖₂  <  0.1 × diameter(object)
```

Industry-standard target: **> 70% of poses correct** under the 10% diameter threshold.

**Known challenges (anticipated):**
- ICP is sensitive to initialization quality; FPFH coarse alignment is critical for textureless objects
- Symmetric objects (e.g., cylindrical bottles) require special handling — standard ADD replaced by ADD-S (closest-point variant)
- Occlusion beyond 50% causes template matching to degrade significantly

**Dependencies:** Phase 4 complete (preprocessed object point clouds required)

---

### Phase 6 — Integration & Evaluation
**Status: ⏳ Planned**

Assembling all pipeline components into a unified real-time system, conducting systematic benchmarking across model variants, and producing the final evaluation report and visualizations.

**Planned deliverables:**
- `src/pipeline.py: RoboticSortingPipeline` — end-to-end inference class combining camera acquisition, segmentation, point cloud extraction, and pose estimation into a single `process_frame()` call
- `src/evaluate.py: ProjectEvaluator` — benchmarking suite implementing:
  - Inference latency profiling (mean, median, P5, P95 across 100 trials)
  - Per-model mAP evaluation on held-out test set
  - 6D pose accuracy (rotation error °, translation error mm, ADD score)
  - Latency vs. accuracy trade-off chart across YOLOv11 model variants
- `results/report.md` — auto-generated evaluation summary
- Live demo script with real-time visualization overlay

**Target system performance:**

| Metric | Target |
|--------|--------|
| End-to-end latency | < 100 ms (≥ 10 fps) |
| Segmentation mAP50 | ≥ 0.80 |
| Pose rotation error | < 10° mean |
| Pose translation error | < 10 mm mean |
| ADD correct (< 10% diam.) | ≥ 70% |

**Planned experiments:**
1. Latency vs. accuracy sweep across YOLOv11-nano / small / medium
2. Pose accuracy vs. occlusion level (0%, 25%, 50%)
3. Per-class failure mode analysis
4. Ablation: FPFH+ICP vs. ICP-only (to quantify coarse alignment contribution)

---

## Key Metrics & Results

*This section will be populated as phases complete. Placeholder targets shown.*

### Segmentation (YOLOv11-small, preliminary)

| Metric | Value |
|--------|-------|
| mAP50 | — |
| mAP50-95 | — |
| Mean Precision | — |
| Mean Recall | — |
| Inference latency (ms) | — |

### 6D Pose Estimation

| Metric | Value |
|--------|-------|
| Mean rotation error (°) | — |
| Mean translation error (mm) | — |
| % poses correct (ADD < 10% diam.) | — |
| ICP mean fitness score | — |

> Results will be updated as Phase 3 training and Phase 6 evaluation complete.

---

## Repository Structure

```
robotsort/
├── data/
│   ├── raw/                        # Timestamped RGB-D frame pairs from RealSense
│   │   ├── rgb/                    # PNG color images
│   │   ├── depth/                  # NPY depth arrays (uint16, raw units)
│   │   ├── depth_colormap/         # JET-colorized depth maps (visualization only)
│   │   └── depth_scale.txt         # Depth scale factor (meters per unit)
│   ├── annotations/                # LabelMe JSON polygon annotations
│   ├── processed/                  # YOLO-format dataset (auto-generated)
│   │   ├── images/train/
│   │   ├── images/val/
│   │   ├── labels/train/
│   │   ├── labels/val/
│   │   └── dataset.yaml
│   └── templates/                  # Per-class canonical point clouds (.pcd)
│
├── models/
│   ├── segmentation/               # YOLOv11 training runs (Ultralytics output)
│   │   └── run1/weights/best.pt
│   └── pose/                       # Reserved for future neural pose models
│
├── src/
│   ├── capture.py                  # RealSense RGB-D acquisition script
│   ├── annotate_helper.py          # LabelMe → YOLO format converter + train/val split
│   ├── train_segmentation.py       # YOLOv11 training, validation, and inference demo
│   ├── pose_estimation.py          # RGBDProcessor + PoseEstimator classes
│   ├── pipeline.py                 # End-to-end RoboticSortingPipeline class
│   └── evaluate.py                 # Benchmarking, metrics, and chart generation
│
├── notebooks/
│   └── exploration.ipynb           # EDA, annotation review, result visualization
│
├── results/
│   ├── metrics/                    # JSON metric dumps per evaluation run
│   ├── latency_vs_accuracy.png     # Trade-off chart across model variants
│   └── report.md                   # Auto-generated evaluation summary
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Setup & Installation

### Prerequisites

- Python 3.12
- NVIDIA GPU with CUDA 11.8+ (strongly recommended; CPU-only is supported but slow)
- Intel RealSense D435 camera + USB 3.0 connection
- [Intel RealSense SDK 2.0](https://github.com/IntelRealSense/librealsense) installed at the system level

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/robotsort.git
cd robotsort

# Create and activate virtual environment
python -m venv robotsort_env
source robotsort_env/bin/activate        # Linux/Mac
# robotsort_env\Scripts\activate         # Windows

# Install PyTorch (adjust CUDA version as needed — see pytorch.org)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install all remaining dependencies
pip install -r requirements.txt

# Verify the environment
python src/test_env.py
```

### Quick Start

```bash
# 1. Capture RGB-D data
python src/capture.py

# 2. Annotate images in LabelMe, then convert to YOLO format
python src/annotate_helper.py

# 3. Train segmentation model
python src/train_segmentation.py

# 4. Run the live pipeline (requires trained model + pose templates)
python src/pipeline.py
```

---

## Current Limitations & Future Work

### Current Limitations

- **ICP initialization sensitivity:** The FPFH + RANSAC coarse alignment can fail on textureless or highly symmetric objects without sufficient geometric features.
- **Single-object occlusion:** The current pipeline degrades when objects are stacked or heavily occluded (> 50% masked).
- **Static templates:** Pose estimation relies on pre-captured point cloud templates, which must be re-captured if lighting or camera setup changes significantly.
- **No robot arm integration:** The gripper command output is currently a data structure; actual motor control requires ROS 2 integration (see below).

### Planned Extensions

- **Neural pose estimation:** Replace ICP with a learned approach (e.g., FoundPose, GDRNet, or FFB6D) for improved robustness on textureless surfaces and symmetric objects.
- **ROS 2 integration:** Publish 6D pose estimates as `geometry_msgs/PoseStamped` topics, enabling direct compatibility with MoveIt 2 motion planning.
- **Stereo depth fallback:** Evaluate software-based stereo depth (SGBM or RAFT-Stereo) as a lower-cost alternative to the RealSense for deployment.
- **Online template-free pose:** Explore zero-shot methods (FoundationPose, GenPose) that do not require per-object template capture.
- **Multi-object grasping:** Extend pipeline to plan sequential pick-and-place for multiple objects with collision-aware ordering.

---

## References

1. Wang, C. et al. (2019). *DenseFusion: 6D Object Pose Estimation by Iterative Dense Fusion.* CVPR.
2. Wohlhart, P. & Lepetit, V. (2015). *Learning Descriptors for Object Recognition and 3D Pose Estimation.* CVPR.
3. Zhou, Q. & Koltun, V. (2014). *Color Map Optimization for 3D Reconstruction with Consumer Depth Cameras.* SIGGRAPH.
4. Ultralytics. (2024). *YOLOv11: Real-Time Object Detection and Segmentation.* [ultralytics.com](https://ultralytics.com)
5. Zhou, Q., Park, J., & Koltun, V. (2018). *Open3D: A Modern Library for 3D Data Processing.* arXiv:1801.09847.
6. Rusinkiewicz, S. & Levoy, M. (2001). *Efficient Variants of the ICP Algorithm.* 3DIM.
7. Rusu, R.B. et al. (2009). *Fast Point Feature Histograms (FPFH) for 3D Registration.* ICRA.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <i>Actively developed · Last updated April 2026</i>
</p>