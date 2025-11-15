from ultralytics import YOLO
from config.settings import Config
from services.supabase_client import supabase_client
import os
import warnings
import numpy as np

warnings.filterwarnings('ignore')

class FaceDetectionService:
    def __init__(self):
        model_path = Config.YOLO_MODEL_PATH
        bucket = Config.EMBEDDINGS_BUCKET

        print(f"🔧 Checking YOLO model at: {model_path}")

        # If model doesn't exist → download from Supabase
        if not os.path.exists(model_path):
            print(f"📥 Model not found locally. Downloading from Supabase bucket '{bucket}'...")
            try:
                data = supabase_client.storage.from_(bucket).download("best.pt")

                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                with open(model_path, "wb") as f:
                    f.write(data)

                print("✅ Best.pt downloaded successfully from Supabase")
            except Exception as e:
                print(f"❌ Failed to download YOLO model: {e}")
                raise

        # Load YOLO
        try:
            self.model = YOLO(model_path)
            print("✅ YOLO model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            raise

    def detect_faces(self, image: np.ndarray) -> np.ndarray:
        """Run YOLO detection on numpy image"""
        predictions = self.model(image, conf=Config.YOLO_CONFIDENCE, verbose=False)
        boxes = predictions[0].boxes.xyxy.cpu().numpy().astype(int)
        return boxes


# Singleton instance
face_detector = FaceDetectionService()
