DROP SCHEMA IF EXISTS `swimmingclub`;
CREATE SCHEMA `swimmingclub`;
USE `swimmingclub`;

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
    `type` ENUM('Annual', 'Monthly', '6 Month') NOT NULL,
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

-- Class name table
CREATE TABLE `class_name` (
    `class_name_id` INT AUTO_INCREMENT,
    `name` ENUM('Zumba', 'Aqua Fit', 'Low-Impact', 'Mums', 'Babies','Aqua Fusion Flow','HydroFit Power Hour','Splash Dance Cardio','Aqua Sculpt & Tone','Aqua Zen Stretch','HydroBlast Intensity','Aqua Beat Blast','Splash & Dash HIIT') NOT NULL,
    `description` TEXT,
    PRIMARY KEY (`class_name_id`)
) AUTO_INCREMENT=1;

-- Class schedule table
CREATE TABLE `class_schedule` (
    `class_id` INT AUTO_INCREMENT,
    `instructor_id` INT,
    `class_name_id` INT,
    `week` ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL,
    `pool_type` VARCHAR(10) NOT NULL DEFAULT 'Deep',
	#`start_time` VARCHAR(10) NOT NULL,
    #`end_time` VARCHAR(10) NOT NULL,
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    `capacity` INT NOT NULL DEFAULT 15,
    `datetime` DATE,
    `availability` INT NOT NULL DEFAULT 15,

    PRIMARY KEY (`class_id`),
    FOREIGN KEY (`instructor_id`) REFERENCES `instructor`(`instructor_id`),
    FOREIGN KEY (`class_name_id`) REFERENCES `class_name`(`class_name_id`)
)AUTO_INCREMENT=1;

-- Lesson name table
CREATE TABLE `lesson_name` (
    `lesson_name_id` INT AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL DEFAULT 'One-on-One Lesson',
    `description` TEXT,
    PRIMARY KEY (`lesson_name_id`)
)AUTO_INCREMENT=1;

-- Lesson schedule table
CREATE TABLE `lesson_schedule` (
    `lesson_id` INT AUTO_INCREMENT,
    `instructor_id` INT,
    `lesson_name_id` INT,
    `week` ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL,
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    `lane_number` INT NOT NULL,
    `capacity` INT NOT NULL DEFAULT 1,
    PRIMARY KEY (`lesson_id`),
    FOREIGN KEY (`instructor_id`) REFERENCES `instructor`(`instructor_id`),
    FOREIGN KEY (`lesson_name_id`) REFERENCES `lesson_name`(`lesson_name_id`)
)AUTO_INCREMENT=1;

-- Booking table
CREATE TABLE `bookings` (
    `booking_id` INT AUTO_INCREMENT,
    `member_id` INT,
    `class_id` INT,
    `lesson_id` INT,
    `schedule_type` ENUM('aerobics class', 'swimming lesson') NOT NULL,
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
'profile_image1.jpg', 'Active'),

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
(20, '6 Month', '2024-05-01', '2024-11-01', 360.00);


INSERT INTO `news` (`manager_id`, `title`, `content`, `publication_date`, `image_id`) VALUES
(1, 'Summer Fitness Fiesta', 'Join us for our Summer Fitness Fiesta! Dive into the world of Aqua Aerobics with our special summer lineup designed to boost your fitness 
and beat the heat. From Aqua Zumba to Water Yoga, there’s something for everyone. Enroll now and make a splash in your fitness journey!', 
'2023-05-10', NULL),

(2, 'Expert Talk: The Benefits of Water Aerobics', 'We are excited to announce an exclusive session on "The Benefits of Water Aerobics" 
by renowned aquatic fitness expert Sandy Cheeks. Sandy will share her insights on how water aerobics can improve cardiovascular health, 
increase strength, and offer low-impact options for all ages. Mark your calendars for this enlightening session on June 5th!', 
'2023-06-05', NULL);


INSERT INTO `class_name` (`name`, `description`) VALUES
('Zumba', 'Zumba class for all levels'),
('Aqua Fit', 'Aqua Fit class for all levels'),
('Low-Impact', 'Low-Impact class for all levels'),
('Mums', 'Mums class for all levels'),
('Babies', 'Babies class for all levels'),
('Aqua Fusion Flow', 'Blend of moves for flexibility and cardio.'),
('HydroFit Power Hour', 'High-energy for strength and calorie burn.'),
('Splash Dance Cardio', 'Fun, rhythmic moves for a pumped-up heart.'),
('Aqua Sculpt & Tone', 'Tone up with water resistance.'),
('Aqua Zen Stretch', 'Relaxing stretches in the water.'),
('HydroBlast Intensity', 'Intense workout for maximum results.'),
('Aqua Beat Blast', 'Energetic routines to upbeat music.'),
('Splash & Dash HIIT', 'Quick, effective interval training in water.');

INSERT INTO `class_schedule` (`instructor_id`, `class_name_id`, `week`, `start_time`, `end_time`, `datetime`) VALUES
(1, 1, 'Monday', '06:00', '07:00','2024-04-08'),
(2, 2, 'Monday', '07:00', '08:00','2024-04-08'),
(3, 3, 'Monday', '18:00', '19:00','2024-04-08'),

(4, 4, 'Tuesday', '06:00', '07:00','2024-04-09'),
(5, 5, 'Tuesday', '07:00', '08:00','2024-04-09'),
(1, 1, 'Tuesday', '18:00', '19:00','2024-04-09'),

(2, 2, 'Wednesday', '06:00', '07:00','2024-04-10'),
(3, 3, 'Wednesday', '07:00', '08:00','2024-04-10'),
(4, 4, 'Wednesday', '18:00', '19:00','2024-04-10'),

(5, 5, 'Thursday', '06:00', '07:00','2024-04-11'),
(1, 1, 'Thursday', '07:00', '08:00','2024-04-11'),
(2, 2, 'Thursday', '18:00', '19:00','2024-04-11'),

(3, 3, 'Friday', '06:00', '07:00','2024-04-12'),
(4, 4, 'Friday', '07:00', '08:00','2024-04-12'),
(5, 5, 'Friday', '18:00', '19:00','2024-04-12'),

(1, 1, 'Saturday', '06:00', '07:00','2024-04-13'),
(2, 2, 'Saturday', '07:00', '08:00','2024-04-13'),
(3, 3, 'Saturday', '18:00', '19:00','2024-04-13'),

(4, 4, 'Sunday', '06:00', '07:00','2024-04-14'),
(5, 5, 'Sunday', '07:00', '08:00','2024-04-14'),
(1, 1, 'Sunday', '18:00', '19:00','2024-04-14');

INSERT INTO `lesson_name` (`description`) VALUES
('Beginner swimming lesson'),
('Intermediate swimming lesson'),
('Advanced swimming lesson');

INSERT INTO `lesson_schedule` (`instructor_id`, `lesson_name_id`, `week`, `start_time`, `end_time`, `lane_number`) VALUES
(1, 1, 'Monday', '09:00', '10:00', 1),
(2, 1, 'Monday', '11:00', '12:00', 2),
(3, 1, 'Monday', '14:00', '15:00', 3),

(4, 2, 'Tuesday', '09:00', '10:00', 4),
(5, 2, 'Tuesday', '11:00', '12:00', 5),
(1, 2, 'Tuesday', '14:00', '15:00', 6),

(2, 3, 'Wednesday', '09:00', '10:00', 7),
(3, 3, 'Wednesday', '11:00', '12:00', 8),
(4, 3, 'Wednesday', '14:00', '15:00', 9),

(5, 1, 'Thursday', '09:00', '10:00', 10), 
(1, 1, 'Thursday', '11:00', '12:00', 1),
(2, 1, 'Thursday', '14:00', '15:00', 2),

(3, 2, 'Friday', '09:00', '10:00', 3),
(4, 2, 'Friday', '11:00', '12:00', 4),
(5, 2, 'Friday', '14:00', '15:00', 5),

(1, 3, 'Saturday', '09:00', '10:00', 6),
(2, 3, 'Saturday', '11:00', '12:00', 7),
(3, 3, 'Saturday', '14:00', '15:00', 8),

(4, 1, 'Sunday', '09:00', '10:00', 9),
(5, 1, 'Sunday', '14:00', '15:00', 10);


INSERT INTO `bookings` (`member_id`, `class_id`, `lesson_id`, `schedule_type`, `booking_status`, `booking_date`)
VALUES
(1, 1, NULL, 'aerobics class', 'confirmed', '2024-05-01'),
(2, 2, NULL, 'aerobics class', 'confirmed', '2024-05-02'),
(3, 3, NULL, 'aerobics class', 'confirmed', '2024-05-03'),
(4, 4, NULL, 'aerobics class', 'confirmed', '2024-05-04'),
(5, 5, NULL, 'aerobics class', 'confirmed', '2024-05-05'),
(6, 6, NULL, 'aerobics class', 'confirmed', '2024-05-06'),
(7, 7, NULL, 'aerobics class', 'confirmed', '2024-05-07'),
(8, 8, NULL, 'aerobics class', 'confirmed', '2024-05-08'),
(9, 9, NULL, 'aerobics class', 'confirmed', '2024-05-09'),
(10, 10, NULL, 'aerobics class', 'confirmed', '2024-05-10'),
(11, 11, NULL, 'aerobics class', 'confirmed', '2024-05-11'),
(12, 12, NULL, 'aerobics class', 'confirmed', '2024-05-12'),
(13, 13, NULL, 'aerobics class', 'confirmed', '2024-05-13'),
(14, 14, NULL, 'aerobics class', 'confirmed', '2024-05-14'),
(15, 15, NULL, 'aerobics class', 'confirmed', '2024-05-15'),
(16, 16, NULL, 'aerobics class', 'confirmed', '2024-05-16'),
(17, 17, NULL, 'aerobics class', 'confirmed', '2024-05-17'),
(18, 18, NULL, 'aerobics class', 'confirmed', '2024-05-18'),
(19, 19, NULL, 'aerobics class', 'confirmed', '2024-05-19'),
(20, 20, NULL, 'aerobics class', 'confirmed', '2024-05-20'),

(10, NULL, 1, 'swimming lesson', 'confirmed', '2024-05-02'),
(11, NULL, 2, 'swimming lesson', 'confirmed', '2024-05-03'),
(12, NULL, 3, 'swimming lesson', 'confirmed', '2024-05-04'),
(13, NULL, 4, 'swimming lesson', 'confirmed', '2024-05-05'),
(14, NULL, 5, 'swimming lesson', 'confirmed', '2024-05-06'),
(15, NULL, 6, 'swimming lesson', 'confirmed', '2024-05-07'),
(16, NULL, 7, 'swimming lesson', 'confirmed', '2024-05-08'),
(17, NULL, 8, 'swimming lesson', 'confirmed', '2024-05-09'),
(18, NULL, 9, 'swimming lesson', 'confirmed', '2024-05-10'),
(19, NULL, 10, 'swimming lesson', 'confirmed', '2024-05-11'),
(20, NULL, 11, 'swimming lesson', 'confirmed', '2024-05-12');

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
(20, 110130, 1, NULL, 'membership', 360.00, '2024-05-01'),

(10, 110120, 2, 1, 'lesson', 50.00, '2024-05-02'),
(11, 110121, 2, 2, 'lesson', 50.00, '2024-05-03'),
(12, 110122, 2, 3, 'lesson', 50.00, '2024-05-04'),
(13, 110123, 2, 4, 'lesson', 50.00, '2024-05-05'),
(14, 110124, 2, 5, 'lesson', 50.00, '2024-05-06'),
(15, 110125, 2, 6, 'lesson', 50.00, '2024-05-07'),
(16, 110126, 2, 7, 'lesson', 50.00, '2024-05-08'),
(17, 110127, 2, 8, 'lesson', 50.00, '2024-05-09'),
(18, 110128, 2, 9, 'lesson', 50.00, '2024-05-10'),
(19, 110129, 2, 10, 'lesson', 50.00, '2024-05-11'),
(20, 110130, 2, 11, 'lesson', 50.00, '2024-05-12');


INSERT INTO `attendance` (`class_id`, `schedule_type`, `member_id`, `attended`, `attendance_status`) VALUES 
(1, 'class', 1, true, 'present'),
(2, 'class', 1, true, 'late');

-- Generate dates from April 15th, 2024 to July 1st, 2024
INSERT INTO `class_schedule` (`instructor_id`, `class_name_id`, `week`, `start_time`, `end_time`, `datetime`) VALUES
-- Day 1: 2024-04-01, Monday
(1, 2, 'Monday', '06:00', '07:00', '2024-04-01 06:00'),
(2, 3, 'Monday', '07:00', '08:00', '2024-04-01 07:00'),
(3, 1, 'Monday', '08:00', '09:00', '2024-04-01 08:00'),
(4, 5, 'Monday', '09:00', '10:00', '2024-04-01 09:00'),
(5, 4, 'Monday', '15:00', '16:00', '2024-04-01 15:00'),
(1, 3, 'Monday', '16:00', '17:00', '2024-04-01 16:00'),
(2, 2, 'Monday', '17:00', '18:00', '2024-04-01 17:00'),

-- Day 2: 2024-04-02, Tuesday
(3, 1, 'Tuesday', '06:00', '07:00', '2024-04-02 06:00'),
(4, 2, 'Tuesday', '07:00', '08:00', '2024-04-02 07:00'),
(5, 3, 'Tuesday', '09:00', '10:00', '2024-04-02 09:00'),
(1, 5, 'Tuesday', '10:00', '11:00', '2024-04-02 10:00'),
(2, 4, 'Tuesday', '14:00', '15:00', '2024-04-02 14:00'),
(3, 2, 'Tuesday', '15:00', '16:00', '2024-04-02 15:00'),
(4, 1, 'Tuesday', '16:00', '17:00', '2024-04-02 16:00'),

-- Day 3: 2024-04-03, Wednesday
(5, 3, 'Wednesday', '06:00', '07:00', '2024-04-03 06:00'),
(1, 2, 'Wednesday', '08:00', '09:00', '2024-04-03 08:00'),
(2, 1, 'Wednesday', '09:00', '10:00', '2024-04-03 09:00'),
(3, 4, 'Wednesday', '11:00', '12:00', '2024-04-03 11:00'),
(4, 5, 'Wednesday', '15:00', '16:00', '2024-04-03 15:00'),
(5, 3, 'Wednesday', '16:00', '17:00', '2024-04-03 16:00'),
(1, 2, 'Wednesday', '17:00', '18:00', '2024-04-03 17:00'),

-- Day 4: 2024-04-04, Thursday
(2, 1, 'Thursday', '06:00', '07:00', '2024-04-04 06:00'),
(3, 3, 'Thursday', '07:00', '08:00', '2024-04-04 07:00'),
(4, 5, 'Thursday', '08:00', '09:00', '2024-04-04 08:00'),
(5, 2, 'Thursday', '15:00', '16:00', '2024-04-04 15:00'),
(1, 4, 'Thursday', '16:00', '17:00', '2024-04-04 16:00'),
(2, 1, 'Thursday', '17:00', '18:00', '2024-04-04 17:00'),
(3, 3, 'Thursday', '18:00', '19:00', '2024-04-04 18:00'),

-- Day 5: 2024-04-05, Friday
(4, 5, 'Friday', '06:00', '07:00', '2024-04-05 06:00'),
(5, 2, 'Friday', '07:00', '08:00', '2024-04-05 07:00'),
(1, 1, 'Friday', '08:00', '09:00', '2024-04-05 08:00'),
(2, 4, 'Friday', '09:00', '10:00', '2024-04-05 09:00'),
(3, 5, 'Friday', '10:00', '11:00', '2024-04-05 10:00'),
(4, 2, 'Friday', '14:00', '15:00', '2024-04-05 14:00'),
(5, 1, 'Friday', '15:00', '16:00', '2024-04-05 15:00'),
(1, 3, 'Friday', '16:00', '17:00', '2024-04-05 16:00'),

-- Day 6: 2024-04-06, Saturday
(2, 4, 'Saturday', '06:00', '07:00', '2024-04-06 06:00'),
(3, 5, 'Saturday', '07:00', '08:00', '2024-04-06 07:00'),
(4, 2, 'Saturday', '08:00', '09:00', '2024-04-06 08:00'),
(5, 1, 'Saturday', '09:00', '10:00', '2024-04-06 09:00'),
(1, 3, 'Saturday', '10:00', '11:00', '2024-04-06 10:00'),
(2, 5, 'Saturday', '11:00', '12:00', '2024-04-06 11:00'),
(3, 2, 'Saturday', '15:00', '16:00', '2024-04-06 15:00'),
(4, 1, 'Saturday', '16:00', '17:00', '2024-04-06 16:00'),

-- Day 7: 2024-04-07, Sunday
(5, 4, 'Sunday', '06:00', '07:00', '2024-04-07 06:00'),
(1, 5, 'Sunday', '07:00', '08:00', '2024-04-07 07:00'),
(2, 3, 'Sunday', '08:00', '09:00', '2024-04-07 08:00'),
(3, 1, 'Sunday', '15:00', '16:00', '2024-04-07 15:00'),
(4, 2, 'Sunday', '16:00', '17:00', '2024-04-07 16:00'),
(5, 4, 'Sunday', '17:00', '18:00', '2024-04-07 17:00'),
(1, 3, 'Sunday', '18:00', '19:00', '2024-04-07 18:00'),

-- Day 8: 2024-04-08, Monday

(3, 11, 'Monday', '08:00', '09:00', '2024-04-08 08:00'),
(4, 10, 'Monday', '16:00', '17:00', '2024-04-08 16:00'),
(5, 9, 'Monday', '17:00', '18:00', '2024-04-08 17:00'),


-- Day 9: 2024-04-09, Tuesday
(4, 5, 'Tuesday', '08:00', '09:00', '2024-04-09 08:00'),
(5, 4, 'Tuesday', '09:00', '10:00', '2024-04-09 09:00'),
(1, 3, 'Tuesday', '10:00', '11:00', '2024-04-09 10:00'),
(3, 1, 'Tuesday', '18:00', '19:00', '2024-04-09 18:00'),

-- Day 10: 2024-04-10, Wedn
(1, 11, 'Wednesday', '08:00', '09:00', '2024-04-10 08:00'),
(2, 10, 'Wednesday', '09:00', '10:00', '2024-04-10 09:00'),
(3, 9, 'Wednesday', '15:00', '16:00', '2024-04-10 15:00'),
(4, 8, 'Wednesday', '16:00', '17:00', '2024-04-10 16:00'),
(5, 7, 'Wednesday', '17:00', '18:00', '2024-04-10 17:00'),

-- Day 11: 2024-04-11, Thursday
(3, 4, 'Thursday', '09:00', '10:00', '2024-04-11 09:00'),
(4, 3, 'Thursday', '10:00', '11:00', '2024-04-11 10:00'),
(5, 2, 'Thursday', '14:00', '15:00', '2024-04-11 14:00'),
(1, 1, 'Thursday', '15:00', '16:00', '2024-04-11 15:00'),
(2, 13, 'Thursday', '16:00', '17:00', '2024-04-11 16:00'),

-- Day 12: 2024-04-12, Friday
(5, 10, 'Friday', '08:00', '09:00', '2024-04-12 08:00'),
(1, 9, 'Friday', '09:00', '10:00', '2024-04-12 09:00'),
(2, 8, 'Friday', '10:00', '11:00', '2024-04-12 10:00'),
(3, 7, 'Friday', '14:00', '15:00', '2024-04-12 14:00'),
(4, 6, 'Friday', '15:00', '16:00', '2024-04-12 15:00'),

-- Day 13: 2024-04-13, Saturday
(2, 3, 'Saturday', '08:00', '09:00', '2024-04-13 08:00'),
(3, 2, 'Saturday', '15:00', '16:00', '2024-04-13 15:00'),
(4, 1, 'Saturday', '16:00', '17:00', '2024-04-13 16:00'),
(5, 13, 'Saturday', '17:00', '18:00', '2024-04-13 17:00'),

-- Day 14: 2024-04-14, Sunday
(3, 10, 'Sunday', '08:00', '09:00', '2024-04-14 08:00'),
(4, 9, 'Sunday', '15:00', '16:00', '2024-04-14 15:00'),
(5, 8, 'Sunday', '16:00', '17:00', '2024-04-14 16:00'),
(1, 7, 'Sunday', '17:00', '18:00', '2024-04-14 17:00'),

-- Day 15: 2024-04-15, Monday
(1, 6, 'Monday', '06:00', '07:00', '2024-04-15 06:00'),
(2, 5, 'Monday', '07:00', '08:00', '2024-04-15 07:00'),
(3, 4, 'Monday', '09:00', '10:00', '2024-04-15 09:00'),
(4, 3, 'Monday', '10:00', '11:00', '2024-04-15 10:00'),
(5, 2, 'Monday', '11:00', '12:00', '2024-04-15 11:00'),
(1, 1, 'Monday', '15:00', '16:00', '2024-04-15 15:00'),
(2, 13, 'Monday', '16:00', '17:00', '2024-04-15 16:00'),

-- Day 16: 2024-04-16, Tuesday
(3, 12, 'Tuesday', '06:00', '07:00', '2024-04-16 06:00'),
(4, 11, 'Tuesday', '07:00', '08:00', '2024-04-16 07:00'),
(5, 10, 'Tuesday', '08:00', '09:00', '2024-04-16 08:00'),
(1, 9, 'Tuesday', '09:00', '10:00', '2024-04-16 09:00'),
(2, 8, 'Tuesday', '10:00', '11:00', '2024-04-16 10:00'),
(3, 7, 'Tuesday', '17:00', '18:00', '2024-04-16 17:00'),
(4, 6, 'Tuesday', '18:00', '19:00', '2024-04-16 18:00'),

-- Day 17: 2024-04-17, Wednesday
(5, 5, 'Wednesday', '06:00', '07:00', '2024-04-17 06:00'),
(1, 4, 'Wednesday', '07:00', '08:00', '2024-04-17 07:00'),
(2, 3, 'Wednesday', '09:00', '10:00', '2024-04-17 09:00'),
(3, 2, 'Wednesday', '10:00', '11:00', '2024-04-17 10:00'),
(4, 1, 'Wednesday', '11:00', '12:00', '2024-04-17 11:00'),
(5, 13, 'Wednesday', '15:00', '16:00', '2024-04-17 15:00'),
(1, 12, 'Wednesday', '16:00', '17:00', '2024-04-17 16:00'),

-- Day 18: 2024-04-18, Thursday
(2, 11, 'Thursday', '06:00', '07:00', '2024-04-18 06:00'),
(3, 10, 'Thursday', '07:00', '08:00', '2024-04-18 07:00'),
(4, 9, 'Thursday', '08:00', '09:00', '2024-04-18 08:00'),
(5, 8, 'Thursday', '09:00', '10:00', '2024-04-18 09:00'),
(1, 7, 'Thursday', '10:00', '11:00', '2024-04-18 10:00'),
(2, 6, 'Thursday', '17:00', '18:00', '2024-04-18 17:00'),
(3, 5, 'Thursday', '18:00', '19:00', '2024-04-18 18:00'),

-- Day 19: 2024-04-19, Friday
(4, 4, 'Friday', '06:00', '07:00', '2024-04-19 06:00'),
(5, 3, 'Friday', '07:00', '08:00', '2024-04-19 07:00'),
(1, 2, 'Friday', '08:00', '09:00', '2024-04-19 08:00'),
(2, 1, 'Friday', '09:00', '10:00', '2024-04-19 09:00'),
(3, 13, 'Friday', '15:00', '16:00', '2024-04-19 15:00'),
(4, 12, 'Friday', '16:00', '17:00', '2024-04-19 16:00'),
(5, 11, 'Friday', '17:00', '18:00', '2024-04-19 17:00'),

-- Day 20: 2024-04-20, Saturday
(1, 10, 'Saturday', '06:00', '07:00', '2024-04-20 06:00'),
(2, 9, 'Saturday', '07:00', '08:00', '2024-04-20 07:00'),
(3, 8, 'Saturday', '08:00', '09:00', '2024-04-20 08:00'),
(4, 7, 'Saturday', '15:00', '16:00', '2024-04-20 15:00'),
(5, 6, 'Saturday', '16:00', '17:00', '2024-04-20 16:00'),
(1, 5, 'Saturday', '17:00', '18:00', '2024-04-20 17:00'),

-- Day 21: 2024-04-21, Sunday
(2, 4, 'Sunday', '06:00', '07:00', '2024-04-21 06:00'),
(3, 3, 'Sunday', '07:00', '08:00', '2024-04-21 07:00'),
(4, 2, 'Sunday', '08:00', '09:00', '2024-04-21 08:00'),
(5, 1, 'Sunday', '15:00', '16:00', '2024-04-21 15:00'),
(1, 13, 'Sunday', '16:00', '17:00', '2024-04-21 16:00'),
(2, 12, 'Sunday', '17:00', '18:00', '2024-04-21 17:00'),

-- Day 22: 2024-04-22, Monday
(3, 5, 'Monday', '06:00', '07:00', '2024-04-22 06:00'),
(5, 1, 'Monday', '09:00', '10:00', '2024-04-22 09:00'),
(2, 4, 'Monday', '10:00', '11:00', '2024-04-22 10:00'),
(4, 2, 'Monday', '13:00', '14:00', '2024-04-22 13:00'),
(1, 3, 'Monday', '16:00', '17:00', '2024-04-22 16:00'),
(3, 1, 'Monday', '17:00', '18:00', '2024-04-22 17:00'),
(5, 6, 'Monday', '19:00', '20:00', '2024-04-22 19:00'),

-- Day 23: 2024-04-23, Tuesday
(1, 2, 'Tuesday', '06:00', '07:00', '2024-04-23 06:00'),
(3, 4, 'Tuesday', '07:00', '08:00', '2024-04-23 07:00'),
(5, 5, 'Tuesday', '08:00', '09:00', '2024-04-23 08:00'),
(2, 1, 'Tuesday', '11:00', '12:00', '2024-04-23 11:00'),
(4, 3, 'Tuesday', '14:00', '15:00', '2024-04-23 14:00'),
(1, 6, 'Tuesday', '15:00', '16:00', '2024-04-23 15:00'),
(3, 2, 'Tuesday', '18:00', '19:00', '2024-04-23 18:00'),

-- Day 24: 2024-04-24, Wednesday
(5, 4, 'Wednesday', '06:00', '07:00', '2024-04-24 06:00'),
(2, 6, 'Wednesday', '09:00', '10:00', '2024-04-24 09:00'),
(4, 5, 'Wednesday', '10:00', '11:00', '2024-04-24 10:00'),
(1, 3, 'Wednesday', '13:00', '14:00', '2024-04-24 13:00'),
(3, 1, 'Wednesday', '14:00', '15:00', '2024-04-24 14:00'),
(5, 2, 'Wednesday', '17:00', '18:00', '2024-04-24 17:00'),
(2, 4, 'Wednesday', '19:00', '20:00', '2024-04-24 19:00'),

-- Day 25: 2024-04-25, Thursday
(4, 3, 'Thursday', '06:00', '07:00', '2024-04-25 06:00'),
(1, 5, 'Thursday', '07:00', '08:00', '2024-04-25 07:00'),
(3, 6, 'Thursday', '08:00', '09:00', '2024-04-25 08:00'),
(5, 1, 'Thursday', '15:00', '16:00', '2024-04-25 15:00'),
(2, 2, 'Thursday', '16:00', '17:00', '2024-04-25 16:00'),
(4, 4, 'Thursday', '17:00', '18:00', '2024-04-25 17:00'),
(1, 3, 'Thursday', '18:00', '19:00', '2024-04-25 18:00'),

-- Day 26: 2024-04-26, Friday
(3, 5, 'Friday', '06:00', '07:00', '2024-04-26 06:00'),
(5, 4, 'Friday', '09:00', '10:00', '2024-04-26 09:00'),
(2, 6, 'Friday', '10:00', '11:00', '2024-04-26 10:00'),
(4, 1, 'Friday', '13:00', '14:00', '2024-04-26 13:00'),
(1, 2, 'Friday', '14:00', '15:00', '2024-04-26 14:00'),
(3, 3, 'Friday', '15:00', '16:00', '2024-04-26 15:00'),
(5, 5, 'Friday', '19:00', '20:00', '2024-04-26 19:00'),

-- Day 27: 2024-04-27, Saturday
(2, 4, 'Saturday', '06:00', '07:00', '2024-04-27 06:00'),
(4, 2, 'Saturday', '07:00', '08:00', '2024-04-27 07:00'),
(1, 1, 'Saturday', '08:00', '09:00', '2024-04-27 08:00'),
(3, 3, 'Saturday', '15:00', '16:00', '2024-04-27 15:00'),
(5, 5, 'Saturday', '16:00', '17:00', '2024-04-27 16:00'),
(2, 6, 'Saturday', '17:00', '18:00', '2024-04-27 17:00'),
(4, 4, 'Saturday', '18:00', '19:00', '2024-04-27 18:00'),

-- Day 28: 2024-04-28, Sunday
(1, 2, 'Sunday', '06:00', '07:00', '2024-04-28 06:00'),
(3, 1, 'Sunday', '07:00', '08:00', '2024-04-28 07:00'),
(5, 3, 'Sunday', '09:00', '10:00', '2024-04-28 09:00'),
(2, 5, 'Sunday', '10:00', '11:00', '2024-04-28 10:00'),
(4, 6, 'Sunday', '14:00', '15:00', '2024-04-28 14:00'),
(1, 4, 'Sunday', '15:00', '16:00', '2024-04-28 15:00'),
(3, 2, 'Sunday', '16:00', '17:00', '2024-04-28 16:00'),

-- Day 29: 2024-04-29, Monday
(5, 1, 'Monday', '06:00', '07:00', '2024-04-29 06:00'),
(2, 3, 'Monday', '07:00', '08:00', '2024-04-29 07:00'),
(4, 5, 'Monday', '08:00', '09:00', '2024-04-29 08:00'),
(1, 6, 'Monday', '09:00', '10:00', '2024-04-29 09:00'),
(3, 4, 'Monday', '17:00', '18:00', '2024-04-29 17:00'),
(5, 2, 'Monday', '18:00', '19:00', '2024-04-29 18:00'),
(2, 1, 'Monday', '19:00', '20:00', '2024-04-29 19:00'),

-- Day 30: 2024-04-30, Tuesday
(4, 3, 'Tuesday', '06:00', '07:00', '2024-04-30 06:00'),
(1, 5, 'Tuesday', '07:00', '08:00', '2024-04-30 07:00'),
(3, 6, 'Tuesday', '15:00', '16:00', '2024-04-30 15:00'),
(5, 4, 'Tuesday', '16:00', '17:00', '2024-04-30 16:00'),
(2, 2, 'Tuesday', '17:00', '18:00', '2024-04-30 17:00'),
(4, 1, 'Tuesday', '18:00', '19:00', '2024-04-30 18:00'),

-- Day 31: 2024-05-01, Wednesday
(1, 3, 'Wednesday', '06:00', '07:00', '2024-05-01 06:00'),
(2, 1, 'Wednesday', '07:00', '08:00', '2024-05-01 07:00'),
(3, 2, 'Wednesday', '08:00', '09:00', '2024-05-01 08:00'),
(4, 5, 'Wednesday', '10:00', '11:00', '2024-05-01 10:00'),
(5, 4, 'Wednesday', '11:00', '12:00', '2024-05-01 11:00'),
(1, 6, 'Wednesday', '14:00', '15:00', '2024-05-01 14:00'),
(2, 12, 'Wednesday', '16:00', '17:00', '2024-05-01 16:00'),
(3, 11, 'Wednesday', '17:00', '18:00', '2024-05-01 17:00'),
(4, 10, 'Wednesday', '19:00', '20:00', '2024-05-01 19:00'),

-- Day 32: 2024-05-02, Thursday
(5, 9, 'Thursday', '06:00', '07:00', '2024-05-02 06:00'),
(1, 8, 'Thursday', '07:00', '08:00', '2024-05-02 07:00'),
(2, 7, 'Thursday', '09:00', '10:00', '2024-05-02 09:00'),
(3, 6, 'Thursday', '10:00', '11:00', '2024-05-02 10:00'),
(4, 5, 'Thursday', '13:00', '14:00', '2024-05-02 13:00'),
(5, 4, 'Thursday', '15:00', '16:00', '2024-05-02 15:00'),
(1, 3, 'Thursday', '16:00', '17:00', '2024-05-02 16:00'),
(2, 2, 'Thursday', '17:00', '18:00', '2024-05-02 17:00'),
(3, 1, 'Thursday', '18:00', '19:00', '2024-05-02 18:00'),

-- Day 33: 2024-05-03, Friday
(4, 13, 'Friday', '06:00', '07:00', '2024-05-03 06:00'),
(5, 12, 'Friday', '08:00', '09:00', '2024-05-03 08:00'),
(1, 11, 'Friday', '09:00', '10:00', '2024-05-03 09:00'),
(2, 10, 'Friday', '11:00', '12:00', '2024-05-03 11:00'),
(3, 9, 'Friday', '13:00', '14:00', '2024-05-03 13:00'),
(4, 8, 'Friday', '14:00', '15:00', '2024-05-03 14:00'),
(5, 7, 'Friday', '15:00', '16:00', '2024-05-03 15:00'),
(1, 6, 'Friday', '17:00', '18:00', '2024-05-03 17:00'),
(2, 5, 'Friday', '19:00', '20:00', '2024-05-03 19:00'),

-- Day 34: 2024-05-04, Saturday
(3, 4, 'Saturday', '06:00', '07:00', '2024-05-04 06:00'),
(4, 3, 'Saturday', '07:00', '08:00', '2024-05-04 07:00'),
(5, 2, 'Saturday', '09:00', '10:00', '2024-05-04 09:00'),
(1, 1, 'Saturday', '10:00', '11:00', '2024-05-04 10:00'),
(2, 13, 'Saturday', '11:00', '12:00', '2024-05-04 11:00'),
(3, 12, 'Saturday', '16:00', '17:00', '2024-05-04 16:00'),
(4, 11, 'Saturday', '17:00', '18:00', '2024-05-04 17:00'),
(5, 10, 'Saturday', '18:00', '19:00', '2024-05-04 18:00'),

-- Day 35: 2024-05-05, Sunday
(1, 9, 'Sunday', '06:00', '07:00', '2024-05-05 06:00'),
(2, 8, 'Sunday', '08:00', '09:00', '2024-05-05 08:00'),
(3, 7, 'Sunday', '09:00', '10:00', '2024-05-05 09:00'),
(4, 6, 'Sunday', '14:00', '15:00', '2024-05-05 14:00'),
(5, 5, 'Sunday', '15:00', '16:00', '2024-05-05 15:00'),
(1, 4, 'Sunday', '16:00', '17:00', '2024-05-05 16:00'),
(2, 3, 'Sunday', '17:00', '18:00', '2024-05-05 17:00'),
(3, 2, 'Sunday', '18:00', '19:00', '2024-05-05 18:00');



