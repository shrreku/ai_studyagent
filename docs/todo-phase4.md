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
