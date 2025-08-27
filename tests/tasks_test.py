import os
import csv
from school_app import db
from school_app.models import Student, Course, Lesson, Assignment, Result
from school_app.tasks import generate_student_report


def test_generate_student_report_creates_csv(app, celery_eager, tmp_path):
    
    student = Student(name="Task User", email="taskuser@example.com")
    course = Course(title="Task Course", description="Celery test course")
    lesson = Lesson(name="Task Lesson", course=course)
    assignment = Assignment(name="Task Assignment", lesson=lesson)
    result = Result(student=student, assignment=assignment, score=85)

    db.session.add_all([student, course, lesson, assignment, result])
    db.session.commit()

    # Act: run task synchronously
    report_path = generate_student_report.delay(student.id).get()

    # Assert: file exists
    assert os.path.exists(report_path)

    # Assert: CSV content
    with open(report_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    assert ["Student", "Task User"] in rows
    assert ["Email", "taskuser@example.com"] in rows
    assert any("Task Assignment" in row for row in rows)
