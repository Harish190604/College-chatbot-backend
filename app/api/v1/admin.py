from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
from app.models import (
    User, Parent, Student, Semester, Subject, Exam, Mark,
    Attendance, Timetable, Activity, Internship, Announcement
)
from app.database.base import db

admin_bp = Blueprint('admin', __name__)

def check_admin():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return False
    return True

# --- DASHBOARD STATS ---
@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    if not check_admin():
        return jsonify({"success": False, "message": "Admin privileges required"}), 403

    total_students = Student.query.count()
    total_parents = Parent.query.count()
    total_subjects = Subject.query.count()
    total_exams = Exam.query.count()
    total_announcements = Announcement.query.count()

    # Calculate average attendance
    attendances = Attendance.query.all()
    present_count = sum(1 for a in attendances if a.status in ['Present', 'On Duty'])
    avg_attendance = round((present_count / len(attendances) * 100), 1) if attendances else 0

    return jsonify({
        "success": True,
        "stats": {
            "total_students": total_students,
            "total_parents": total_parents,
            "total_subjects": total_subjects,
            "total_exams": total_exams,
            "total_announcements": total_announcements,
            "average_attendance": avg_attendance
        }
    }), 200

# --- STUDENTS CRUD ---
@admin_bp.route('/students', methods=['GET', 'POST'])
@jwt_required()
def handle_students():
    if not check_admin():
        return jsonify({"success": False, "message": "Admin privileges required"}), 403

    if request.method == 'GET':
        students = Student.query.order_by(Student.id.desc()).all()
        return jsonify({"success": True, "students": [s.to_dict() for s in students]}), 200

    if request.method == 'POST':
        data = request.get_json() or {}
        try:
            student = Student(
                parent_id=data.get('parent_id'),
                roll_number=data.get('roll_number'),
                register_number=data.get('register_number'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                dob=datetime.strptime(data.get('dob'), '%Y-%m-%d').date() if data.get('dob') else datetime.now().date(),
                gender=data.get('gender', 'Male'),
                department=data.get('department', 'Computer Science and Engineering'),
                degree=data.get('degree', 'B.E.'),
                current_year=int(data.get('current_year', 3)),
                current_semester=int(data.get('current_semester', 6)),
                batch=data.get('batch', '2023-2027'),
                section=data.get('section', 'A'),
                mentor_name=data.get('mentor_name'),
                mentor_contact=data.get('mentor_contact'),
                avatar_url=data.get('avatar_url')
            )
            db.session.add(student)
            db.session.commit()
            return jsonify({"success": True, "message": "Student created successfully", "student": student.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 400

@admin_bp.route('/students/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def handle_student_detail(id):
    if not check_admin():
        return jsonify({"success": False, "message": "Admin privileges required"}), 403

    student = Student.query.get_or_404(id)

    if request.method == 'DELETE':
        db.session.delete(student)
        db.session.commit()
        return jsonify({"success": True, "message": "Student deleted successfully"}), 200

    if request.method == 'PUT':
        data = request.get_json() or {}
        for key in ['first_name', 'last_name', 'department', 'degree', 'current_year', 'current_semester', 'batch', 'section', 'mentor_name', 'mentor_contact', 'avatar_url', 'parent_id', 'roll_number', 'register_number']:
            if key in data:
                setattr(student, key, data[key])
        if 'dob' in data and data['dob']:
            student.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        db.session.commit()
        return jsonify({"success": True, "message": "Student updated successfully", "student": student.to_dict()}), 200

# --- PARENTS CRUD ---
@admin_bp.route('/parents', methods=['GET', 'POST'])
@jwt_required()
def handle_parents():
    if not check_admin():
        return jsonify({"success": False, "message": "Admin privileges required"}), 403

    if request.method == 'GET':
        parents = Parent.query.order_by(Parent.id.desc()).all()
        return jsonify({"success": True, "parents": [p.to_dict() for p in parents]}), 200

    if request.method == 'POST':
        data = request.get_json() or {}
        try:
            # Create user account for parent first
            user = User(
                username=data.get('username') or f"parent_{data.get('primary_phone')[-4:]}",
                email=data.get('email'),
                role='parent'
            )
            user.set_password(data.get('password', 'parent123'))
            db.session.add(user)
            db.session.flush()

            parent = Parent(
                user_id=user.id,
                father_name=data.get('father_name'),
                mother_name=data.get('mother_name'),
                primary_phone=data.get('primary_phone'),
                secondary_phone=data.get('secondary_phone'),
                occupation=data.get('occupation'),
                address=data.get('address')
            )
            db.session.add(parent)
            db.session.commit()
            return jsonify({"success": True, "message": "Parent registered successfully", "parent": parent.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 400

# --- SUBJECTS CRUD ---
@admin_bp.route('/subjects', methods=['GET', 'POST'])
@jwt_required()
def handle_subjects():
    if not check_admin():
        return jsonify({"success": False, "message": "Admin privileges required"}), 403

    if request.method == 'GET':
        subjects = Subject.query.order_by(Subject.id.desc()).all()
        return jsonify({"success": True, "subjects": [s.to_dict() for s in subjects]}), 200

    if request.method == 'POST':
        data = request.get_json() or {}
        subject = Subject(
            subject_code=data.get('subject_code'),
            subject_name=data.get('subject_name'),
            department=data.get('department'),
            semester_number=int(data.get('semester_number', 6)),
            credits=int(data.get('credits', 3)),
            faculty_name=data.get('faculty_name')
        )
        db.session.add(subject)
        db.session.commit()
        return jsonify({"success": True, "message": "Subject added", "subject": subject.to_dict()}), 201

# --- EXAMS CRUD ---
@admin_bp.route('/exams', methods=['GET', 'POST'])
@jwt_required()
def handle_exams():
    if not check_admin():
        return jsonify({"success": False, "message": "Admin privileges required"}), 403

    if request.method == 'GET':
        exams = Exam.query.order_by(Exam.id.desc()).all()
        return jsonify({"success": True, "exams": [e.to_dict() for e in exams]}), 200

    if request.method == 'POST':
        data = request.get_json() or {}
        exam = Exam(
            exam_name=data.get('exam_name'),
            semester_id=int(data.get('semester_id', 2)),
            exam_type=data.get('exam_type', 'Internal'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None
        )
        db.session.add(exam)
        db.session.commit()
        return jsonify({"success": True, "message": "Exam scheduled", "exam": exam.to_dict()}), 201

# --- MARKS CRUD ---
@admin_bp.route('/marks', methods=['GET', 'POST'])
@jwt_required()
def handle_marks():
    if not check_admin():
        return jsonify({"success": False, "message": "Admin privileges required"}), 403

    if request.method == 'GET':
        student_id = request.args.get('student_id')
        query = Mark.query
        if student_id:
            query = query.filter_by(student_id=student_id)
        marks = query.order_by(Mark.id.desc()).all()
        return jsonify({"success": True, "marks": [m.to_dict() for m in marks]}), 200

    if request.method == 'POST':
        data = request.get_json() or {}
        mark = Mark(
            student_id=int(data.get('student_id')),
            exam_id=int(data.get('exam_id')),
            subject_id=int(data.get('subject_id')),
            marks_obtained=float(data.get('marks_obtained')),
            max_marks=float(data.get('max_marks', 100)),
            grade=data.get('grade', 'A'),
            remarks=data.get('remarks')
        )
        db.session.add(mark)
        db.session.commit()
        return jsonify({"success": True, "message": "Mark recorded", "mark": mark.to_dict()}), 201

# --- ATTENDANCE CRUD ---
@admin_bp.route('/attendance', methods=['GET', 'POST'])
@jwt_required()
def handle_attendance():
    if not check_admin():
        return jsonify({"success": False, "message": "Admin privileges required"}), 403

    if request.method == 'GET':
        student_id = request.args.get('student_id')
        query = Attendance.query
        if student_id:
            query = query.filter_by(student_id=student_id)
        attendance_list = query.order_by(Attendance.date.desc()).all()
        return jsonify({"success": True, "attendance": [a.to_dict() for a in attendance_list]}), 200

    if request.method == 'POST':
        data = request.get_json() or {}
        att = Attendance(
            student_id=int(data.get('student_id')),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d').date() if data.get('date') else datetime.now().date(),
            subject_id=data.get('subject_id'),
            status=data.get('status', 'Present'),
            remarks=data.get('remarks')
        )
        db.session.add(att)
        db.session.commit()
        return jsonify({"success": True, "message": "Attendance marked", "attendance": att.to_dict()}), 201

# --- TIMETABLE CRUD ---
@admin_bp.route('/timetable', methods=['GET', 'POST'])
@jwt_required()
def handle_timetable():
    if not check_admin():
        return jsonify({"success": False, "message": "Admin privileges required"}), 403

    if request.method == 'GET':
        items = Timetable.query.all()
        return jsonify({"success": True, "timetable": [t.to_dict() for t in items]}), 200

    if request.method == 'POST':
        data = request.get_json() or {}
        t = Timetable(
            department=data.get('department'),
            semester_number=int(data.get('semester_number')),
            section=data.get('section', 'A'),
            day_of_week=data.get('day_of_week'),
            period_number=int(data.get('period_number')),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            subject_id=int(data.get('subject_id')),
            room_number=data.get('room_number')
        )
        db.session.add(t)
        db.session.commit()
        return jsonify({"success": True, "message": "Timetable period added", "timetable": t.to_dict()}), 201

# --- ANNOUNCEMENTS CRUD ---
@admin_bp.route('/announcements', methods=['GET', 'POST'])
@jwt_required()
def handle_announcements():
    if not check_admin():
        return jsonify({"success": False, "message": "Admin privileges required"}), 403

    if request.method == 'GET':
        ann = Announcement.query.order_by(Announcement.publish_date.desc()).all()
        return jsonify({"success": True, "announcements": [a.to_dict() for a in ann]}), 200

    if request.method == 'POST':
        data = request.get_json() or {}
        a = Announcement(
            title=data.get('title'),
            content=data.get('content'),
            category=data.get('category', 'General'),
            target_audience=data.get('target_audience', 'All'),
            publish_date=datetime.strptime(data.get('publish_date'), '%Y-%m-%d').date() if data.get('publish_date') else datetime.now().date(),
            is_urgent=bool(data.get('is_urgent', False))
        )
        db.session.add(a)
        db.session.commit()
        return jsonify({"success": True, "message": "Announcement published", "announcement": a.to_dict()}), 201

# --- ACTIVITIES CRUD ---
@admin_bp.route('/activities', methods=['GET', 'POST'])
@jwt_required()
def handle_activities():
    if not check_admin():
        return jsonify({"success": False, "message": "Admin privileges required"}), 403

    if request.method == 'GET':
        student_id = request.args.get('student_id')
        query = Activity.query
        if student_id:
            query = query.filter_by(student_id=student_id)
        activities = query.order_by(Activity.id.desc()).all()
        return jsonify({"success": True, "activities": [act.to_dict() for act in activities]}), 200

    if request.method == 'POST':
        data = request.get_json() or {}
        act = Activity(
            student_id=int(data.get('student_id')),
            activity_type=data.get('activity_type', 'Symposium'),
            title=data.get('title'),
            event_date=datetime.strptime(data['event_date'], '%Y-%m-%d').date() if data.get('event_date') else None,
            organizer=data.get('organizer'),
            achievement=data.get('achievement')
        )
        db.session.add(act)
        db.session.commit()
        return jsonify({"success": True, "message": "Activity recorded", "activity": act.to_dict()}), 201

# --- INTERNSHIPS CRUD ---
@admin_bp.route('/internships', methods=['GET', 'POST'])
@jwt_required()
def handle_internships():
    if not check_admin():
        return jsonify({"success": False, "message": "Admin privileges required"}), 403

    if request.method == 'GET':
        student_id = request.args.get('student_id')
        query = Internship.query
        if student_id:
            query = query.filter_by(student_id=student_id)
        internships = query.order_by(Internship.id.desc()).all()
        return jsonify({"success": True, "internships": [intern.to_dict() for intern in internships]}), 200

    if request.method == 'POST':
        data = request.get_json() or {}
        intern = Internship(
            student_id=int(data.get('student_id')),
            company_name=data.get('company_name'),
            role=data.get('role'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            stipend=float(data.get('stipend', 0.0)),
            status=data.get('status', 'In Progress'),
            mentor_contact=data.get('mentor_contact')
        )
        db.session.add(intern)
        db.session.commit()
        return jsonify({"success": True, "message": "Internship recorded", "internship": intern.to_dict()}), 201


