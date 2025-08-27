from sqlalchemy import (
    Float,
    Integer,
    String,
    Text,
    ForeignKey,
    and_,
    select,
    func
)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from school_app import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property


class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()


class Student(db.Model):
    __tablename__ = 'students'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="student",
        cascade="all, delete-orphan"
    )
    results: Mapped[list['Result']] = relationship('Result', back_populates='student')

    @hybrid_property
    def average_score(self) -> float:
        """Calculate average score"""
        if not self.results:
            return 0.0
        total_score = sum(result.score for result in self.results if result.score is not None)
        count = sum(1 for result in self.results if result.score is not None)
        return total_score / count if count > 0 else 0.0

    @average_score.expression
    def average_score(cls):
        return (
            select(func.coalesce(func.avg(Result.score), 0.0))
            .where(and_(Result.student_id == cls.id, Result.score.isnot(None)))
            .correlate(cls)
            .scalar_subquery()
        )


class Course(db.Model, SoftDeleteMixin):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete-orphan"
    )
    lessons: Mapped[list['Lesson']] = relationship('Lesson', back_populates='course')


class Lesson(db.Model, SoftDeleteMixin):
    __tablename__ = 'lessons'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    course_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('courses.id'))
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    course: Mapped['Course | None'] = relationship('Course', back_populates='lessons')
    assignments: Mapped[list['Assignment']] = relationship('Assignment', back_populates='lesson')


class Assignment(db.Model, SoftDeleteMixin):
    __tablename__ = 'assignments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    lesson_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('lessons.id'))
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    lesson: Mapped['Lesson | None'] = relationship('Lesson', back_populates='assignments')
    results: Mapped[list['Result']] = relationship('Result', back_populates='assignment')


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey('students.id'), nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey('courses.id'), nullable=False)
    enrolled_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)

    student: Mapped["Student"] = relationship("Student", back_populates="enrollments")
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")


class Result(db.Model):
    __tablename__ = 'results'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('students.id'))
    assignment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('assignments.id'))
    score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    student: Mapped['Student | None'] = relationship('Student', back_populates='results')
    assignment: Mapped['Assignment | None'] = relationship(
        'Assignment',
        back_populates='results'
    )
