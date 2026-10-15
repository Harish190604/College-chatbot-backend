import os
from datetime import datetime, date, timedelta
from app.app import create_app
from app.database.base import db
from app.models import (
    User, Parent, Student, Semester, Subject, Exam, Mark,
    Attendance, Timetable, Activity, Internship, Announcement,
    Assignment, AssignmentSubmission
)

app = create_app()

def seed_database():
    with app.app_context():
        # Drop and create all tables
        db.drop_all()
        db.create_all()

        print("Creating default users...")
        # 1. Admin User
        admin = User(
            username='admin',
            email='admin@karpagam.edu.in',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # 2. Parent User 1
        parent_user1 = User(
            username='parent_ramesh',
            email='ramesh.parent@gmail.com',
            role='parent'
        )
        parent_user1.set_password('parent123')
        db.session.add(parent_user1)

        # 3. Parent User 2
        parent_user2 = User(
            username='parent_priya',
            email='priya.s@gmail.com',
            role='parent'
        )
        parent_user2.set_password('parent123')
        db.session.add(parent_user2)

        db.session.flush()

        # Parents Profile
        parent1 = Parent(
            user_id=parent_user1.id,
            father_name='Ramesh Krishnan',
            mother_name='Saraswathi Ramesh',
            primary_phone='+91 98401 23456',
            secondary_phone='+91 94440 65432',
            occupation='Senior Accounts Consultant',
            address='No 42, Karpagam Nagar, Eachanari, Coimbatore - 641021'
        )
        parent2 = Parent(
            user_id=parent_user2.id,
            father_name='Sundaram K',
            mother_name='Priya Sundaram',
            primary_phone='+91 98940 77889',
            occupation='Business Executive',
            address='12, Race Course Road, Coimbatore - 641018'
        )
        db.session.add_all([parent1, parent2])
        db.session.flush()

        # Students Profile
        student1 = Student(
            parent_id=parent1.id,
            roll_number='23CS101',
            register_number='717823P101',
            first_name='Harish',
            last_name='Ramesh',
            dob=date(2004, 5, 14),
            gender='Male',
            department='Computer Science and Engineering',
            degree='B.E.',
            current_year=3,
            current_semester=6,
            batch='2023-2027',
            section='A',
            mentor_name='Dr. R. Kavitha (Associate Professor)',
            mentor_contact='+91 98422 12345',
            avatar_url='https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200'
        )
        student2 = Student(
            parent_id=parent2.id,
            roll_number='23CS145',
            register_number='717823P145',
            first_name='Ananya',
            last_name='Sundaram',
            dob=date(2004, 8, 22),
            gender='Female',
            department='Computer Science and Engineering',
            degree='B.E.',
            current_year=3,
            current_semester=6,
            batch='2023-2027',
            section='A',
            mentor_name='Prof. S. Suresh Kumar',
            mentor_contact='+91 94433 54321',
            avatar_url='https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=200'
        )
        db.session.add_all([student1, student2])
        db.session.flush()

        # Semesters
        sem = Semester(
            name='Even Semester 2025-2026',
            academic_year='2025-2026',
            semester_number=6,
            start_date=date(2025, 12, 15),
            end_date=date(2026, 5, 20),
            is_current=True
        )
        db.session.add(sem)
        db.session.flush()

        # Subjects
        subjects = [
            Subject(subject_code='CS8601', subject_name='Mobile App Development (React Native & Flutter)', department='Computer Science and Engineering', semester_number=6, credits=4, faculty_name='Dr. R. Kavitha'),
            Subject(subject_code='CS8602', subject_name='Artificial Intelligence & Deep Learning', department='Computer Science and Engineering', semester_number=6, credits=4, faculty_name='Prof. S. Suresh Kumar'),
            Subject(subject_code='CS8603', subject_name='Cloud Computing & DevOps Architecture', department='Computer Science and Engineering', semester_number=6, credits=3, faculty_name='Dr. M. Priyadharshini'),
            Subject(subject_code='CS8604', subject_name='Cryptography and Cyber Security', department='Computer Science and Engineering', semester_number=6, credits=3, faculty_name='Prof. A. Vignesh'),
            Subject(subject_code='CS8651', subject_name='Mobile Applications Design Laboratory', department='Computer Science and Engineering', semester_number=6, credits=2, faculty_name='Dr. R. Kavitha')
        ]
        db.session.add_all(subjects)
        db.session.flush()

        # Exams
        exam1 = Exam(exam_name='Internal Assessment 1 (IA-1)', semester_id=sem.id, exam_type='Internal', start_date=date(2026, 2, 10), end_date=date(2026, 2, 16))
        exam2 = Exam(exam_name='Internal Assessment 2 (IA-2)', semester_id=sem.id, exam_type='Internal', start_date=date(2026, 3, 20), end_date=date(2026, 3, 27))
        exam3 = Exam(exam_name='Model University Examinations', semester_id=sem.id, exam_type='Model', start_date=date(2026, 4, 22), end_date=date(2026, 4, 29))
        db.session.add_all([exam1, exam2, exam3])
        db.session.flush()

        # Marks for Harish
        marks_harish = [
            Mark(student_id=student1.id, exam_id=exam1.id, subject_id=subjects[0].id, marks_obtained=94, max_marks=100, grade='O', remarks='Outstanding coding and architecture implementation'),
            Mark(student_id=student1.id, exam_id=exam1.id, subject_id=subjects[1].id, marks_obtained=88, max_marks=100, grade='A+', remarks='Great conceptual clarity in Neural Networks'),
            Mark(student_id=student1.id, exam_id=exam1.id, subject_id=subjects[2].id, marks_obtained=85, max_marks=100, grade='A+', remarks='Good practical cloud containerization understanding'),
            Mark(student_id=student1.id, exam_id=exam1.id, subject_id=subjects[3].id, marks_obtained=91, max_marks=100, grade='O', remarks='Excellent analysis in encryption protocols'),
            
            Mark(student_id=student1.id, exam_id=exam2.id, subject_id=subjects[0].id, marks_obtained=96, max_marks=100, grade='O', remarks='Flawless mobile UI component design'),
            Mark(student_id=student1.id, exam_id=exam2.id, subject_id=subjects[1].id, marks_obtained=90, max_marks=100, grade='O', remarks='Well written LLM inference answers'),
            Mark(student_id=student1.id, exam_id=exam2.id, subject_id=subjects[2].id, marks_obtained=89, max_marks=100, grade='A+', remarks='Very good Kubernetes cluster deployment solution'),
            Mark(student_id=student1.id, exam_id=exam2.id, subject_id=subjects[3].id, marks_obtained=93, max_marks=100, grade='O', remarks='Strong cyber defense strategies')
        ]
        db.session.add_all(marks_harish)

        # Marks for Ananya
        marks_ananya = [
            Mark(student_id=student2.id, exam_id=exam1.id, subject_id=subjects[0].id, marks_obtained=91, max_marks=100, grade='O', remarks='Very good app layouts'),
            Mark(student_id=student2.id, exam_id=exam1.id, subject_id=subjects[1].id, marks_obtained=95, max_marks=100, grade='O', remarks='Top score in Machine Learning algorithms')
        ]
        db.session.add_all(marks_ananya)

        # Attendance generation (last 30 days)
        base_day = date(2026, 3, 1)
        for i in range(35):
            cur = base_day + timedelta(days=i)
            if cur.weekday() < 5: # Mon to Fri
                status = 'Present'
                if i in [7, 18]:
                    status = 'Absent'
                elif i in [22]:
                    status = 'On Duty'
                db.session.add(Attendance(
                    student_id=student1.id,
                    date=cur,
                    subject_id=subjects[i % len(subjects)].id,
                    status=status,
                    remarks='Regular session' if status == 'Present' else ('Sick leave informed' if status == 'Absent' else 'Inter-college symposium OD')
                ))

        # Timetable (Monday to Friday)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        for day in days:
            periods = [
                (1, "09:00", "09:50", subjects[0].id, "Lab-4 / CS302"),
                (2, "09:50", "10:40", subjects[1].id, "CS302"),
                (3, "10:55", "11:45", subjects[2].id, "CS302"),
                (4, "11:45", "12:35", subjects[3].id, "CS302"),
                (5, "01:30", "02:20", subjects[4].id, "Mobile Lab"),
                (6, "02:20", "03:10", subjects[0].id, "Mobile Lab"),
                (7, "03:20", "04:10", subjects[1].id, "Seminar Hall")
            ]
            for p_num, s_time, e_time, sub_id, room in periods:
                db.session.add(Timetable(
                    department='Computer Science and Engineering',
                    semester_number=6,
                    section='A',
                    day_of_week=day,
                    period_number=p_num,
                    start_time=s_time,
                    end_time=e_time,
                    subject_id=sub_id,
                    room_number=room
                ))

        # Activities
        act1 = Activity(
            student_id=student1.id,
            activity_type='Symposium',
            title='National Level Hackathon 2026 - Smart Education',
            event_date=date(2026, 2, 28),
            organizer='IIT Madras Research Park',
            achievement='1st Prize & Best Innovation Trophy'
        )
        act2 = Activity(
            student_id=student1.id,
            activity_type='Club',
            title='Karpagam AI & Robotics Innovation Club',
            event_date=date(2026, 1, 15),
            organizer='Karpagam College of Engineering',
            achievement='Student Lead & Project Coordinator'
        )
        db.session.add_all([act1, act2])

        # Internships
        intern1 = Internship(
            student_id=student1.id,
            company_name='Ascentz Technologies Solutions',
            role='Full-Stack Mobile & AI Intern',
            start_date=date(2026, 1, 5),
            end_date=date(2026, 6, 30),
            stipend=18000.0,
            status='In Progress',
            mentor_contact='HR Lead - careers@ascentz.in'
        )
        db.session.add(intern1)

        # Announcements
        ann1 = Announcement(
            title='Upcoming Model Examinations Schedule - Semester 6',
            content='Model practical and theory examinations commence from April 22nd, 2026. Hall tickets available on parent portal and class advisor desk.',
            category='Exam',
            target_audience='All',
            publish_date=date(2026, 4, 2),
            is_urgent=True
        )
        ann2 = Announcement(
            title='Annual Parent-Teacher Interaction Meet (PTM)',
            content='The Department of CSE welcomes parents to attend the individual performance review meeting on Saturday, 18th April 2026 from 10:00 AM at Karpagam Seminar Hall.',
            category='Academic',
            target_audience='Parents',
            publish_date=date(2026, 4, 8),
            is_urgent=False
        )
        ann3 = Announcement(
            title='Tier-1 Placement Training & Mock Technical Interviews',
            content='Special mock coding interviews and resume vetting sessions for top product companies are scheduled every Tuesday and Thursday afternoon.',
            category='Event',
            target_audience='Students',
            publish_date=date(2026, 4, 10),
            is_urgent=False
        )
        db.session.add_all([ann1, ann2, ann3])

        # Assignments
        asgn1 = Assignment(
            subject_id=subjects[0].id,
            title='React Native State Management & Offline Cache',
            description='Build an Expo screen with Redux Toolkit / Zustand and AsyncStorage.',
            due_date=date(2026, 4, 18),
            max_marks=10
        )
        asgn2 = Assignment(
            subject_id=subjects[1].id,
            title='Fine-Tuning Convolutional Neural Networks on Medical Imaging',
            description='Implement PyTorch ResNet50 model with transfer learning.',
            due_date=date(2026, 4, 25),
            max_marks=10
        )
        db.session.add_all([asgn1, asgn2])
        db.session.flush()

        db.session.add(AssignmentSubmission(
            assignment_id=asgn1.id,
            student_id=student1.id,
            status='Submitted',
            marks_awarded=9.5,
            submission_date=date(2026, 4, 15),
            feedback='Clean modular components and excellent responsiveness.'
        ))

        db.session.commit()
        print("[SUCCESS] Database successfully seeded with rich mock data for Karpagam College!")

if __name__ == '__main__':
    seed_database()
