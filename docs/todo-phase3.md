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


### Phase 3: Frontend Development - Initial Page (Input Form)

- **Task 8: Build Input Form UI with Numerical Inputs**
    - **ID:** 8
    - **Context:** Develop the initial page for user inputs, including numerical fields for total days and hours per day, to collect study duration data for plan generation, following Next.js/React modular structure rules.
    - **Dependencies:** Task 2
    - **Subtasks:**
        - [x] **8.1:** Create a React/Next.js component (`InputForm`) in `/src/components/forms/input-form.tsx` for the initial page with a form layout using Tailwind CSS for responsive design.
        - [x] **8.2:** Implement two numerical input fields for total days and hours per day using HTML `<input type="number">`, with constraints (e.g., min=1 for days, min=1/max=24 for hours) managed via React state.
        - [x] **8.3:** Display calculated total hours (days × hours per day) dynamically below the inputs for user feedback, using declarative JSX.
          - [x] **8.4:** Integrate the `InputForm` component into `src/app/page.tsx` for local testing, replacing default Next.js template. (Requires manual verification: run `npm run dev` in the `/src` directory and check if the form displays correctly)
- **Task 9: Add File Upload Fields to Form**
    - **ID:** 9
    - **Context:** Enhance the input form with separate upload fields for notes and question sets to gather user materials for processing, adhering to UI organization rules with Shadcn UI components.
    - **Dependencies:** Task 8
    - **Subtasks:**
         - [x] **9.1:** Research best practices and common libraries/APIs for handling multiple file uploads in Next.js (e.g., using `FormData`, serverless functions, or dedicated services like Cloudinary/S3). - *Outcome: Will use FormData with a Next.js API Route.*
         - [x] **9.2:** Add a file input field (`<input type="file" multiple>`) to the `InputForm` component, allowing users to select multiple study material files (PDFs, DOCXs, TXTs). Manage selected files in React state.
         - [x] **9.3:** Implement client-side validation for uploaded file types (e.g., allow PDF, DOCX, TXT) and display an error message if invalid files are selected.
          - [ ] **9.4:** Test the file upload fields locally: ensure files can be selected, validation works (type/size), error messages display, and valid file names/sizes are shown. (Requires manual verification: run `npm run dev` in the `/src` directory)
  - **Task 10: Implement Preview Plan Functionality**
    - **ID:** 10
    - **Context:** Add a button to preview the study plan on the initial page, displaying a draft below the form for user review before finalization, using server components for static content where possible.
    - **Dependencies:** Task 9, Task 6
    - **Subtasks:**
        - [x] **10.1:** Add a "Preview Plan" button to the `InputForm` component, styled with Shadcn UI `Button` and Tailwind CSS for clarity.
         - [x] **10.2:** Create a state variable in React to store the preview plan data received from the backend, minimizing `useState` by favoring server-side rendering if feasible.
          - [x] **10.3:** Implement a UI section below the form to display the preview plan as formatted text using declarative JSX, structured per Study Plan Template.
          - [ ] **10.4:** Test the preview functionality by ensuring the UI updates correctly with backend-generated data once integrated, handling errors with fallback UI. (Mock data currently used; requires manual verification with backend integration)
- **Task 11: Add Start Study Session Button**
    - **ID:** 11
    - **Context:** Include a button to finalize the plan and redirect to the study session page, completing the initial page’s user flow, following Next.js routing best practices.
    - **Dependencies:** Task 10
      - **Subtasks:**
          - [x] **11.1:** Add a "Start Study Session" button to the `InputForm` component, styled with Shadcn UI `Button` and Tailwind CSS, placed logically after plan preview.
          - [x] **11.2:** Implement basic routing logic in Next.js (e.g., using `next/router`) to redirect to the study session page on click.
          - [ ] **11.3:** Store the finalized plan data in state or context to pass to the next page during redirection, minimizing client-side state as per rules. (Requires manual verification)
          - [ ] **11.4:** Test the button to ensure it triggers redirection and carries over necessary data. (Requires manual verification: run `npm run dev` in the `/src` directory and test navigation and data persistence)



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
