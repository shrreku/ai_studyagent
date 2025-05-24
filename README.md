# AI StudyAgent

An intelligent study planning application that generates personalized study plans using AI. The application helps users create structured study schedules based on their available time and study materials.

## Features

- **Personalized Study Plans**: Generate study schedules tailored to your available study days and hours per day
- **AI-Powered Structuring**: Automatically structures raw study materials into an organized study plan
- **Preview Mode**: Test the study plan generation with sample data before processing your actual materials
- **Flexible Input**: Accepts various study materials and adapts to different study durations
- **Interactive Web Interface**: User-friendly interface for easy interaction with the study planning system

## Tech Stack

- **Frontend**: Next.js with TypeScript
- **Backend**: FastAPI (Python)
- **AI/ML**: LangChain, OpenAI
- **Database**: (Specify if applicable)
- **Authentication**: (Specify if applicable)

## Prerequisites

- Node.js (v18 or later)
- Python (3.9 or later)
- npm or yarn
- OpenAI API key

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/shrreku/ai_studyagent.git
cd ai_studyagent
```

### 2. Set up the backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and settings
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### 3. Set up the frontend

1. In a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

1. **Create a Study Plan**:
   - Enter your study materials
   - Specify the number of study days
   - Set your available study hours per day
   - Click "Generate Study Plan"

2. **Preview Mode**:
   - Use the preview mode to test the AI's structuring capabilities
   - The system will generate a sample plan based on your time constraints

3. **Save and Manage Plans**:
   - (Feature to be implemented) Save your study plans
   - (Feature to be implemented) Track your progress

## API Documentation

Once the backend server is running, you can access the API documentation at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Environment Variables

### Backend (`.env` file)

```
OPENAI_API_KEY=your_openai_api_key
# Add other environment variables as needed
```

## Project Structure

```
studyagent_v2/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── config.py        # Configuration settings
│   │   └── ...
│   ├── requirements.txt     # Python dependencies
│   └── ...
├── frontend/                # Next.js frontend
│   ├── public/              # Static files
│   ├── src/
│   │   ├── app/           # Next.js app directory
│   │   └── ...
│   ├── package.json        # Node.js dependencies
│   └── ...
├── .gitignore
├── README.md               # This file
└── ...
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Future Enhancements

### Short-term Goals
- **Progress Tracking**: Add functionality to track study progress and adjust plans dynamically
- **Mobile App**: Develop a companion mobile application for on-the-go study planning
- **Subject-Specific Templates**: Create specialized templates for different subjects (e.g., Mathematics, History, Science)
- **Gamification**: Add achievement badges and progress rewards to boost motivation

### Long-term Vision
- **AI-Powered Q&A**: Integrate an AI tutor for answering subject-specific questions
- **Collaborative Study**: Enable group study planning and progress sharing
- **Adaptive Learning**: Implement ML algorithms to adjust study plans based on performance
- **Offline Mode**: Add support for offline access to study materials and plans
- **Integration with Calendars**: Sync study schedule with Google Calendar, Apple Calendar, etc.

## License

[MIT]

## Contact

[Shreyash Kumar] - [kshreyash12345@gmail.com]
Project Link: [https://github.com/shrreku/ai_studyagent](https://github.com/shrreku/ai_studyagent)
