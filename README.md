# Molecule WorkFlow Pro - Backend

FastAPI backend with MongoDB integration.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run server:
```bash
python main.py
```

3. Access API docs:
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

Create `.env` file (already created):
```
MONGODB_URI=mongodb+srv://Molecule:@admin123@@moleculedata.lu7rmug.mongodb.net/molecule_workflow
JWT_SECRET=molecule_workflow_secret_key_2024_secure_token
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── models/              # Pydantic models
│   ├── user.py
│   ├── report.py
│   └── task.py
├── routes/              # API endpoints
│   ├── auth.py
│   ├── users.py
│   ├── reports.py
│   ├── tasks.py
│   └── dashboard.py
├── utils/               # Utilities
│   └── auth.py         # JWT & password hashing
├── requirements.txt     # Python dependencies
└── .env                # Environment variables
```

## API Testing

Use the Swagger UI at http://localhost:8000/docs to test all endpoints interactively.
"# Reporting-Backend" 
