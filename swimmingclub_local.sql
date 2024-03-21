CREATE SCHEMA `swimmingclub`;
USE `swimmingclub`;

DROP DATABASE `swimmingclub`;

-- User table
CREATE TABLE `user` (
    `user_id` INT AUTO_INCREMENT,
    `username` VARCHAR(255) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `usertype` ENUM('member', 'instructor', 'manager') NOT NULL,
    PRIMARY KEY (`user_id`)
)AUTO_INCREMENT=1000;

-- Manager table
CREATE TABLE `manager` (
    `manager_id` INT AUTO_INCREMENT,
    `user_id` INT UNIQUE NOT NULL,
    `title` ENUM('Mr', 'Mrs', 'Miss', 'Dr') NOT NULL,
    `first_name` VARCHAR(100) NOT NULL,
    `last_name` VARCHAR(100) NOT NULL, 
    `email` VARCHAR(255),
    `phone` VARCHAR(20),
    `position`  VARCHAR(255),
    `status` ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    PRIMARY KEY (`manager_id`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`)
)AUTO_INCREMENT=1;

-- Instructor table
CREATE TABLE `instructor` (
    `instructor_id` INT AUTO_INCREMENT,
    `user_id` INT UNIQUE NOT NULL,
    `title` ENUM('Mr', 'Mrs', 'Miss', 'Dr') NOT NULL,
    `first_name` VARCHAR(100) NOT NULL,
    `last_name` VARCHAR(100) NOT NULL, 
    `email` VARCHAR(255),
    `phone` VARCHAR(20),
    `position` VARCHAR(255),
    `bio` TEXT,
    `image_profile` VARCHAR(500),
    `status` ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    PRIMARY KEY (`instructor_id`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`)
)AUTO_INCREMENT=1;

-- Member table
CREATE TABLE `member` (
    `member_id` INT AUTO_INCREMENT,
    `user_id` INT UNIQUE NOT NULL,
    `title` ENUM('Mr', 'Mrs', 'Miss', 'Dr') NOT NULL,
    `first_name` VARCHAR(100) NOT NULL,
    `last_name` VARCHAR(100) NOT NULL, 
    `email` VARCHAR(255),
    `phone` VARCHAR(20),
    `address` TEXT,
    `dob` DATE,
    `occupation` VARCHAR(255),
    `health_info` TEXT,
    `image_profile` VARCHAR(500),
    `status` ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    PRIMARY KEY (`member_id`),
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`)
)AUTO_INCREMENT=1;

-- Membership table
CREATE TABLE `memberships` (
    `membership_id` INT AUTO_INCREMENT,
    `member_id` INT NOT NULL,
    `type` ENUM('Annual', 'Monthly') NOT NULL,
    `start_date` DATE NOT NULL,
    `end_date` DATE NOT NULL,
    `membership_fee` DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (`membership_id`),
    FOREIGN KEY (`member_id`) REFERENCES `member`(`member_id`)
)AUTO_INCREMENT=110111;

-- Image table
CREATE TABLE `images` (
    `image_id` INT AUTO_INCREMENT,
    `image_data` VARCHAR(500),
    `instructor_id` INT,
    `member_id` INT,
    PRIMARY KEY (`image_id`),
    FOREIGN KEY (`instructor_id`) REFERENCES `instructor`(`instructor_id`),
    FOREIGN KEY (`member_id`) REFERENCES `member`(`member_id`)
)AUTO_INCREMENT=1;

-- News table
CREATE TABLE `news` (
    `news_id` INT AUTO_INCREMENT,
    `manager_id` INT,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NOT NULL,
    `publication_date` DATE NOT NULL,
    `image_id` INT,
	PRIMARY KEY (`news_id`),
    FOREIGN KEY (`image_id`) REFERENCES `images`(`image_id`),
    FOREIGN KEY (`manager_id`) REFERENCES `manager`(`manager_id`)
)AUTO_INCREMENT=1;

-- Settings table
CREATE TABLE `settings` (
    `setting_id` INT AUTO_INCREMENT,
    `manager_id` INT,
    `setting_type` ENUM('general', 'fee', 'schedule') NOT NULL,
    `setting_name` VARCHAR(100) NOT NULL,
    `setting_value` TEXT NOT NULL,
    `description` TEXT,
    PRIMARY KEY (`setting_id`),
    FOREIGN KEY (`manager_id`) REFERENCES `manager`(`manager_id`)
)AUTO_INCREMENT=1;

-- Class schedule table
CREATE TABLE `class_schedule` (
    `class_id` INT AUTO_INCREMENT,
    `instructor_id` INT,
    `name` ENUM('Zumba', 'Aqua Fit', 'Low-Impact', 'Mums', 'Babies') NOT NULL,
    `week` ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL,
    `description` TEXT,
    `pool_type` VARCHAR(10) NOT NULL DEFAULT 'Deep',
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    `capacity` INT NOT NULL CHECK (`capacity` >= 1 AND `capacity` <= 15),
    PRIMARY KEY (`class_id`),
    FOREIGN KEY (`instructor_id`) REFERENCES `instructor`(`instructor_id`)
)AUTO_INCREMENT=1;

-- Lesson schedule table
CREATE TABLE `lesson_schedule` (
    `lesson_id` INT AUTO_INCREMENT,
    `instructor_id` INT,
    `name` VARCHAR(255) NOT NULL DEFAULT 'One-on-One Lesson',
    `week` ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL,
    `description` TEXT,
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    `lane_number` INT NOT NULL,
    `capacity` INT NOT NULL DEFAULT 1,
    PRIMARY KEY (`lesson_id`),
    FOREIGN KEY (`instructor_id`) REFERENCES `instructor`(`instructor_id`)
)AUTO_INCREMENT=1;

-- Booking table
CREATE TABLE `bookings` (
    `booking_id` INT AUTO_INCREMENT,
    `member_id` INT,
    `class_id` INT,
    `lesson_id` INT,
    `schedule_type` ENUM('class', 'lesson') NOT NULL,
    `booking_status` ENUM('confirmed', 'cancelled') NOT NULL,
    `booking_date` DATE NOT NULL,
    PRIMARY KEY (`booking_id`),
    FOREIGN KEY (`member_id`) REFERENCES `member`(`member_id`),
    FOREIGN KEY (`lesson_id`) REFERENCES `lesson_schedule`(`lesson_id`),
    FOREIGN KEY (`class_id`) REFERENCES `class_schedule`(`class_id`)
)AUTO_INCREMENT=1;

-- Payment table
CREATE TABLE `payments` (
    `payment_id` INT PRIMARY KEY AUTO_INCREMENT,
    `member_id` INT,
    `membership_id` INT NULL,
    `manager_id` INT,
    `lesson_id` INT NULL,
    `payment_type` ENUM('membership', 'lesson') NOT NULL,
    `amount` DECIMAL(10,2) NOT NULL,
    `payment_date` DATE NOT NULL,
    FOREIGN KEY (`member_id`) REFERENCES `member`(`member_id`),
    FOREIGN KEY (`membership_id`) REFERENCES `memberships`(`membership_id`),
    FOREIGN KEY (`lesson_id`) REFERENCES `lesson_schedule`(`lesson_id`),
    FOREIGN KEY (`manager_id`) REFERENCES `manager`(`manager_id`)
)AUTO_INCREMENT=1;

-- Attendance table 
CREATE TABLE `attendance` (
    `attendance_id` INT AUTO_INCREMENT,
    `class_id` INT NOT NULL,
    `schedule_type` ENUM('class', 'lesson') NOT NULL,
    `member_id` INT NOT NULL,
    `attended` BOOLEAN NOT NULL,
	`attendance_status` ENUM('present', 'absent', 'late') NOT NULL,
    PRIMARY KEY (`attendance_id`),
    FOREIGN KEY (`member_id`) REFERENCES `member`(`member_id`),
    FOREIGN KEY (`class_id`) REFERENCES `class_schedule`(`class_id`)
)AUTO_INCREMENT=1;

-- Populate data as required
-- user
INSERT INTO `user` (`username`, `password`, `usertype`) VALUES 
('manager001', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'manager'),
('manager002', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'manager'),

('instructor001', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'instructor'),
('instructor002', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'instructor'),
('instructor003', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'instructor'),
('instructor004', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'instructor'),
('instructor005', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'instructor'),

('member001', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member002', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member003', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member004', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member005', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member006', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member007', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member008', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member009', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member010', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member011', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member012', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member013', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member014', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member015', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member016', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member017', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member018', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member019', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member'),
('member020', '$2b$12$oMM.xMssDCBOZbLB0vstsO98YNlF4Fj7HHf12GLZUOzFvAOa..KWK', 'member');


INSERT INTO `manager` (`user_id`, `title`, `first_name`, `last_name`, `email`, `phone`, `position`, `status`) VALUES
(1000, 'Mr', 'John', 'Doe', 'john@example.com', '1234567890', 'Senior Manager', 'Active'),
(1001, 'Mr', 'Squidward', 'Tentacles', 'squidward@bikinibottom.net', '1234567890', 'Manager', 'Active');

INSERT INTO `instructor` (`user_id`, `title`, `first_name`, `last_name`, `email`, `phone`, `position`, `bio`, `image_profile`, `status`) VALUES
(1002, 'Mrs', 'Jane', 'Doe', 'jane@example.com', '1234567890', 'Instructor', 
'Jane has a passion for teaching and has been a professional swimming instructor for over 10 years. She specializes in beginner to advanced swimming techniques', 
'profile_image0.jpg', 'Active'),

(1003, 'Mr', 'Tom', 'Smith', 'tom@example.com', '1234567890', 'Instructor', 
'Tom is an enthusiastic aerobics instructor with a deep passion for promoting health and fitness through fun and engaging water aerobics classes. 
With over 5 years of experience in fitness instruction, he specializes in creating dynamic workouts that are accessible to individuals of all skill levels.',
'profile_image.jpg1', 'Active'),

(1004, 'Miss', 'Emily', 'Brown', 'emily@example.com', '1234567890', 'Instructor', 
'Emily brings energy and enthusiasm to water aerobics. With a background in fitness and nutrition, she ensures her classes are fun and effective for all fitness levels.',
'profile_image2.jpg', 'Active'),

(1005, 'Mr', 'Patrick', 'Star', 'patrick@bikinibottom.net', '1234567890', 'Swimming Coach', 
'Best friend of SpongeBob. Loves rock.', 
'patrick.jpg', 'Active'),

(1006, 'Mrs', 'Sandy', 'Cheeks', 'sandy@bikinibottom.net', '1234567890', 'Aquatic Aerobics Instructor', 
'Sandy Cheeks is an energetic squirrel from Texas who lives under the sea in an air dome. A lover of all aquatic sports, 
Sandy is passionate about bringing fitness and fun to Bikini Bottom through her engaging aquatic aerobics classes. 
Her unique approach combines science and sports to provide an unforgettable fitness experience.', 
'sandy_aerobics.jpg', 'Active');


INSERT INTO `member` (`user_id`, `title`, `first_name`, `last_name`, `email`, `phone`, `address`, `dob`, `occupation`, `health_info`, `image_profile`, `status`) VALUES
(1007, 'Mr', 'Michael', 'Johnson', 'michael@example.com', '1234567890', '123 Member St, City', '1990-01-01', 'Engineer', 'No health issues', 'profile_image.jpg', 'Active'),
(1008, 'Mrs', 'Sarah', 'Williams', 'sarah@example.com', '1234567890', '123 Member St, City', '1992-01-01', 'Teacher', 'No health issues', 'profile_image.jpg', 'Active'),
(1009, 'Mr', 'Chris', 'Jones', 'chris@example.com', '1234567890', '123 Member St, City', '1995-01-01', 'Student', 'No health issues', 'profile_image.jpg', 'Active'),
(1010, 'Mrs', 'Velma', 'Dinkley', 'velma@dinkley.com', '1234567891', '124 Mystery Lane', '1980-03-01', 'Detective', 'Healthy', 'velma_image.jpg', 'Active'),
(1011, 'Mr', 'Fred', 'Jones', 'fred@jones.com', '1234567892', '125 Mystery Lane', '1979-02-01', 'Detective', 'Healthy', 'fred_image.jpg', 'Active'),
(1012, 'Mrs', 'Daphne', 'Blake', 'daphne@blake.com', '1234567893', '126 Mystery Lane', '1981-04-01', 'Journalist', 'Healthy', 'daphne_image.jpg', 'Active'),
(1013, 'Mr', 'Shaggy', 'Rogers', 'shaggy@rogers.com', '1234567894', '127 Mystery Lane', '1980-05-01', 'Chef', 'Healthy', 'shaggy_image.jpg', 'Active'),
(1014, 'Mr', 'Scooby', 'Doo', 'scooby@doo.com', '1234567895', '128 Mystery Lane', '1969-09-01', 'Adventurer', 'Healthy', 'scooby_image.jpg', 'Active'),
(1015, 'Mr', 'Homer', 'Simpson', 'homer@simpson.com', '1234567896', '742 Evergreen Terrace', '1956-05-12', 'Safety Inspector', 'Healthy', 'homer_image.jpg', 'Active'),
(1016, 'Mrs', 'Marge', 'Simpson', 'marge@simpson.com', '1234567897', '742 Evergreen Terrace', '1956-10-01', 'Homemaker', 'Healthy', 'marge_image.jpg', 'Active'),
(1017, 'Mr', 'Bart', 'Simpson', 'bart@simpson.com', '1234567898', '742 Evergreen Terrace', '1980-04-01', 'Student', 'Healthy', 'bart_image.jpg', 'Active'),
(1018, 'Mrs', 'Lisa', 'Simpson', 'lisa@simpson.com', '1234567899', '742 Evergreen Terrace', '1981-05-09', 'Student and Musician', 'Healthy', 'lisa_image.jpg', 'Active'),
(1019, 'Mrs', 'Maggie', 'Simpson', 'maggie@simpson.com', '1234567890', '742 Evergreen Terrace', '1989-01-12', 'Baby', 'Healthy', 'maggie_image.jpg', 'Active'),
(1020, 'Mr', 'Goku', 'Son', 'goku@dbz.com', '1234567891', 'Mount Paozu', '737-04-18', 'Martial Artist', 'Super healthy', 'goku_image.jpg', 'Active'),
(1021, 'Mr', 'Naruto', 'Uzumaki', 'naruto@konoha.com', '1234567890', 'Hidden Leaf Village', '1999-10-10', 'Hokage', 'Healthy', 'naruto_image.jpg', 'Active'),
(1022, 'Mr', 'Ash', 'Ketchum', 'ash@pallettown.com', '1234567890', 'Pallet Town', '1996-05-22', 'Pokemon Trainer', 'Healthy', 'ash_image.jpg', 'Active'),
(1023, 'Mrs', 'Diana', 'Prince', 'diana@themyscira.com', '1234567890', 'Themyscira', '1920-03-22', 'Ambassador', 'Super healthy', 'diana_image.jpg', 'Active'),
(1024, 'Mr', 'Tony', 'Stark', 'tony@starkindustries.com', '1234567890', '10880 Malibu Point', '1970-05-29', 'Inventor', 'Healthy', 'tony_image.jpg', 'Active'),
(1025, 'Mr', 'Bruce', 'Wayne', 'bruce@wayneenterprises.com', '1234567890', '1007 Mountain Drive, Gotham', '1939-05-27', 'Businessman', 'Healthy', 'bruce_image.jpg', 'Active'),
(1026, 'Mr', 'Peter', 'Parker', 'peter@dailybugle.com', '1234567890', '20 Ingram Street, Forest Hills', '2001-08-10', 'Photographer', 'Healthy', 'peter_image.jpg', 'Active');


-- Membership
INSERT INTO `memberships` (`member_id`, `type`, `start_date`, `end_date`, `membership_fee`) VALUES
(1, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(2, 'Monthly', '2024-05-01', '2024-05-31', 60.00),
(3, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(4, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(5, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(6, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(7, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(8, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(9, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(10, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(11, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(12, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(13, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(14, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(15, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(16, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(17, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(18, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(19, 'Annual', '2024-05-01', '2025-04-30', 700.00),
(20, 'Monthly', '2024-05-01', '2024-05-31', 60.00);


INSERT INTO `news` (`manager_id`, `title`, `content`, `publication_date`, `image_id`) VALUES
(1, 'Summer Fitness Fiesta', 'Join us for our Summer Fitness Fiesta! Dive into the world of Aqua Aerobics with our special summer lineup designed to boost your fitness 
and beat the heat. From Aqua Zumba to Water Yoga, there’s something for everyone. Enroll now and make a splash in your fitness journey!', 
'2023-05-10', NULL),

(2, 'Expert Talk: The Benefits of Water Aerobics', 'We are excited to announce an exclusive session on "The Benefits of Water Aerobics" 
by renowned aquatic fitness expert Sandy Cheeks. Sandy will share her insights on how water aerobics can improve cardiovascular health, 
increase strength, and offer low-impact options for all ages. Mark your calendars for this enlightening session on June 5th!', 
'2023-06-05', NULL);


INSERT INTO `class_schedule` (`instructor_id`, `name`, `week`, `description`, `start_time`, `end_time`, `capacity`) VALUES
(1, 'Zumba', 'Monday', 'Zumba class for beginners', '06:00:00', '07:00:00', 15),
(2, 'Aqua Fit', 'Monday', 'Aqua Fit class for all levels', '07:00:00', '08:00:00', 15),
(3, 'Low-Impact', 'Monday', 'Low-Impact class for seniors', '18:00:00', '19:00:00', 15),

(4, 'Mums', 'Tuesday', 'Mums class for intermediate level', '06:00:00', '07:00:00', 15),
(5, 'Babies', 'Tuesday', 'Babies class for all levels',  '07:00:00', '08:00:00', 15),
(1, 'Zumba', 'Tuesday', 'Zumba class for beginners',  '18:00:00', '19:00:00', 15),

(2, 'Aqua Fit', 'Wednesday', 'Aqua Fit class for all levels',  '06:00:00', '07:00:00', 15),
(3, 'Low-Impact', 'Wednesday', 'Low-Impact class for intermediate level', '07:00:00', '08:00:00', 15),
(4, 'Mums', 'Wednesday', 'Mums class for intermediate level', '18:00:00', '19:00:00', 15),

(5, 'Babies', 'Thursday', 'Babies class for all levels',  '06:00:00', '07:00:00', 15),
(1, 'Zumba', 'Thursday', 'Zumba class for beginners', '07:00:00', '08:00:00', 15),
(2, 'Aqua Fit', 'Thursday', 'Aqua Fit class for all levels',  '18:00:00', '19:00:00', 15),

(3, 'Low-Impact', 'Friday', 'Low-Impact class for seniors',  '06:00:00', '07:00:00', 15),
(4, 'Aqua Fit', 'Friday', 'Aqua Fit class in the shallow pool', '07:00:00', '08:00:00', 15),
(5, 'Mums', 'Friday', 'Mums class for intermediate level', '18:00:00', '19:00:00', 15),

(1, 'Babies', 'Saturday', 'Babies class for all levels', '06:00:00', '07:00:00', 15),
(2, 'Zumba', 'Saturday', 'Zumba class for beginners', '07:00:00', '08:00:00', 15),
(3, 'Aqua Fit', 'Saturday', 'Aqua Fit class for all levels',  '18:00:00', '19:00:00', 15),

(4, 'Low-Impact', 'Sunday', 'Low-Impact class for intermediate level',  '06:00:00', '07:00:00', 15),
(5, 'Mums', 'Sunday', 'Mums class in the all levels',  '07:00:00', '08:00:00', 15),
(1, 'Babies', 'Sunday', 'Babies class for all levels',  '18:00:00', '19:00:00', 15);


INSERT INTO `lesson_schedule` (`instructor_id`, `week`, `description`, `start_time`, `end_time`, `lane_number`, `capacity`) VALUES
(1, 'Monday', 'Advanced swimming techniques for competitive swimmers.', '12:30', '13:30', 1, 1),
(2, 'Monday', 'Beginner swimming lessons focusing on basic strokes and water safety.', '14:00', '15:00', 2, 1),
(3, 'Monday', 'Intermediate swimming lessons to improve technique and endurance.', '16:30', '17:30', 3, 1),

(4, 'Tuesday', 'Personalized water aerobics session for fitness and rehabilitation.', '12:30', '13:30', 4, 1),
(5, 'Tuesday', 'One-on-one diving lessons focusing on techniques and safety.', '14:00', '15:00', 5, 1),
(1, 'Tuesday', 'Personalized training session for triathlon swimming preparation.', '16:30', '17:30', 6, 1),

(2, 'Wednesday', 'Advanced breathing techniques for enhanced underwater performance.', '12:30', '13:30', 7, 1),
(3, 'Wednesday', 'Stroke refinement and efficiency training for competitive swimmers.', '14:00', '15:00', 8, 1),
(4, 'Wednesday', 'Underwater photography techniques and safety for divers.', '16:30', '17:30', 9, 1),

(5, 'Thursday', 'Personalized open water swimming lessons for long-distance swimmers.', '12:30', '13:30', 10, 1), 
(1, 'Thursday', 'Speed and agility drills for competitive swimmers.', '14:00', '15:00', 1, 1),
(2, 'Thursday', 'Survival swimming techniques and safety training.', '16:30', '17:30', 2, 1),

(3, 'Friday', 'One-on-one synchronized swimming techniques for all levels.', '12:30', '13:30', 3, 1),
(4, 'Friday', 'Aquatic therapy sessions for rehabilitation and relaxation.', '14:00', '15:00', 4, 1),
(5, 'Friday', 'Tailored swim workouts for fitness enthusiasts.', '16:30', '17:30', 5, 1),

(1, 'Saturday', 'Technique and tactics for open water racing.', '12:30', '13:30', 6, 1),
(2, 'Saturday', 'Personal coaching for mastering the butterfly stroke.', '14:00', '15:00', 7, 1),
(3, 'Saturday', 'Endurance training sessions for distance swimmers.', '16:30', '17:30', 8, 1),

(4, 'Sunday', 'Customized workout plans for swimmers looking to lose weight.', '12:30', '13:30', 9, 1),
(5, 'Sunday', 'Pre-competition nerves and mental preparation coaching.', '14:00', '15:00', 10, 1);


INSERT INTO `bookings` (`member_id`, `class_id`, `lesson_id`, `schedule_type`, `booking_status`, `booking_date`)
VALUES
(1, 1, NULL, 'class', 'confirmed', '2024-05-01'),
(2, 2, NULL, 'class', 'confirmed', '2024-05-02'),
(3, 3, NULL, 'class', 'confirmed', '2024-05-03'),
(4, 4, NULL, 'class', 'confirmed', '2024-05-04'),
(5, 5, NULL, 'class', 'confirmed', '2024-05-05'),
(6, 6, NULL, 'class', 'confirmed', '2024-05-06'),
(7, 7, NULL, 'class', 'confirmed', '2024-05-07'),
(8, 8, NULL, 'class', 'confirmed', '2024-05-08'),
(9, 9, NULL, 'class', 'confirmed', '2024-05-09'),
(10, 10, NULL, 'class', 'confirmed', '2024-05-10'),
(11, 11, NULL, 'class', 'confirmed', '2024-05-11'),
(12, 12, NULL, 'class', 'confirmed', '2024-05-12'),
(13, 13, NULL, 'class', 'confirmed', '2024-05-13'),
(14, 14, NULL, 'class', 'confirmed', '2024-05-14'),
(15, 15, NULL, 'class', 'confirmed', '2024-05-15'),
(16, 16, NULL, 'class', 'confirmed', '2024-05-16'),
(17, 17, NULL, 'class', 'confirmed', '2024-05-17'),
(18, 18, NULL, 'class', 'confirmed', '2024-05-18'),
(19, 19, NULL, 'class', 'confirmed', '2024-05-19'),
(20, 20, NULL, 'class', 'confirmed', '2024-05-20');


INSERT INTO `payments` (`member_id`, `membership_id`, `manager_id`, `lesson_id`, `payment_type`, `amount`, `payment_date`)
VALUES
(1, 110111, 1, NULL, 'membership', 700.00, '2024-05-01'),
(2, 110112, 1, NULL, 'membership', 60.00, '2024-05-01'),
(3, 110113, 1, NULL, 'membership', 700.00, '2024-05-01'),
(4, 110114, 1, NULL, 'membership', 700.00, '2024-05-01'),
(5, 110115, 1, NULL, 'membership', 700.00, '2024-05-01'),
(6, 110116, 1, NULL, 'membership', 700.00, '2024-05-01'),
(7, 110117, 1, NULL, 'membership', 700.00, '2024-05-01'),
(8, 110118, 1, NULL, 'membership', 700.00, '2024-05-01'),
(9, 110119, 1, NULL, 'membership', 700.00, '2024-05-01'),
(10, 110120, 1, NULL, 'membership', 700.00, '2024-05-01'),
(11, 110121, 1, NULL, 'membership', 700.00, '2024-05-01'),
(12, 110122, 1, NULL, 'membership', 700.00, '2024-05-01'),
(13, 110123, 1, NULL, 'membership', 700.00, '2024-05-01'),
(14, 110124, 1, NULL, 'membership', 700.00, '2024-05-01'),
(15, 110125, 1, NULL, 'membership', 700.00, '2024-05-01'),
(16, 110126, 1, NULL, 'membership', 700.00, '2024-05-01'),
(17, 110127, 1, NULL, 'membership', 700.00, '2024-05-01'),
(18, 110128, 1, NULL, 'membership', 700.00, '2024-05-01'),
(19, 110129, 1, NULL, 'membership', 700.00, '2024-05-01'),
(20, 110130, 1, NULL, 'membership', 60.00, '2024-05-01');


INSERT INTO `attendance` (`class_id`, `schedule_type`, `member_id`, `attended`, `attendance_status`) VALUES 
(1, 'class', 1, true, 'present'),
(2, 'class', 1, true, 'late');

