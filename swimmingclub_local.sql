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
    `image_profile` VARCHAR(500),
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
    `image_profile` VARCHAR(500) DEFAULT '123.jpeg',
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
    `status` ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    PRIMARY KEY (`membership_id`),
    FOREIGN KEY (`member_id`) REFERENCES `member`(`member_id`)
)AUTO_INCREMENT=110111;

-- Membership_refund table
CREATE TABLE `memberships_refund` (
    `membership_refund_id` INT AUTO_INCREMENT,
    `membership_id` INT NOT NULL,
    `member_id` INT NOT NULL,
    `refund_amount` DECIMAL(10,2) NOT NULL,
    `refund_date` DATE NOT NULL,
    PRIMARY KEY (`membership_refund_id`),
    FOREIGN KEY (`membership_id`) REFERENCES `memberships`(`membership_id`),
    FOREIGN KEY (`member_id`) REFERENCES `member`(`member_id`)
) AUTO_INCREMENT=1;

-- News table
CREATE TABLE `news` (
    `news_id` INT AUTO_INCREMENT,
    `manager_id` INT,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NOT NULL,
    `publication_date` DATE NOT NULL,
    `image` VARCHAR(500),
	PRIMARY KEY (`news_id`),
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

INSERT INTO `manager` (`user_id`, `title`, `first_name`, `last_name`, `email`, `phone`, `position`, `image_profile`, `status`) VALUES
(1000, 'Mr', 'John', 'Doe', 'john@example.com', '1234567890', 'Senior Manager', 'doe.jpg', 'Active'),
(1001, 'Mr', 'Squidward', 'Tentacles', 'squidward@bikinibottom.net', '1234567890', 'Manager', 'squidward.jpg', 'Active');

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
(1, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(2, 'Monthly', '2024-04-01', '2024-04-30', 60.00),
(3, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(4, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(5, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(6, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(7, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(8, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(9, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(10, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(11, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(12, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(13, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(14, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(15, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(16, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(17, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(18, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(19, 'Annual', '2024-04-01', '2025-03-31', 700.00),
(20, '6 Month', '2024-04-01', '2024-09-30', 360.00);

-- news 
INSERT INTO `news` (`manager_id`, `title`, `content`, `publication_date`, `image`) VALUES
(1, 'A hot bath or sauna shows similar benefits to running, research indicates', 
'• I study the effects of exercise on the body - so it’s perhaps unsurprising that when I’m not in the lab, I like to keep active by hitting the gym or going for a run. But for many people, it’s much harder to get out and move their bodies. Modern life doesn’t always make it easy to maintain a healthy, active lifestyle.
\n• Yet even for someone like me, exercise isn’t always enjoyable. I have to repeatedly push myself to the point of tiredness and discomfort, in the hope I will get fitter and stay healthy. Surely the health benefits of a hot bath or a stint in a sauna — a far more attractive proposition — can’t be compared? Yet this is the question I have dedicated myself to answering. And the evidence, thus far, is promising.
\n• The term “exercise is medicine” is rightly well-publicised. It’s one of the best ways to stay healthy, yet medicine doesn’t work if you aren’t prepared to take it. Exercise adherence is very poor, with many people unwilling to exercise due to lack of time and motivation. And for those who are older or have chronic diseases, exercise can also cause pain, which for obvious reasons limits exercise further.
\n• Globally, about 25 per cent of adults don’t meet the minimum recommended physical activity levels of 150 minutes of moderate-intensity activity or 75 minutes of vigorous-intensity activity per week, or a combination of both. In the UK the figures are even worse, with around 34 per cent of men and 42 per cent of women not achieving these guidelines. Sadly, such high levels of sedentary behaviour are thought to be linked to about 11.6 per cent of UK deaths annually.
\n• In a world where many of us are working nine-to-five office jobs and our daily tasks can be completed by a mere click of a button, it’s easy to see why the modernisation of societies has led to higher levels of sedentary behaviour. There is an urgent need to find alternative strategies to improve health that people are willing to follow.
\n• In an effort to find such a solution, I’m looking into how hot baths and saunas affect the body. Throughout human history, multiple cultures around the world have used heat therapy to improve health. But until recently, the benefits of bathing were anecdotal and largely viewed as unscientific. However, in the last few decades evidence has been growing and today we know that regular bathing in a sauna or hot tub can help reduce the risk of cardiovascular disease — and may well have wider health benefits too.
\n• Our recent review of the research found that regular sauna or hot tub bathing can indeed bring about some similar health benefits to that of low- to moderate-intensity aerobic exercise, such as walking, jogging and cycling. At first glance, comparing a hot bath or sauna to a jog might seem illogical – after all, the former tends to be seen as relaxing and the latter tiring — but they are more similar than you may think.', 
'2023-05-10', 'news1.jpg'),

(2, 'Spongebob Squarepants promotes ‘violent and racist’ colonialism, university professor claims', 
'• Spongebob Squarepants has been accused of normalising the colonisation of indigenous lands by a professor at the University of Washington.
\n• The children’s cartoon – which marked its 20th anniversary this year – was criticised in a report by Professor Holly M Barker.
\n• She wrote: “SpongeBob SquarePants and his friends play a role in normalising the settler colonial takings of indigenous lands while erasing the ancestral Bikinian people from their nonfictional homeland.”
\n• The character Spongebob is a friendly sea sponge who lives in a pineapple under the sea among the other residents of a town called Bikini Bottom.
\n• Professor Barker believes that this is a reference to the real-life Bikini Atoll in the Marshall Islands in the Pacific Ocean.
\n• Natives of Bikini Atoll were relocated in 1946 so the US military could use the area for nuclear testing during the Cold War, which drew criticism from the media after it was revealed that the inhabitants were left without adequate food or water to prevent them from starvation.
\n• Later nuclear tests left the islands of the atoll contaminated with enough radiation to affect food grown in the soil, which meant the islands’ inhabitants were unable to return, and those who did experienced issues such as stillbirths, miscarriages and genetic abnormalities.
\n• This has given rise to fan theories that the cartoon inhabitants of Bikini Bottom owe their mutation to the testing.', 
'2023-06-05', 'news2.jpg');

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

-- Generate dates from April 15th, 2024 to July 1st, 2024
INSERT INTO `class_schedule` (`instructor_id`, `class_name_id`, `week`, `start_time`, `end_time`, `datetime`) VALUES
-- Day 1: 2024-04-01, Monday
(1, 2, 'Monday', '06:00', '07:00', '2024-04-01'),
(2, 3, 'Monday', '07:00', '08:00', '2024-04-01'),
(3, 1, 'Monday', '08:00', '09:00', '2024-04-01'),
(4, 5, 'Monday', '09:00', '10:00', '2024-04-01'),
(5, 4, 'Monday', '15:00', '16:00', '2024-04-01'),
(1, 3, 'Monday', '16:00', '17:00', '2024-04-01'),
(2, 2, 'Monday', '17:00', '18:00', '2024-04-01'),

-- Day 2: 2024-04-02, Tuesday
(3, 1, 'Tuesday', '06:00', '07:00', '2024-04-02'),
(4, 2, 'Tuesday', '07:00', '08:00', '2024-04-02'),
(5, 3, 'Tuesday', '09:00', '10:00', '2024-04-02'),
(1, 5, 'Tuesday', '10:00', '11:00', '2024-04-02'),
(2, 4, 'Tuesday', '14:00', '15:00', '2024-04-02'),
(3, 2, 'Tuesday', '15:00', '16:00', '2024-04-02'),
(4, 1, 'Tuesday', '16:00', '17:00', '2024-04-02'),

-- Day 3: 2024-04-03, Wednesday
(5, 3, 'Wednesday', '06:00', '07:00', '2024-04-03'),
(1, 2, 'Wednesday', '08:00', '09:00', '2024-04-03'),
(2, 1, 'Wednesday', '09:00', '10:00', '2024-04-03'),
(3, 4, 'Wednesday', '11:00', '12:00', '2024-04-03'),
(4, 5, 'Wednesday', '15:00', '16:00', '2024-04-03'),
(5, 3, 'Wednesday', '16:00', '17:00', '2024-04-03'),
(1, 2, 'Wednesday', '17:00', '18:00', '2024-04-03'),

-- Day 4: 2024-04-04, Thursday
(2, 1, 'Thursday', '06:00', '07:00', '2024-04-04'),
(3, 3, 'Thursday', '07:00', '08:00', '2024-04-04'),
(4, 5, 'Thursday', '08:00', '09:00', '2024-04-04'),
(5, 2, 'Thursday', '15:00', '16:00', '2024-04-04'),
(1, 4, 'Thursday', '16:00', '17:00', '2024-04-04'),
(2, 1, 'Thursday', '17:00', '18:00', '2024-04-04'),
(3, 3, 'Thursday', '18:00', '19:00', '2024-04-04'),

-- Day 5: 2024-04-05, Friday
(4, 5, 'Friday', '06:00', '07:00', '2024-04-05'),
(5, 2, 'Friday', '07:00', '08:00', '2024-04-05'),
(1, 1, 'Friday', '08:00', '09:00', '2024-04-05'),
(2, 4, 'Friday', '09:00', '10:00', '2024-04-05'),
(3, 5, 'Friday', '10:00', '11:00', '2024-04-05'),
(4, 2, 'Friday', '14:00', '15:00', '2024-04-05'),
(5, 1, 'Friday', '15:00', '16:00', '2024-04-05'),
(1, 3, 'Friday', '16:00', '17:00', '2024-04-05'),

-- Day 6: 2024-04-06, Saturday
(2, 4, 'Saturday', '06:00', '07:00', '2024-04-06'),
(3, 5, 'Saturday', '07:00', '08:00', '2024-04-06'),
(4, 2, 'Saturday', '08:00', '09:00', '2024-04-06'),
(5, 1, 'Saturday', '09:00', '10:00', '2024-04-06'),
(1, 3, 'Saturday', '10:00', '11:00', '2024-04-06'),
(2, 5, 'Saturday', '11:00', '12:00', '2024-04-06'),
(3, 2, 'Saturday', '15:00', '16:00', '2024-04-06'),
(4, 1, 'Saturday', '16:00', '17:00', '2024-04-06'),

-- Day 7: 2024-04-07, Sunday
(5, 4, 'Sunday', '06:00', '07:00', '2024-04-07'),
(1, 5, 'Sunday', '07:00', '08:00', '2024-04-07'),
(2, 3, 'Sunday', '08:00', '09:00', '2024-04-07'),
(3, 1, 'Sunday', '15:00', '16:00', '2024-04-07'),
(4, 2, 'Sunday', '16:00', '17:00', '2024-04-07'),
(5, 4, 'Sunday', '17:00', '18:00', '2024-04-07'),
(1, 3, 'Sunday', '18:00', '19:00', '2024-04-07'),

-- Day 8: 2024-04-08, Monday

(3, 11, 'Monday', '08:00', '09:00', '2024-04-08'),
(4, 10, 'Monday', '16:00', '17:00', '2024-04-08'),
(5, 9, 'Monday', '17:00', '18:00', '2024-04-08'),


-- Day 9: 2024-04-09, Tuesday
(4, 5, 'Tuesday', '08:00', '09:00', '2024-04-09'),
(5, 4, 'Tuesday', '09:00', '10:00', '2024-04-09'),
(1, 3, 'Tuesday', '10:00', '11:00', '2024-04-09'),
(3, 1, 'Tuesday', '18:00', '19:00', '2024-04-09'),

-- Day 10: 2024-04-10, Wedn
(1, 11, 'Wednesday', '08:00', '09:00', '2024-04-10'),
(2, 10, 'Wednesday', '09:00', '10:00', '2024-04-10'),
(3, 9, 'Wednesday', '15:00', '16:00', '2024-04-10'),
(4, 8, 'Wednesday', '16:00', '17:00', '2024-04-10'),
(5, 7, 'Wednesday', '17:00', '18:00', '2024-04-10'),

-- Day 11: 2024-04-11, Thursday
(3, 4, 'Thursday', '09:00', '10:00', '2024-04-11'),
(4, 3, 'Thursday', '10:00', '11:00', '2024-04-11'),
(5, 2, 'Thursday', '14:00', '15:00', '2024-04-11'),
(1, 1, 'Thursday', '15:00', '16:00', '2024-04-11'),
(2, 13, 'Thursday', '16:00', '17:00', '2024-04-11'),

-- Day 12: 2024-04-12, Friday
(5, 10, 'Friday', '08:00', '09:00', '2024-04-12'),
(1, 9, 'Friday', '09:00', '10:00', '2024-04-12'),
(2, 8, 'Friday', '10:00', '11:00', '2024-04-12'),
(3, 7, 'Friday', '14:00', '15:00', '2024-04-12'),
(4, 6, 'Friday', '15:00', '16:00', '2024-04-12'),

-- Day 13: 2024-04-13, Saturday
(2, 3, 'Saturday', '08:00', '09:00', '2024-04-13'),
(3, 2, 'Saturday', '15:00', '16:00', '2024-04-13'),
(4, 1, 'Saturday', '16:00', '17:00', '2024-04-13'),
(5, 13, 'Saturday', '17:00', '18:00', '2024-04-13'),

-- Day 14: 2024-04-14, Sunday
(3, 10, 'Sunday', '08:00', '09:00', '2024-04-14'),
(4, 9, 'Sunday', '15:00', '16:00', '2024-04-14'),
(5, 8, 'Sunday', '16:00', '17:00', '2024-04-14'),
(1, 7, 'Sunday', '17:00', '18:00', '2024-04-14'),

-- Day 15: 2024-04-15, Monday
(1, 6, 'Monday', '06:00', '07:00', '2024-04-15'),
(2, 5, 'Monday', '07:00', '08:00', '2024-04-15'),
(3, 4, 'Monday', '09:00', '10:00', '2024-04-15'),
(4, 3, 'Monday', '10:00', '11:00', '2024-04-15'),
(5, 2, 'Monday', '11:00', '12:00', '2024-04-15'),
(1, 1, 'Monday', '15:00', '16:00', '2024-04-15'),
(2, 13, 'Monday', '16:00', '17:00', '2024-04-15'),

-- Day 16: 2024-04-16, Tuesday
(3, 12, 'Tuesday', '06:00', '07:00', '2024-04-16'),
(4, 11, 'Tuesday', '07:00', '08:00', '2024-04-16'),
(5, 10, 'Tuesday', '08:00', '09:00', '2024-04-16'),
(1, 9, 'Tuesday', '09:00', '10:00', '2024-04-16'),
(2, 8, 'Tuesday', '10:00', '11:00', '2024-04-16'),
(3, 7, 'Tuesday', '17:00', '18:00', '2024-04-16'),
(4, 6, 'Tuesday', '18:00', '19:00', '2024-04-16'),

-- Day 17: 2024-04-17, Wednesday
(5, 5, 'Wednesday', '06:00', '07:00', '2024-04-17'),
(1, 4, 'Wednesday', '07:00', '08:00', '2024-04-17'),
(2, 3, 'Wednesday', '09:00', '10:00', '2024-04-17'),
(3, 2, 'Wednesday', '10:00', '11:00', '2024-04-17'),
(4, 1, 'Wednesday', '11:00', '12:00', '2024-04-17'),
(5, 13, 'Wednesday', '15:00', '16:00', '2024-04-17'),
(1, 12, 'Wednesday', '16:00', '17:00', '2024-04-17'),

-- Day 18: 2024-04-18, Thursday
(2, 11, 'Thursday', '06:00', '07:00', '2024-04-18'),
(3, 10, 'Thursday', '07:00', '08:00', '2024-04-18'),
(4, 9, 'Thursday', '08:00', '09:00', '2024-04-18'),
(5, 8, 'Thursday', '09:00', '10:00', '2024-04-18'),
(1, 7, 'Thursday', '10:00', '11:00', '2024-04-18'),
(2, 6, 'Thursday', '17:00', '18:00', '2024-04-18'),
(3, 5, 'Thursday', '18:00', '19:00', '2024-04-18'),

-- Day 19: 2024-04-19, Friday
(4, 4, 'Friday', '06:00', '07:00', '2024-04-19'),
(5, 3, 'Friday', '07:00', '08:00', '2024-04-19'),
(1, 2, 'Friday', '08:00', '09:00', '2024-04-19'),
(2, 1, 'Friday', '09:00', '10:00', '2024-04-19'),
(3, 13, 'Friday', '15:00', '16:00', '2024-04-19'),
(4, 12, 'Friday', '16:00', '17:00', '2024-04-19'),
(5, 11, 'Friday', '17:00', '18:00', '2024-04-19'),

-- Day 20: 2024-04-20, Saturday
(1, 10, 'Saturday', '06:00', '07:00', '2024-04-20'),
(2, 9, 'Saturday', '07:00', '08:00', '2024-04-20'),
(3, 8, 'Saturday', '08:00', '09:00', '2024-04-20'),
(4, 7, 'Saturday', '15:00', '16:00', '2024-04-20'),
(5, 6, 'Saturday', '16:00', '17:00', '2024-04-20'),
(1, 5, 'Saturday', '17:00', '18:00', '2024-04-20'),

-- Day 21: 2024-04-21, Sunday
(2, 4, 'Sunday', '06:00', '07:00', '2024-04-21'),
(3, 3, 'Sunday', '07:00', '08:00', '2024-04-21'),
(4, 2, 'Sunday', '08:00', '09:00', '2024-04-21'),
(5, 1, 'Sunday', '15:00', '16:00', '2024-04-21'),
(1, 13, 'Sunday', '16:00', '17:00', '2024-04-21'),
(2, 12, 'Sunday', '17:00', '18:00', '2024-04-21'),

-- Day 22: 2024-04-22, Monday
(3, 5, 'Monday', '06:00', '07:00', '2024-04-22'),
(5, 1, 'Monday', '09:00', '10:00', '2024-04-22'),
(2, 4, 'Monday', '10:00', '11:00', '2024-04-22'),
(4, 2, 'Monday', '13:00', '14:00', '2024-04-22'),
(1, 3, 'Monday', '16:00', '17:00', '2024-04-22'),
(3, 1, 'Monday', '17:00', '18:00', '2024-04-22'),
(5, 6, 'Monday', '19:00', '20:00', '2024-04-22'),

-- Day 23: 2024-04-23, Tuesday
(1, 2, 'Tuesday', '06:00', '07:00', '2024-04-23'),
(3, 4, 'Tuesday', '07:00', '08:00', '2024-04-23'),
(5, 5, 'Tuesday', '08:00', '09:00', '2024-04-23'),
(2, 1, 'Tuesday', '11:00', '12:00', '2024-04-23'),
(4, 3, 'Tuesday', '14:00', '15:00', '2024-04-23'),
(1, 6, 'Tuesday', '15:00', '16:00', '2024-04-23'),
(3, 2, 'Tuesday', '18:00', '19:00', '2024-04-23'),

-- Day 24: 2024-04-24, Wednesday
(5, 4, 'Wednesday', '06:00', '07:00', '2024-04-24'),
(2, 6, 'Wednesday', '09:00', '10:00', '2024-04-24'),
(4, 5, 'Wednesday', '10:00', '11:00', '2024-04-24'),
(1, 3, 'Wednesday', '13:00', '14:00', '2024-04-24'),
(3, 1, 'Wednesday', '14:00', '15:00', '2024-04-24'),
(5, 2, 'Wednesday', '17:00', '18:00', '2024-04-24'),
(2, 4, 'Wednesday', '19:00', '20:00', '2024-04-24'),

-- Day 25: 2024-04-25, Thursday
(4, 3, 'Thursday', '06:00', '07:00', '2024-04-25'),
(1, 5, 'Thursday', '07:00', '08:00', '2024-04-25'),
(3, 6, 'Thursday', '08:00', '09:00', '2024-04-25'),
(5, 1, 'Thursday', '15:00', '16:00', '2024-04-25'),
(2, 2, 'Thursday', '16:00', '17:00', '2024-04-25'),
(4, 4, 'Thursday', '17:00', '18:00', '2024-04-25'),
(1, 3, 'Thursday', '18:00', '19:00', '2024-04-25'),

-- Day 26: 2024-04-26, Friday
(3, 5, 'Friday', '06:00', '07:00', '2024-04-26'),
(5, 4, 'Friday', '09:00', '10:00', '2024-04-26'),
(2, 6, 'Friday', '10:00', '11:00', '2024-04-26'),
(4, 1, 'Friday', '13:00', '14:00', '2024-04-26'),
(1, 2, 'Friday', '14:00', '15:00', '2024-04-26'),
(3, 3, 'Friday', '15:00', '16:00', '2024-04-26'),
(5, 5, 'Friday', '19:00', '20:00', '2024-04-26'),

-- Day 27: 2024-04-27, Saturday
(2, 4, 'Saturday', '06:00', '07:00', '2024-04-27'),
(4, 2, 'Saturday', '07:00', '08:00', '2024-04-27'),
(1, 1, 'Saturday', '08:00', '09:00', '2024-04-27'),
(3, 3, 'Saturday', '15:00', '16:00', '2024-04-27'),
(5, 5, 'Saturday', '16:00', '17:00', '2024-04-27'),
(2, 6, 'Saturday', '17:00', '18:00', '2024-04-27'),
(4, 4, 'Saturday', '18:00', '19:00', '2024-04-27'),

-- Day 28: 2024-04-28, Sunday
(1, 2, 'Sunday', '06:00', '07:00', '2024-04-28'),
(3, 1, 'Sunday', '07:00', '08:00', '2024-04-28'),
(5, 3, 'Sunday', '09:00', '10:00', '2024-04-28'),
(2, 5, 'Sunday', '10:00', '11:00', '2024-04-28'),
(4, 6, 'Sunday', '14:00', '15:00', '2024-04-28'),
(1, 4, 'Sunday', '15:00', '16:00', '2024-04-28'),
(3, 2, 'Sunday', '16:00', '17:00', '2024-04-28'),

-- Day 29: 2024-04-29, Monday
(5, 1, 'Monday', '06:00', '07:00', '2024-04-29'),
(2, 3, 'Monday', '07:00', '08:00', '2024-04-29'),
(4, 5, 'Monday', '08:00', '09:00', '2024-04-29'),
(1, 6, 'Monday', '09:00', '10:00', '2024-04-29'),
(3, 4, 'Monday', '17:00', '18:00', '2024-04-29'),
(5, 2, 'Monday', '18:00', '19:00', '2024-04-29'),
(2, 1, 'Monday', '19:00', '20:00', '2024-04-29'),

-- Day 30: 2024-04-30, Tuesday
(4, 3, 'Tuesday', '06:00', '07:00', '2024-04-30'),
(1, 5, 'Tuesday', '07:00', '08:00', '2024-04-30'),
(3, 6, 'Tuesday', '15:00', '16:00', '2024-04-30'),
(5, 4, 'Tuesday', '16:00', '17:00', '2024-04-30'),
(2, 2, 'Tuesday', '17:00', '18:00', '2024-04-30'),
(4, 1, 'Tuesday', '18:00', '19:00', '2024-04-30'),

-- Day 31: 2024-05-01, Wednesday
(1, 3, 'Wednesday', '06:00', '07:00', '2024-05-01'),
(2, 1, 'Wednesday', '07:00', '08:00', '2024-05-01'),
(3, 2, 'Wednesday', '08:00', '09:00', '2024-05-01'),
(4, 5, 'Wednesday', '10:00', '11:00', '2024-05-01'),
(5, 4, 'Wednesday', '11:00', '12:00', '2024-05-01'),
(1, 6, 'Wednesday', '14:00', '15:00', '2024-05-01'),
(2, 12, 'Wednesday', '16:00', '17:00', '2024-05-01'),
(3, 11, 'Wednesday', '17:00', '18:00', '2024-05-01'),
(4, 10, 'Wednesday', '19:00', '20:00', '2024-05-01'),

-- Day 32: 2024-05-02, Thursday
(5, 9, 'Thursday', '06:00', '07:00', '2024-05-02'),
(1, 8, 'Thursday', '07:00', '08:00', '2024-05-02'),
(2, 7, 'Thursday', '09:00', '10:00', '2024-05-02'),
(3, 6, 'Thursday', '10:00', '11:00', '2024-05-02'),
(4, 5, 'Thursday', '13:00', '14:00', '2024-05-02'),
(5, 4, 'Thursday', '15:00', '16:00', '2024-05-02'),
(1, 3, 'Thursday', '16:00', '17:00', '2024-05-02'),
(2, 2, 'Thursday', '17:00', '18:00', '2024-05-02'),
(3, 1, 'Thursday', '18:00', '19:00', '2024-05-02'),

-- Day 33: 2024-05-03, Friday
(4, 13, 'Friday', '06:00', '07:00', '2024-05-03'),
(5, 12, 'Friday', '08:00', '09:00', '2024-05-03'),
(1, 11, 'Friday', '09:00', '10:00', '2024-05-03'),
(2, 10, 'Friday', '11:00', '12:00', '2024-05-03'),
(3, 9, 'Friday', '13:00', '14:00', '2024-05-03'),
(4, 8, 'Friday', '14:00', '15:00', '2024-05-03'),
(5, 7, 'Friday', '15:00', '16:00', '2024-05-03'),
(1, 6, 'Friday', '17:00', '18:00', '2024-05-03'),
(2, 5, 'Friday', '19:00', '20:00', '2024-05-03'),

-- Day 34: 2024-05-04, Saturday
(3, 4, 'Saturday', '06:00', '07:00', '2024-05-04'),
(4, 3, 'Saturday', '07:00', '08:00', '2024-05-04'),
(5, 2, 'Saturday', '09:00', '10:00', '2024-05-04'),
(1, 1, 'Saturday', '10:00', '11:00', '2024-05-04'),
(2, 13, 'Saturday', '11:00', '12:00', '2024-05-04'),
(3, 12, 'Saturday', '16:00', '17:00', '2024-05-04'),
(4, 11, 'Saturday', '17:00', '18:00', '2024-05-04'),
(5, 10, 'Saturday', '18:00', '19:00', '2024-05-04'),

-- Day 35: 2024-05-05, Sunday
(1, 9, 'Sunday', '06:00', '07:00', '2024-05-05'),
(2, 8, 'Sunday', '08:00', '09:00', '2024-05-05'),
(3, 7, 'Sunday', '09:00', '10:00', '2024-05-05'),
(4, 6, 'Sunday', '14:00', '15:00', '2024-05-05'),
(5, 5, 'Sunday', '15:00', '16:00', '2024-05-05'),
(1, 4, 'Sunday', '16:00', '17:00', '2024-05-05'),
(2, 3, 'Sunday', '17:00', '18:00', '2024-05-05'),
(3, 2, 'Sunday', '18:00', '19:00', '2024-05-05');

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
(1, 152, NULL, 'aerobics class', 'confirmed', '2024-04-20'),
(2, 152, NULL, 'aerobics class', 'confirmed', '2024-04-20'),
(3, 152, NULL, 'aerobics class', 'confirmed', '2024-04-20'),
(4, 152, NULL, 'aerobics class', 'confirmed', '2024-04-20'),
(5, 152, NULL, 'aerobics class', 'confirmed', '2024-04-20'),
(6, 152, NULL, 'aerobics class', 'confirmed', '2024-04-20'),
(7, 152, NULL, 'aerobics class', 'confirmed', '2024-04-20'),
(8, 152, NULL, 'aerobics class', 'confirmed', '2024-04-20'),
(9, 152, NULL, 'aerobics class', 'confirmed', '2024-04-20'),
(10, 152, NULL, 'aerobics class', 'confirmed', '2024-04-20'),
(11, 152, NULL, 'aerobics class', 'confirmed', '2024-04-20'),
(12, 157, NULL, 'aerobics class', 'confirmed', '2024-04-21'),
(13, 157, NULL, 'aerobics class', 'confirmed', '2024-04-21'),
(14, 157, NULL, 'aerobics class', 'confirmed', '2024-04-21'),
(15, 157, NULL, 'aerobics class', 'confirmed', '2024-04-21'),
(16, 157, NULL, 'aerobics class', 'confirmed', '2024-04-21'),
(17, 157, NULL, 'aerobics class', 'confirmed', '2024-04-21'),
(18, 157, NULL, 'aerobics class', 'confirmed', '2024-04-21'),
(19, 157, NULL, 'aerobics class', 'confirmed', '2024-04-21'),
(20, 157, NULL, 'aerobics class', 'confirmed', '2024-04-21'),

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
(1, 110111, 1, NULL, 'membership', 700.00, '2024-03-01'),
(2, 110112, 1, NULL, 'membership', 60.00, '2024-04-01'),
(3, 110113, 1, NULL, 'membership', 700.00, '2024-03-01'),
(4, 110114, 1, NULL, 'membership', 700.00, '2024-03-01'),
(5, 110115, 1, NULL, 'membership', 700.00, '2024-03-01'),
(6, 110116, 1, NULL, 'membership', 700.00, '2024-03-01'),
(7, 110117, 1, NULL, 'membership', 700.00, '2024-03-01'),
(8, 110118, 1, NULL, 'membership', 700.00, '2024-03-01'),
(9, 110119, 1, NULL, 'membership', 700.00, '2024-03-01'),
(10, 110120, 1, NULL, 'membership', 700.00, '2024-03-01'),
(11, 110121, 1, NULL, 'membership', 700.00, '2024-03-01'),
(12, 110122, 1, NULL, 'membership', 700.00, '2024-03-01'),
(13, 110123, 1, NULL, 'membership', 700.00, '2024-03-01'),
(14, 110124, 1, NULL, 'membership', 700.00, '2024-03-01'),
(15, 110125, 1, NULL, 'membership', 700.00, '2024-03-01'),
(16, 110126, 1, NULL, 'membership', 700.00, '2024-03-01'),
(17, 110127, 1, NULL, 'membership', 700.00, '2024-03-01'),
(18, 110128, 1, NULL, 'membership', 700.00, '2024-03-01'),
(19, 110129, 1, NULL, 'membership', 700.00, '2024-03-01'),
(20, 110130, 1, NULL, 'membership', 360.00, '2024-03-01'),

(10, 110120, 2, 1, 'lesson', 50.00, '2024-04-22'),
(11, 110121, 2, 2, 'lesson', 50.00, '2024-04-22'),
(12, 110122, 2, 3, 'lesson', 50.00, '2024-04-22'),
(13, 110123, 2, 4, 'lesson', 50.00, '2024-04-23'),
(14, 110124, 2, 5, 'lesson', 50.00, '2024-04-23'),
(15, 110125, 2, 6, 'lesson', 50.00, '2024-04-23'),
(16, 110126, 2, 7, 'lesson', 50.00, '2024-04-24'),
(17, 110127, 2, 8, 'lesson', 50.00, '2024-04-24'),
(18, 110128, 2, 9, 'lesson', 50.00, '2024-04-24'),
(19, 110129, 2, 10, 'lesson', 50.00, '2024-04-25'),
(20, 110130, 2, 11, 'lesson', 50.00, '2024-04-25');

INSERT INTO `attendance` (`class_id`, `schedule_type`, `member_id`, `attended`, `attendance_status`) VALUES 
(1, 'class', 1, true, 'present'),
(2, 'class', 1, true, 'late');




