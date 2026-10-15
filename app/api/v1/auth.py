from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User, Parent, Student
from app.database.base import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username_or_email = data.get('username') or data.get('email')
    password = data.get('password')
    expected_role = data.get('role') # optional enforcement: 'admin' or 'parent'

    if not username_or_email or not password:
        return jsonify({"success": False, "message": "Username/Email and password required"}), 400

    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

    if expected_role and user.role != expected_role:
        return jsonify({"success": False, "message": f"Unauthorized. This portal is for {expected_role}s only."}), 403

    # Generate token
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "username": user.username})

    # Prepare response payload
    user_info = user.to_dict()
    parent_info = None
    students_info = []

    if user.role == 'parent' and user.parent_profile:
        parent_info = user.parent_profile.to_dict()
        students_info = [s.to_dict() for s in user.parent_profile.students]

    return jsonify({
        "success": True,
        "token": token,
        "user": user_info,
        "parent": parent_info,
        "students": students_info
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    user_info = user.to_dict()
    parent_info = None
    students_info = []

    if user.role == 'parent' and user.parent_profile:
        parent_info = user.parent_profile.to_dict()
        students_info = [s.to_dict() for s in user.parent_profile.students]

    return jsonify({
        "success": True,
        "user": user_info,
        "parent": parent_info,
        "students": students_info
    }), 200

