import pickle
import numpy as np

# Load existing pickle
with open('sface_embeddings_database.pickle', 'rb') as f:
    old_embeddings = pickle.load(f)

print("Converting embeddings to correct format...")
print("="*50)

new_embeddings = {}

for student_name, embeddings_list in old_embeddings.items():
    print(f"\nProcessing {student_name}...")
    print(f"  Number of photos: {len(embeddings_list)}")
    
    # Check if it's already in correct format
    if isinstance(embeddings_list[0], (int, float)):
        # Already flat - just copy
        new_embeddings[student_name] = embeddings_list
        print(f"  ✓ Already in correct format ({len(embeddings_list)} values)")
    else:
        # Convert list of embeddings to average
        embeddings_array = np.array(embeddings_list)
        avg_embedding = np.mean(embeddings_array, axis=0).tolist()
        new_embeddings[student_name] = avg_embedding
        
        print(f"  ✓ Averaged {len(embeddings_list)} photos into single embedding")
        print(f"  ✓ Final embedding size: {len(avg_embedding)}")

# Save corrected pickle
with open('sface_embeddings_database.pickle', 'wb') as f:
    pickle.dump(new_embeddings, f)

print("\n" + "="*50)
print("✅ Pickle file corrected!")
print(f"Total students: {len(new_embeddings)}")
print("\nVerification:")
for name, embedding in new_embeddings.items():
    print(f"  {name}: {len(embedding)} values (type: {type(embedding[0]).__name__})")
