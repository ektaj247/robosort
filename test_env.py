import torch
import cv2
import open3d as o3d
import pyrealsense2 as rs
from ultralytics import YOLO

print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"OpenCV: {cv2.__version__}")
print(f"Open3D: {o3d.__version__}")
print(f"PyRealsense2: {rs.__version__}")
print(f"YOLO: {YOLO.__version__}")
print("All imports successful!")