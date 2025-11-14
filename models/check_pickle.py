import pickle

# Load the pickle file
with open('sface_embeddings_database.pickle', 'rb') as f:
    embeddings = pickle.load(f)

print(f"Total students in pickle file: {len(embeddings)}")
print(f"\nPickle file structure type: {type(embeddings)}")

print("\n" + "="*50)
print("Student IDs/Keys and their data:")
print("="*50)

for key, value in embeddings.items():
    print(f"\nKey: {key}")
    print(f"  Value type: {type(value)}")
    
    # If value is a list (embedding vector)
    if isinstance(value, list):
        print(f"  Embedding length: {len(value)}")
        print(f"  First 5 values: {value[:5]}")
    
    # If value is a dict
    elif isinstance(value, dict):
        print(f"  Name: {value.get('name', 'N/A')}")
        print(f"  Enrollment: {value.get('enrollment_number', 'N/A')}")
        if 'embedding' in value:
            print(f"  Embedding length: {len(value['embedding'])}")
    
    # If value is something else
    else:
        print(f"  Value: {value}")

print("\n" + "="*50)
print("Summary:")
print("="*50)
print(f"Keys in file: {list(embeddings.keys())}")
