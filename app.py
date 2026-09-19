from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import time
import random

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_video_saas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)


# Simple User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }


# Simple Video Model
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    topic = db.Column(db.String(500), nullable=False)  # Increased length for detailed topics
    age_group = db.Column(db.String(50), nullable=False)  # New field for age group
    status = db.Column(db.String(20), default='pending')
    video_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'topic': self.topic,
            'age_group': self.age_group,
            'status': self.status,
            'video_url': self.video_url,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


# Simple AI Video Generator (simulating Crew AI)
class AIVideoGenerator:
    def __init__(self):
        self.age_group_configs = {
            "2-5 years": {
                "complexity": "very_simple",
                "vocabulary": "basic",
                "duration_range": (60, 120),  # 1-2 minutes
                "visual_style": "bright_colorful_cartoons",
                "pace": "slow"
            },
            "6-10 years": {
                "complexity": "simple",
                "vocabulary": "elementary",
                "duration_range": (120, 240),  # 2-4 minutes
                "visual_style": "animated_characters",
                "pace": "moderate"
            },
            "11-15 years": {
                "complexity": "intermediate",
                "vocabulary": "middle_school",
                "duration_range": (180, 360),  # 3-6 minutes
                "visual_style": "detailed_animations",
                "pace": "moderate_fast"
            },
            "16+ years": {
                "complexity": "advanced",
                "vocabulary": "high_school_plus",
                "duration_range": (240, 480),  # 4-8 minutes
                "visual_style": "realistic_detailed",
                "pace": "fast"
            }
        }

    def generate_educational_video(self, topic, age_group):
        """
        Generate educational video based on topic and age group
        In real implementation, this would call your Crew AI agents
        """
        print(f"🎓 Starting educational video generation")
        print(f"📚 Topic: {topic}")
        print(f"👶 Age Group: {age_group}")

        config = self.age_group_configs.get(age_group, self.age_group_configs["6-10 years"])

        # Simulate processing time based on complexity
        base_time = 15
        complexity_multiplier = {
            "very_simple": 1.0,
            "simple": 1.2,
            "intermediate": 1.5,
            "advanced": 2.0
        }

        processing_time = int(base_time * complexity_multiplier[config["complexity"]])
        print(f"⏱️ Estimated processing time: {processing_time} seconds")
        print(f"🎨 Visual style: {config['visual_style']}")
        print(f"📖 Vocabulary level: {config['vocabulary']}")

        # Simulate the educational AI workflow
        steps = [
            f"🧠 Analyzing topic '{topic}' for {age_group}",
            f"📝 Creating {config['vocabulary']}-level script",
            f"🎨 Designing {config['visual_style']} visuals",
            f"🎵 Adding age-appropriate audio and music",
            f"🎞️ Rendering educational video at {config['pace']} pace",
            "✅ Adding interactive learning elements"
        ]

        for i, step in enumerate(steps):
            print(f"Step {i + 1}/6: {step}")
            time.sleep(processing_time / len(steps))

        # Generate duration within age-appropriate range
        duration = random.randint(*config["duration_range"])

        # Generate a mock video URL
        video_filename = f"edu_video_{int(time.time())}_{random.randint(1000, 9999)}.mp4"
        video_url = f"/videos/{video_filename}"

        print(f"✅ Educational video generation completed!")
        print(f"📹 Video URL: {video_url}")
        print(f"⏰ Duration: {duration} seconds")

        return {
            'success': True,
            'video_url': video_url,
            'duration': duration,
            'processing_time': processing_time,
            'educational_level': config['vocabulary'],
            'visual_style': config['visual_style']
        }


# Initialize AI generator
ai_generator = AIVideoGenerator()


# Routes
@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        name = data.get('name', '').strip()
        password = data.get('password', '')

        if not email or not name or not password:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already exists'}), 409

        user = User(email=email, name=name)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=user.id)

        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'access_token': access_token
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

        access_token = create_access_token(identity=user.id)

        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'access_token': access_token
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        return jsonify({
            'success': True,
            'user': user.to_dict()
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/videos/generate', methods=['POST'])
@jwt_required()
def generate_video():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        title = data.get('title', '').strip()
        topic = data.get('topic', '').strip()
        age_group = data.get('ageGroup', '6-10 years')  # Note: frontend sends 'ageGroup'

        if not title or not topic:
            return jsonify({'success': False, 'message': 'Title and topic are required'}), 400

        # Create video record
        video = Video(
            user_id=user_id,
            title=title,
            topic=topic,
            age_group=age_group,
            status='processing'
        )

        db.session.add(video)
        db.session.commit()

        # Start AI generation (in real app, this would be async)
        try:
            result = ai_generator.generate_educational_video(topic, age_group)

            if result['success']:
                video.status = 'completed'
                video.video_url = result['video_url']
                video.completed_at = datetime.utcnow()
            else:
                video.status = 'failed'

            db.session.commit()

            return jsonify({
                'success': True,
                'video': video.to_dict(),
                'message': f'Educational video for {age_group} created successfully!',
                'generation_details': {
                    'duration': result.get('duration'),
                    'educational_level': result.get('educational_level'),
                    'visual_style': result.get('visual_style')
                }
            })

        except Exception as e:
            video.status = 'failed'
            db.session.commit()
            return jsonify({'success': False, 'message': f'Generation failed: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/videos', methods=['GET'])
@jwt_required()
def get_user_videos():
    try:
        user_id = get_jwt_identity()
        videos = Video.query.filter_by(user_id=user_id).order_by(Video.created_at.desc()).all()

        return jsonify({
            'success': True,
            'videos': [video.to_dict() for video in videos]
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/videos/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video(video_id):
    try:
        user_id = get_jwt_identity()
        video = Video.query.filter_by(id=video_id, user_id=user_id).first()

        if not video:
            return jsonify({'success': False, 'message': 'Video not found'}), 404

        return jsonify({
            'success': True,
            'video': video.to_dict()
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# Serve static files (for the React frontend)
@app.route('/')
def serve_frontend():
    return send_from_directory('frontend/build', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend/build', path)


# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("🚀 Starting AI Video Generator SaaS...")
    print("📱 Frontend will be available at: http://localhost:5000")
    print("🔗 API endpoints available at: http://localhost:5000/auth/* and /videos/*")
    app.run(debug=True, host='0.0.0.0', port=5000)
