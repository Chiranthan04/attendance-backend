import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    INPUT_WIDTH = 640
    INPUT_HEIGHT = 640
    # Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Models
    YOLO_MODEL_PATH = os.getenv('YOLO_MODEL_PATH', 'models/best.pt')  # ONNX model path default
    SFACE_THRESHOLD = float(os.getenv('SFACE_THRESHOLD', 0.8))
    YOLO_CONFIDENCE = float(os.getenv('YOLO_CONFIDENCE', 0.2))
    FACE_MODEL_NAME = 'SFace'
    
    # Storage
    EMBEDDINGS_BUCKET = os.getenv('EMBEDDINGS_BUCKET', 'model-files')
    EMBEDDINGS_FILE = os.getenv('EMBEDDINGS_FILE', 'sface_embeddings_database.pickle')
    ATTENDANCE_PHOTOS_BUCKET = os.getenv('ATTENDANCE_PHOTOS_BUCKET', 'attendance-photos')
    
    # JWT
    JWT_EXPIRATION_HOURS = 24
    
    # Validation
    MAX_IMAGE_SIZE_MB = 10
    MIN_FACE_SIZE_PX = 20
