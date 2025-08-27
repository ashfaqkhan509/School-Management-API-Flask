import os
import csv
from typing import Optional
from sqlalchemy.orm import selectinload, load_only
from school_app.models import Student, Result, Assignment, Lesson, Course
from celery import shared_task


@shared_task
def generate_student_report(student_id: int) -> str:
    """Background task to generate a CSV report for a student."""
    from school_app import db
    # Fetch student in a single roundtrip with eager loading
    student: Optional[Student] = (
        db.session.query(Student)
        .options(
            load_only(Student.id, Student.name, Student.email),
            selectinload(Student.results)
            .joinedload(Result.assignment)
            .load_only(Assignment.id, Assignment.name, Assignment.lesson_id, Assignment.is_deleted)
            .joinedload(Assignment.lesson)
            .load_only(Lesson.id, Lesson.name, Lesson.course_id, Lesson.is_deleted)
            .joinedload(Lesson.course)
            .load_only(Course.id, Course.title, Course.is_deleted)
        )
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise ValueError("Student not found")

    # Prepare rows
    rows = [("Assignment", "Lesson", "Course", "Score")]
    for result in student.results:
        assignment = result.assignment
        if not assignment or assignment.is_deleted:
            continue
        lesson = assignment.lesson
        if lesson and lesson.is_deleted:
            continue
        course = lesson.course if lesson else None
        if course and course.is_deleted:
            continue

        rows.append((
            assignment.name,
            lesson.name if lesson else "",
            course.title if course else "",
            result.score if result.score is not None else "N/A"
        ))

    avg = student.average_score

    # Save report in reports/ directory
    os.makedirs("reports", exist_ok=True)
    path = os.path.abspath(os.path.join("reports", f"student_{student.id}_report.csv"))

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Student", student.name])
        writer.writerow(["Email", student.email])
        writer.writerow(["Average Score", avg if avg is not None else "N/A"])
        writer.writerow([])
        writer.writerows(rows)

    return path
