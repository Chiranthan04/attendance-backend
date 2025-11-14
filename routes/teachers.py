from flask import Blueprint, request, jsonify
from services.supabase_client import supabase_client
from middleware.auth_middleware import teacher_required

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('/classes', methods=['GET'])
@teacher_required
def get_teacher_classes():
    """Get all classes assigned to teacher"""
    try:
        teacher_id = request.user_id
        
        classes = supabase_client.table('classes')\
            .select('*')\
            .eq('teacher_id', teacher_id)\
            .execute()
        
        return jsonify({
            'success': True,
            'classes': classes.data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
