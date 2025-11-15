from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import Config
from services.embeddings_loader import embeddings_loader
import os

# Create Flask app
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Import routes
from routes.auth import auth_bp
from routes.attendance import attendance_bp
from routes.students import students_bp
from routes.teachers import teachers_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
app.register_blueprint(students_bp, url_prefix='/api/students')
app.register_blueprint(teachers_bp, url_prefix='/api/teachers')

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Attendance Backend API is running',
        'embeddings_loaded': embeddings_loader.loaded
    }), 200

# Load embeddings on startup
print("🚀 Starting Attendance Backend API...")
print(f"📍 Environment: {Config.FLASK_ENV}")
embeddings_loader.load_embeddings_database()
print("✅ Backend ready!")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=Config.FLASK_ENV=='development')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
