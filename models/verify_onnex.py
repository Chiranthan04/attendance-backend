import onnxruntime as ort
import numpy as np

# Load ONNX model
ort_session = ort.InferenceSession('best.onnx')

# Prepare dummy input with correct shape, e.g., 1x3x640x640 (batch, channels, height, width)
dummy_input = np.random.randn(1, 3, 640, 640).astype(np.float32)

# Run inference
outputs = ort_session.run(None, {'images': dummy_input})

print("ONNX inference success. Outputs:", outputs)
