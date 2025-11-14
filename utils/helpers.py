import cv2
import numpy as np
import base64
from PIL import Image
import io

def decode_base64_image(base64_string: str) -> np.ndarray:
    """Convert base64 string to OpenCV image"""
    try:
        # Remove header if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode
        img_bytes = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(img_bytes))
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        return img_cv
    except Exception as e:
        raise ValueError(f"Invalid image data: {e}")

def encode_image_to_base64(image: np.ndarray) -> str:
    """Convert OpenCV image to base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"

def resize_image_if_needed(image: np.ndarray, max_width: int = 1920) -> np.ndarray:
    """Resize image if too large"""
    height, width = image.shape[:2]
    if width > max_width:
        ratio = max_width / width
        new_height = int(height * ratio)
        image = cv2.resize(image, (max_width, new_height))
    return image
