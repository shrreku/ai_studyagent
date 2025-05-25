from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from typing import Any, Dict, Optional
import json # Added for JSON validation
from utils.ai_workflow import run_study_plan_crew, structure_raw_plan # Import the AI workflow functions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class StudyPlanRequest(BaseModel):
    total_days: int
    hours_per_day: int

class RawPlanRequest(BaseModel):
    raw_plan: str
    simplified_json: Optional[Dict[str, Any]] = None

class StudyPlanData(BaseModel):
    text_plan: str
    topic_list_json: str # This will store the JSON string of topics for future task creation

class StructuredPlanResponse(BaseModel):
    structured_plan: Dict[str, Any]
    message: Optional[str] = "Plan structured successfully"

class StudyPlanResponse(BaseModel):
    message: str
    plan: StudyPlanData

@router.post("/generate-plan", response_model=StudyPlanResponse)
async def generate_plan_route(request: StudyPlanRequest):
    """
    Generates a study plan based on the total number of days and hours per day.
    """
    try:
        logger.info(f"Received request to generate plan: {request.total_days} days, {request.hours_per_day} hours/day")
        total_hours = request.total_days * request.hours_per_day
        if total_hours <= 0:
            raise HTTPException(status_code=400, detail="Total study hours must be positive.")

        # Placeholder for study_materials_text - this should come from uploaded files
        # In a real scenario, this text would be retrieved based on a session or user ID
        # linking to previously uploaded and processed notes and questions.
        # For now, using a placeholder.
        placeholder_study_materials = "Placeholder: Text from notes and questions would go here."

        logger.info("Calling Crew AI to generate study plan...")
        # The run_study_plan_crew now returns a dictionary with 'text_plan' and 'topic_list_json'
        crew_output = run_study_plan_crew(
            study_materials_text=placeholder_study_materials,
            study_duration_days=str(request.total_days),
            study_hours_per_day=str(request.hours_per_day)
        )

        # Check if the crew_output itself is an error dictionary
        if isinstance(crew_output, dict) and "error" in crew_output:
            error_detail = crew_output.get('details', crew_output['error'])
            logger.error(f"Crew AI execution failed: {error_detail}")
            raise HTTPException(status_code=500, detail=f"Failed to generate study plan: {error_detail}")

        # Validate that crew_output is a dictionary and contains the expected keys
        if not isinstance(crew_output, dict):
            logger.error(f"Unexpected output type from Crew AI: {type(crew_output)}. Expected a dictionary.")
            raise HTTPException(status_code=500, detail="Failed to process study plan: Unexpected output format from AI.")

        text_plan_content = crew_output.get("text_plan")
        topic_list_json_content = crew_output.get("topic_list_json")

        if not text_plan_content or not isinstance(text_plan_content, str):
            logger.error(f"'text_plan' missing or not a string in Crew AI output. Output: {crew_output}")
            raise HTTPException(status_code=500, detail="Failed to process study plan: 'text_plan' missing or invalid.")

        if not topic_list_json_content or not isinstance(topic_list_json_content, str):
            logger.error(f"'topic_list_json' missing or not a string in Crew AI output. Output: {crew_output}")
            raise HTTPException(status_code=500, detail="Failed to process study plan: 'topic_list_json' missing or invalid.")
        
        # Basic validation for JSON string
        try:
            json.loads(topic_list_json_content) # Check if it's valid JSON
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON detected for topic list: {topic_list_json_content[:500]}... Error: {e}")
            raise HTTPException(status_code=500, detail="Failed to parse topic list: Invalid JSON format.")

        study_plan_data = StudyPlanData(
            text_plan=text_plan_content,
            topic_list_json=topic_list_json_content
        )

        logger.info(f"Successfully generated and parsed study plan. Total hours: {total_hours}")
        return StudyPlanResponse(message="Study plan generated successfully.", plan=study_plan_data)
    except HTTPException as http_exc:
        logger.error(f"HTTPException in generate_plan_route: {http_exc.detail}")
        raise http_exc # Re-raise HTTPException to let FastAPI handle it
    except Exception as e:
        logger.error(f"Unexpected error in generate_plan_route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/structure-plan", response_model=StructuredPlanResponse)
async def structure_plan_route(request: RawPlanRequest):
    """
    Structures a raw study plan text into a structured format for the frontend.
    """
    try:
        logger.info(f"Received request to structure plan, content length: {len(request.raw_plan)} characters")
        
        if not request.raw_plan or len(request.raw_plan.strip()) < 10:
            raise HTTPException(status_code=400, detail="Raw plan text is too short or empty.")

        # Call the AI workflow function to structure the raw plan
        # Pass simplified_json if available
        logger.info(f"Simplified JSON available: {request.simplified_json is not None}")
        structured_plan = await structure_raw_plan(
            raw_plan_text=request.raw_plan,
            simplified_json=request.simplified_json
        )
        
        # Check if there was an error in the structuring process
        if structured_plan and isinstance(structured_plan, dict) and "error" in structured_plan:
            error_message = structured_plan.get("details", structured_plan["error"])
            logger.error(f"Error structuring plan: {error_message}")
            raise HTTPException(status_code=500, detail=f"Failed to structure study plan: {error_message}")
        
        # Validate that we have a proper structured plan
        if not structured_plan or not isinstance(structured_plan, dict):
            logger.error(f"Invalid structured plan format: {type(structured_plan)}")
            raise HTTPException(status_code=500, detail="Failed to structure study plan: Invalid format")
            
        # Validate required fields are present
        required_fields = ["overallGoal", "totalStudyDays", "hoursPerDay", "dailyBreakdown"]
        missing_fields = [field for field in required_fields if field not in structured_plan]
        if missing_fields:
            logger.error(f"Missing required fields in structured plan: {missing_fields}")
            raise HTTPException(status_code=500, detail=f"Failed to structure study plan: Missing fields {missing_fields}")
        
        logger.info("Successfully structured the raw plan")
        return StructuredPlanResponse(structured_plan=structured_plan)
    except json.JSONDecodeError as json_exc:
        error_msg = f"JSON parsing error: {str(json_exc)}"
        logger.error(f"Error structuring plan: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    except HTTPException as http_exc:
        logger.error(f"HTTPException in structure_plan_route: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error in structure_plan_route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")