import requests

API_URL = 'http://localhost:5000/api/auth/register'

students = [
    "Abhi",
    "Chiranthan",
    "Divya",
    "Manu",
    "Nandiswar",
    "Sakshitha",
    "Sanjana",
    "Varshini"
]

print("Registering students...")
print("="*50)

student_ids = {}

for i, name in enumerate(students, start=1):
    data = {
        "email": f"{name.lower()}@student.com",
        "password": "pass123",
        "full_name": name,
        "role": "student",
        "enrollment_number": f"2023CS{i:03d}",
        "department": "Computer Science",
        "year": 2,
        "section": "A"
    }
    
    try:
        response = requests.post(API_URL, json=data)
        
        if response.status_code == 201:
            result = response.json()
            student_id = result['user']['user_id']
            student_ids[name] = student_id
            print(f"✅ {name:15} | {student_id}")
        else:
            print(f"❌ {name:15} | Error: {response.text[:50]}")
    except Exception as e:
        print(f"❌ {name:15} | Error: {e}")

print("\n" + "="*50)
print("SAVE THESE STUDENT IDs FOR NEXT STEP:")
print("="*50)
for name, sid in student_ids.items():
    print(f"(gen_random_uuid(), 'CLASS_ID', '{sid}'),  -- {name}")
