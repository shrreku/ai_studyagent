## Project Overview

The AI-Powered Study Assistant Agent is an EdTech tool designed to help students study more effectively by generating personalized study plans from uploaded class notes and practice question sets. The demo version focuses on core functionality to demonstrate technical skills and product thinking, leveraging Generative AI (Gen AI) for rapid development with Crew AI orchestrating the AI workflow. The app addresses real student needs by providing tailored study schedules, task tracking, and doubt resolution, aligning with modern AI agent trends and full-stack requirements of target internships. Integration with the free DeepSeek V3 API via OpenRouter ensures cost-effective AI capabilities for concept extraction, prioritization, and chat interactions.

## Core Requirements

- **Full-Stack Development:** Implement a functional web app with backend and frontend components, using Python, FastAPI, React, and/or Next.js as highlighted in the internship form.
- **AI Agent Functionality:** Integrate AI (via Crew AI and DeepSeek V3 API through OpenRouter) to extract concepts, prioritize topics, and generate study plans, reflecting the AI agent focus of the target startup.
- **End-to-End Product Experience:** Design a complete user flow from input (uploads, time selection) to output (study plan, task list, chat support), showcasing product ownership.
- **Resume Impact:** Highlight skills in full-stack development, AI orchestration with Crew AI, and UI/UX design to strengthen internship applications.


## Core Features

- **Study Plan Generation:** Extract core concepts from uploaded notes and question sets, prioritize high-impact topics based on frequency of mention in both, and create a tailored study plan based on user-provided total days and hours per day.
- **Time Input as Numerical Values:** Allow users to specify study duration via numerical inputs for total number of days and hours per day to calculate total study hours for plan generation.
- **Task List with Progress Tracking:** Display the study plan as actionable tasks and subtasks in a sidebar with checkboxes, applying a strikethrough effect on checked items to indicate completion.
- **Chat Support with LLM:** Provide a fully functional chat interface for doubt resolution and concept explanation, contextualized to uploaded materials and study plan, powered by DeepSeek V3 via OpenRouter.
- **Task-Specific Instructions:** Enable users to click tasks for detailed instructions (e.g., pages to refer, questions to solve) displayed in the chat area.
- **Quick Reference for Formulas:** Show key formulas extracted from notes in a scrollable bullet list for easy access during study sessions.
- **User Flow with Preview:** Offer a plan preview on the initial page before finalizing, then redirect to a detailed study session page upon confirmation.
- **AI Workflow Orchestration:** Use Crew AI to manage the AI flow, coordinating multiple tasks like concept extraction, prioritization, and chat responses through DeepSeek V3 API, ensuring efficient and structured AI interactions.


## Core Components

- **Initial Page (Input Form):**
    - Numerical input fields for total number of days and hours per day to define study duration.
    - Separate upload fields for notes and practice question sets.
    - "Preview Plan" button to view draft study plan on the same page.
    - "Start Study Session" button to finalize and redirect to the study session page.
- **Study Session Page (Detailed Interface):**
    - **Left Sidebar - Task List:** Bullet list of tasks (topics) and subtasks (e.g., Notes Study, Video Study) with checkboxes; strikethrough on checked items.
    - **Main Content Area:** Full study plan display (following Study Plan Template structure) and chat interface for LLM interaction and task instructions.
    - **Right Sidebar or Footer - Key Formulas:** Scrollable bullet list of formulas with bolded names and brief descriptions for quick reference.


## App/User Flow

1. **Initial Page (Input and Preview):**
    - User accesses the app and sees a form with numerical input fields for total number of days and hours per day, and upload fields for notes and question sets.
    - User uploads materials, inputs study duration values, and clicks "Preview Plan" to see a draft study plan (based on frequency-based prioritization) below the form.
    - If satisfied, user clicks "Start Study Session" to finalize the plan and redirect to the study session page; if not, they adjust inputs and preview again.
2. **Study Session Page (Study and Interaction):**
    - User lands on a new page with a left sidebar showing the task list (tasks/subtasks with checkboxes), main area with full study plan and chat, and right sidebar/footer with key formulas.
    - User checks off tasks/subtasks, seeing a strikethrough effect on completion.
    - User clicks a task to view specific instructions (e.g., reference pages, questions) in the chat area.
    - User types queries in the chat for doubt resolution or concept explanation, receiving contextual responses from the LLM powered by DeepSeek V3 via Crew AI orchestration.
    - User references key formulas in the scrollable list as needed during study.

## Tech Stack

| Component | Technology | Purpose |
| :-- | :-- | :-- |
| Frontend | React or Next.js | User interface for input form, plan display, chat, and task list |
| Backend | Python + FastAPI | API for processing uploads, generating plans, handling chat queries |
| AI/NLP | DeepSeek V3 API via OpenRouter | Concept extraction, topic prioritization, study plan generation, chat responses |
| AI Orchestration | Crew AI | Manage AI workflow, coordinating tasks like extraction, prioritization, and chat |
| Styling | CSS (via React/Next.js), Tailwind CSS | Layout design (sidebars, scrollable lists), visual feedback (strikethrough) |
| Deployment | Vercel (Frontend), PythonAnywhere/Replit (Backend) | Live demo if feasible, otherwise GitHub repo |
| Version Control | GitHub | Public repository with clear README for project setup and explanation |

## Implementation Plan

- **Prioritization:** Focus on must-have features first, with the chat feature and Crew AI integration confirmed as fully implementable using Gen AI assistance for rapid development.
- **Steps:**

1. **Setup and Environment:**
        - Initialize project structure with React/Next.js for frontend and FastAPI for backend using Gen AI to scaffold boilerplate code.
        - Set up GitHub repo for version control and basic README outline.
2. **Backend - File Processing and Crew AI Integration:**
        - Develop FastAPI endpoints to process file uploads (notes, question sets) and extract text for AI analysis.
        - Integrate Crew AI to orchestrate AI tasks, configuring it to manage workflows for concept extraction, topic prioritization, and chat responses using DeepSeek V3 API via OpenRouter.
        - Set up environment variables for OpenRouter API keys to securely access DeepSeek V3 services.
3. **Backend - Study Plan Generation:**
        - Create an endpoint (`/generate-plan`) to generate study plans based on total hours calculated from user inputs (days × hours per day), using Crew AI to coordinate AI tasks for concept extraction and prioritization (frequency in notes/questions).
        - Format outputs to match the Study Plan Template structure, adjusting plans dynamically based on total hours.
4. **Backend - Chat Functionality:**
        - Build a chat endpoint (`/chat`) using Crew AI to handle user queries and task-specific instructions, ensuring contextual responses from DeepSeek V3.
        - Test AI workflow to confirm Crew AI effectively manages multiple AI tasks with minimal latency.
5. **Initial Page - Input Form:**
        - Implement numerical input fields for total days and hours per day in a React/Next.js component (`InputForm`), calculating total hours for plan generation.
        - Add separate upload fields for notes and question sets with basic validation.
        - Create "Preview Plan" button to trigger draft plan generation via backend processing.
6. **Study Session Page - Core UI:**
        - Build new page layout with left sidebar (task list as bullet list with checkboxes), main area (plan display), and right sidebar/footer (formulas list).
        - Add strikethrough effect for checked tasks/subtasks using CSS (`text-decoration: line-through`).
        - Implement scrollable formulas list with CSS (`overflow-y: auto`).
7. **Chat and Task Instructions:**
        - Add fully functional chat UI in main area for LLM interaction (input field, scrollable responses) using FastAPI endpoint and Crew AI-managed DeepSeek V3 API.
        - Enable task click to show instructions in chat (e.g., reference pages, questions) via pre-crafted LLM prompts, ensuring contextual responses.
8. **Integration:**
        - Connect initial page to backend for plan preview, sending numerical inputs (days, hours) and uploads to generate draft plans.
        - Integrate study session page with backend for finalized plan display, chat, and task instructions, ensuring seamless data flow.
9. **Testing and Polish:**
        - Test core flow (input → preview → study session → chat) for functionality and UI bugs, verifying Crew AI orchestration of AI tasks.
        - Refine styling for readability (e.g., font sizes, spacing) and ensure responsive design if feasible.
        - Update README with project overview, tech stack (including Crew AI and DeepSeek V3 via OpenRouter), setup instructions, and future enhancements (e.g., advanced chat features, visual cards).
10. **Deployment (Optional):**
        - Deploy frontend on Vercel and backend on PythonAnywhere/Replit for a live demo if feasible; otherwise, ensure GitHub repo is complete for showcase.
- **Fallbacks for Constraints:**
    - If backend processing or Crew AI orchestration for plan generation encounters issues, ensure at least a minimal functional flow with simplified logic (e.g., basic topic extraction without full prioritization).
    - If DeepSeek V3 API rate limits are encountered via OpenRouter, implement basic caching of frequent responses or note fallback to alternative free APIs as a future enhancement in README.
    - Note advanced features (e.g., visual cards for instructions, persistent checkbox state) as future enhancements in README to demonstrate forward-thinking design.
