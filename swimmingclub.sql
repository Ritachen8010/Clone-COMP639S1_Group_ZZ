-- Drop existing swimmingclub schema if exists
DROP SCHEMA IF EXISTS swimmingclub;
CREATE SCHEMA swimmingclub;
USE swimmingclub;

-- User table with modified columns
CREATE TABLE IF NOT EXISTS `user` (
    `user_id` INT AUTO_INCREMENT,
    `Username` VARCHAR(255) NOT NULL UNIQUE,
    `Password` VARCHAR(255) NOT NULL,
    `UserType` ENUM('member', 'instructor', 'manager') NOT NULL,
    PRIMARY KEY (`user_id`)
)AUTO_INCREMENT=1000;

-- Manager table
CREATE TABLE IF NOT EXISTS `manager` (
    `manager_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT UNIQUE NOT NULL,
    `title` VARCHAR(10),
    `first_name` VARCHAR(100) NOT NULL,
    `last_name` VARCHAR(100) NOT NULL, 
    `email` VARCHAR(255),
    `phone` VARCHAR(20),
    `address` TEXT,
    `dob` DATE,
    `occupation` VARCHAR(255),
    `position`  VARCHAR(255),
    `health_info` TEXT,
    `image_profile` VARCHAR(500),
    `join_date` DATE,
    `status` ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
);

-- Instructor table
CREATE TABLE IF NOT EXISTS `instructor` (
    `instructor_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT UNIQUE NOT NULL,
    `title` VARCHAR(10),
    `first_name` VARCHAR(100) NOT NULL,
    `last_name` VARCHAR(100) NOT NULL, 
    `email` VARCHAR(255),
    `phone` VARCHAR(20),
    `address` TEXT,
    `dob` DATE,
    `occupation` VARCHAR(255),
    `position`  VARCHAR(255),
    `health_info` TEXT,
    `image_profile` VARCHAR(500),
    `join_date` DATE,
    `status` ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
);

-- Member table
CREATE TABLE IF NOT EXISTS `member` (
    `member_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT UNIQUE NOT NULL,
    `title` VARCHAR(10),
    `first_name` VARCHAR(100) NOT NULL,
    `last_name` VARCHAR(100) NOT NULL, 
    `email` VARCHAR(255),
    `phone` VARCHAR(20),
    `address` TEXT,
    `dob` DATE,
    `occupation` VARCHAR(255),
    `position`  VARCHAR(255),
    `health_info` TEXT,
    `image_profile` VARCHAR(500),
    `join_date` DATE,
    `status` ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
);

-- Membership table
CREATE TABLE IF NOT EXISTS `memberships` (
    `membership_id` INT AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `type` ENUM('annual', 'monthly') NOT NULL,
    `start_date` DATE NOT NULL,
    `end_date` DATE NOT NULL,
    `membership_fee` DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (`membership_id`),
    FOREIGN KEY (`user_id`) REFERENCES `member`(`user_id`) ON DELETE CASCADE
);

-- Image table
CREATE TABLE IF NOT EXISTS `images` (
    `image_id` INT PRIMARY KEY AUTO_INCREMENT,
    `image_data` VARCHAR(500)
);

-- News table
CREATE TABLE IF NOT EXISTS `news` (
    `news_id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NOT NULL,
    `publication_date` DATE NOT NULL,
    `image_id` INT,
    `user_id` INT,
    FOREIGN KEY (`image_id`) REFERENCES `images`(`image_id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE RESTRICT
);

-- Instructors table
CREATE TABLE IF NOT EXISTS `instructors` (
    `instructor_id` INT AUTO_INCREMENT,
    `user_id` INT UNIQUE NOT NULL,
    `experience` TEXT,
    `bio` TEXT,
    PRIMARY KEY (`instructor_id`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
);

-- Settings table
CREATE TABLE IF NOT EXISTS `settings` (
    `setting_id` INT AUTO_INCREMENT,
    `setting_type` ENUM('general', 'fee', 'schedule') NOT NULL,
    `setting_name` VARCHAR(100) NOT NULL,
    `setting_value` TEXT NOT NULL,
    `description` TEXT,
    PRIMARY KEY (`setting_id`)
);

-- Class schedule table
CREATE TABLE IF NOT EXISTS `class_schedule` (
    `class_id` INT AUTO_INCREMENT,
    `name` ENUM('zumba', 'aqua fit', 'low-impact', 'mums', 'babies') NOT NULL,
    `description` TEXT,
    `instructor_id` INT,
    `pool_type` ENUM('deep', 'lane') NOT NULL,
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    `date` DATE NOT NULL,
    `capacity` INT NOT NULL DEFAULT 15,
    PRIMARY KEY (`class_id`),
    FOREIGN KEY (`instructor_id`) REFERENCES `instructors`(`instructor_id`) ON DELETE CASCADE
);

-- Lesson schedule table
CREATE TABLE IF NOT EXISTS `lesson_schedule` (
    `lesson_id` INT AUTO_INCREMENT,
    `instructor_id` INT,
    `description` TEXT,
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    `date` DATE NOT NULL,
    `lane_number` INT NOT NULL,
    `capacity` INT NOT NULL DEFAULT 1,
    PRIMARY KEY (`lesson_id`),
    FOREIGN KEY (`instructor_id`) REFERENCES `instructors`(`instructor_id`) ON DELETE CASCADE
);

-- Booking table
CREATE TABLE IF NOT EXISTS `bookings` (
    `booking_id` INT PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT,
    `class_schedule_id` INT,
    `lesson_schedule_id` INT,
    `schedule_type` ENUM('class', 'lesson') NOT NULL,
    `booking_status` ENUM('confirmed', 'cancelled') NOT NULL,
    `booking_date` DATE NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`lesson_schedule_id`) REFERENCES `lesson_schedule`(`lesson_id`) ON DELETE CASCADE,
    FOREIGN KEY (`class_schedule_id`) REFERENCES `class_schedule`(`class_id`) ON DELETE CASCADE
);

-- Payment table
CREATE TABLE IF NOT EXISTS `payments` (
    `payment_id` INT PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT,
    `payment_type` ENUM('membership', 'class', 'lesson') NOT NULL,
    `amount` DECIMAL(10,2) NOT NULL,
    `payment_date` DATE NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE 
);

-- Attendance table 
CREATE TABLE IF NOT EXISTS `attendance` (
    `attendance_id` INT PRIMARY KEY AUTO_INCREMENT,
    `schedule_id` INT NOT NULL,
    `schedule_type` ENUM('class', 'lesson') NOT NULL,
    `user_id` INT NOT NULL,
    `attended` BOOLEAN NOT NULL,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
);

-- Populate data as required
INSERT INTO `user` (Username, Password, UserType) VALUES 
('manager001', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'manager'),
('instructor001', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'instructor'),
('instructor002', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'instructor'),
('instructor003', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'instructor'),
('member001', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member002', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member003', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member');

INSERT INTO `manager` (user_id, title, first_name, last_name, email, phone, address, dob, occupation, position, health_info, image_profile, join_date, status) VALUES
(1000, 'Mr', 'John', 'Doe', 'john@example.com', '1234567890', '123 Manager St, City', '1980-01-01', 'Manager', 'Senior Manager', 'No health issues', 'profile_image.jpg', '2020-01-01', 'active');

INSERT INTO `instructor` (user_id, title, first_name, last_name, email, phone, address, dob, occupation, position, health_info, image_profile, join_date, status) VALUES
(1001, 'Mrs', 'Jane', 'Doe', 'jane@example.com', '1234567890', '123 Instructor St, City', '1985-01-01', 'Instructor', 'Senior Instructor', 'No health issues', 'profile_image.jpg', '2020-01-01', 'active'),
(1002, 'Mr', 'Tom', 'Smith', 'tom@example.com', '1234567890', '123 Instructor St, City', '1987-01-01', 'Instructor', 'Junior Instructor', 'No health issues', 'profile_image.jpg', '2020-02-01', 'active'),
(1003, 'Miss', 'Emily', 'Brown', 'emily@example.com', '1234567890', '123 Instructor St, City', '1988-01-01', 'Instructor', 'Assistant Instructor', 'No health issues', 'profile_image.jpg', '2020-03-01', 'active');

INSERT INTO `member` (user_id, title, first_name, last_name, email, phone, address, dob, occupation, position, health_info, image_profile, join_date, status) VALUES
(1004, 'Mr', 'Michael', 'Johnson', 'michael@example.com', '1234567890', '123 Member St, City', '1990-01-01', 'Engineer', 'Senior Engineer', 'No health issues', 'profile_image.jpg', '2020-01-01', 'active'),
(1005, 'Mrs', 'Sarah', 'Williams', 'sarah@example.com', '1234567890', '123 Member St, City', '1992-01-01', 'Teacher', 'Senior Teacher', 'No health issues', 'profile_image.jpg', '2020-02-01', 'active'),
(1006, 'Mr', 'Chris', 'Jones', 'chris@example.com', '1234567890', '123 Member St, City', '1995-01-01', 'Student', 'Senior Student', 'No health issues', 'profile_image.jpg', '2020-03-01', 'active');
