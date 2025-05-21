# Detailed Step-by-Step Plan to Build AI-Powered Study Assistant Agent Demo

This plan outlines a structured approach to building the AI-Powered Study Assistant Agent demo as defined in the updated Product Requirements Document (PRD). It follows best practices in software development and project management, breaking the project into small, manageable tasks and subtasks with clear dependencies to ensure a logical progression without complexity jumps. Each task and subtask is designed to be implementable in a single step while contributing to the overall success of the project. Dependencies are wired to avoid orphan tasks, ensuring a cohesive development flow.

## High-Level Step-by-Step Plan

The development process is divided into sequential phases, each building on the previous one, to create a functional demo that showcases full-stack skills, AI integration with Crew AI, and user-centric design for internship applications.

1. **Project Setup and Environment Configuration:** Initialize the development environment, tools, and version control to establish a foundation for coding.
2. **Backend Development - Core Logic and AI Orchestration:** Build the backend to process uploads, generate study plans, and handle AI interactions using Crew AI with DeepSeek V3 API via OpenRouter.
3. **Frontend Development - Initial Page (Input Form):** Create the user input interface with numerical fields for study duration and upload fields to collect data for plan generation.
4. **Frontend Development - Study Session Page:** Develop the detailed study interface with task lists, plan display, chat, and formulas for user interaction.
5. **Integration and API Connectivity:** Connect frontend and backend components to ensure seamless data flow and functionality across the app.
6. **Testing and Refinement:** Validate the app’s functionality, fix bugs, and polish the UI for a professional demo.
7. **Documentation and Deployment:** Finalize documentation and deploy the app (if feasible) to showcase the project for internship applications.

## Detailed Task Breakdown with Subtasks and Dependencies

Below, each high-level step is broken into tasks, and each task into subtasks, with checklist items, context for implementation, and dependency mappings. Task IDs are numeric, and dependencies are listed to ensure a connected workflow. 


### Phase 2: Backend Development - Core Logic and AI Orchestration

- **Task 3: Develop File Upload and Processing Endpoint**
    - **ID:** 3
    - **Context:** Build a backend endpoint to handle file uploads (notes and question sets) and process them for concept extraction, forming the foundation for study plan generation. Follow FastAPI-specific guidelines for declarative routes and Pydantic models.
    - **Dependencies:** Task 1
    - **Subtasks:**
        - [x] **3.1:** Create a FastAPI route (`/upload`) in `routers/upload_routes.py` to accept file uploads for notes and question sets using `fastapi.File` and `fastapi.UploadFile`, with type hints.
        - [x] **3.2:** Implement basic file storage logic to save uploaded files temporarily in a backend directory (e.g., `./uploads/`) for processing, using async operations to avoid blocking I/O.
        - [x] **3.3:** Add text extraction logic for common file types (e.g., PDF, text) using libraries like `PyPDF2` or `textract`, ensuring early error handling with `HTTPException` for invalid files.
        - [x] **3.4:** Test the endpoint locally using `uvicorn` to ensure files are received and processed correctly (`uvicorn main:app --reload`), logging errors as per rules. (Server running, manual testing required by user via POST request to `/upload`)
- **Task 4: Integrate DeepSeek V3 API via OpenRouter for AI Tasks**
    - **ID:** 4
    - **Context:** Set up integration with the free DeepSeek V3 API through OpenRouter for concept extraction, prioritization, and chat responses, ensuring secure access and optimized performance as per FastAPI performance rules.
    - **Dependencies:** Task 3
    - **Subtasks:**
        - [x] **4.1:** Set up environment variables for API keys (`OPENROUTER_API_KEY`, `DEEPSEEK_MODEL_NAME`) using `python-dotenv` in the backend, ensuring keys are not hardcoded. (USER ACTION REQUIRED: Create a `.env` file in the `/Users/shreyashkumar/coding/projects/studyagent_v2/backend` directory with your `OPENROUTER_API_KEY` and `DEEPSEEK_MODEL_NAME` (e.g., `DEEPSEEK_MODEL_NAME=deepseek/deepseek-coder`). The `openai` library has been installed.)
        - [x] **4.2:** Create a utility function in `utils/ai_client.py` to send extracted text from uploads to DeepSeek V3 API with a prompt for identifying core topics and subtopics (e.g., "Extract key concepts from this text"), using `async def` for non-blocking calls.
        - [x] **4.3:** Add logic to count frequency of mentions in notes and question sets via another API prompt (e.g., "Rank topics by frequency in provided texts"), returning prioritized topics as a Pydantic model.
        - [x] **4.4:** Test the integration by passing sample text data to the API, verifying returned concepts and prioritization, and handling rate limits with basic retry logic or error logging. (AI integration complete in `/upload` route. USER ACTION REQUIRED: Ensure your `OPENROUTER_API_KEY` is correctly set in `backend/.env` and test by uploading files. The Uvicorn server might need a restart to pick up these changes if it was already running.)
- **Task 5: Set Up Crew AI for AI Workflow Orchestration**
    - **ID:** 5
    - **Context:** Integrate Crew AI to orchestrate AI tasks like concept extraction, topic prioritization, and chat responses using DeepSeek V3, ensuring structured and efficient AI interactions as a key feature for the demo.
    - **Dependencies:** Task 4
    - **Subtasks:**
        - [x] **5.1: Install Crew AI (`pip install crewai`)**
            - In the `backend` directory, run `pip install crewai`.
            - *Dependency*: 4.2
            - *Action Required by User*: Monitor installation. If errors, resolve them (e.g., missing system dependencies). Note: Previous attempt failed due to network timeout during kubernetes package download.
        - [x] **5.2:** Define Crew AI agents in `utils/ai_workflow.py` for specific tasks (e.g., one agent for concept extraction, another for prioritization), each using DeepSeek V3 API calls via OpenRouter.
        - [x] **5.3:** Create a crew to coordinate these agents, ensuring sequential task execution (e.g., extraction before prioritization) with clear input/output using Pydantic models.
    - [x] **5.4: Test the Crew AI setup with sample data**
        - In `utils/ai_workflow.py`, in the `if __name__ == '__main__':` block, add code to:
        - Define sample study materials (a short text string).
        - Define a sample study duration (e.g., 7 days, 2 hours/day).
        - Kickoff the `study_crew` with these inputs.
        - Print the result.
        NOTE: test setup removed and crew ai setup tested along with backend setup, without study plan generation.
    - *Dependency*: 5.3
- **Task 6: Build Study Plan Generation Endpoint**
    - **ID:** 6
    - **Context:** Develop an endpoint to generate a study plan based on extracted concepts, prioritized topics, and user-provided total hours (calculated from days and hours per day), using Crew AI for orchestration and following the Study Plan Template structure.
    - **Dependencies:** Task 5
    - **Subtasks:**
        - [x] **6.1:** Create a FastAPI route (`/generate-plan`) in `routers/study_plan_routes.py` to accept total days and hours per day, calculating total hours as input, using type hints and Pydantic models.
        - [x] **6.2:** Use Crew AI to orchestrate concept extraction and prioritization via DeepSeek V3, then distribute total hours across topics (prioritize high-impact if limited, comprehensive if ample) with functional logic.
        - [x] **6.3:** Format the output to match the Study Plan Template (e.g., "Extracted Core Concepts," "Condensed Study Plan") using JSON structure for frontend compatibility.
        - [x] **6.4:** Test the endpoint with varied inputs (e.g., 2 days at 3 hours/day vs. 5 days at 4 hours/day) to ensure dynamic plan adjustment, handling errors early with `HTTPException`.
- **Task 7: Develop Chat Endpoint for LLM Interaction**
    - **ID:** 7
    - **Context:** Create a backend endpoint to handle chat queries for doubt resolution and task instructions, using Crew AI to manage contextual responses from DeepSeek V3, adhering to FastAPI route declaration rules.
    - **Dependencies:** Task 5
    - **Subtasks:**
        - [x] **7.1:** Create a FastAPI route (`/chat`) in `routers/chat_routes.py` to accept user queries and context (e.g., study plan data, specific task clicked), using Pydantic for input validation.
    - [x] 7.2: Configure Crew AI to handle chat tasks. This involves:
        - Defining a new task in `utils/ai_workflow.py` (or directly in `chat_routes.py`) for the `chat_support_agent`.
        - Crafting effective prompts for DeepSeek V3 to ensure contextual responses based on `user_query`, `study_plan_context`, and `task_context`.
        - Creating a new Crew specifically for chat interactions, or adapting the existing one if suitable.
        - [x] **7.3:** Implement async response handling from the API to return answers to the frontend for display, optimizing for performance with non-blocking calls.
        - [x] **7.4:** Test the endpoint with sample queries to ensure responses are relevant to uploaded content and study plan, logging interactions for debugging.



## Summary of Task Dependencies

This dependency list ensures no orphan tasks and provides a clear development sequence:


| Task ID | Task Name | Dependencies |
| :-- | :-- | :-- |
| 1 | Initialize Project Structure | None |
| 2 | Set Up Version Control with GitHub | Task 1 |
| 3 | Develop File Upload and Processing Endpoint | Task 1 |
| 4 | Integrate DeepSeek V3 API via OpenRouter | Task 3 |
| 5 | Set Up Crew AI for AI Workflow Orchestration | Task 4 |
| 6 | Build Study Plan Generation Endpoint | Task 5 |
| 7 | Develop Chat Endpoint for LLM Interaction | Task 5 |
| 8 | Build Input Form UI with Numerical Inputs | Task 2 |
| 9 | Add File Upload Fields to Form | Task 8 |
| 10 | Implement Preview Plan Functionality | Task 9, Task 6 |
| 11 | Add Start Study Session Button | Task 10 |
| 12 | Create Study Session Page Layout | Task 11 |
| 13 | Implement Task List Sidebar with Checkboxes | Task 12, Task 6 |
| 14 | Display Full Study Plan in Main Area | Task 12, Task 6 |
| 15 | Implement Chat Interface for LLM Interaction | Task 12, Task 7 |
| 16 | Enable Task-Specific Instructions on Click | Task 13, Task 15 |
| 17 | Add Key Formulas Section | Task 12, Task 6 |
| 18 | Connect Initial Page to Backend for Plan Preview | Task 10, Task 6 |
| 19 | Connect Study Session Page to Backend for Full Functionality | Task 14, Task 15, Task 18 |
| 20 | Conduct Functional Testing | Task 19 |
| 21 | Refine UI and UX | Task 20 |
| 22 | Finalize Documentation in README | Task 21 |
| 23 | Deploy Application (Optional) | Task 22 |
