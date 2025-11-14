import pickle
import tempfile
import os
import numpy as np
from typing import Dict, List
from services.supabase_client import supabase_client
from config.settings import Config


class EmbeddingsLoader:
    def __init__(self):
        self.embeddings_cache = None
        self.loaded = False
    
    def load_embeddings_database(self) -> Dict[str, List]:
        """
        Download and load pickle file from Supabase Storage
        Returns dict: {"Student Name": [128 floats], ...}
        """
        if self.embeddings_cache is not None:
            return self.embeddings_cache
        
        try:
            print(f"📥 Downloading {Config.EMBEDDINGS_FILE} from Supabase Storage...")
            
            # Download pickle file
            res = supabase_client.storage.from_(Config.EMBEDDINGS_BUCKET)\
                .download(Config.EMBEDDINGS_FILE)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pickle') as tmp_file:
                tmp_file.write(res)
                tmp_path = tmp_file.name
            
            # Load pickle
            with open(tmp_path, 'rb') as f:
                self.embeddings_cache = pickle.load(f)
            
            # Cleanup
            os.remove(tmp_path)
            
            print(f"✅ Loaded embeddings for {len(self.embeddings_cache)} students")
            self.loaded = True
            return self.embeddings_cache
            
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            return {}
    
    def get_embeddings_for_class(self, class_id: str) -> Dict:
        """
        Get embeddings for all students enrolled in a class
        
        Returns dict:
        {
            "student-uuid-1": numpy_array_128_dim,
            "student-uuid-2": numpy_array_128_dim,
            ...
        }
        """
        all_embeddings = self.load_embeddings_database()
        
        # Get enrolled students from Supabase
        enrollments = supabase_client.table('enrollments')\
            .select('student_id')\
            .eq('class_id', class_id)\
            .execute()
        
        student_ids = [e['student_id'] for e in enrollments.data]
        
        # Get student details and map to embeddings
        result = {}
        for student_id in student_ids:
            try:
                profile = supabase_client.table('user_profiles')\
                    .select('full_name')\
                    .eq('user_id', student_id)\
                    .single()\
                    .execute()
                
                student_name = profile.data['full_name']
                
                # Match with pickle file (keys are student names)
                if student_name in all_embeddings:
                    embedding = all_embeddings[student_name]
                    
                    # Convert to flat numpy array (CRITICAL FIX)
                    embedding_array = np.array(embedding, dtype=np.float32).flatten()
                    
                    # Verify correct shape
                    if embedding_array.shape[0] != 128:
                        print(f"⚠️  {student_name} has embedding size {embedding_array.shape[0]}, expected 128")
                        continue
                    
                    # Store UUID -> flat numpy array (not dict!)
                    result[student_id] = embedding_array
                else:
                    print(f"⚠️  No embeddings found for {student_name}")
            
            except Exception as e:
                print(f"⚠️  Error processing student {student_id}: {e}")
                continue
        
        return result


# Singleton instance
embeddings_loader = EmbeddingsLoader()
