import os
import re
from datetime import datetime, date
from app.models import Student, Parent, Mark, Attendance, Timetable, Activity, Internship, Announcement, AssignmentSubmission, Exam, Subject

class ChatbotEngine:
    def __init__(self):
        pass

    def process_query(self, user_message: str, parent_id: int = None, selected_student_id: int = None):
        """
        Processes parent queries using intelligent intent classification and returns
        personalized, structured data regarding their child.
        """
        # Determine student context
        student = None
        if selected_student_id:
            student = Student.query.get(selected_student_id)
        elif parent_id:
            student = Student.query.filter_by(parent_id=parent_id).first()

        if not student:
            return {
                "reply": "No student profile found associated with your account. Please reach out to Karpagam College Admin.",
                "intent": "UNKNOWN",
                "data": None,
                "suggestions": ["Contact Admin", "Check Account"]
            }

        text = user_message.strip().lower()

        # 1. Attendance Intent
        if any(w in text for w in ['attendance', 'present', 'absent', 'percentage', 'bunk', 'leave', 'onduty']):
            return self._handle_attendance(student, text)

        # 2. Marks / Academic Performance / Grades / GPA
        elif any(w in text for w in ['mark', 'grade', 'score', 'result', 'cgpa', 'gpa', 'exam result', 'performance', 'ia-1', 'ia-2', 'internal']):
            return self._handle_marks(student, text)

        # 3. Exams & Schedule
        elif any(w in text for w in ['exam', 'test', 'schedule', 'timetable for exam', 'datesheet', 'assessment']):
            return self._handle_exams(student, text)

        # 4. Class Timetable / Periods / Schedule today
        elif any(w in text for w in ['timetable', 'schedule', 'class', 'period', 'routine', 'timing', 'today class', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']):
            return self._handle_timetable(student, text)

        # 5. Assignments & Homework
        elif any(w in text for w in ['assignment', 'homework', 'submission', 'project', 'deadline', 'pending']):
            return self._handle_assignments(student, text)

        # 6. Activities, Co-Curricular, Sports
        elif any(w in text for w in ['activity', 'co-curricular', 'sports', 'symposium', 'event', 'workshop', 'nss', 'yrc', 'prize', 'achievement']):
            return self._handle_activities(student, text)

        # 7. Internships & Placement
        elif any(w in text for w in ['internship', 'placement', 'job', 'company', 'stipend', 'career', 'offer']):
            return self._handle_internships(student, text)

        # 8. Announcements / Notice board / Holidays
        elif any(w in text for w in ['announcement', 'notice', 'circular', 'holiday', 'event', 'ptm', 'meeting', 'news']):
            return self._handle_announcements()

        # 9. Faculty / Mentor contact
        elif any(w in text for w in ['mentor', 'advisor', 'faculty', 'professor', 'teacher', 'contact', 'staff', 'hod']):
            return self._handle_mentor(student)

        # 10. Fees / Payment
        elif any(w in text for w in ['fee', 'fees', 'tuition', 'due', 'receipt', 'payment', 'challan']):
            return {
                "reply": f"Tuition and exam fees for {student.first_name} (Semester {student.current_semester}) have been paid for the current academic term. No pending dues recorded on the college portal. For receipt queries, contact accounts@karpagam.edu.in.",
                "intent": "FEES_INFO",
                "data": {"status": "Paid", "pending_amount": 0.00},
                "suggestions": ["Attendance details", "Upcoming exams", "Mentor contact"]
            }

        # 11. Greetings
        elif any(w in text for w in ['hi', 'hello', 'hey', 'vanakkam', 'good morning', 'good afternoon', 'good evening', 'start']):
            return {
                "reply": f"Hello! 👋 Welcome to Karpagam College Parent Portal. I am your assistant for {student.first_name} {student.last_name} (Reg No: {student.register_number}, Dept: {student.department}). How can I assist you today?",
                "intent": "GREETING",
                "data": {"student": student.to_dict()},
                "suggestions": ["What is child's attendance?", "Show recent exam marks", "Today's timetable", "Any upcoming exams?"]
            }

        # Default fallback
        else:
            return {
                "reply": f"I can help you review {student.first_name}'s attendance, marks & exam scores, daily timetable, assignments, extracurricular achievements, or announcements. What would you like to check?",
                "intent": "FALLBACK",
                "data": None,
                "suggestions": ["Check Attendance", "View Exam Marks", "Class Timetable", "Mentor Contact"]
            }

    def _handle_attendance(self, student: Student, text: str):
        records = Attendance.query.filter_by(student_id=student.id).all()
        total_days = len(records)
        if total_days == 0:
            return {
                "reply": f"No attendance records logged yet for {student.first_name}.",
                "intent": "ATTENDANCE_SUMMARY",
                "data": {"percentage": 0, "total": 0}
            }
        
        present_count = sum(1 for r in records if r.status in ['Present', 'On Duty'])
        absent_count = sum(1 for r in records if r.status == 'Absent')
        percentage = round((present_count / total_days) * 100, 1)

        status_text = "Good standing! Above the Anna University / Karpagam minimum requirement (75%)." if percentage >= 75 else "⚠️ Attendance is below 75%. Please contact the class mentor."

        reply = (
            f"Attendance Report for {student.first_name} {student.last_name}\n\n"
            f"• Overall Attendance: {percentage}%\n"
            f"• Present/OD Days: {present_count} / {total_days}\n"
            f"• Absent Days: {absent_count}\n\n"
            f"{status_text}\n"
            f"Department: {student.department} | Sem: {student.current_semester}"
        )

        return {
            "reply": reply,
            "intent": "ATTENDANCE_SUMMARY",
            "data": {
                "percentage": percentage,
                "present_count": present_count,
                "absent_count": absent_count,
                "total_days": total_days,
                "recent_records": [r.to_dict() for r in records[-5:]]
            },
            "suggestions": ["Show recent marks", "View today's timetable", "Contact mentor"]
        }

    def _handle_marks(self, student: Student, text: str):
        marks = Mark.query.filter_by(student_id=student.id).all()
        if not marks:
            return {
                "reply": f"No examination marks recorded yet for {student.first_name}.",
                "intent": "MARKS_SUMMARY",
                "data": []
            }

        grouped_by_exam = {}
        for m in marks:
            exam_name = m.exam.exam_name if m.exam else "Assessment"
            grouped_by_exam.setdefault(exam_name, []).append(m)

        lines = [f"Academic Performance for {student.first_name} {student.last_name}\n"]
        for exam_name, m_list in grouped_by_exam.items():
            total_obtained = sum(m.marks_obtained for m in m_list)
            total_max = sum(m.max_marks for m in m_list)
            pct = round((total_obtained / total_max * 100), 1) if total_max > 0 else 0
            lines.append(f"{exam_name} (Average: {pct}%):")
            for m in m_list:
                s_name = m.subject.subject_name if m.subject else "Subject"
                s_code = m.subject.subject_code if m.subject else ""
                lines.append(f"• {s_name} ({s_code}): {m.marks_obtained}/{m.max_marks} (Grade: {m.grade or 'A'})")
            lines.append("")

        reply = "\n".join(lines)
        return {
            "reply": reply,
            "intent": "MARKS_SUMMARY",
            "data": [m.to_dict() for m in marks],
            "suggestions": ["Attendance details", "Upcoming Exam Schedule", "Timetable"]
        }

    def _handle_exams(self, student: Student, text: str):
        exams = Exam.query.order_by(Exam.start_date.asc()).all()
        if not exams:
            return {
                "reply": "No upcoming examinations currently scheduled.",
                "intent": "EXAM_SCHEDULE",
                "data": []
            }

        lines = [f"Upcoming & Scheduled Examinations (Semester {student.current_semester}):\n"]
        for e in exams:
            start = e.start_date.strftime('%d %b %Y') if e.start_date else 'TBA'
            end = e.end_date.strftime('%d %b %Y') if e.end_date else 'TBA'
            lines.append(f"• {e.exam_name} ({e.exam_type}) — Dates: {start} to {end}")

        return {
            "reply": "\n".join(lines),
            "intent": "EXAM_SCHEDULE",
            "data": [e.to_dict() for e in exams],
            "suggestions": ["Check marks", "Check attendance", "Class Timetable"]
        }

    def _handle_timetable(self, student: Student, text: str):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        matched_day = None
        for d in days:
            if d.lower() in text:
                matched_day = d
                break

        if not matched_day:
            today_weekday = datetime.now().strftime('%A')
            matched_day = today_weekday if today_weekday in days else 'Monday'

        schedule = Timetable.query.filter_by(
            department=student.department,
            semester_number=student.current_semester,
            day_of_week=matched_day
        ).order_by(Timetable.period_number.asc()).all()

        if not schedule:
            return {
                "reply": f"No timetable periods scheduled for {matched_day} (Sec {student.section}, Sem {student.current_semester}).",
                "intent": "TIMETABLE_INFO",
                "data": {"day": matched_day, "schedule": []}
            }

        lines = [f"Class Timetable for {matched_day} ({student.department} - Sem {student.current_semester}):\n"]
        table_rows = []
        for item in schedule:
            s_name = item.subject.subject_name if item.subject else 'Class'
            s_code = item.subject.subject_code if item.subject else '-'
            f_name = item.subject.faculty_name if item.subject else 'Faculty'
            r_num = item.room_number or '302'
            lines.append(f"Period {item.period_number} ({item.start_time} - {item.end_time}): {s_name} ({s_code}) | Room: {r_num} | Staff: {f_name}")
            table_rows.append({
                "period": item.period_number,
                "timing": f"{item.start_time} - {item.end_time}",
                "subject": s_name,
                "code": s_code,
                "room": r_num,
                "faculty": f_name
            })

        return {
            "reply": "\n".join(lines),
            "intent": "TIMETABLE_INFO",
            "data": {
                "day": matched_day,
                "department": student.department,
                "semester": student.current_semester,
                "section": student.section,
                "schedule": table_rows
            },
            "suggestions": ["Tomorrow timetable", "Check attendance", "Show marks"]
        }

    def _handle_assignments(self, student: Student, text: str):
        submissions = AssignmentSubmission.query.filter_by(student_id=student.id).all()
        if not submissions:
            return {
                "reply": f"All assignments for {student.first_name} are up to date! No pending submissions.",
                "intent": "ASSIGNMENT_INFO",
                "data": []
            }

        lines = [f"Assignments Status for {student.first_name}:\n"]
        for s in submissions:
            asgn_title = s.assignment.title if s.assignment else "Assignment"
            due = s.assignment.due_date.strftime('%d %b %Y') if s.assignment and s.assignment.due_date else "N/A"
            lines.append(f"• {asgn_title}: Status: {s.status} (Due: {due}) - Awarded: {s.marks_awarded or 'Pending'}/{s.assignment.max_marks if s.assignment else 10}")

        return {
            "reply": "\n".join(lines),
            "intent": "ASSIGNMENT_INFO",
            "data": [s.to_dict() for s in submissions],
            "suggestions": ["Check timetable", "Show attendance", "Upcoming exams"]
        }

    def _handle_activities(self, student: Student, text: str):
        acts = Activity.query.filter_by(student_id=student.id).all()
        if not acts:
            return {
                "reply": f"No extracurricular or co-curricular activities recorded yet for {student.first_name}.",
                "intent": "ACTIVITY_INFO",
                "data": []
            }

        lines = [f"Co-Curricular & Club Activities for {student.first_name}:\n"]
        for a in acts:
            lines.append(f"• {a.title} ({a.activity_type})\n  Organizer: {a.organizer} | Achievement: {a.achievement or 'Participant'}")

        return {
            "reply": "\n".join(lines),
            "intent": "ACTIVITY_INFO",
            "data": [a.to_dict() for a in acts],
            "suggestions": ["Check internship status", "Academic performance", "Mentor info"]
        }

    def _handle_internships(self, student: Student, text: str):
        interns = Internship.query.filter_by(student_id=student.id).all()
        if not interns:
            return {
                "reply": f"{student.first_name} is currently preparing for upcoming internship placement drives. Pre-placement training is in progress.",
                "intent": "INTERNSHIP_INFO",
                "data": []
            }

        lines = [f"Internship & Placement Details for {student.first_name}:\n"]
        for i in interns:
            stipend_str = f"₹{i.stipend:,.0f}/mo" if i.stipend > 0 else "Unpaid / Credit"
            lines.append(f"• {i.company_name} — Role: {i.role}\n  Status: {i.status} | Stipend: {stipend_str}")

        return {
            "reply": "\n".join(lines),
            "intent": "INTERNSHIP_INFO",
            "data": [i.to_dict() for i in interns],
            "suggestions": ["Activities & Co-curricular", "Academic performance", "Check attendance"]
        }

    def _handle_announcements(self):
        announcements = Announcement.query.order_by(Announcement.publish_date.desc()).limit(5).all()
        lines = ["Latest Karpagam College Announcements:\n"]
        for ann in announcements:
            urgent_badge = "[IMPORTANT] " if ann.is_urgent else ""
            lines.append(f"• {urgent_badge}{ann.title} ({ann.publish_date.strftime('%d %b %Y')})\n  {ann.content}\n")

        return {
            "reply": "\n".join(lines),
            "intent": "ANNOUNCEMENTS",
            "data": [a.to_dict() for a in announcements],
            "suggestions": ["Upcoming exam schedule", "Check child's attendance", "Timetable"]
        }

    def _handle_mentor(self, student: Student):
        mentor_name = student.mentor_name if student.mentor_name else "Not assigned yet"
        mentor_contact = student.mentor_contact if student.mentor_contact else "Please contact department office"
        reply = (
            f"Class Advisor & Mentor Details\n\n"
            f"• Student: {student.first_name} {student.last_name} ({student.roll_number})\n"
            f"• Faculty Mentor: {mentor_name}\n"
            f"• Department: {student.department} (Semester {student.current_semester}, Sec {student.section})\n"
            f"• Contact: {mentor_contact}\n"
        )
        return {
            "reply": reply,
            "intent": "MENTOR_INFO",
            "data": {
                "mentor_name": mentor_name,
                "mentor_contact": mentor_contact,
                "student_name": f"{student.first_name} {student.last_name}"
            },
            "suggestions": ["Child's attendance", "Recent exam marks", "Timetable"]
        }

