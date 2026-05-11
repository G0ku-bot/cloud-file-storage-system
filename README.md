Cloud File Storage System

A secure and user-friendly cloud-based file storage system developed using Python (Flask), HTML, CSS, and JavaScript. This project allows users to upload, manage, and access files through a simple web interface with authentication features.

Features:
User Registration & Login Authentication
Secure File Upload System
File Management Dashboard
Download & Access Stored Files
Responsive User Interface
Database Integration
Session Management & Authentication

Tech Stack:
Frontend
HTML5
CSS3
JavaScript
Backend
Python
Flask
Database
MySQL

Project Structure

```bash
DRIVE-APPLICATION/
│
├── backend/
│   ├── config/
│   ├── uploads/
│   ├── venv/
│   ├── .env
│   ├── .gitignore
│   └── app.py
│
├── Frontend/
│   ├── css/
│   ├── js/
│   ├── dashboard.html
│   ├── files.html
│   ├── index.html
│   ├── register.html
│   └── upload.html
│
└── README.md
```

Installation & Setup

1. Clone the Repository

```bash
git clone https://github.com/G0ku-bot/cloud-file-storage-system.git
cd DRIVE-APPLICATION
```

2. Create Virtual Environment

```bash
python -m venv venv
```

3. Activate Virtual Environment

Windows
```bash
venv\Scripts\activate
```

Linux / Mac
```bash
source venv/bin/activate
```

4. Install Dependencies

```bash
pip install -r requirements.txt
```

5. Configure Environment Variables

Create a `.env` file inside the `backend/` folder and add your database credentials and secret keys.

Example:

```env
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database
SECRET_KEY=your_secret_key
```

6. Run the Application

```bash
cd backend
python app.py
```

7. Open in Browser

```bash
http://127.0.0.1:5000
```
 screenshots:

Login Page <img width="1916" height="975" alt="Screenshot 2026-05-06 221732" src="https://github.com/user-attachments/assets/0b6b16df-503a-4d81-973d-f9d19ca0df81" />
Register Page <img width="1916" height="977" alt="Screenshot 2026-05-06 221749" src="https://github.com/user-attachments/assets/c03a42bc-f2b7-42e1-9136-f46b99ecb6eb" />
Dashboard <img width="1919" height="973" alt="Screenshot 2026-05-06 221823" src="https://github.com/user-attachments/assets/45692cfb-627c-4f71-a1e5-6e0dcc3eb40e" />
File Upload Page<img width="1919" height="977" alt="Screenshot 2026-05-06 221841" src="https://github.com/user-attachments/assets/0393bf60-0452-4de3-b821-71c7152ad190" />
File Management System <img width="1918" height="976" alt="Screenshot 2026-05-06 221913" src="https://github.com/user-attachments/assets/3d158074-f026-4bb3-a802-065c91cad33b" />

Learning Outcomes:

Through this project, I gained practical experience in:
Flask Web Development
Backend & Frontend Integration
Database Connectivity
User Authentication
File Handling in Python
Building Full Stack Applications
Future Improvements
Cloud Deployment
File Sharing Feature
Password Encryption
User Roles & Permissions
Drag & Drop Uploads
Email Verification
Author

Salik Ahmed
GitHub: G0ku-bot

