# StudyAgent

StudyAgent is an AI-powered study assistant that helps students create personalized study plans, provides interactive learning support, and offers real-time assistance through an intelligent chat interface.

## Features

- **AI-Generated Study Plans**: Upload your study materials and get a personalized, structured study plan
- **Interactive Chat Support**: Ask questions about your study materials and get instant, contextually-relevant answers
- **Daily Breakdown**: Organized day-by-day study schedule with clear topics and time allocations
- **Key Concepts & Formulas**: Automatic extraction of important concepts and formulas from your materials
- **Progress Tracking**: Mark topics as completed and track your study progress

## Tech Stack

### Backend
- FastAPI
- CrewAI for AI agent orchestration
- Pydantic for data validation
- OpenRouter API for LLM access

### Frontend
- Next.js
- TypeScript
- Tailwind CSS for styling

## Project Structure

The project is divided into two main parts:

### Backend (/backend)
- FastAPI application with routes for uploading materials, generating study plans, and chat functionality
- AI workflow utilities for processing study materials and generating plans
- Data adapters for transforming between backend and frontend data structures

### Frontend (/src)
- Next.js application with pages for uploading materials, viewing study plans, and interactive study sessions
- Components for chat interface, study plan visualization, and navigation
- Responsive design for desktop and mobile use

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenRouter API key

### Installation

1. Clone the repository
2. Set up the backend:
   ```
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```
   cd src
   npm install
   ```

4. Create a `.env` file in the backend directory with your API keys:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   DEEPSEEK_MODEL_NAME=deepseek/deepseek-chat-v3-0324:free
   ```

### Running the Application

1. Start the backend server:
   ```
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Start the frontend development server:
   ```
   cd src
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:3000`

## Deployment

The StudyAgent application is deployed and accessible online:

- **Frontend**: [https://ai-studyagent.vercel.app](https://ai-studyagent.vercel.app)
- **Backend API**: 
  - Railway (Primary): [https://aistudyagent-production.up.railway.app](https://aistudyagent-production.up.railway.app)
  - Render (Backup): [https://ai-studyagent.onrender.com](https://ai-studyagent.onrender.com)

You can use the deployed version without setting up the local development environment. The frontend connects to the deployed backend automatically.

### Sample Data

If you want to explore the application without uploading your own materials, you can use the "Load Sample Data" button available on various pages to load pre-configured study plans.

## License

MIT
