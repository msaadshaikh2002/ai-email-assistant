# ai-email-assistant
An AI-powered communication assistant that helps support teams handle large volumes of customer emails.


ai-email-assistant/
│
├── backend/                       # Backend (FastAPI)
│   ├── fastapi_ai_email_assistant.py   ✅ your existing Python code
│   ├── requirements.txt
│   ├── Dockerfile
│
├── frontend/                      # Frontend (Next.js)
│   ├── package.json
│   ├── pages/
│   │   └── index.jsx
│   ├── Dockerfile
│
├── docker-compose.yml             # Orchestrates backend + frontend + MongoDB
└── README.md                      # Docs & description
