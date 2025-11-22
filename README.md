📚 Library Management System (Python + MySQL)

A simple and efficient Library Management System built using Python (Tkinter GUI) and MySQL.
This repository contains all the core files required to run the project, including the main GUI program, complete SQL database script, and project report.

📂 Files Included
1. main.py

Complete Python GUI application

Built using Tkinter

Login system with three roles:

Admin

Librarian

Viewer

Fully functional CRUD operations:

Books

Members

Publishers

Librarians

Issue / Return

Fines

Auto-updates available copies using triggers

Uses stored procedures & SQL functions

Displays reports using aggregate, nested, and join queries

2. database.sql

Complete SQL script containing:

Database creation

All tables (DDL)

Insert statements (DML)

Triggers

Stored Procedures

SQL Functions

Aggregate, Join & Nested Queries

This file can be directly imported into MySQL to create the full database.

3. Project Report

A professional document that includes:

Title page

Abstract

User Requirement Specification

ER Diagram

Relational Schema

DDL Commands

CRUD Screenshots

Triggers, Procedures, Functions

SQL Queries

GitHub Repository link

How to Run
1. Import the database

Run this command after installing MySQL:

mysql -u root -p < database.sql

2. Install required Python modules
pip install mysql-connector-python

3. Run the application
python main.py

🛠 Technologies Used

Python 3

Tkinter (GUI)

MySQL Database

mysql-connector-python

SQL Triggers, Procedures, Functions

🧾 Features

User login & authentication

Full CRUD operations for all modules

Issue and return books

Automatic copy update using Triggers

Fine management

Stored procedures for insert/update/delete

Function-based reporting

Clean and simple Tkinter interface
