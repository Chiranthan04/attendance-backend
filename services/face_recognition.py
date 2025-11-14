import numpy as np
from deepface import DeepFace
from scipy.spatial.distance import cosine
from config.settings import Config
from typing import Dict, List, Set


class FaceRecognitionService:
    def __init__(self):
        self.model_name = Config.FACE_MODEL_NAME
        self.threshold = Config.SFACE_THRESHOLD
    
    def _safe_flatten(self, embedding):
        """Safely flatten embedding to 1D array"""
        if embedding is None:
            return None
        
        # Convert to numpy array and flatten
        flat = np.array(embedding, dtype=float).flatten()
        
        # Ensure it's 1D
        if len(flat.shape) != 1:
            raise ValueError(f"Failed to flatten embedding: {flat.shape}")
        
        return flat
    
    def process_attendance_image(
        self,
        image: np.ndarray,
        face_boxes: np.ndarray,
        enrolled_students_embeddings: Dict
    ) -> Dict:
        """
        Process attendance with fixed embedding handling
        
        Args:
            image: OpenCV image
            face_boxes: YOLO detected boxes [[x1,y1,x2,y2], ...]
            enrolled_students_embeddings: Dict from embeddings_loader
                Format: {'student_name': [embedding_values]}
        
        Returns:
            {
                'present_students': [...],
                'absent_students': [...],
                'total_faces_detected': int,
                'recognized_count': int,
                'unknown_faces': int
            }
        """
        total_faces_detected = len(face_boxes)
        recognized_student_ids: Set[str] = set()
        already_labeled_in_image: Set[str] = set()
        
        face_results = []
        
        for box in face_boxes:
            x1, y1, x2, y2 = box
            face_crop = image[y1:y2, x1:x2]
            
            if face_crop.size == 0:
                continue
            
            try:
                # Generate embedding for detected face
                embedding_obj = DeepFace.represent(
                    img_path=face_crop,
                    model_name=self.model_name,
                    enforce_detection=False
                )
                
                # Flatten the new embedding
                new_embedding = self._safe_flatten(embedding_obj[0]['embedding'])
                
                # Find best match among enrolled students
                min_distance = float('inf')
                predicted_student_id = None
                predicted_name = 'Unknown'
                
                for student_id, student_embedding in enrolled_students_embeddings.items():
                    try:
                        # Flatten stored embedding
                        stored_embedding = self._safe_flatten(student_embedding)
                        
                        # Check dimensions match
                        if len(new_embedding) != len(stored_embedding):
                            print(f"⚠️  Dimension mismatch for {student_id}:")
                            print(f"   New embedding: {len(new_embedding)} dims")
                            print(f"   Stored embedding: {len(stored_embedding)} dims")
                            print(f"   Type: {type(student_embedding)}")
                            continue
                        
                        # Calculate cosine distance
                        dist = cosine(new_embedding, stored_embedding)
                        
                        if dist < min_distance:
                            min_distance = dist
                            predicted_student_id = student_id
                            predicted_name = student_id  # Using student_id as name
                    
                    except Exception as e:
                        print(f"⚠️  Error comparing with {student_id}: {e}")
                        continue
                
                # Apply threshold and duplicate check
                if min_distance < self.threshold:
                    if predicted_student_id not in already_labeled_in_image:
                        recognized_student_ids.add(predicted_student_id)
                        already_labeled_in_image.add(predicted_student_id)
                        
                        face_results.append({
                            'student_id': predicted_student_id,
                            'name': predicted_name,
                            'confidence': round((1 - min_distance) * 100, 2),
                            'distance': round(min_distance, 3),
                            'bbox': [int(x1), int(y1), int(x2), int(y2)]
                        })
                
            except Exception as e:
                print(f"⚠️  Error processing face: {e}")
                continue
        
        # Identify absent students
        all_enrolled_ids = set(enrolled_students_embeddings.keys())
        absent_student_ids = all_enrolled_ids - recognized_student_ids
        
        absent_students = [
            {
                'student_id': sid,
                'name': sid  # Using student_id as name
            }
            for sid in absent_student_ids
        ]
        
        return {
            'present_students': face_results,
            'absent_students': absent_students,
            'total_faces_detected': total_faces_detected,
            'recognized_count': len(recognized_student_ids),
            'unknown_faces': total_faces_detected - len(recognized_student_ids),
            'processing_details': {
                'model': self.model_name,
                'threshold': self.threshold,
                'total_enrolled': len(all_enrolled_ids)
            }
        }


# Singleton instance
face_recognizer = FaceRecognitionService()
