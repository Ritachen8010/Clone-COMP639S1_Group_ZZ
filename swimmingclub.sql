-- create database
CREATE DATABASE `swimmingclub`;
SHOW DATABASES;

DROP DATABASE `swimmingclub`;

USE `swimmingclub`;

CREATE DATABASE IF NOT EXISTS swimmingclub;

-- user table 
CREATE TABLE `users` (
    `user_id` INT AUTO_INCREMENT,
    `instructor_id` INT,
    `username` VARCHAR(255) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('member', 'instructor', 'manager') NOT NULL,
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
    PRIMARY KEY (`user_id`)
)AUTO_INCREMENT=1000;

-- instructors table
CREATE TABLE `instructors` (
    `instructor_id` INT AUTO_INCREMENT,
    `user_id` INT UNIQUE NOT NULL,
    `experience` TEXT,
    `bio` TEXT,
    PRIMARY KEY (`instructor_id`),
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

-- setting table
CREATE TABLE `settings` (
    `setting_id` INT AUTO_INCREMENT,
    `setting_type` ENUM('general', 'fee', 'schedule') NOT NULL,
    `setting_name` VARCHAR(100) NOT NULL,
    `setting_value` TEXT NOT NULL,
    `description` TEXT,
    PRIMARY KEY (`setting_id`)
);

-- group class schedule
CREATE TABLE `class_schedule` (
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

-- one to one class
CREATE TABLE `lesson_schedule` (
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

-- booking table
CREATE TABLE `bookings` (
    `booking_id` INT AUTO_INCREMENT,
    `user_id` INT,
    `class_id` INT,
    `lesson_id` INT,
    `schedule_type` ENUM('class', 'lesson') NOT NULL,
    `booking_status` ENUM('confirmed', 'cancelled') NOT NULL,
    `booking_date` DATE NOT NULL,
	PRIMARY KEY (`booking_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`lesson_id`) REFERENCES `lesson_schedule`(`lesson_id`) ON DELETE CASCADE,
    FOREIGN KEY (`class_id`) REFERENCES `class_schedule`(`class_id`) ON DELETE CASCADE
);

-- payment table
CREATE TABLE `payments` (
    `payment_id` INT AUTO_INCREMENT,
    `user_id` INT,
    `payment_type` ENUM('membership', 'extra lesson') NOT NULL,
    `amount` DECIMAL(10,2) NOT NULL,
    `payment_date` DATE NOT NULL,
    PRIMARY KEY (`payment_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE 
);

-- news table
CREATE TABLE `news` (
    `news_id` INT AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NOT NULL,
    `publication_date` DATE NOT NULL,
    `image_id` INT,
    `user_id` INT,
    PRIMARY KEY (`news_id`),
    FOREIGN KEY (`image_id`) REFERENCES `images`(`image_id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE RESTRICT
);

-- image table
CREATE TABLE `images` (
    `image_id` INT AUTO_INCREMENT,
    `image_data` VARCHAR(500),
	PRIMARY KEY (`image_id`)
);

-- attendance table 
CREATE TABLE `attendance` (
    `attendance_id` INT AUTO_INCREMENT,
    `schedule_id` INT NOT NULL,
    `schedule_type` ENUM('class', 'lesson') NOT NULL,
    `user_id` INT NOT NULL,
    `attended` BOOLEAN NOT NULL,
	`attendance_status` ENUM('present', 'absent', 'late') NOT NULL,
    PRIMARY KEY (`attendance_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
);

