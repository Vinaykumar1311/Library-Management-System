-- ============================
-- DATABASE
-- ============================
CREATE DATABASE IF NOT EXISTS LibraryDB;
USE LibraryDB;

-- ============================
-- TABLES (DDL)
-- ============================
CREATE TABLE Publishers (
    publisher_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    address VARCHAR(200)
);

CREATE TABLE Books (
    book_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100) NOT NULL,
    publisher_id INT,
    year_published YEAR CHECK (year_published >= 1800),
    available_copies INT DEFAULT 1 CHECK (available_copies >= 0),
    CONSTRAINT fk_publisher FOREIGN KEY (publisher_id)
        REFERENCES Publishers(publisher_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE Members (
    member_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    join_date DATE DEFAULT (CURRENT_DATE)
);

CREATE TABLE Librarian (
    librarian_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15)
);

CREATE TABLE Issue (
    issue_id INT PRIMARY KEY AUTO_INCREMENT,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    librarian_id INT,
    issue_date DATE DEFAULT (CURRENT_DATE),
    return_date DATE,
    CONSTRAINT fk_book FOREIGN KEY (book_id)
        REFERENCES Books(book_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_member FOREIGN KEY (member_id)
        REFERENCES Members(member_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_librarian FOREIGN KEY (librarian_id)
        REFERENCES Librarian(librarian_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE Fine (
    fine_id INT PRIMARY KEY AUTO_INCREMENT,
    issue_id INT NOT NULL,
    amount DECIMAL(8,2) CHECK (amount >= 0),
    status VARCHAR(20) DEFAULT 'Unpaid' CHECK (status IN ('Paid','Unpaid')),
    CONSTRAINT fk_issue FOREIGN KEY (issue_id)
        REFERENCES Issue(issue_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE DeletedBooksLog (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT,
    title VARCHAR(150),
    deleted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE DeletedMembersLog (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    name VARCHAR(100),
    deleted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Librarian', 'Viewer') DEFAULT 'Librarian'
);

-- ============================
-- INSERT STATEMENTS (DML)
-- ============================
INSERT INTO Publishers (name, address) VALUES
('Pearson Education', 'New Delhi, India'),
('O’Reilly Media', 'Sebastopol, USA'),
('McGraw Hill', 'Bangalore, India'),
('Oxford University Press', 'Oxford, UK'),
('Springer Nature', 'Berlin, Germany'),
('vinaykatnur', 'bengaluru');

INSERT INTO Books (title, author, publisher_id, year_published, available_copies) VALUES
('Database System Concepts', 'Abraham Silberschatz', 3, 2019, 5),
('Learning Python', 'Mark Lutz', 2, 2021, 3),
('Operating System Concepts', 'Peter Galvin', 3, 2018, 4),
('Artificial Intelligence: A Modern Approach', 'Stuart Russell', 1, 2020, 2),
('Computer Networks', 'Andrew Tanenbaum', 4, 2017, 6);

INSERT INTO Members (name, email, phone, join_date) VALUES
('Ravi Kumar', 'ravi.kumar@example.com', '9876543210', '2023-01-10'),
('Sneha Reddy', 'sneha.reddy@example.com', '9876501234', '2023-02-14'),
('Aman Verma', 'aman.verma@example.com', '9123456780', '2023-03-20'),
('Priya Nair', 'priya.nair@example.com', '9345678123', '2023-04-05'),
('Karthik Shetty', 'karthik.shetty@example.com', '9456789012', '2023-05-18'),
('vikram', 'vikram@gmail.com', '7897897890', '2025-11-11');

INSERT INTO Librarian (name, email, phone) VALUES
('Anita Sharma', 'anita.sharma@library.com', '9871112222'),
('Rahul Menon', 'rahul.menon@library.com', '9873334444');

INSERT INTO Issue (book_id, member_id, librarian_id, issue_date) VALUES
(1, 1, 1, '2025-11-10'),
(2, 2, 2, '2025-11-09'),
(3, 3, 1, '2025-11-08');

UPDATE Issue SET return_date = '2025-11-11' WHERE issue_id = 1;

INSERT INTO Fine (issue_id, amount, status) VALUES
(1, 100, 'Unpaid'),
(2, 50, 'Paid'),
(3, 150, 'Unpaid');

INSERT INTO Users (username, password, role) VALUES
('admin', 'admin123', 'Admin'),
('anita', 'lib123', 'Librarian'),
('viewer', 'view123', 'Viewer');

-- ============================
-- TRIGGERS
-- ============================
DELIMITER $$

CREATE TRIGGER trg_after_issue_insert
AFTER INSERT ON Issue
FOR EACH ROW
BEGIN
    UPDATE Books
    SET available_copies = available_copies - 1
    WHERE book_id = NEW.book_id;
END$$

CREATE TRIGGER trg_after_return_update
AFTER UPDATE ON Issue
FOR EACH ROW
BEGIN
    IF NEW.return_date IS NOT NULL AND 
       (OLD.return_date IS NULL OR OLD.return_date <> NEW.return_date) THEN
        UPDATE Books
        SET available_copies = available_copies + 1
        WHERE book_id = NEW.book_id;
    END IF;
END$$

CREATE TRIGGER trg_after_book_delete
AFTER DELETE ON Books
FOR EACH ROW
BEGIN
    INSERT INTO DeletedBooksLog (book_id, title)
    VALUES (OLD.book_id, OLD.title);
END$$

CREATE TRIGGER trg_after_member_delete
AFTER DELETE ON Members
FOR EACH ROW
BEGIN
    INSERT INTO DeletedMembersLog (member_id, name)
    VALUES (OLD.member_id, OLD.name);
END$$

DELIMITER ;

-- ============================
-- STORED PROCEDURES
-- ============================
DELIMITER $$

CREATE PROCEDURE AddNewBook(
    IN p_title VARCHAR(150),
    IN p_author VARCHAR(100),
    IN p_publisher_id INT,
    IN p_year YEAR,
    IN p_copies INT
)
BEGIN
    INSERT INTO Books (title, author, publisher_id, year_published, available_copies)
    VALUES (p_title, p_author, p_publisher_id, p_year, p_copies);
END$$

CREATE PROCEDURE AddNewMember(
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_phone VARCHAR(15)
)
BEGIN
    INSERT INTO Members (name, email, phone)
    VALUES (p_name, p_email, p_phone);
END$$

CREATE PROCEDURE UpdateMemberDetails(
    IN p_member_id INT,
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_phone VARCHAR(15)
)
BEGIN
    UPDATE Members
    SET name = p_name,
        email = p_email,
        phone = p_phone
    WHERE member_id = p_member_id;
END$$

CREATE PROCEDURE DeleteBook(IN p_book_id INT)
BEGIN
    DELETE FROM Books WHERE book_id = p_book_id;
END$$

CREATE PROCEDURE DeleteMember(IN p_member_id INT)
BEGIN
    DELETE FROM Members WHERE member_id = p_member_id;
END$$

CREATE PROCEDURE RecordFinePayment(IN p_fine_id INT)
BEGIN
    UPDATE Fine
    SET status = 'Paid'
    WHERE fine_id = p_fine_id;
END$$

DELIMITER ;

-- ============================
-- FUNCTIONS
-- ============================
DELIMITER $$

CREATE FUNCTION GetTotalFine(p_member_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10,2);
    SELECT SUM(f.amount)
    INTO total
    FROM Fine f
    JOIN Issue i ON f.issue_id = i.issue_id
    WHERE i.member_id = p_member_id;

    RETURN IFNULL(total, 0.00);
END$$

CREATE FUNCTION GetAvailableBooks()
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total INT;
    SELECT SUM(available_copies) INTO total FROM Books;
    RETURN total;
END$$

CREATE FUNCTION GetMemberCount()
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE cnt INT;
    SELECT COUNT(*) INTO cnt FROM Members;
    RETURN cnt;
END$$

CREATE FUNCTION GetBooksByPublisher(p_publisher_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE count_books INT;
    SELECT COUNT(*) INTO count_books FROM Books WHERE publisher_id = p_publisher_id;
    RETURN count_books;
END$$

DELIMITER ;

-- ============================
-- SQL QUERIES
-- ============================
SELECT p.name AS Publisher, COUNT(b.book_id) AS TotalBooks
FROM Publishers p
LEFT JOIN Books b ON p.publisher_id = b.publisher_id
GROUP BY p.name;

SELECT m.name AS MemberName, b.title AS BookTitle, i.issue_date, i.return_date
FROM Members m
JOIN Issue i ON m.member_id = i.member_id
JOIN Books b ON i.book_id = b.book_id;

SELECT title
FROM Books
WHERE publisher_id IN (
    SELECT publisher_id
    FROM Publishers
    WHERE name = 'McGraw Hill'
);
