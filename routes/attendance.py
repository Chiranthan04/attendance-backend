from flask import Blueprint, request, jsonify
from services.supabase_client import supabase_client
from services.embeddings_loader import embeddings_loader
from services.face_detection import face_detector
from services.face_recognition import face_recognizer
from middleware.auth_middleware import teacher_required
from utils.helpers import decode_base64_image, resize_image_if_needed


attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/process-image', methods=['POST'])
@teacher_required
def process_attendance():
    """Process group photo for attendance detection"""
    try:
        data = request.json
        
        if 'image' not in data or 'class_id' not in data:
            return jsonify({'error': 'image and class_id required'}), 400
        
        # Decode image
        image = decode_base64_image(data['image'])
        image = resize_image_if_needed(image, max_width=1920)
        
        # Get enrolled students with embeddings
        enrolled_embeddings = embeddings_loader.get_embeddings_for_class(data['class_id'])
        
        if not enrolled_embeddings:
            return jsonify({'error': 'No students enrolled or no embeddings found'}), 404
        
        # Fetch all student names in ONE query (efficient!)
        all_student_ids = list(enrolled_embeddings.keys())
        profiles_response = supabase_client.table('user_profiles')\
            .select('user_id, full_name')\
            .in_('user_id', all_student_ids)\
            .execute()
        
        # Create UUID -> Name mapping
        name_map = {p['user_id']: p['full_name'] for p in profiles_response.data}
        
        # Detect faces with YOLO
        face_boxes = face_detector.detect_faces(image)
        
        if len(face_boxes) == 0:
            # ALL students are absent (no faces detected)
            absent_students = [
                {
                    'student_id': sid,
                    'name': name_map.get(sid, sid)
                }
                for sid in all_student_ids
            ]
            
            return jsonify({
                'success': True,
                'warning': 'No faces detected in image',
                'present_students': [],
                'absent_students': absent_students,
                'total_faces_detected': 0,
                'recognized_count': 0,
                'unknown_faces': 0,
                'processing_details': {
                    'total_enrolled': len(all_student_ids),
                    'model': 'SFace',
                    'threshold': 0.8
                }
            }), 200
        
        # Recognize faces with SFace
        result = face_recognizer.process_attendance_image(
            image,
            face_boxes,
            enrolled_embeddings
        )
        
        # Get recognized student IDs
        recognized_ids = set([s['student_id'] for s in result.get('present_students', [])])
        
        # Calculate absent students (CRITICAL: Done here, not in face_recognizer)
        absent_student_ids = [sid for sid in all_student_ids if sid not in recognized_ids]
        
        # Add names to present students
        for student in result.get('present_students', []):
            student['name'] = name_map.get(student['student_id'], student['student_id'])
        
        # Build absent students with names
        absent_students = [
            {
                'student_id': sid,
                'name': name_map.get(sid, sid)
            }
            for sid in absent_student_ids
        ]
        
        return jsonify({
            'success': True,
            'present_students': result.get('present_students', []),
            'absent_students': absent_students,
            'total_faces_detected': result.get('total_faces_detected', len(face_boxes)),
            'recognized_count': len(recognized_ids),
            'unknown_faces': result.get('unknown_faces', 0),
            'processing_details': {
                'model': result.get('processing_details', {}).get('model', 'SFace'),
                'threshold': result.get('processing_details', {}).get('threshold', 0.8),
                'total_enrolled': len(all_student_ids)
            }
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500




@attendance_bp.route('/save', methods=['POST'])
@teacher_required
def save_attendance():
    """Save attendance record to database"""
    try:
        data = request.json
        teacher_id = request.user_id
        
        required = ['class_id', 'date', 'present_students', 'absent_students']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({'error': f'Missing fields: {missing}'}), 400
        
        record_data = {
            'class_id': data['class_id'],
            'teacher_id': teacher_id,
            'date': data['date'],
            'total_students': len(data['present_students']) + len(data['absent_students']),
            'present_count': len(data['present_students']),
            'absent_count': len(data['absent_students'])
        }
        
        record = supabase_client.table('attendance_records')\
            .insert(record_data)\
            .execute()
        
        record_id = record.data[0]['record_id']
        
        attendance_entries = []
        
        for student_id in data['present_students']:
            attendance_entries.append({
                'record_id': record_id,
                'student_id': student_id,
                'status': 'present',
                'marked_by_ai': not data.get('manually_edited', False),
                'manually_edited': data.get('manually_edited', False)
            })
        
        for student_id in data['absent_students']:
            attendance_entries.append({
                'record_id': record_id,
                'student_id': student_id,
                'status': 'absent',
                'marked_by_ai': not data.get('manually_edited', False),
                'manually_edited': data.get('manually_edited', False)
            })
        
        supabase_client.table('student_attendance').insert(attendance_entries).execute()
        
        return jsonify({
            'success': True,
            'message': 'Attendance saved successfully',
            'record_id': record_id
        }), 201
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
