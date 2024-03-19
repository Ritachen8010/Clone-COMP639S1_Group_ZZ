-- create database
CREATE DATABASE `swimmingclub`;
SHOW DATABASES;

DROP DATABASE `swimmingclub`;

USE `swimmingclub`;

CREATE DATABASE IF NOT EXISTS `swimmingclub`;

-- user table 
CREATE TABLE `users` (
    `user_id` INT AUTO_INCREMENT,
    `username` VARCHAR(255) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `role` ENUM('member', 'instructor', 'manager') NOT NULL,
    `status` ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    PRIMARY KEY (`user_id`)
)AUTO_INCREMENT=1000;

-- members table
CREATE TABLE `members` (
    `member_id` INT AUTO_INCREMENT,
    `user_id` INT NOT NULL UNIQUE,
    `title` VARCHAR(10),
    `first_name` VARCHAR(100) NOT NULL,
    `last_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20),
    `address` TEXT,
    `dob` DATE,
    `occupation` VARCHAR(255),
    `health_info` TEXT,
    `image_profile` VARCHAR(500),
    `join_date` DATE,
    PRIMARY KEY (`member_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
);

-- instructors table
CREATE TABLE `instructors` (
    `instructor_id` INT AUTO_INCREMENT,
    `user_id` INT NOT NULL UNIQUE,
    `title` VARCHAR(10),
    `first_name` VARCHAR(100) NOT NULL,
    `last_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20),
    `position` VARCHAR(100) DEFAULT 'instructor',
    `experience` TEXT,
    `bio` TEXT,
    `hire_date` DATE,
    PRIMARY KEY (`instructor_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
);

-- managers table
CREATE TABLE `managers` (
    `manager_id` INT AUTO_INCREMENT,
    `user_id` INT NOT NULL UNIQUE,
    `title` VARCHAR(10),
    `first_name` VARCHAR(100) NOT NULL,
    `last_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20),
    `position` VARCHAR(255),
    `hire_date` DATE,
    PRIMARY KEY (`manager_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
);

-- memeberships table
CREATE TABLE `memberships` (
    `membership_id` INT AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `type` ENUM('annual', 'monthly') NOT NULL,
    `start_date` DATE NOT NULL,
    `end_date` DATE NOT NULL,
    `membership_fee` DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (`membership_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
);

-- membership_payments table
CREATE TABLE `membership_payments` (
    `payment_id` INT AUTO_INCREMENT,
    `member_id` INT NOT NULL,
    `membership_id` INT NOT NULL,
    `amount` DECIMAL(10,2) NOT NULL,
    `payment_date` DATE NOT NULL,
    PRIMARY KEY (`payment_id`),
    FOREIGN KEY (`member_id`) REFERENCES `members`(`member_id`) ON DELETE CASCADE,
    FOREIGN KEY (`membership_id`) REFERENCES `memberships`(`membership_id`) ON DELETE CASCADE
);

-- group_classes table
CREATE TABLE `group_classes` (
    `class_id` INT AUTO_INCREMENT,
    `instructor_id` INT,
    `class_name` VARCHAR(50) NOT NULL,
    `description` TEXT,
    `pool_type`  VARCHAR(10) DEFAULT 'deep',
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    `date` DATE NOT NULL,
    `capacity` INT NOT NULL,
    PRIMARY KEY (`class_id`),
    FOREIGN KEY (`instructor_id`) REFERENCES `instructors`(`instructor_id`)
);

-- one_to_one_lessons table
CREATE TABLE `one_to_one_lessons` (
    `lesson_id` INT AUTO_INCREMENT,
    `instructor_id` INT,
    `description` TEXT,
    `lane_number` INT NOT NULL,
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    `date` DATE NOT NULL,
    `capacity` INT NOT NULL DEFAULT 1,
    PRIMARY KEY (`lesson_id`),
    FOREIGN KEY (`instructor_id`) REFERENCES `instructors`(`instructor_id`) ON DELETE SET NULL
);

-- bookings table
CREATE TABLE `bookings` (
    `booking_id` INT AUTO_INCREMENT,
    `member_id` INT NOT NULL,
    `class_id` INT,
    `lesson_id` INT,
    `schedule_type` ENUM('group_class', 'one_to_one_lesson') NOT NULL,
    `booking_status` ENUM('confirmed', 'cancelled') NOT NULL,
    `booking_date` DATE NOT NULL,
    `booking_time` TIME NOT NULL,
    PRIMARY KEY (`booking_id`),
    FOREIGN KEY (`member_id`) REFERENCES `members`(`member_id`) ON DELETE CASCADE,
    FOREIGN KEY (`lesson_id`) REFERENCES `one_to_one_lessons`(`lesson_id`) ON DELETE CASCADE,
    FOREIGN KEY (`class_id`) REFERENCES `group_classes`(`class_id`) ON DELETE CASCADE
);

-- extra lesson_payments table
CREATE TABLE `lesson_payments` (
    `payment_id` INT AUTO_INCREMENT,
    `member_id` INT NOT NULL,
    `lesson_id` INT NOT NULL,
    `amount` DECIMAL(10,2) NOT NULL,
    `payment_date` DATE NOT NULL,
    PRIMARY KEY (`payment_id`),
    FOREIGN KEY (`member_id`) REFERENCES `members`(`member_id`) ON DELETE CASCADE,
    FOREIGN KEY (`lesson_id`) REFERENCES `one_to_one_lessons`(`lesson_id`) ON DELETE CASCADE
);

-- attendance_for_classes table
CREATE TABLE `attendance_for_classes` (
    `attendance_id` INT AUTO_INCREMENT,
    `class_id` INT NOT NULL,
    `member_id` INT NOT NULL,
    `attended` BOOLEAN NOT NULL,
    `attendance_status` ENUM('present', 'absent', 'late') NOT NULL,
    PRIMARY KEY (`attendance_id`),
    FOREIGN KEY (`class_id`) REFERENCES `group_classes`(`class_id`) ON DELETE CASCADE,
    FOREIGN KEY (`member_id`) REFERENCES `members`(`member_id`) ON DELETE CASCADE
);

-- attendance_for_lessons table
CREATE TABLE `attendance_for_lessons` (
    `attendance_id` INT AUTO_INCREMENT,
    `lesson_id` INT NOT NULL,
    `member_id` INT NOT NULL,
    `attended` BOOLEAN NOT NULL,
    `attendance_status` ENUM('present', 'absent', 'late') NOT NULL,
    PRIMARY KEY (`attendance_id`),
    FOREIGN KEY (`lesson_id`) REFERENCES `one_to_one_lessons`(`lesson_id`) ON DELETE CASCADE,
    FOREIGN KEY (`member_id`) REFERENCES `members`(`member_id`) ON DELETE CASCADE
);

-- news table
CREATE TABLE `news` (
    `news_id` INT AUTO_INCREMENT,
    `manager_id` INT,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NOT NULL,
    `publication_date` DATE NOT NULL,
    `image_id` INT,
    `user_id` INT,
    PRIMARY KEY (`news_id`),
    FOREIGN KEY (`image_id`) REFERENCES `images`(`image_id`) ON DELETE SET NULL,
    FOREIGN KEY (`manager_id`) REFERENCES `managers`(`manager_id`)
);

-- images table
CREATE TABLE `images` (
    `image_id` INT AUTO_INCREMENT,
    `image_data` VARCHAR(500),
    PRIMARY KEY (`image_id`)
);

-- settings table
CREATE TABLE `settings` (
    `setting_id` INT AUTO_INCREMENT,
    `manager_id` INT,
    `setting_type` ENUM('general', 'fee', 'schedule') NOT NULL,
    `setting_name` VARCHAR(100) NOT NULL,
    `setting_value` TEXT NOT NULL,
    `description` TEXT,
    PRIMARY KEY (`setting_id`),
    FOREIGN KEY (`manager_id`) REFERENCES `managers`(`manager_id`)
);

