# Student Management System

A beginner-friendly but professionally designed web application for managing academic student records and course enrollments, built with **Python Flask**, **MySQL**, **mysql-connector-python**, **HTML5**, **CSS3**, and **Bootstrap 5**.

This project demonstrates **raw SQL query execution** without any ORM (like SQLAlchemy), illustrating fundamental concepts of relational database design, foreign keys, parameterized queries, and web application architecture.

---

## 1. Technology Stack

- **Backend Framework:** Python Flask 3.x
- **Database Engine:** MySQL Server 8.x
- **Database Driver:** `mysql-connector-python` (Official Oracle driver)
- **Frontend Framework:** Bootstrap 5.3 & Bootstrap Icons
- **Templating Engine:** Jinja2
- **Configuration & Security:** `python-dotenv`
- **Development Tools:** VS Code & MySQL Workbench

---

## 2. System Architecture

The application adopts the classic **3-Tier Model-View-Controller (MVC)** architectural pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Browser                        │
│      (HTML5, CSS3, Bootstrap 5, Jinja2 Rendered Pages)      │
└──────────────────────────────▲──────────────────────────────┘
                               │ HTTP Requests (GET / POST)
                               │ HTTP Responses (HTML Pages)
┌──────────────────────────────▼──────────────────────────────┐
│                    Flask Backend (app.py)                   │
│   - Routes & Request Handlers                               │
│   - Form Validation & Sanitization                          │
│   - Flash Notifications & Session Alerts                    │
│   - Jinja2 Template Engine Context Builder                  │
└──────────────────────────────▲──────────────────────────────┘
                               │ Raw SQL with Parameters
                               │ Dict-formatted Record Rows
┌──────────────────────────────▼──────────────────────────────┐
│                  Database Layer (database.py)               │
│   - mysql-connector-python Connection Handler               │
│   - Parameterized Query Execution & Commit / Rollback       │
└──────────────────────────────▲──────────────────────────────┘
                               │ TCP/IP Connection (Port 3306)
┌──────────────────────────────▼──────────────────────────────┐
│                   MySQL Relational Database                 │
│   - Database: student_management                            │
│   - Tables: courses, students (1-to-many relationship)      │
└─────────────────────────────────────────────────────────────┘
```

### Why Raw SQL instead of an ORM?
- **Learn Underlying Mechanics:** Understand how `JOIN`, `GROUP BY`, `FOREIGN KEY`, and transactions actually operate at the database engine level.
- **Direct Query Control:** Inspect exact SQL statements sent across the wire.
- **Security Awareness:** Understand how parameterized queries (`%s`) protect against SQL injection vulnerabilities.

---

## 3. Project Folder Structure

```text
student-management-system/
│
├── app.py                  # Main Flask application and route handlers
├── config.py               # Centralized configuration (reads .env variables)
├── database.py             # Reusable MySQL connection & query helper functions
├── requirements.txt        # Python library dependencies
├── schema.sql              # Database creation and sample seed data
├── README.md               # Setup and architecture documentation
├── .env.example            # Environment variables template
├── .env                    # Local credentials file (git-ignored)
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Master layout (sidebar navigation, navbar, alerts)
│   ├── dashboard.html      # Metrics, overview cards, recently added students
│   ├── students.html       # Student directory table with search bar
│   ├── add_student.html    # Student registration form
│   ├── edit_student.html   # Student edit form with pre-filled values
│   ├── student_details.html# Comprehensive single-student profile view
│   ├── courses.html        # Courses directory and quick-add form
│   ├── 404.html            # Custom Page Not Found error page
│   └── 500.html            # Custom Server Error page
│
└── static/                 # Static assets
    ├── css/
    │   └── style.css       # Clean SaaS dashboard styling
    └── js/
        └── script.js       # Client-side helpers (sidebar toggle, delete modal)
```

---

## 4. Database Schema & Design

The database `student_management` consists of two relational tables:

### 1. `courses` (Parent Table)
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique course ID |
| `course_name` | `VARCHAR(150)` | `NOT NULL`, `UNIQUE` | Full title of the degree program |
| `course_code` | `VARCHAR(50)` | `NOT NULL`, `UNIQUE` | Academic code (e.g., `CS101`) |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Record creation timestamp |

### 2. `students` (Child Table)
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique student ID |
| `full_name` | `VARCHAR(150)` | `NOT NULL` | Student's full legal name |
| `registration_number`| `VARCHAR(50)` | `NOT NULL`, `UNIQUE` | Academic matriculation roll number |
| `email` | `VARCHAR(150)` | `NOT NULL`, `UNIQUE` | Student's email address |
| `phone` | `VARCHAR(30)` | `NOT NULL` | Contact telephone number |
| `gender` | `ENUM` | `'Male', 'Female', 'Other'` | Student gender |
| `course_id` | `INT` | `NOT NULL`, `FOREIGN KEY` | References `courses(id)` |
| `year_of_study` | `INT` | `NOT NULL` | Current academic year (1 - 8) |
| `date_of_birth` | `DATE` | `NOT NULL` | Birth date |
| `admission_date` | `DATE` | `NOT NULL` | Enrollment date |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Record creation timestamp |

### Relational Integrity
- **One-to-Many Relationship:** One course can have many enrolled students (`courses.id` 1 ──< `students.course_id`).
- **`ON DELETE RESTRICT`:** Prevents an administrator from deleting a course if students are actively enrolled in it.

---

## 5. Step-by-Step Installation & Setup

### Step 1: Open the Project in VS Code
Open VS Code and navigate to the project directory:
```bash
cd "d:\student management system - python"
```

### Step 2: Create and Activate a Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
python -m venv venv
.\venv\Scripts\activate.bat
```

### Step 3: Install Required Packages
```bash
pip install -r requirements.txt
```

### Step 4: Initialize the Database in MySQL Workbench
1. Launch **MySQL Workbench** and open your MySQL connection (default port `3306`).
2. Go to **File -> Open SQL Script...** and select `schema.sql` from this project folder.
3. Click the **Execute (lightning bolt icon)** to run the entire script.
4. This creates the `student_management` database, tables, foreign keys, and inserts sample starter records.

### Step 5: Configure Environment Variables
Open the `.env` file in the project root and enter your MySQL root password:
```ini
FLASK_SECRET_KEY=sms-dev-secret-key-998877665544
FLASK_DEBUG=True

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_actual_mysql_password_here
DB_NAME=student_management
DB_PORT=3306
```

### Step 6: Test Database Connectivity
Run the test utility built into `database.py`:
```bash
python database.py
```
If configured correctly, you will see:
```text
SUCCESS: Connected to MySQL Server version 8.0.x
Active database: student_management
```

### Step 7: Run the Flask Application
```bash
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 6. Route & Query Reference

| Route | Method | Purpose | Raw SQL Query Executed |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Admin Dashboard | `SELECT COUNT(*) AS total FROM students`<br>`SELECT COUNT(*) AS total FROM courses`<br>`SELECT s.*, c.course_name, c.course_code FROM students s INNER JOIN courses c ON s.course_id = c.id ORDER BY s.id DESC LIMIT 5` |
| `/courses` | `GET` | View Courses & Enrollments | `SELECT c.id, c.course_name, c.course_code, COUNT(s.id) AS enrolled_students FROM courses c LEFT JOIN students s ON c.id = s.course_id GROUP BY c.id, c.course_name, c.course_code ORDER BY c.course_name ASC` |
| `/courses` | `POST` | Add New Course | `SELECT id FROM courses WHERE course_name = %s OR course_code = %s`<br>`INSERT INTO courses (course_name, course_code) VALUES (%s, %s)` |
| `/students/add` | `GET` | Registration Form | `SELECT id, course_name, course_code FROM courses ORDER BY course_name ASC` |
| `/students/add` | `POST` | Process Registration | `SELECT registration_number, email FROM students WHERE registration_number = %s OR email = %s`<br>`INSERT INTO students (...) VALUES (%s, %s, ...)` |
| `/students` | `GET` | Student Directory & Search | `SELECT s.*, c.course_name, c.course_code FROM students s INNER JOIN courses c ON s.course_id = c.id WHERE (s.full_name LIKE %s OR s.registration_number LIKE %s OR s.email LIKE %s) ORDER BY s.id DESC` |
| `/students/<id>` | `GET` | Student Profile | `SELECT s.*, c.course_name, c.course_code FROM students s INNER JOIN courses c ON s.course_id = c.id WHERE s.id = %s` |
| `/students/edit/<id>` | `GET` | Edit Form Pre-fill | `SELECT * FROM students WHERE id = %s`<br>`SELECT id, course_name, course_code FROM courses ORDER BY course_name ASC` |
| `/students/edit/<id>` | `POST` | Save Student Updates | `SELECT id FROM students WHERE (registration_number = %s OR email = %s) AND id != %s`<br>`UPDATE students SET full_name = %s, ... WHERE id = %s` |
| `/students/delete/<id>` | `POST` | Delete Student Record | `DELETE FROM students WHERE id = %s` |

---

## 7. Security Best Practices Implemented

1. **Parameterized Queries (`%s`):**
   User inputs are never concatenated directly into SQL strings. The MySQL driver escapes and sanitizes inputs separately, preventing SQL Injection.
2. **Environment Isolation:**
   Database credentials and session secrets are managed via `.env` and loaded using `python-dotenv`.
3. **HTTP Verb Safety for Deletions:**
   Record deletions are strictly restricted to `POST` requests triggered by a modal confirmation form, preventing accidental deletions via web crawler pre-fetching.
4. **Duplicate Prevention:**
   Both application-level validation and database-level `UNIQUE` constraints prevent duplicate matriculation IDs or emails.
5. **Relational Constraints:**
   Foreign key relationships maintain integrity between academic courses and enrolled students.

---

## 8. Common Troubleshooting

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| `Can't connect to MySQL server on 'localhost:3306' (2003)` | MySQL service is stopped. | Open Windows Services (`services.msc`), find **MySQL80**, and click **Start**. |
| `Access denied for user 'root'@'localhost' (1045)` | Incorrect password in `.env`. | Verify your MySQL root password and update `DB_PASSWORD=` in `.env`. |
| `Table 'student_management.students' doesn't exist (1146)` | `schema.sql` was not run. | Open `schema.sql` in MySQL Workbench and execute the script. |
| Port `3306` already in use or custom port | MySQL is running on a non-standard port. | Update `DB_PORT=3307` (or your port) in `.env`. |

