from flask import Flask, request, jsonify
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)

# Database Models
class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(80), nullable=False)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_description = db.Column(db.String(200))

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))

class Enrollment(db.Model):
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    student = db.relationship('Student', backref=db.backref('enrollments', lazy=True))
    course = db.relationship('Course', backref=db.backref('enrollments', lazy=True))

# API Resources
class CourseResource(Resource):
    def get(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return {"error_code": "COURSE404", "message": "Course not found"}, 404
        return {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "course_code": course.course_code,
            "course_description": course.course_description
        }, 200

    def post(self):
        data = request.json
        if 'course_name' not in data:
            return {"error_code": "COURSE001", "message": "Course Name is required"}, 400
        if 'course_code' not in data:
            return {"error_code": "COURSE002", "message": "Course Code is required"}, 400

        # Check if course code already exists
        existing_course = Course.query.filter_by(course_code=data['course_code']).first()
        if existing_course:
            return {"error_code": "COURSE409", "message": "Course already exists"}, 409

        new_course = Course(
            course_name=data['course_name'],
            course_code=data['course_code'],
            course_description=data.get('course_description', '')
        )
        db.session.add(new_course)
        db.session.commit()
        return {"message": "Course created", "course_id": new_course.course_id}, 201

    def put(self, course_id):
        data = request.json
        course = Course.query.get(course_id)
        if not course:
            return {"error_code": "COURSE404", "message": "Course not found"}, 404

        course.course_name = data.get('course_name', course.course_name)
        course.course_code = data.get('course_code', course.course_code)
        course.course_description = data.get('course_description', course.course_description)
        db.session.commit()
        return {"message": "Course updated"}, 200

    def delete(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return {"error_code": "COURSE404", "message": "Course not found"}, 404
        db.session.delete(course)
        db.session.commit()
        return {"message": "Course deleted"}, 200

class StudentResource(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {"error_code": "STUDENT404", "message": "Student not found"}, 404
        return {
            "student_id": student.student_id,
            "roll_number": student.roll_number,
            "first_name": student.first_name,
            "last_name": student.last_name
        }, 200

    def post(self):
        data = request.json
        if 'roll_number' not in data:
            return {"error_code": "STUDENT001", "message": "Roll Number required"}, 400
        if 'first_name' not in data:
            return {"error_code": "STUDENT002", "message": "First Name is required"}, 400

        # Check if roll number already exists
        existing_student = Student.query.filter_by(roll_number=data['roll_number']).first()
        if existing_student:
            return {"error_code": "STUDENT409", "message": "Student already exists"}, 409

        new_student = Student(
            roll_number=data['roll_number'],
            first_name=data['first_name'],
            last_name=data.get('last_name', '')
        )
        db.session.add(new_student)
        db.session.commit()
        return {"message": "Student created", "student_id": new_student.student_id}, 201

    def put(self, student_id):
        data = request.json
        student = Student.query.get(student_id)
        if not student:
            return {"error_code": "STUDENT404", "message": "Student not found"}, 404

        student.roll_number = data.get('roll_number', student.roll_number)
        student.first_name = data.get('first_name', student.first_name)
        student.last_name = data.get('last_name', student.last_name)
        db.session.commit()
        return {"message": "Student updated"}, 200

    def delete(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {"error_code": "STUDENT404", "message": "Student not found"}, 404
        db.session.delete(student)
        db.session.commit()
        return {"message": "Student deleted"}, 200

class EnrollmentResource(Resource):
    def post(self, student_id):
        data = request.json
        course_id = data.get('course_id')
        student = Student.query.get(student_id)
        course = Course.query.get(course_id)

        if not student:
            return {"error_code": "ENROLLMENT002", "message": "Student does not exist"}, 404
        if not course:
            return {"error_code": "ENROLLMENT001", "message": "Course does not exist"}, 404

        # Check if the enrollment already exists
        existing_enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if existing_enrollment:
            return {"error_code": "ENROLLMENT409", "message": "Enrollment already exists"}, 409

        new_enrollment = Enrollment(student_id=student_id, course_id=course_id)
        db.session.add(new_enrollment)
        db.session.commit()
        return {"message": "Enrollment created", "enrollment_id": new_enrollment.enrollment_id}, 201

    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {"error_code": "ENROLLMENT002", "message": "Student does not exist"}, 404

        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        if not enrollments:
            return {"error_code": "ENROLLMENT404", "message": "No enrollments found for this student"}, 404

        enrollment_data = [
            {
                "enrollment_id": enrollment.enrollment_id,
                "course_id": enrollment.course.course_id,
                "course_name": enrollment.course.course_name,
                "course_code": enrollment.course.course_code
            } for enrollment in enrollments
        ]
        return {"enrollments": enrollment_data}, 200

    def delete(self, student_id, course_id):
        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if not enrollment:
            return {"error": "Enrollment not found"}, 404
        db.session.delete(enrollment)
        db.session.commit()
        return {"message": "Enrollment deleted"}, 200

# API Endpoints
api.add_resource(CourseResource, '/api/course', '/api/course/<int:course_id>')
api.add_resource(StudentResource, '/api/student', '/api/student/<int:student_id>')
api.add_resource(EnrollmentResource, '/api/student/<int:student_id>/course', '/api/student/<int:student_id>/course/<int:course_id>')

if __name__ == '__main__':
    app.run(debug=True)


