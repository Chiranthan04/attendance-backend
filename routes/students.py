from flask import Blueprint, request, jsonify
from services.supabase_client import supabase_client
from middleware.auth_middleware import student_required

students_bp = Blueprint('students', __name__)

@students_bp.route('/attendance', methods=['GET'])
@student_required
def get_student_attendance():
    """Get student's own attendance"""
    try:
        student_id = request.user_id
        
        enrollments = supabase_client.table('enrollments')\
            .select('class_id')\
            .eq('student_id', student_id)\
            .execute()
        
        return jsonify({
            'success': True,
            'message': 'Student attendance endpoint'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
