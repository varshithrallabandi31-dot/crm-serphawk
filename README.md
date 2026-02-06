# Cold Outreach CRM

AI-powered cold email outreach automation platform with intelligent lead analysis and personalized email generation.

## 🚀 Features

- **AI-Powered Analysis**: Automatically analyzes prospect websites using Google Gemini AI
- **Smart Email Generation**: Creates personalized cold emails based on company analysis
- **Market Intelligence**: Identifies pain points and recommends relevant services
- **Email Automation**: Sends emails via SMTP with rate limiting
- **Activity Tracking**: Logs all outreach activities in PostgreSQL database
- **Duplicate Prevention**: Ensures you don't contact the same company twice
- **Rate Limiting**: Prevents spam (50 emails/hour by default)

## 🏗️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** (Neon) - Cloud database
- **Google Gemini AI** - Content analysis and email generation
- **Playwright** - Website scraping
- **SQLModel** - Type-safe database ORM

### Frontend
- **Next.js 16** - React framework
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

## 📋 Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL database (Neon recommended)
- Google Gemini API key
- SMTP email credentials

## 🛠️ Local Development

### Backend Setup

```bash
cd Agent_Email
pip install -r requirements.txt
python main.py
```

Backend runs on: http://localhost:8000

### Frontend Setup

```bash
cd Agent_Email/frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:3000

## 🌍 Environment Variables

Create `.env` file in `Agent_Email/` directory:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Email Configuration
OUTLOOK_EMAIL=your_email@domain.com
OUTLOOK_PASSWORD=your_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
USE_SSL=True

# Database
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Application Settings
SENDER_EMAIL=your_email@domain.com
HOURLY_EMAIL_LIMIT=50
```

## 🚀 Deployment

This project is configured for deployment on Railway.

### Deploy to Railway

1. Push code to GitHub
2. Create Railway project
3. Add two services:
   - Backend: Root directory `Agent_Email`
   - Frontend: Root directory `Agent_Email/frontend`
4. Add environment variables to each service
5. Deploy!

See [deployment_guide.md](deployment_guide.md) for detailed instructions.

## 📝 API Endpoints

- `GET /` - API health check
- `POST /draft-lead` - Generate email draft
- `POST /send-lead` - Send approved email
- `GET /activities` - Fetch recent activities
- `GET /health` - Health check

## 🔒 Security Features

- Environment-based configuration
- CORS protection
- Rate limiting
- Duplicate prevention
- SSL/TLS email encryption

## 📄 License

Private project - All rights reserved

## 👨‍💻 Author

Developed by Sreeja
