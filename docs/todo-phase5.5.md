# Detailed Step-by-Step Plan for AI-Powered Study Assistant Agent Demo - Phase 5.5

This plan outlines the tasks for implementing a backend-driven LLM structuring workflow for the study plan data. This phase builds upon the existing integration and aims to improve data consistency and reduce frontend complexity.

## High-Level Goal for Phase 5.5

Transition the study plan generation to a two-step LLM process on the backend:
1.  Initial generation of the study plan in text/markdown format.
2.  A subsequent LLM call to transform this text/markdown into a structured JSON object adhering to the `StudyPlan` interface defined in `StudyPlanContext.tsx`.

This approach centralizes data transformation, ensures the frontend receives data in the expected format, and allows for more robust error handling and flexibility.

## Detailed Task Breakdown with Subtasks and Dependencies

### Phase 5.5: Backend-Driven Study Plan Structuring

- **Task 20: Modify Backend for LLM-Based Study Plan Structuring**
    - **ID:** 20
    - **Context:** Update the backend to incorporate a second LLM call specifically for structuring the generated study plan into a JSON format that matches the `StudyPlan` interface. This will ensure data consistency and simplify frontend data handling.
    - **Dependencies:** Task 6 (from todo-phase5.md - Build Study Plan Generation Endpoint)
    - **Subtasks:**
        - [ ] **20.1:** Update the `/generate-plan` endpoint in `backend/routers/study_plan_routes.py`. After the initial plan generation, add a call to a new function (e.g., in `ai_workflow.py`) that uses an LLM to transform the text/markdown plan into structured JSON.
        - [ ] **20.2:** Develop a robust prompt for the LLM transformation. This prompt should clearly instruct the LLM to output JSON conforming to the `StudyPlan` interface (defined in `src/context/StudyPlanContext.tsx`). Include examples in the prompt if necessary.
        - [ ] **20.3:** Implement error handling for the LLM structuring process. This includes handling cases where the LLM fails to return valid JSON or the structuring call itself fails. Consider retry mechanisms or fallback strategies.
        - [ ] **20.4:** Ensure the `/generate-plan` endpoint returns the structured JSON study plan to the frontend.

- **Task 21: Update Frontend to Consume Structured Study Plan**
    - **ID:** 21
    - **Context:** Modify the frontend components to expect and correctly utilize the structured JSON study plan received from the backend. This will involve removing any client-side logic previously used for parsing or transforming the study plan data.
    - **Dependencies:** Task 20, Task 18 (from todo-phase5.md - Connect Initial Page to Backend for Plan Preview)
    - **Subtasks:**
        - [x] **21.1:** Adjust `src/app/page.tsx` (containing `InputForm`) to correctly handle the structured JSON `previewData` received from the `/generate-plan` endpoint. The `previewData` should now directly match the `StudyPlan` type.
        - [x] **21.2:** Verify that `src/context/StudyPlanContext.tsx` and all components consuming the `studyPlan` from context (e.g., `src/app/study-session-active/page.tsx`, `StudyPlanDisplay`) correctly render and utilize the structured `StudyPlan` object without needing further transformation.
        - [x] **21.3:** Remove any redundant frontend logic in `InputForm.tsx` or other components that was previously responsible for parsing or manipulating the `previewData` into the `StudyPlan` format.

- **Task 22: Testing and Validation of Backend Structuring**
    - **ID:** 22
    - **Context:** Thoroughly test the new backend-driven structuring workflow to ensure correctness, robustness, and adherence to the defined data structures.
    - **Dependencies:** Task 20, Task 21
    - **Subtasks:**
        - [ ] **22.1:** Conduct end-to-end testing: from submitting inputs in the `InputForm`, through backend plan generation and structuring, to displaying the structured plan in the preview and study session page.
        - [ ] **22.2:** Validate that the JSON output from the backend strictly adheres to the `StudyPlan` interface defined in `src/context/StudyPlanContext.tsx`.
        - [ ] **22.3:** Test error handling scenarios for the LLM structuring step (e.g., simulate LLM failure, invalid JSON response from LLM) and ensure the application handles these gracefully.

## Summary of Task Dependencies for Phase 5.5

| Task ID | Task Name                                          | Dependencies                                     |
| :------ | :------------------------------------------------- | :----------------------------------------------- |
| 20      | Modify Backend for LLM-Based Study Plan Structuring | Task 6 (from todo-phase5.md)                     |
| 21      | Update Frontend to Consume Structured Study Plan     | Task 20, Task 18 (from todo-phase5.md)           |
| 22      | Testing and Validation of Backend Structuring      | Task 20, Task 21                                 |

This phase ensures that the study plan data is consistently structured before it reaches the frontend, leading to a more maintainable and robust application.