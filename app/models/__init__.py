from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.base import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin' or 'parent'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent_profile = db.relationship('Parent', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Parent(db.Model):
    __tablename__ = 'parents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    father_name = db.Column(db.String(100))
    mother_name = db.Column(db.String(100))
    primary_phone = db.Column(db.String(20), nullable=False)
    secondary_phone = db.Column(db.String(20))
    occupation = db.Column(db.String(100))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to students
    students = db.relationship('Student', backref='parent', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "father_name": self.father_name,
            "mother_name": self.mother_name,
            "primary_phone": self.primary_phone,
            "secondary_phone": self.secondary_phone,
            "occupation": self.occupation,
            "address": self.address,
            "email": self.user.email if self.user else None,
            "username": self.user.username if self.user else None
        }


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id', ondelete='RESTRICT'), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    register_number = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10))
    department = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(50), nullable=False)
    current_year = db.Column(db.Integer, nullable=False)
    current_semester = db.Column(db.Integer, nullable=False)
    batch = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(10), default='A')
    mentor_name = db.Column(db.String(100))
    mentor_contact = db.Column(db.String(20))
    avatar_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    marks = db.relationship('Mark', backref='student', cascade="all, delete-orphan")
    attendances = db.relationship('Attendance', backref='student', cascade="all, delete-orphan")
    activities = db.relationship('Activity', backref='student', cascade="all, delete-orphan")
    internships = db.relationship('Internship', backref='student', cascade="all, delete-orphan")
    submissions = db.relationship('AssignmentSubmission', backref='student', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "roll_number": self.roll_number,
            "register_number": self.register_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": f"{self.first_name} {self.last_name}",
            "dob": self.dob.strftime('%Y-%m-%d') if self.dob else None,
            "gender": self.gender,
            "department": self.department,
            "degree": self.degree,
            "current_year": self.current_year,
            "current_semester": self.current_semester,
            "batch": self.batch,
            "section": self.section,
            "mentor_name": self.mentor_name,
            "mentor_contact": self.mentor_contact,
            "avatar_url": self.avatar_url,
            "parent_name": f"{self.parent.father_name or self.parent.mother_name}" if self.parent else None,
            "parent_phone": self.parent.primary_phone if self.parent else None
        }


class Semester(db.Model):
    __tablename__ = 'semesters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    semester_number = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "academic_year": self.academic_year,
            "semester_number": self.semester_number,
            "start_date": self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            "end_date": self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            "is_current": self.is_current
        }


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(20), unique=True, nullable=False)
    subject_name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    semester_number = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, default=3)
    faculty_name = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "subject_code": self.subject_code,
            "subject_name": self.subject_name,
            "department": self.department,
            "semester_number": self.semester_number,
            "credits": self.credits,
            "faculty_name": self.faculty_name
        }


class Exam(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    exam_name = db.Column(db.String(100), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='CASCADE'), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    semester = db.relationship('Semester', backref='exams')

    def to_dict(self):
        return {
            "id": self.id,
            "exam_name": self.exam_name,
            "semester_id": self.semester_id,
            "semester_name": self.semester.name if self.semester else None,
            "exam_type": self.exam_type,
            "start_date": self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            "end_date": self.end_date.strftime('%Y-%m-%d') if self.end_date else None
        }


class Mark(db.Model):
    __tablename__ = 'marks'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)
    max_marks = db.Column(db.Float, default=100.0)
    grade = db.Column(db.String(5))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    exam = db.relationship('Exam')
    subject = db.relationship('Subject')

    def to_dict(self):
        percentage = round((self.marks_obtained / self.max_marks * 100), 1) if self.max_marks else 0
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": f"{self.student.first_name} {self.student.last_name}" if self.student else None,
            "student_roll": self.student.roll_number if self.student else None,
            "exam_id": self.exam_id,
            "exam_name": self.exam.exam_name if self.exam else None,
            "subject_id": self.subject_id,
            "subject_code": self.subject.subject_code if self.subject else None,
            "subject_name": self.subject.subject_name if self.subject else None,
            "marks_obtained": self.marks_obtained,
            "max_marks": self.max_marks,
            "percentage": percentage,
            "grade": self.grade,
            "remarks": self.remarks
        }


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)
    status = db.Column(db.String(20), nullable=False) # 'Present', 'Absent', 'On Duty', 'Leave'
    remarks = db.Column(db.String(255))

    subject = db.relationship('Subject')

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": f"{self.student.first_name} {self.student.last_name}" if self.student else None,
            "date": self.date.strftime('%Y-%m-%d') if self.date else None,
            "subject_id": self.subject_id,
            "subject_name": self.subject.subject_name if self.subject else 'Full Day',
            "status": self.status,
            "remarks": self.remarks
        }


class Timetable(db.Model):
    __tablename__ = 'timetable'

    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), nullable=False)
    semester_number = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10), default='A')
    day_of_week = db.Column(db.String(20), nullable=False)
    period_number = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    room_number = db.Column(db.String(50))

    subject = db.relationship('Subject')

    def to_dict(self):
        return {
            "id": self.id,
            "department": self.department,
            "semester_number": self.semester_number,
            "section": self.section,
            "day_of_week": self.day_of_week,
            "period_number": self.period_number,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "subject_id": self.subject_id,
            "subject_code": self.subject.subject_code if self.subject else None,
            "subject_name": self.subject.subject_name if self.subject else None,
            "faculty_name": self.subject.faculty_name if self.subject else None,
            "room_number": self.room_number
        }


class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False) # Sports, NSS, YRC, Symposium, Workshop
    title = db.Column(db.String(150), nullable=False)
    event_date = db.Column(db.Date)
    organizer = db.Column(db.String(150))
    achievement = db.Column(db.String(150))
    certificate_url = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "activity_type": self.activity_type,
            "title": self.title,
            "event_date": self.event_date.strftime('%Y-%m-%d') if self.event_date else None,
            "organizer": self.organizer,
            "achievement": self.achievement,
            "certificate_url": self.certificate_url
        }


class Internship(db.Model):
    __tablename__ = 'internships'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    stipend = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default='In Progress')
    mentor_contact = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "company_name": self.company_name,
            "role": self.role,
            "start_date": self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            "end_date": self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            "stipend": self.stipend,
            "status": self.status,
            "mentor_contact": self.mentor_contact
        }


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='General') # Academic, Exam, Holiday, Fees, Event
    target_audience = db.Column(db.String(50), default='All')
    publish_date = db.Column(db.Date, nullable=False)
    is_urgent = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "target_audience": self.target_audience,
            "publish_date": self.publish_date.strftime('%Y-%m-%d') if self.publish_date else None,
            "is_urgent": self.is_urgent
        }


class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False)
    max_marks = db.Column(db.Float, default=10.0)

    subject = db.relationship('Subject')

    def to_dict(self):
        return {
            "id": self.id,
            "subject_id": self.subject_id,
            "subject_name": self.subject.subject_name if self.subject else None,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            "max_marks": self.max_marks
        }


class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Submitted, Late, Graded
    marks_awarded = db.Column(db.Float)
    submission_date = db.Column(db.Date)
    feedback = db.Column(db.Text)

    assignment = db.relationship('Assignment')

    def to_dict(self):
        return {
            "id": self.id,
            "assignment_id": self.assignment_id,
            "assignment_title": self.assignment.title if self.assignment else None,
            "student_id": self.student_id,
            "status": self.status,
            "marks_awarded": self.marks_awarded,
            "submission_date": self.submission_date.strftime('%Y-%m-%d') if self.submission_date else None,
            "feedback": self.feedback
        }

