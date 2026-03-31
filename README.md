📖 About The Project
A lightweight, functional desktop application developed for a university project. This Insurance Management System handles core operations like user authentication, database management, and flexible insurance policy tracking.

Built entirely in Python and backed by a MySQL database, the application is designed to be compiled into a standalone .exe file for easy distribution and use without requiring a local Python environment on the end user's machine.

✨ Key Features
User Authentication: Secure Login and Registration pages for users to access the system.

Flexible Insurance Schemes: Dynamic policy management supporting various subscription billing cycles (Weekly, Monthly, 6-Months, Yearly).

Database Integration: Persistent data storage using MySQL to track user credentials, policies, and active schemes.

Standalone Executable: Fully compiled .exe application for seamless desktop deployment.

💻 Tech Stack & Development Environment
Language: Python 3.x

Database: MySQL

Development Environment: Visual Studio Community / VS Code

GUI Framework: (e.g., Tkinter, PyQt, or CustomTkinter - update this based on what you use!)

Executable Compiler: PyInstaller (or auto-py-to-exe)

🚀 Getting Started
Prerequisites
To run the source code or build the executable yourself, you will need:

Python 3.x: Installed and added to your system PATH.

MySQL Server: Installed and running locally.

Required Python Libraries: mysql-connector-python, plus any GUI libraries you choose.

Installation & Setup
Clone the repository:

Bash
git clone https://github.com/yourusername/insurance-management-system.git
cd insurance-management-system
Set up the Database:

Open your MySQL client or command line.

Run the provided SQL script to create the database and tables:

SQL
SOURCE db_schema.sql; 
Update the database connection credentials (host, user, password) inside the Python source code to match your local MySQL setup.

Install Dependencies:

Bash
pip install -r requirements.txt
Run the Source Code:

Bash
python main.py
📦 Building the Executable (.exe)
To convert the Python scripts into a standalone desktop application, we use PyInstaller.

Install PyInstaller:

Bash
pip install pyinstaller
Build the .exe file:

Bash
pyinstaller --noconsole --onefile main.py
(Note: The generated .exe will be located in the dist/ folder. Ensure your MySQL server is running when executing the application.)

🎓 Academic Disclaimer
This project was created for educational purposes as part of a university curriculum. It is a functional prototype and is not intended for real-world commercial use. It lacks the advanced encryption, compliance (like HIPAA/GDPR), and security features required for actual financial and personal insurance data handling.
