
def test_create_student(client):
    response = client.post('/api/students', json={
        'name': 'Test User',
        'email': 'test@example.com'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Student created successfully'
    assert data['student']['name'] == 'Test User'
    assert data['student']['email'] == 'test@example.com'
    assert 'id' in data['student']


def test_create_student_missing_fields(client):
    response = client.post('/api/students', json={
        'name': 'Test User'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Name and email are required'
    response = client.post('/api/students', json={
        'email': 'test@example.com'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Name and email are required'


def test_create_course(client):
    response = client.post('/api/courses', json={
        'title': 'Test Course',
        'description': 'A course for testing'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Course created successfully'
    assert data['course']['title'] == 'Test Course'
    assert data['course']['description'] == 'A course for testing'


def test_create_course_missing_title(client):
    response = client.post('/api/courses', json={
        'description': 'A course for testing'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Title is required'


def test_create_course_no_description(client):
    response = client.post('/api/courses', json={
        'title': 'Test Course'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Course created successfully'
    assert data['course']['title'] == 'Test Course'
    assert data['course']['description'] is None
    assert 'id' in data['course']


def test_enroll_student(client):
    # First, create a student and a course
    student_responese = client.post('/api/students', json={
        'name': 'Enroll User',
        'email': 'test@example.com'
    })
    course_response = client.post('/api/courses', json={
        'title': 'Enroll Course',
        'description': 'A course for enrollment testing'
    })
    print(student_responese.get_json())

    student_id = student_responese.get_json()['student']['id']
    course_id = course_response.get_json()['course']['id']
    # Now, enroll the student in the course
    response = client.post('/api/enroll', json={
        'student_id': student_id,
        'course_id': course_id
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['enrollment']['student_id'] == student_id
    assert data['enrollment']['course_id'] == course_id


def test_enroll_student_missing_fields(client):
    response = client.post('/api/enroll', json={
        'student_id': 1
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'student_id and course_id are required'
    response = client.post('/api/enroll', json={
        'course_id': 1
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'student_id and course_id are required'


def test_enroll_student_nonexistent_ids(client):
    response = client.post('/api/enroll', json={
        'student_id': 999,
        'course_id': 1
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Student or Course not found'
    response = client.post('/api/enroll', json={
        'student_id': 1,
        'course_id': 999
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Student or Course not found'


def test_enroll_student_already_enrolled(client):
    # First, create a student and a course
    student_responese = client.post('/api/students', json={
        'name': 'Enroll User',
        'email': 'test@example.com'
    })
    course_response = client.post('/api/courses', json={
        'title': 'Enroll Course',
        'description': 'A course for enrollment testing'
    })
    student_id = student_responese.get_json()['student']['id']
    course_id = course_response.get_json()['course']['id']
    # Enroll the student in the course
    client.post('/api/enroll', json={
        'student_id': student_id,
        'course_id': course_id
    })
    # Try enrolling again
    response = client.post('/api/enroll', json={
        'student_id': student_id,
        'course_id': course_id
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Student already enrolled in this course'


def test_create_lesson(client):
    # First, create a course
    course_response = client.post('/api/courses', json={
        'title': 'Lesson Course',
        'description': 'A course for lesson testing'
    })
    course_id = course_response.get_json()['course']['id']
    # Now, create a lesson
    response = client.post('/api/lessons', json={
        'name': 'Test Lesson',
        'course_id': course_id
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['lesson']['name'] == 'Test Lesson'
    assert data['lesson']['course_id'] == course_id
    assert 'lesson_id' in data['lesson']


def test_create_lesson_missing_fields(client):
    response = client.post('/api/lessons', json={
        'course_id': 1
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'course_id and name are required'
    response = client.post('/api/lessons', json={
        'name': 'Test Lesson'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'course_id and name are required'


def test_create_lesson_nonexistent_course(client):
    response = client.post('/api/lessons', json={
        'name': 'Test Lesson',
        'course_id': 999
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Invalid course_id'


def test_create_assignment(client):
    # First, create a course and a lesson
    course_response = client.post('/api/courses', json={
        'title': 'Assignment Course',
        'description': 'A course for assignment testing'
    })
    course_id = course_response.get_json()['course']['id']
    lesson_response = client.post('/api/lessons', json={
        'name': 'Test Lesson',
        'course_id': course_id
    })
    lesson_id = lesson_response.get_json()['lesson']['lesson_id']
    # Now, create an assignment
    response = client.post('/api/assignments', json={
        'name': 'Test Assignment',
        'lesson_id': lesson_id
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['assignment']['name'] == 'Test Assignment'
    assert data['assignment']['lesson_id'] == lesson_id
    assert 'assignment_id' in data['assignment']


def test_create_assignment_missing_fields(client):
    response = client.post('/api/assignments', json={
        'lesson_id': 1
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'lesson_id and name are required'
    response = client.post('/api/assignments', json={
        'name': 'Test Assignment'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'lesson_id and name are required'


def test_create_assignment_nonexistent_lesson(client):
    response = client.post('/api/assignments', json={
        'name': 'Test Assignment',
        'lesson_id': 999
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Invalid lesson_id'


def test_submit_assignment(client):
    # First, create a student, course, lesson, and assignment
    student_response = client.post('/api/students', json={
        'name': 'Submit User',
        'email': 'test@example.com'
    })
    course_response = client.post('/api/courses', json={
        'title': 'Submit Course',
        'description': 'A course for submission testing'
    })
    student_id = student_response.get_json()['student']['id']
    course_id = course_response.get_json()['course']['id']
    lesson_response = client.post('/api/lessons', json={
        'name': 'Submit Lesson',
        'course_id': course_id
    })
    lesson_id = lesson_response.get_json()['lesson']['lesson_id']
    assignment_response = client.post('/api/assignments', json={
        'name': 'Submit Assignment',
        'lesson_id': lesson_id
    })
    assignment_id = assignment_response.get_json()['assignment']['assignment_id']
    # Now, submit the assignment
    response = client.post('/api/submit', json={
        'student_id': student_id,
        'assignment_id': assignment_id,
        'score': 95.0
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['result']['student_id'] == student_id
    assert data['result']['assignment_id'] == assignment_id
    assert data['result']['score'] == 95.0
