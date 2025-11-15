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
        if self.embeddings_cache is not None:
            return self.embeddings_cache

        try:
            print(f"📥 Downloading {Config.EMBEDDINGS_FILE} from Supabase Storage...")

            data = supabase_client.storage.from_(Config.EMBEDDINGS_BUCKET)\
                .download(Config.EMBEDDINGS_FILE)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pickle') as tmp:
                tmp.write(data)
                tmp_path = tmp.name

            with open(tmp_path, 'rb') as f:
                raw_dict = pickle.load(f)

            os.remove(tmp_path)

            # Convert list → numpy array
            self.embeddings_cache = {
                name: np.array(emb, dtype=np.float32).flatten()
                for name, emb in raw_dict.items()
            }

            print(f"✅ Loaded embeddings for {len(self.embeddings_cache)} students")
            self.loaded = True
            return self.embeddings_cache

        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            return {}

    def get_embeddings_for_class(self, class_id: str) -> Dict:
        all_embeddings = self.load_embeddings_database()

        # Get enrolled students
        enrollments = supabase_client.table("enrollments")\
            .select("student_id")\
            .eq("class_id", class_id)\
            .execute()

        student_ids = [rec["student_id"] for rec in enrollments.data]

        result = {}

        for student_id in student_ids:
            try:
                res = supabase_client.table("user_profiles")\
                    .select("full_name")\
                    .eq("user_id", student_id)\
                    .single().execute()

                name = res.data["full_name"]

                if name in all_embeddings:
                    emb = all_embeddings[name]

                    if emb.shape[0] != 128:
                        print(f"⚠️ Invalid embedding size for {name}, skipping")
                        continue

                    result[student_id] = emb
                else:
                    print(f"⚠️ No embedding for {name}")

            except Exception as e:
                print(f"⚠️ Error handling {student_id}: {e}")

        return result

embeddings_loader = EmbeddingsLoader()
