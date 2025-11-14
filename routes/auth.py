from flask import Blueprint, request, jsonify
from services.supabase_client import supabase_client
from utils.validators import validate_email, validate_password, validate_required_fields
import jwt
from datetime import datetime, timedelta
from config.settings import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (teacher or student)"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['email', 'password', 'full_name', 'role']
        is_valid, missing = validate_required_fields(data, required)
        if not is_valid:
            return jsonify({'error': f'Missing fields: {missing}'}), 400
        
        # Validate email
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, msg = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': msg}), 400
        
        # Validate role
        if data['role'] not in ['teacher', 'student']:
            return jsonify({'error': 'Role must be teacher or student'}), 400
        
        # Create user in Supabase Auth
        auth_response = supabase_client.auth.sign_up({
            'email': data['email'],
            'password': data['password']
        })
        
        if not auth_response.user:
            return jsonify({'error': 'User registration failed'}), 400
        
        user_id = auth_response.user.id
        
        # Create user profile
        profile_data = {
            'user_id': user_id,
            'email': data['email'],
            'full_name': data['full_name'],
            'role': data['role'],
            'department': data.get('department', '')
        }
        
        supabase_client.table('user_profiles').insert(profile_data).execute()
        
        # Create role-specific entry
        if data['role'] == 'teacher':
            if 'employee_id' not in data:
                return jsonify({'error': 'employee_id required for teachers'}), 400
            
            teacher_data = {
                'teacher_id': user_id,
                'employee_id': data['employee_id'],
                'designation': data.get('designation', '')
            }
            supabase_client.table('teachers').insert(teacher_data).execute()
        
        elif data['role'] == 'student':
            if 'enrollment_number' not in data:
                return jsonify({'error': 'enrollment_number required for students'}), 400
            
            student_data = {
                'student_id': user_id,
                'enrollment_number': data['enrollment_number'],
                'year': data.get('year', 1),
                'section': data.get('section', '')
            }
            supabase_client.table('students').insert(student_data).execute()
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_id,
            'email': data['email'],
            'role': data['role'],
            'exp': datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
        }, Config.SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'message': f'{data["role"].capitalize()} registered successfully',
            'token': token,
            'user': {
                'user_id': user_id,
                'email': data['email'],
                'full_name': data['full_name'],
                'role': data['role']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['email', 'password']
        is_valid, missing = validate_required_fields(data, required)
        if not is_valid:
            return jsonify({'error': f'Missing fields: {missing}'}), 400
        
        # Authenticate with Supabase
        auth_response = supabase_client.auth.sign_in_with_password({
            'email': data['email'],
            'password': data['password']
        })
        
        if not auth_response.user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user_id = auth_response.user.id
        
        # Get user profile
        profile = supabase_client.table('user_profiles')\
            .select('*')\
            .eq('user_id', user_id)\
            .single()\
            .execute()
        
        if not profile.data:
            return jsonify({'error': 'User profile not found'}), 404
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_id,
            'email': profile.data['email'],
            'role': profile.data['role'],
            'exp': datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
        }, Config.SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'user_id': user_id,
                'email': profile.data['email'],
                'full_name': profile.data['full_name'],
                'role': profile.data['role'],
                'department': profile.data.get('department', '')
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 401
