from ultralytics import YOLO
from config.settings import Config
from services.supabase_client import supabase_client
import os
import warnings
import numpy as np

# Suppress warnings
warnings.filterwarnings('ignore')

class FaceDetectionService:
    def __init__(self):
        print(f"🔧 Loading YOLO model from {Config.YOLO_MODEL_PATH}...")

        # Check if model exists locally, else download from Supabase
        if not os.path.exists(Config.YOLO_MODEL_PATH):
            print(f"📥 Model not found locally. Downloading from Supabase Storage...")
            try:
                res = supabase_client.storage.from_(Config.EMBEDDINGS_BUCKET) \
                    .download('best.pt')
                os.makedirs(os.path.dirname(Config.YOLO_MODEL_PATH), exist_ok=True)
                with open(Config.YOLO_MODEL_PATH, 'wb') as f:
                    f.write(res)
                print("✅ Model downloaded successfully")
            except Exception as e:
                print(f"❌ Error downloading model: {e}")
                print("⚠️  Please manually place best.pt in models/ folder")
                raise

        # Load the YOLO PyTorch model
        try:
            self.model = YOLO(Config.YOLO_MODEL_PATH)
            print("✅ YOLO model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            raise

    def detect_faces(self, image: np.ndarray) -> np.ndarray:
        """Detect faces in an image using YOLOv12 .pt model"""
        results = self.model(image, conf=Config.YOLO_CONFIDENCE, verbose=False)
        boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
        return boxes

# Singleton instance
face_detector = FaceDetectionService()
