-- =========================================================
-- Database Schema for Student Management System
-- Database Engine: MySQL
-- =========================================================

-- 1. Create the database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS student_management
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- 2. Select the database for use
USE student_management;

-- 3. Drop existing tables if re-initializing (dropping child table first)
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS courses;

-- 4. Create 'courses' table (Parent Table)
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL UNIQUE,
    course_code VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Create 'students' table (Child Table)
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    registration_number VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(30) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    course_id INT NOT NULL,
    year_of_study INT NOT NULL,
    date_of_birth DATE NOT NULL,
    admission_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_students_courses 
        FOREIGN KEY (course_id) 
        REFERENCES courses(id) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================
-- Initial Seed Data for Testing & Learning
-- =========================================================

-- Insert sample courses
INSERT INTO courses (course_name, course_code) VALUES
('Bachelor of Science in Computer Science', 'CS101'),
('Bachelor of Science in Information Technology', 'IT102'),
('Bachelor of Science in Data Science', 'DS103'),
('Bachelor of Business Administration', 'BBA201'),
('Bachelor of Mechanical Engineering', 'ME301');

-- Insert sample students
INSERT INTO students (
    full_name, registration_number, email, phone, gender, course_id, year_of_study, date_of_birth, admission_date
) VALUES
('Alex Morgan', 'REG2024001', 'alex.morgan@university.edu', '+1-555-0101', 'Male', 1, 2, '2004-05-14', '2023-09-01'),
('Sophia Chen', 'REG2024002', 'sophia.chen@university.edu', '+1-555-0102', 'Female', 1, 3, '2003-11-20', '2022-09-01'),
('Liam Johnson', 'REG2024003', 'liam.johnson@university.edu', '+1-555-0103', 'Male', 2, 1, '2005-02-18', '2024-09-01'),
('Emma Williams', 'REG2024004', 'emma.williams@university.edu', '+1-555-0104', 'Female', 3, 2, '2004-08-30', '2023-09-01'),
('Noah Patel', 'REG2024005', 'noah.patel@university.edu', '+1-555-0105', 'Male', 4, 4, '2002-04-12', '2021-09-01');

