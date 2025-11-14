from ultralytics import YOLO

# Load your custom trained YOLOv12 model
model = YOLO('best.pt')

# Export model to ONNX format
model.export(format='onnx')  # Saves best.onnx by default
