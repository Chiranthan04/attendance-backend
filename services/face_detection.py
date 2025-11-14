import onnxruntime as ort
import numpy as np
import cv2
import os
import warnings
from config.settings import Config
from services.supabase_client import supabase_client

# Suppress warnings
warnings.filterwarnings('ignore')

class FaceDetectionService:
    def __init__(self):
        # ONNX session will be created after downloading model
        self.session = None
        self.model_path = Config.YOLO_MODEL_PATH

        print(f"🔧 Loading ONNX model from {self.model_path}...")

        # Check if model exists locally
        if not os.path.exists(self.model_path):
            print(f"📥 Model not found locally. Downloading from Supabase Storage...")
            try:
                # Download from Supabase Storage
                res = supabase_client.storage.from_(Config.EMBEDDINGS_BUCKET) \
                    .download('best.onnx')

                # Create models directory if not exists
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

                # Save ONNX model
                with open(self.model_path, 'wb') as f:
                    f.write(res)

                print("✅ ONNX model downloaded successfully")
            except Exception as e:
                print(f"❌ Error downloading ONNX model: {e}")
                print("⚠️  Please manually place best.onnx in models/ folder")
                raise

        # Create ONNX Runtime session
        try:
            self.session = ort.InferenceSession(self.model_path)
            print("✅ ONNX Runtime session created successfully")
        except Exception as e:
            print(f"❌ Error creating ONNX Runtime session: {e}")
            raise

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image to match YOLO input requirements"""
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (640, 640))
        img = img.astype(np.float32) / 255.0  # normalize to [0,1]
        img = np.transpose(img, (2, 0, 1))  # HWC to CHW
        img = np.expand_dims(img, axis=0)  # batch dimension
        return img

    def postprocess(self, outputs, conf_threshold=0.25):
        """Postprocess ONNX output to boxes"""
        # Typical YOLO output format:
        # outputs[0] shape: [1, num_predictions, 85] (x,y,w,h,obj,cls probabilities)

        preds = outputs[0]
        preds = preds[0]  # remove batch dim

        boxes = []
        for pred in preds:
            conf = pred[4]
            if conf < conf_threshold:
                continue  # filter low confidence detections

            # Convert center x,y,w,h to x1,y1,x2,y2
            cx, cy, w, h = pred[:4]
            x1 = int((cx - w / 2) * Config.INPUT_WIDTH)
            y1 = int((cy - h / 2) * Config.INPUT_HEIGHT)
            x2 = int((cx + w / 2) * Config.INPUT_WIDTH)
            y2 = int((cy + h / 2) * Config.INPUT_HEIGHT)
            boxes.append([x1, y1, x2, y2])

        return np.array(boxes)

    def detect_faces(self, image: np.ndarray) -> np.ndarray:
        """Detect faces using ONNX model"""
        input_tensor = self.preprocess(image)

        # Run inference
        outputs = self.session.run(None, {"images": input_tensor})

        # Postprocess detections
        boxes = self.postprocess(outputs, conf_threshold=Config.YOLO_CONFIDENCE)
        return boxes


# Singleton instance
face_detector = FaceDetectionService()
