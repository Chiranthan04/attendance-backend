import numpy as np
from ultralytics import YOLO
import os


class YOLODetector:
    def __init__(self):
        model_path = os.getenv('YOLO_MODEL_PATH', 'models/best.pt')
        confidence = float(os.getenv('YOLO_CONFIDENCE', 0.2))
        
        try:
            print(f"🔧 Loading YOLO model from {model_path}...")
            self.model = YOLO(model_path)
            self.confidence = confidence
            print("✅ YOLO model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading YOLO: {e}")
            self.model = None
    
    def detect_faces(self, image):
        """
        Detect faces in image using YOLO
        
        Args:
            image: OpenCV image (numpy array)
        
        Returns:
            numpy array of boxes [[x1, y1, x2, y2], ...]
        """
        if self.model is None:
            return np.array([])
        
        try:
            results = self.model(image, conf=self.confidence, verbose=False)
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            return boxes
        except Exception as e:
            print(f"❌ YOLO detection error: {e}")
            return np.array([])


yolo_detector = YOLODetector()
