## Django REST Framework Task Manager API with Full JWT Authentication

## To Run this Project follow below:

📝 Task Manager REST API

A simple yet powerful Task Manager API built with Django & Django REST Framework (DRF).
This API provides endpoints to manage tasks with full CRUD (Create, Read, Update, Delete) functionality and includes user authentication for secure access.

🚀 Features

🔐 User Authentication (JWT-based)

📌 Task Management – Create, Read, Update, Delete tasks

📄 Pagination support for task lists

⚡ Built with Django REST Framework

🗂️ Clean and scalable project structure

📚 API Endpoints
Authentication
```
POST /api/auth/register/ → Register new user

POST /api/auth/login/ → Obtain JWT token

POST /api/auth/profile/ → Check current login user details using Bearer auth token

POST /auth/api/changepassword/ Change password
```
Tasks
```
GET /api/auth/tasks/?Page=1 → List all tasks (with pagination)

GET /api/auth/tasks?completed=true  List all tasks (is Marked Completed)

POST /api/auth/tasks/ → Create a new task

GET /api/auth/tasks/{id}/ → Retrieve a single task

PUT /api/auth/tasks/{id}/ → Update a task (all fields required)

PATCH /api/auth/tasks/{id}/ → Update a task (only some fields)

DELETE /api/auth/tasks/{id}/ → Delete a task
```
🛠️ Tech Stack

Django 5.2.6

Django REST Framework

SimpleJWT

for authentication

SQLite (configurable)

⚙️ Installation
# Clone the repo
```
git clone https://github.com/yourusername/task-manager-api.git
cd task-manager-api
```

# Create virtual environment
```
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```
# Install dependencies
```
pip install -r requirements.txt
```

# Apply migrations
```
python manage.py migrate
```

# Run server
```
python manage.py runserver
```

🔑 Usage

Register a new account using /api/auth/register/

Obtain a JWT token using /api/auth/login/

Use the token to access protected task endpoints and Change password
