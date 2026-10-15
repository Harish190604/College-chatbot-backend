from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import Parent, Student
from app.chatbot.engine import ChatbotEngine

chatbot_bp = Blueprint('chatbot', __name__)
engine = ChatbotEngine()

@chatbot_bp.route('/message', methods=['POST'])
@jwt_required()
def send_message():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get('role')

    data = request.get_json() or {}
    message_text = data.get('message', '').strip()
    student_id = data.get('student_id')

    if not message_text:
        return jsonify({"success": False, "message": "Message text is required"}), 400

    parent_id = None
    if role == 'parent':
        parent = Parent.query.filter_by(user_id=user_id).first()
        if parent:
            parent_id = parent.id

    result = engine.process_query(
        user_message=message_text,
        parent_id=parent_id,
        selected_student_id=student_id
    )

    return jsonify({
        "success": True,
        "reply": result["reply"],
        "intent": result["intent"],
        "data": result["data"],
        "suggestions": result.get("suggestions", [])
    }), 200

@chatbot_bp.route('/quick-prompts', methods=['GET'])
def get_quick_prompts():
    prompts = [
        {"id": "attendance", "label": "📊 Attendance Summary", "query": "What is my child's current attendance percentage?"},
        {"id": "marks", "label": "📈 Exam Marks & Grades", "query": "Show the recent exam marks and internal assessment scores"},
        {"id": "timetable", "label": "📅 Today's Schedule", "query": "What is today's class timetable?"},
        {"id": "exams", "label": "📝 Upcoming Exams", "query": "When are the upcoming examinations and dates?"},
        {"id": "mentor", "label": "👨‍🏫 Class Mentor Details", "query": "Who is my child's faculty mentor and contact number?"},
        {"id": "activities", "label": "🏆 Extracurriculars", "query": "Tell me about child's co-curricular achievements and sports"}
    ]
    return jsonify({"success": True, "prompts": prompts}), 200

