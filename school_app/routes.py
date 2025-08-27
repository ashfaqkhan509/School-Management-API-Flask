from flask import Blueprint, request, jsonify
from school_app import db
from school_app.models import (
    Student,
    Course,
    Enrollment,
    Assignment,
    Lesson,
    Result
)
from sqlalchemy.orm import selectinload, load_only
from school_app.tasks import generate_student_report


bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('students', methods=['POST'])
def create_student():
    try:
        data = request.get_json()
        if not data or not data.get('name') or not data.get('email'):
            return jsonify({'error': 'Name and email are required'}), 400

        student = Student(
            name=data['name'],
            email=data['email']
        )

        db.session.add(student)
        db.session.commit()

        return jsonify({
            'message': 'Student created successfully',
            'student': {
                'id': student.id,
                'name': student.name,
                'email': student.email
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/courses', methods=['POST'])
def create_course():
    try:
        data = request.get_json()
        if not data or not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400

        course = Course(
            title=data['title'],
            description=data.get('description')
        )

        db.session.add(course)
        db.session.commit()

        return jsonify({
            'message': 'Course created successfully',
            'course': {
                'id': course.id,
                'title': course.title,
                'description': course.description
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/enroll', methods=['POST'])
def enroll_student():
    """Enroll a student in a course"""
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        course_id = data.get('course_id')

        if not student_id or not course_id:
            return jsonify({'error': 'student_id and course_id are required'}), 400

        student = Student.query.get(student_id)
        course = Course.query.get(course_id)

        if not student or not course:
            return jsonify({'error': 'Student or Course not found'}), 404

        enroll_student_exists = Enrollment.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()

        if enroll_student_exists:
            return jsonify({'error': 'Student already enrolled in this course'}), 400

        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id
        )

        db.session.add(enrollment)
        db.session.commit()

        return jsonify({
            'message': f'Student {student.name} enrolled in {course.title}',
            'enrollment': {
                'enrollment_id': enrollment.id,
                'student_id': enrollment.student_id,
                'course_id': enrollment.course_id
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/lessons', methods=['POST'])
def create_lesson():
    """Create a new lesson for a course"""
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        name = data.get('name')

        if not course_id or not name:
            return jsonify({'error': 'course_id and name are required'}), 400

        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Invalid course_id'}), 404

        lesson = Lesson(
            course_id=course_id,
            name=name
        )

        db.session.add(lesson)
        db.session.commit()

        return jsonify({
            'message': f'Lesson {name} created for course {course.title}',
            'lesson': {
                'lesson_id': lesson.id,
                'course_id': lesson.course_id,
                'name': lesson.name
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/assignments', methods=['POST'])
def create_assignment():
    """Create a new assignment for a lesson"""
    try:
        data = request.get_json()
        lesson_id = data.get('lesson_id')
        name = data.get('name')

        if not lesson_id or not name:
            return jsonify({'error': 'lesson_id and name are required'}), 400

        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return jsonify({'error': 'Invalid lesson_id'}), 404

        assignment = Assignment(
            lesson_id=lesson_id,
            name=name
        )

        db.session.add(assignment)
        db.session.commit()

        return jsonify({
            'message': f'Assignment {name} created for lesson {lesson.name}',
            'assignment': {
                'assignment_id': assignment.id,
                'lesson_id': assignment.lesson_id,
                'name': assignment.name
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/submit', methods=['POST'])
def submit_assignment():
    """Submit an assignment result for a student"""
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        assignment_id = data.get('assignment_id')
        score = data.get('score')

        if not student_id or not assignment_id or score is None:
            return jsonify({'error': 'student_id, assignment_id, and score are required'}), 400

        student = Student.query.get(student_id)
        assignment = Assignment.query.get(assignment_id)

        if not student or not assignment:
            return jsonify({'error': 'Invalid student_id or assignment_id'}), 404

        result = Result(
            student_id=student_id,
            assignment_id=assignment_id,
            score=score
        )

        db.session.add(result)
        db.session.commit()

        return jsonify({
            'message': f'Assignment {assignment.name} submitted by {student.name}',
            'result': {
                'result_id': result.id,
                'student_id': result.student_id,
                'assignment_id': result.assignment_id,
                'score': result.score
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Retrives a student info with average score - Using efficient queries"""
    try:
        student = (
            db.session.query(Student)
            .options(
                load_only(Student.id, Student.name, Student.email),
                selectinload(Student.enrollments)
                .joinedload(Enrollment.course)
                .load_only(Course.id, Course.title),
                selectinload(Student.results)
                .joinedload(Result.assignment)
                .load_only(Assignment.id, Assignment.name)
                .joinedload(Assignment.lesson)
                .load_only(Lesson.id, Lesson.name),
            )
            .filter(Student.id == student_id)
            .first()
        )

        if not student:
            return jsonify({'error': 'Student not found'}), 404

        return jsonify({
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'average_score': student.average_score,
            'enrollments': [
                {
                    'course_id': enrollment.course.id,
                    'course_title': enrollment.course.title
                } for enrollment in student.enrollments
            ],
            'results': [
                {
                    'assignment_id': result.assignment.id,
                    'assignment_name': result.assignment.name,
                    'lesson_name': (
                        result.assignment.lesson.name
                        if result.assignment.lesson else None
                    ),
                    'score': result.score,
                }
                for result in student.results
            ],
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Soft delete a course by its ID"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        course.soft_delete()
        db.session.commit()

        return jsonify({'message': f'Course {course.title} has been soft deleted'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route("/reports/<int:student_id>", methods=["POST"])
def create_student_report(student_id):
    """Trigger a Celery background task to generate a student report."""
    try:
        task = generate_student_report.delay(student_id)
        return jsonify({
            "message": f"Report generation started for student {student_id}",
            "task_id": task.id
        }), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500
