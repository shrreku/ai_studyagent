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

Below, each high-level step is broken into tasks, and each task into subtasks, with checklist items, context for implementation, and dependency mappings. Task IDs are numeric, and dependencies are listed to ensure a connected workflow. The tasks adhere to the coding rules provided in `python-fastapi-Cursor-Rules.txt` and `Next.js-React-Tailwind-Cursorrules.txt` for consistency and scalability.

### Phase 1: Project Setup and Environment Configuration

- **Task 1: Initialize Project Structure**
    - **ID:** 1
    - **Context:** Set up the basic project structure for frontend and backend to organize code and facilitate development. This ensures a clean workspace for collaboration and version control, following the modular structure guidelines from the provided rules.
    - **Dependencies:** None
    - **Subtasks:**
        - [x] **1.1:** Create a root project folder with subfolders for frontend (`/src`) and backend (`/backend`) to separate concerns as per separation of concerns principle.
        - [x] **1.2:** Initialize a new Next.js project in the frontend folder using `npx create-next-app@latest` with TypeScript, placing `/app` and `/components` under `/src` as per Next.js rules.
        - [x] **1.3:** Initialize a new FastAPI project in the backend folder by creating a virtual environment (`python -m venv env`) and installing FastAPI (`pip install fastapi uvicorn`) for API development, following the file structure guidelines (e.g., `routers/`, `utils/`).
        - [x] **1.4:** Install basic dependencies (e.g., `axios` for frontend API calls, `python-dotenv` for backend environment variables, `pydantic` v2 for validation) to prepare for development.
- **Task 2: Set Up Version Control with GitHub**
    - **ID:** 2
    - **Context:** Establish version control to track changes and create a public repository for showcasing the project to potential internship recruiters, ensuring visibility for your SDE/ML portfolio.
    - **Dependencies:** Task 1
    - **Subtasks:**
        - [x] **2.1:** Initialize a Git repository in the root folder (`git init`) to start tracking changes.
        - [x] **2.2:** Create a `.gitignore` file to exclude unnecessary files (e.g., `node_modules`, `env/`) from version control.
        - [x] **2.3:** Create a public GitHub repository and link it to the local project (`git remote add origin <url>`).
        - [ ] **2.4:** Make an initial commit with the project structure (`git add . && git commit -m "Initial project setup"`) and push to GitHub (`git push origin main`).


### Phase 2: Backend Development - Core Logic and AI Orchestration

- **Task 3: Develop File Upload and Processing Endpoint**
    - **ID:** 3
    - **Context:** Build a backend endpoint to handle file uploads (notes and question sets) and process them for concept extraction, forming the foundation for study plan generation. Follow FastAPI-specific guidelines for declarative routes and Pydantic models.
    - **Dependencies:** Task 1
    - **Subtasks:**
        - [ ] **3.1:** Create a FastAPI route (`/upload`) in `routers/upload_routes.py` to accept file uploads for notes and question sets using `fastapi.File` and `fastapi.UploadFile`, with type hints.
        - [ ] **3.2:** Implement basic file storage logic to save uploaded files temporarily in a backend directory (e.g., `./uploads/`) for processing, using async operations to avoid blocking I/O.
        - [ ] **3.3:** Add text extraction logic for common file types (e.g., PDF, text) using libraries like `PyPDF2` or `textract`, ensuring early error handling with `HTTPException` for invalid files.
        - [ ] **3.4:** Test the endpoint locally using `uvicorn` to ensure files are received and processed correctly (`uvicorn main:app --reload`), logging errors as per rules.
- **Task 4: Integrate DeepSeek V3 API via OpenRouter for AI Tasks**
    - **ID:** 4
    - **Context:** Set up integration with the free DeepSeek V3 API through OpenRouter for concept extraction, prioritization, and chat responses, ensuring secure access and optimized performance as per FastAPI performance rules.
    - **Dependencies:** Task 3
    - **Subtasks:**
        - [ ] **4.1:** Set up environment variables for OpenRouter API keys using `python-dotenv` to securely access the DeepSeek V3 service, following security best practices.
        - [ ] **4.2:** Create a utility function in `utils/ai_client.py` to send extracted text from uploads to DeepSeek V3 API with a prompt for identifying core topics and subtopics (e.g., "Extract key concepts from this text"), using `async def` for non-blocking calls.
        - [ ] **4.3:** Add logic to count frequency of mentions in notes and question sets via another API prompt (e.g., "Rank topics by frequency in provided texts"), returning prioritized topics as a Pydantic model.
        - [ ] **4.4:** Test the integration by passing sample text data to the API, verifying returned concepts and prioritization, and handling rate limits with basic retry logic or error logging.
- **Task 5: Set Up Crew AI for AI Workflow Orchestration**
    - **ID:** 5
    - **Context:** Integrate Crew AI to orchestrate AI tasks like concept extraction, topic prioritization, and chat responses using DeepSeek V3, ensuring structured and efficient AI interactions as a key feature for the demo.
    - **Dependencies:** Task 4
    - **Subtasks:**
        - [ ] **5.1:** Install Crew AI (`pip install crewai`) in the backend environment to manage AI workflows, following modularization principles from the rules.
        - [ ] **5.2:** Define Crew AI agents in `utils/ai_workflow.py` for specific tasks (e.g., one agent for concept extraction, another for prioritization), each using DeepSeek V3 API calls via OpenRouter.
        - [ ] **5.3:** Create a crew to coordinate these agents, ensuring sequential task execution (e.g., extraction before prioritization) with clear input/output using Pydantic models.
        - [ ] **5.4:** Test the Crew AI setup with sample data to confirm agents collaborate effectively, logging outputs and errors for debugging as per error handling rules.
- **Task 6: Build Study Plan Generation Endpoint**
    - **ID:** 6
    - **Context:** Develop an endpoint to generate a study plan based on extracted concepts, prioritized topics, and user-provided total hours (calculated from days and hours per day), using Crew AI for orchestration and following the Study Plan Template structure.
    - **Dependencies:** Task 5
    - **Subtasks:**
        - [ ] **6.1:** Create a FastAPI route (`/generate-plan`) in `routers/study_plan_routes.py` to accept total days and hours per day, calculating total hours as input, using type hints and Pydantic models.
        - [ ] **6.2:** Use Crew AI to orchestrate concept extraction and prioritization via DeepSeek V3, then distribute total hours across topics (prioritize high-impact if limited, comprehensive if ample) with functional logic.
        - [ ] **6.3:** Format the output to match the Study Plan Template (e.g., "Extracted Core Concepts," "Condensed Study Plan") using JSON structure for frontend compatibility.
        - [ ] **6.4:** Test the endpoint with varied inputs (e.g., 2 days at 3 hours/day vs. 5 days at 4 hours/day) to ensure dynamic plan adjustment, handling errors early with `HTTPException`.
- **Task 7: Develop Chat Endpoint for LLM Interaction**
    - **ID:** 7
    - **Context:** Create a backend endpoint to handle chat queries for doubt resolution and task instructions, using Crew AI to manage contextual responses from DeepSeek V3, adhering to FastAPI route declaration rules.
    - **Dependencies:** Task 5
    - **Subtasks:**
        - [ ] **7.1:** Create a FastAPI route (`/chat`) in `routers/chat_routes.py` to accept user queries and context (e.g., study plan data, specific task clicked), using Pydantic for input validation.
        - [ ] **7.2:** Configure Crew AI to handle chat tasks, crafting prompts for DeepSeek V3 (e.g., "Explain Topic 1 based on provided notes") to ensure contextual responses.
        - [ ] **7.3:** Implement async response handling from the API to return answers to the frontend for display, optimizing for performance with non-blocking calls.
        - [ ] **7.4:** Test the endpoint with sample queries to ensure responses are relevant to uploaded content and study plan, logging interactions for debugging.


### Phase 3: Frontend Development - Initial Page (Input Form)

- **Task 8: Build Input Form UI with Numerical Inputs**
    - **ID:** 8
    - **Context:** Develop the initial page for user inputs, including numerical fields for total days and hours per day, to collect study duration data for plan generation, following Next.js/React modular structure rules.
    - **Dependencies:** Task 2
    - **Subtasks:**
        - [ ] **8.1:** Create a React/Next.js component (`InputForm`) in `/src/components/forms/input-form.tsx` for the initial page with a form layout using Tailwind CSS for responsive design.
        - [ ] **8.2:** Implement two numerical input fields for total days and hours per day using HTML `<input type="number">`, with constraints (e.g., min=1 for days, min=1/max=24 for hours) managed via React state.
        - [ ] **8.3:** Display calculated total hours (days × hours per day) dynamically below the inputs for user feedback, using declarative JSX.
        - [ ] **8.4:** Test the inputs locally to ensure values update correctly, are constrained within limits, and total hours calculation reflects accurately.
- **Task 9: Add File Upload Fields to Form**
    - **ID:** 9
    - **Context:** Enhance the input form with separate upload fields for notes and question sets to gather user materials for processing, adhering to UI organization rules with Shadcn UI components.
    - **Dependencies:** Task 8
    - **Subtasks:**
        - [ ] **9.1:** Add two file input fields to the `InputForm` component, labeled "Upload Notes" and "Upload Question Sets," using HTML `<input type="file">` styled with Tailwind CSS.
        - [ ] **9.2:** Implement basic file selection state in React to store selected files for submission, displaying file names for user feedback with a Shadcn UI component like `Card`.
        - [ ] **9.3:** Add minimal validation (e.g., accept only PDF/text files if feasible) using file type checks in JavaScript, with error messages in UI.
        - [ ] **9.4:** Test the upload fields to ensure files can be selected and their names are displayed correctly in the UI.
- **Task 10: Implement Preview Plan Functionality**
    - **ID:** 10
    - **Context:** Add a button to preview the study plan on the initial page, displaying a draft below the form for user review before finalization, using server components for static content where possible.
    - **Dependencies:** Task 9, Task 6
    - **Subtasks:**
        - [ ] **10.1:** Add a "Preview Plan" button to the `InputForm` component, styled with Shadcn UI `Button` and Tailwind CSS for clarity.
        - [ ] **10.2:** Create a state variable in React to store the preview plan data received from the backend, minimizing `useState` by favoring server-side rendering if feasible.
        - [ ] **10.3:** Implement a UI section below the form to display the preview plan as formatted text using declarative JSX, structured per Study Plan Template.
        - [ ] **10.4:** Test the preview functionality by ensuring the UI updates correctly with backend-generated data once integrated, handling errors with fallback UI.
- **Task 11: Add Start Study Session Button**
    - **ID:** 11
    - **Context:** Include a button to finalize the plan and redirect to the study session page, completing the initial page’s user flow, following Next.js routing best practices.
    - **Dependencies:** Task 10
    - **Subtasks:**
        - [ ] **11.1:** Add a "Start Study Session" button below the preview section in the `InputForm` component, styled distinctly from "Preview Plan" using Tailwind CSS.
        - [ ] **11.2:** Implement basic routing logic in Next.js (e.g., using `next/router`) to redirect to the study session page on click.
        - [ ] **11.3:** Store the finalized plan data in state or context to pass to the next page during redirection, minimizing client-side state as per rules.
        - [ ] **11.4:** Test the button to ensure it triggers redirection and carries over necessary data.


### Phase 4: Frontend Development - Study Session Page

- **Task 12: Create Study Session Page Layout**
    - **ID:** 12
    - **Context:** Build the study session page with a multi-section layout (task list sidebar, main content, formulas sidebar/footer) for the detailed study interface, using Tailwind CSS for responsive design.
    - **Dependencies:** Task 11
    - **Subtasks:**
        - [ ] **12.1:** Create a new React/Next.js component (`StudySession`) in `/src/app/study-session/page.tsx` for the study session page, accessible via routing from the initial page.
        - [ ] **12.2:** Implement a CSS grid or flexbox layout with Tailwind classes (e.g., `grid grid-cols-1 md:grid-cols-3`) for three sections: left sidebar (task list), main content area (plan and chat), and right sidebar/footer (formulas).
        - [ ] **12.3:** Add placeholder content (e.g., dummy text) to each section to visualize the layout structure, using server components for static parts.
        - [ ] **12.4:** Test the layout locally to ensure sections are positioned correctly and responsive on basic screen sizes with mobile-first approach.
- **Task 13: Implement Task List Sidebar with Checkboxes**
    - **ID:** 13
    - **Context:** Develop the left sidebar to display tasks and subtasks as a bullet list with checkboxes for progress tracking, including strikethrough on completion, using minimal client-side state.
    - **Dependencies:** Task 12, Task 6
    - **Subtasks:**
        - [ ] **13.1:** Create a sub-component (`TaskList`) in `/src/components/ui/task-list.tsx` to render tasks and subtasks as a bullet list from the study plan data, using named exports.
        - [ ] **13.2:** Add checkboxes to each task and subtask using HTML `<input type="checkbox">`, linked to labels for accessibility, styled with Tailwind.
        - [ ] **13.3:** Implement state management in React to track checked status with `useState` only where necessary, applying CSS `text-decoration: line-through` to checked items.
        - [ ] **13.4:** Test the sidebar to ensure checkboxes toggle correctly and strikethrough effect applies to the corresponding text.
- **Task 14: Display Full Study Plan in Main Area**
    - **ID:** 14
    - **Context:** Render the complete study plan in the main content area, following the Study Plan Template structure for user reference, favoring server components for static rendering.
    - **Dependencies:** Task 12, Task 6
    - **Subtasks:**
        - [ ] **14.1:** Create a sub-component (`StudyPlanDisplay`) in `/src/components/ui/study-plan-display.tsx` to format and display the study plan data received from the backend.
        - [ ] **14.2:** Structure the content into sections (e.g., "Extracted Core Concepts," "Condensed Study Plan") using HTML headings and lists as per the template, with Tailwind styling.
        - [ ] **14.3:** Style the display for readability (e.g., proper spacing, font hierarchy) using Tailwind classes like `text-sm md:text-base`.
        - [ ] **14.4:** Test the component with plan data to ensure all sections render correctly and match the Study Plan Template.
- **Task 15: Implement Chat Interface for LLM Interaction**
    - **ID:** 15
    - **Context:** Add a fully functional chat UI in the main area for doubt resolution and task instructions, connected to the backend chat endpoint, using `use client` only for necessary interactivity.
    - **Dependencies:** Task 12, Task 7
    - **Subtasks:**
        - [ ] **15.1:** Create a sub-component (`ChatInterface`) in `/src/components/ui/chat-interface.tsx` for the chat UI, placed below or beside the study plan display, styled with Tailwind.
        - [ ] **15.2:** Implement a text input field for user queries and a scrollable area (`overflow-y-auto`) to display chat history (user messages and LLM responses).
        - [ ] **15.3:** Add state management with `useState` to store chat history and handle sending queries to the backend via API calls (using `axios` or `fetch`), wrapping in `Suspense` if async.
        - [ ] **15.4:** Test the chat locally by sending sample queries and displaying real responses from the backend.
- **Task 16: Enable Task-Specific Instructions on Click**
    - **ID:** 16
    - **Context:** Allow users to click tasks in the sidebar to display specific instructions in the chat area, enhancing study guidance, minimizing client-side logic as per rules.
    - **Dependencies:** Task 13, Task 15
    - **Subtasks:**
        - [ ] **16.1:** Add click event handlers to each task and subtask in the `TaskList` component to trigger an action when clicked, using minimal `use client` directive.
        - [ ] **16.2:** Implement logic to send the clicked task’s details (e.g., topic name) to the chat backend endpoint with a specific prompt for instructions via API call.
        - [ ] **16.3:** Update the `ChatInterface` to display the received instructions as a new message in the chat history.
        - [ ] **16.4:** Test the feature by clicking tasks and verifying that relevant instructions appear in the chat area.
- **Task 17: Add Key Formulas Section**
    - **ID:** 17
    - **Context:** Implement a scrollable bullet list for key formulas in the right sidebar or footer for quick reference during study, using server components for static content.
    - **Dependencies:** Task 12, Task 6
    - **Subtasks:**
        - [ ] **17.1:** Create a sub-component (`KeyFormulas`) in `/src/components/ui/key-formulas.tsx` to render formulas extracted from the study plan (Section 4 of Study Plan Template).
        - [ ] **17.2:** Format the list as bullet points with bolded formula names and brief descriptions using HTML and Tailwind CSS (e.g., `font-bold` for names).
        - [ ] **17.3:** Add CSS `overflow-y: auto` via Tailwind (`overflow-y-auto`) to make the list scrollable within a fixed height container (e.g., `h-72`).
        - [ ] **17.4:** Test the component with formula data to ensure it renders correctly and scrolls when content exceeds height.


### Phase 5: Integration and API Connectivity

- **Task 18: Connect Initial Page to Backend for Plan Preview**
    - **ID:** 18
    - **Context:** Integrate the initial page’s "Preview Plan" functionality with the backend to fetch and display the draft study plan dynamically, following Next.js data fetching best practices.
    - **Dependencies:** Task 10, Task 6
    - **Subtasks:**
        - [ ] **18.1:** Implement an API call in the `InputForm` component to send calculated total hours (days × hours per day) and uploaded files to the `/upload` and `/generate-plan` endpoints using `axios`.
        - [ ] **18.2:** Update the preview section to display the real study plan data returned from the backend, structured per Study Plan Template.
        - [ ] **18.3:** Handle basic error states (e.g., upload failure, API error) with user-friendly messages in the UI using Shadcn UI components.
        - [ ] **18.4:** Test the integration by inputting duration values, uploading files, and verifying the preview updates with backend-generated plan data.
- **Task 19: Connect Study Session Page to Backend for Full Functionality**
    - **ID:** 19
    - **Context:** Ensure the study session page fetches and displays the finalized study plan and supports chat interactions via backend APIs, optimizing for performance with server components as per Next.js rules.
    - **Dependencies:** Task 14, Task 15, Task 18
    - **Subtasks:**
        - [ ] **19.1:** Pass the finalized plan data from the initial page to the `StudySession` component via state or context during redirection, minimizing client-side state as per rules.
        - [ ] **19.2:** Implement API calls in `ChatInterface` to send user queries to the `/chat` endpoint and display responses in real-time, using async fetching with `Suspense` for performance.
        - [ ] **19.3:** Ensure `TaskList`, `StudyPlanDisplay`, and `KeyFormulas` components render the latest plan data from the backend response, favoring server-side rendering where possible.
        - [ ] **19.4:** Test the full flow (input → preview → study session → chat) to confirm data consistency and API interactions work as expected, verifying Crew AI orchestration.


### Phase 6: Testing and Refinement

- **Task 20: Conduct Functional Testing**
    - **ID:** 20
    - **Context:** Test the entire app flow to ensure all features work as intended, identifying and fixing critical bugs for a polished demo, following error-first mindset from FastAPI rules.
    - **Dependencies:** Task 19
    - **Subtasks:**
        - [ ] **20.1:** Test the initial page by inputting different duration values (days, hours per day) and uploading files, verifying preview plan updates correctly with backend data.
        - [ ] **20.2:** Test the study session page by checking tasks, interacting with chat, and clicking for instructions, ensuring responses are contextual via Crew AI and DeepSeek V3.
        - [ ] **20.3:** Verify UI elements (numerical inputs, checkboxes with strikethrough, scrollable formulas) function across basic screen sizes using Tailwind’s responsive classes.
        - [ ] **20.4:** Log and prioritize bugs (e.g., UI glitches, API failures) for quick fixes, implementing proper error logging as per FastAPI guidelines.
- **Task 21: Refine UI and UX**
    - **ID:** 21
    - **Context:** Polish the user interface for readability and professionalism, enhancing the demo’s appeal for internship showcases, adhering to Tailwind and Shadcn UI styling rules.
    - **Dependencies:** Task 20
    - **Subtasks:**
        - [ ] **21.1:** Adjust Tailwind CSS for consistent spacing, font sizes, and color contrast across all components (e.g., `p-4`, `text-base`) for better readability.
        - [ ] **21.2:** Add minimal visual feedback (e.g., button hover effects with `hover:bg-gray-100`, loading spinner for API calls using Shadcn UI) to improve user experience.
        - [ ] **21.3:** Ensure responsive design for mobile and tablet views using Tailwind media queries (e.g., `md:grid-cols-3`), following mobile-first approach.
        - [ ] **21.4:** Review the UI against the Study Plan Template structure (Study-Plan-Template.md) to confirm alignment with expected output format, adjusting layout if needed.


### Phase 7: Documentation and Deployment

- **Task 22: Finalize Documentation in README**
    - **ID:** 22
    - **Context:** Create comprehensive documentation in the GitHub README to explain the project, setup, and future enhancements for internship reviewers, showcasing technical proficiency and forward-thinking design.
    - **Dependencies:** Task 21
    - **Subtasks:**
        - [ ] **22.1:** Write a project overview in the README, describing the AI-Powered Study Assistant Agent’s purpose, relevance to EdTech, and use of Crew AI with DeepSeek V3.
        - [ ] **22.2:** Detail the tech stack (Next.js, FastAPI, Crew AI, DeepSeek V3 via OpenRouter), installation steps, and how to run the app locally (e.g., `npm start` for frontend, `uvicorn main:app` for backend).
        - [ ] **22.3:** List implemented features (e.g., numerical inputs, AI orchestration) and note future enhancements (e.g., visual cards, persistent state) to demonstrate planning.
        - [ ] **22.4:** Commit and push the updated README to GitHub for public access (`git add README.md && git commit -m "Add detailed README" && git push`).
- **Task 23: Deploy Application (Optional)**
    - **ID:** 23
    - **Context:** Deploy the app to public platforms for a live demo if feasible, enhancing visibility for internship applications, ensuring performance optimization as per rules.
    - **Dependencies:** Task 22
    - **Subtasks:**
        - [ ] **23.1:** Deploy the frontend to Vercel by connecting the GitHub repo and following Vercel’s deployment wizard for Next.js apps, optimizing for Web Vitals (LCP, CLS).
        - [ ] **23.2:** Deploy the backend to PythonAnywhere or Replit, uploading the FastAPI code and configuring environment variables for OpenRouter API keys, using async operations for performance.
        - [ ] **23.3:** Update frontend API URLs to point to the deployed backend endpoint for seamless integration, testing connectivity.
        - [ ] **23.4:** Test the live demo to ensure all features (upload, plan generation, chat) work in the deployed environment, updating README with the live URL if successful.


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
