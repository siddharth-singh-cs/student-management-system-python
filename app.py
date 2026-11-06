"""
Student Management System - Flask Application
Backend web application using Flask, raw MySQL queries via mysql-connector-python, and Jinja2 templates.
"""

import csv
import io
import math
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from config import Config
from database import execute_query, execute_commit
from mysql.connector import Error

app = Flask(__name__)
app.config.from_object(Config)


# ==============================================================================
# ROUTE 1: Dashboard (Overview & Quick Metrics)
# HTTP Method: GET
# ==============================================================================
@app.route('/')
def dashboard():
    """
    Renders the administrator dashboard.
    Fetches aggregate counts and the 5 most recently registered students.
    """
    total_students = 0
    total_courses = 0
    recent_students = []
    db_error = None

    try:
        # SQL Query 1: Aggregate count of students
        student_count_res = execute_query(
            "SELECT COUNT(*) AS total FROM students",
            fetch_one=True
        )
        total_students = student_count_res['total'] if student_count_res else 0

        # SQL Query 2: Aggregate count of academic courses
        course_count_res = execute_query(
            "SELECT COUNT(*) AS total FROM courses",
            fetch_one=True
        )
        total_courses = course_count_res['total'] if course_count_res else 0

        # SQL Query 3: Fetch last 5 enrolled students with their enrolled course info
        # Using INNER JOIN to resolve course_name and course_code from the courses table
        recent_students = execute_query(
            """
            SELECT 
                s.id, 
                s.full_name, 
                s.registration_number, 
                s.email, 
                s.admission_date,
                c.course_name, 
                c.course_code
            FROM students s
            INNER JOIN courses c ON s.course_id = c.id
            ORDER BY s.id DESC
            LIMIT 5
            """
        )
    except Error as e:
        db_error = f"Database connection issue: {e}"

    return render_template(
        'dashboard.html',
        total_students=total_students,
        total_courses=total_courses,
        recent_students=recent_students,
        db_error=db_error
    )


# ==============================================================================
# ROUTE PLACEHOLDERS (To be fully implemented in upcoming stages)
# ==============================================================================

# ==============================================================================
# ROUTE 4: Student Directory (List, Search & Paginate Students)
# HTTP Method: GET
# ==============================================================================
@app.route('/students')
def view_students():
    """
    Displays the directory of registered students with search, course filtering,
    and SQL-based pagination (LIMIT / OFFSET).
    """
    search_query = request.args.get('search', '').strip()
    course_filter = request.args.get('course', '').strip()
    
    # Pagination parameters
    try:
        page = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page = 1
    per_page = 8  # Students per page

    students = []
    courses = []
    total_students_count = 0
    total_pages = 1

    try:
        # 1. Fetch all courses for the filter dropdown
        courses = execute_query("SELECT id, course_name, course_code FROM courses ORDER BY course_name ASC")

        # 2. Build dynamic filter conditions
        conditions = []
        params = []

        if search_query:
            conditions.append("(s.full_name LIKE %s OR s.registration_number LIKE %s OR s.email LIKE %s)")
            wildcard = f"%{search_query}%"
            params.extend([wildcard, wildcard, wildcard])

        if course_filter:
            conditions.append("s.course_id = %s")
            params.append(course_filter)

        where_clause = ""
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)

        # 3. Query total matching records for pagination calculation
        count_sql = f"SELECT COUNT(*) AS total FROM students s {where_clause}"
        count_res = execute_query(count_sql, tuple(params), fetch_one=True)
        total_students_count = count_res['total'] if count_res else 0
        total_pages = max(1, math.ceil(total_students_count / per_page))
        if page > total_pages:
            page = total_pages

        # 4. Fetch paginated records using parameterized LIMIT and OFFSET
        offset = (page - 1) * per_page
        data_sql = f"""
            SELECT 
                s.id,
                s.full_name,
                s.registration_number,
                s.email,
                s.phone,
                s.gender,
                s.year_of_study,
                s.date_of_birth,
                s.admission_date,
                c.id AS course_id,
                c.course_name,
                c.course_code
            FROM students s
            INNER JOIN courses c ON s.course_id = c.id
            {where_clause}
            ORDER BY s.id DESC
            LIMIT %s OFFSET %s
        """
        pagination_params = list(params) + [per_page, offset]
        students = execute_query(data_sql, tuple(pagination_params))

    except Error as err:
        flash(f"Database error loading student directory: {err}", "error")

    return render_template(
        'students.html',
        students=students,
        courses=courses,
        search_query=search_query,
        course_filter=course_filter,
        page=page,
        total_pages=total_pages,
        total_count=total_students_count
    )


# ==============================================================================
# ROUTE 4B: Export Students to CSV
# HTTP Method: GET
# ==============================================================================
@app.route('/students/export')
def export_students_csv():
    """
    Exports registered students matching active search/filter criteria into a downloadable CSV file.
    Demonstrates in-memory streaming using io.StringIO and Flask Response.
    """
    search_query = request.args.get('search', '').strip()
    course_filter = request.args.get('course', '').strip()

    try:
        conditions = []
        params = []

        if search_query:
            conditions.append("(s.full_name LIKE %s OR s.registration_number LIKE %s OR s.email LIKE %s)")
            wildcard = f"%{search_query}%"
            params.extend([wildcard, wildcard, wildcard])

        if course_filter:
            conditions.append("s.course_id = %s")
            params.append(course_filter)

        where_clause = ""
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)

        sql = f"""
            SELECT 
                s.id,
                s.full_name,
                s.registration_number,
                s.email,
                s.phone,
                s.gender,
                c.course_code,
                c.course_name,
                s.year_of_study,
                s.date_of_birth,
                s.admission_date
            FROM students s
            INNER JOIN courses c ON s.course_id = c.id
            {where_clause}
            ORDER BY s.id ASC
        """
        rows = execute_query(sql, tuple(params))

        # Build in-memory CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write CSV header row
        writer.writerow([
            'Student ID', 'Full Name', 'Registration Number', 'Email',
            'Phone', 'Gender', 'Course Code', 'Course Name',
            'Year of Study', 'Date of Birth', 'Date of Admission'
        ])

        # Write data rows
        for row in rows:
            writer.writerow([
                row['id'],
                row['full_name'],
                row['registration_number'],
                row['email'],
                row['phone'],
                row['gender'],
                row['course_code'],
                row['course_name'],
                f"Year {row['year_of_study']}",
                str(row['date_of_birth']),
                str(row['admission_date'])
            ])

        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=students_directory.csv"}
        )

    except Error as err:
        flash(f"Error generating CSV export: {err}", "error")
        return redirect(url_for('view_students'))


# ==============================================================================
# ROUTE 3: Add Student (Registration Form & Processing)
# HTTP Methods: GET (display form with course options), POST (process registration)
# ==============================================================================
@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    """
    Handles student registration.
    - GET: Loads available courses for the dropdown and displays the registration form.
    - POST: Validates all inputs, verifies uniqueness of email & registration number,
            and executes a parameterized INSERT query.
    """
    # 1. Fetch available courses for the dropdown (needed for both GET and invalid POST)
    courses = []
    try:
        courses = execute_query("SELECT id, course_name, course_code FROM courses ORDER BY course_name ASC")
    except Error as err:
        flash(f"Error loading course list from database: {err}", "error")

    if request.method == 'POST':
        # 2. Extract and sanitize all submitted form values
        full_name = request.form.get('full_name', '').strip()
        registration_number = request.form.get('registration_number', '').strip().upper()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        gender = request.form.get('gender', '').strip()
        course_id = request.form.get('course_id', '').strip()
        year_of_study = request.form.get('year_of_study', '').strip()
        date_of_birth = request.form.get('date_of_birth', '').strip()
        admission_date = request.form.get('admission_date', '').strip()

        # Dictionary to pass back entered values if validation fails (preserves user inputs)
        form_data = {
            'full_name': full_name,
            'registration_number': registration_number,
            'email': email,
            'phone': phone,
            'gender': gender,
            'course_id': course_id,
            'year_of_study': year_of_study,
            'date_of_birth': date_of_birth,
            'admission_date': admission_date
        }

        # 3. Comprehensive Server-Side Validation
        # A. Required fields check
        required_fields = [
            ('Full Name', full_name),
            ('Registration Number', registration_number),
            ('Email Address', email),
            ('Phone Number', phone),
            ('Gender', gender),
            ('Course', course_id),
            ('Year of Study', year_of_study),
            ('Date of Birth', date_of_birth),
            ('Date of Admission', admission_date)
        ]
        missing_fields = [label for label, val in required_fields if not val]
        if missing_fields:
            flash(f"Please fill in all required fields: {', '.join(missing_fields)}.", "error")
            return render_template('add_student.html', courses=courses, form=form_data)

        # B. Validate year of study
        try:
            year_int = int(year_of_study)
            if year_int < 1 or year_int > 8:
                flash("Year of study must be a number between 1 and 8.", "error")
                return render_template('add_student.html', courses=courses, form=form_data)
        except ValueError:
            flash("Year of study must be a valid whole number.", "error")
            return render_template('add_student.html', courses=courses, form=form_data)

        # C. Validate course_id exists
        try:
            course_check = execute_query("SELECT id FROM courses WHERE id = %s", (course_id,), fetch_one=True)
            if not course_check:
                flash("Selected course is invalid. Please select an existing course.", "error")
                return render_template('add_student.html', courses=courses, form=form_data)
        except Error as err:
            flash(f"Database error verifying course: {err}", "error")
            return render_template('add_student.html', courses=courses, form=form_data)

        # D. Check for duplicate registration_number or email
        try:
            duplicate = execute_query(
                "SELECT registration_number, email FROM students WHERE registration_number = %s OR email = %s",
                (registration_number, email),
                fetch_one=True
            )
            if duplicate:
                if duplicate['registration_number'] == registration_number:
                    flash(f"A student with Registration Number '{registration_number}' is already registered.", "error")
                else:
                    flash(f"A student with Email Address '{email}' is already registered.", "error")
                return render_template('add_student.html', courses=courses, form=form_data)

            # 4. Insert new student using parameterized query
            insert_query = """
                INSERT INTO students (
                    full_name, registration_number, email, phone, gender,
                    course_id, year_of_study, date_of_birth, admission_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                full_name,
                registration_number,
                email,
                phone,
                gender,
                int(course_id),
                year_int,
                date_of_birth,
                admission_date
            )
            result = execute_commit(insert_query, params)
            new_id = result.get('lastrowid')

            flash(f"Student '{full_name}' was registered successfully (ID: #{new_id})!", "success")
            return redirect(url_for('view_students'))

        except Error as err:
            flash(f"Database error while saving student: {err}", "error")
            return render_template('add_student.html', courses=courses, form=form_data)

    # GET Request: Initial blank form
    return render_template('add_student.html', courses=courses, form={})


# ==============================================================================
# ROUTE 5: Student Profile / Details
# HTTP Method: GET
# ==============================================================================
@app.route('/students/<int:id>')
def student_details(id):
    """
    Displays the full profile and details for a single student.
    Fetches student attributes joined with course details.
    """
    try:
        query = """
            SELECT 
                s.id,
                s.full_name,
                s.registration_number,
                s.email,
                s.phone,
                s.gender,
                s.year_of_study,
                s.date_of_birth,
                s.admission_date,
                s.created_at,
                c.id AS course_id,
                c.course_name,
                c.course_code
            FROM students s
            INNER JOIN courses c ON s.course_id = c.id
            WHERE s.id = %s
        """
        student = execute_query(query, (id,), fetch_one=True)

        if not student:
            flash(f"Student with ID #{id} was not found.", "warning")
            return redirect(url_for('view_students'))

        return render_template('student_details.html', student=student)

    except Error as err:
        flash(f"Database error loading student details: {err}", "error")
        return redirect(url_for('view_students'))


# ==============================================================================
# ROUTE 6: Edit Student Information
# HTTP Methods: GET (display form pre-populated), POST (process updates)
# ==============================================================================
@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    """
    Handles updating an existing student's record.
    - GET: Retrieves existing data from MySQL and renders edit form.
    - POST: Validates input, checks uniqueness against OTHER students,
            and executes a parameterized UPDATE statement.
    """
    # 1. Verify student exists
    student = None
    courses = []
    try:
        student = execute_query("SELECT * FROM students WHERE id = %s", (id,), fetch_one=True)
        courses = execute_query("SELECT id, course_name, course_code FROM courses ORDER BY course_name ASC")

        if not student:
            flash(f"Student with ID #{id} was not found.", "warning")
            return redirect(url_for('view_students'))

    except Error as err:
        flash(f"Database error: {err}", "error")
        return redirect(url_for('view_students'))

    if request.method == 'POST':
        # 2. Extract and sanitize submitted values
        full_name = request.form.get('full_name', '').strip()
        registration_number = request.form.get('registration_number', '').strip().upper()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        gender = request.form.get('gender', '').strip()
        course_id = request.form.get('course_id', '').strip()
        year_of_study = request.form.get('year_of_study', '').strip()
        date_of_birth = request.form.get('date_of_birth', '').strip()
        admission_date = request.form.get('admission_date', '').strip()

        # 3. Validation: All fields required
        if not all([full_name, registration_number, email, phone, gender, course_id, year_of_study, date_of_birth, admission_date]):
            flash("All fields are required. Please fill in the complete form.", "error")
            return render_template('edit_student.html', student=student, courses=courses)

        # Validate year of study range
        try:
            year_int = int(year_of_study)
            if year_int < 1 or year_int > 8:
                flash("Year of study must be between 1 and 8.", "error")
                return render_template('edit_student.html', student=student, courses=courses)
        except ValueError:
            flash("Year of study must be a valid number.", "error")
            return render_template('edit_student.html', student=student, courses=courses)

        # Validate duplicate checks (excluding the current student's record using `AND id != %s`)
        try:
            duplicate = execute_query(
                """
                SELECT id, registration_number, email 
                FROM students 
                WHERE (registration_number = %s OR email = %s) AND id != %s
                """,
                (registration_number, email, id),
                fetch_one=True
            )
            if duplicate:
                if duplicate['registration_number'] == registration_number:
                    flash(f"Registration number '{registration_number}' is already taken by another student.", "error")
                else:
                    flash(f"Email '{email}' is already taken by another student.", "error")
                return render_template('edit_student.html', student=student, courses=courses)

            # 4. Parameterized UPDATE query
            update_sql = """
                UPDATE students SET
                    full_name = %s,
                    registration_number = %s,
                    email = %s,
                    phone = %s,
                    gender = %s,
                    course_id = %s,
                    year_of_study = %s,
                    date_of_birth = %s,
                    admission_date = %s
                WHERE id = %s
            """
            params = (
                full_name,
                registration_number,
                email,
                phone,
                gender,
                int(course_id),
                year_int,
                date_of_birth,
                admission_date,
                id
            )
            execute_commit(update_sql, params)
            flash(f"Student '{full_name}' was successfully updated!", "success")
            return redirect(url_for('student_details', id=id))

        except Error as err:
            flash(f"Database error while updating record: {err}", "error")
            return render_template('edit_student.html', student=student, courses=courses)

    # GET Request: Display pre-filled form
    return render_template('edit_student.html', student=student, courses=courses)


# ==============================================================================
# ROUTE 7: Delete Student Record
# HTTP Method: POST
# ==============================================================================
@app.route('/students/delete/<int:id>', methods=['POST'])
def delete_student(id):
    """
    Deletes a student record permanently from MySQL.
    Accepted via POST only to prevent accidental GET-based deletions.
    """
    try:
        # Check student existence before deletion
        student = execute_query("SELECT id, full_name FROM students WHERE id = %s", (id,), fetch_one=True)
        if not student:
            flash("Student record not found or already deleted.", "warning")
            return redirect(url_for('view_students'))

        # Execute parameterized DELETE statement
        execute_commit("DELETE FROM students WHERE id = %s", (id,))
        flash(f"Student '{student['full_name']}' (ID: #{id}) was permanently deleted.", "success")

    except Error as err:
        flash(f"Database error while deleting student: {err}", "error")

    return redirect(url_for('view_students'))


# ==============================================================================
# ROUTE 2: Course Management (List & Add Courses)
# HTTP Methods: GET (display list and form), POST (process new course submission)
# ==============================================================================
@app.route('/courses', methods=['GET', 'POST'])
def view_courses():
    """
    Handles viewing all academic courses and adding a new course.
    - GET: Fetches courses with enrollment counts using LEFT JOIN.
    - POST: Validates and inserts a new course with duplicate checking.
    """
    if request.method == 'POST':
        # 1. Retrieve and sanitize input from the submitted form
        course_name = request.form.get('course_name', '').strip()
        course_code = request.form.get('course_code', '').strip().upper()

        # 2. Server-side validation: Ensure fields are not blank
        if not course_name or not course_code:
            flash("Both Course Name and Course Code are required.", "error")
            return redirect(url_for('view_courses'))

        try:
            # 3. Check for duplicates: Course names and codes must be unique
            existing_course = execute_query(
                "SELECT id, course_name, course_code FROM courses WHERE course_name = %s OR course_code = %s",
                (course_name, course_code),
                fetch_one=True
            )

            if existing_course:
                if existing_course['course_code'] == course_code:
                    flash(f"Course code '{course_code}' is already registered.", "error")
                else:
                    flash(f"Course name '{course_name}' already exists.", "error")
                return redirect(url_for('view_courses'))

            # 4. Insert new course using a parameterized query
            execute_commit(
                "INSERT INTO courses (course_name, course_code) VALUES (%s, %s)",
                (course_name, course_code)
            )
            flash(f"Course '{course_code} - {course_name}' was added successfully!", "success")
            return redirect(url_for('view_courses'))

        except Error as err:
            flash(f"Database error while adding course: {err}", "error")
            return redirect(url_for('view_courses'))

    # GET Request: Fetch all courses and how many students are enrolled in each
    courses = []
    try:
        courses = execute_query(
            """
            SELECT 
                c.id, 
                c.course_name, 
                c.course_code, 
                c.created_at,
                COUNT(s.id) AS enrolled_students
            FROM courses c
            LEFT JOIN students s ON c.id = s.course_id
            GROUP BY c.id, c.course_name, c.course_code, c.created_at
            ORDER BY c.course_name ASC
            """
        )
    except Error as err:
        flash(f"Could not load courses from database: {err}", "error")

    return render_template('courses.html', courses=courses)


# ==============================================================================
# Error Handlers
# ==============================================================================
@app.errorhandler(404)
def not_found(e):
    """Handles HTTP 404 - Not Found errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """Handles HTTP 500 - Internal Server Errors."""
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Run development server
    app.run(debug=Config.DEBUG, host='127.0.0.1', port=5000)

