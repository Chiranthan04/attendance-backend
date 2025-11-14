from ultralytics import YOLO
from config.settings import Config
from services.supabase_client import supabase_client
import cv2
import numpy as np
import os
import warnings

# Suppress torch warnings
warnings.filterwarnings('ignore')

class FaceDetectionService:
    def __init__(self):
        print(f"🔧 Loading YOLO model from {Config.YOLO_MODEL_PATH}...")
        
        # Check if model exists locally
        if not os.path.exists(Config.YOLO_MODEL_PATH):
            print(f"📥 Model not found locally. Downloading from Supabase Storage...")
            try:
                # Download from Supabase Storage
                res = supabase_client.storage.from_(Config.EMBEDDINGS_BUCKET)\
                    .download('best.pt')
                
                # Create models directory if it doesn't exist
                os.makedirs('models', exist_ok=True)
                
                # Save model file
                with open(Config.YOLO_MODEL_PATH, 'wb') as f:
                    f.write(res)
                
                print("✅ Model downloaded successfully")
            except Exception as e:
                print(f"❌ Error downloading model: {e}")
                print("⚠️  Please manually place best.pt in models/ folder")
                raise
        
        # Load YOLO model - simple version that works with all PyTorch versions
        try:
            # Set environment variable to allow loading custom models
            os.environ['YOLO_VERBOSE'] = 'False'
            
            # Load model with custom weights
            self.model = YOLO(Config.YOLO_MODEL_PATH)
            print("✅ YOLO model loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading YOLO model: {e}")
            print("⚠️  Trying alternative loading method...")
            
            # Alternative: Use ultralytics' safe loading
            try:
                from ultralytics import YOLO
                self.model = YOLO(Config.YOLO_MODEL_PATH, task='detect')
                print("✅ YOLO model loaded successfully (alternative method)")
            except Exception as e2:
                print(f"❌ Alternative method also failed: {e2}")
                raise
    
    def detect_faces(self, image: np.ndarray) -> np.ndarray:
        """
        Detect faces in image using YOLO
        Returns: numpy array of bounding boxes [[x1,y1,x2,y2], ...]
        """
        results = self.model(
            image,
            conf=Config.YOLO_CONFIDENCE,
            verbose=False
        )
        
        boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
        return boxes

# Singleton instance
face_detector = FaceDetectionService()
