import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import logging
from pathlib import Path
from utils.file_parser import extract_text_from_file
from utils.ai_workflow import run_study_plan_crew, generate_preview_study_plan # Import the crew runner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "./uploads"

@router.post("/upload")
async def upload_files(
    notes: list[UploadFile] = File(...), 
    questions: list[UploadFile] = File(None), 
    study_duration_days: str = None, 
    study_hours_per_day: str = None
):
    logger.info("Received upload request")
    logger.info(f"Notes files: {[n.filename for n in notes] if notes else 'None'}")
    logger.info(f"Question files: {[q.filename for q in questions] if questions else 'None'}")
    logger.info(f"Study duration days: {study_duration_days}")
    logger.info(f"Study hours per day: {study_hours_per_day}")
    
    # Validate and set defaults if needed
    if not study_duration_days:
        logger.warning("No study duration days provided, using default value of 7")
        study_duration_days = "7"
    
    if not study_hours_per_day:
        logger.warning("No study hours per day provided, using default value of 2")
        study_hours_per_day = "2"
        
    # Convert to appropriate types and validate
    try:
        days = int(study_duration_days)
        hours = float(study_hours_per_day)
        
        if days <= 0 or days > 7:  # Set reasonable limits
            logger.warning(f"Invalid study duration days: {days}, using default value of 7")
            study_duration_days = "7"
            
        if hours <= 0 or hours > 24:  # Set reasonable limits
            logger.warning(f"Invalid study hours per day: {hours}, using default value of 2")
            study_hours_per_day = "2"
    except ValueError:
        logger.warning(f"Invalid numeric values: days={study_duration_days}, hours={study_hours_per_day}, using defaults")
        study_duration_days = "7"
        study_hours_per_day = "2"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    processed_notes_files = []
    processed_questions_files = []
    all_saved_paths = []

    try:
        # Process notes files
        for note_file in notes:
            notes_filename = getattr(note_file, 'filename', f"note_{len(processed_notes_files)}.bin")
            notes_path = os.path.join(UPLOAD_DIR, notes_filename)
            all_saved_paths.append(notes_path)
            with open(notes_path, "wb") as buffer:
                shutil.copyfileobj(note_file.file, buffer)
            processed_notes_files.append({"filename": notes_filename, "path": notes_path})
            if hasattr(note_file, 'file') and note_file.file:
                 note_file.file.close()

        # Process questions files (optional)
        if questions:
            for question_file in questions:
                questions_filename = getattr(question_file, 'filename', f"question_{len(processed_questions_files)}.bin")
                questions_path = os.path.join(UPLOAD_DIR, questions_filename)
                all_saved_paths.append(questions_path)
                with open(questions_path, "wb") as buffer:
                    shutil.copyfileobj(question_file.file, buffer)
                processed_questions_files.append({"filename": questions_filename, "path": questions_path})
                if hasattr(question_file, 'file') and question_file.file:
                    question_file.file.close()

    except Exception as e:
        for path in all_saved_paths: # Clean up any saved files on error
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=f"Could not save one or more files: {e}")

    # Extract text from uploaded files
    extracted_notes_text_list = []
    extracted_questions_text_list = []

    try:
        for note_info in processed_notes_files:
            extracted_notes_text_list.append(extract_text_from_file(note_info["path"]))
        
        for question_info in processed_questions_files:
            extracted_questions_text_list.append(extract_text_from_file(question_info["path"]))

    except HTTPException as e:
        raise e # Re-raise the HTTPException from text extraction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during text extraction: {e}")
    finally:
        # Clean up uploaded files after processing
        for path in all_saved_paths:
            if os.path.exists(path):
                os.remove(path)

    extracted_notes_text = "\n\n".join(extracted_notes_text_list)
    extracted_questions_text = "\n\n".join(extracted_questions_text_list)

    # Combine extracted texts for the crew
    combined_study_materials = f"Class Notes:\n{extracted_notes_text}\n\nPractice Questions:\n{extracted_questions_text}"

    study_plan_result = None
    if extracted_notes_text or extracted_questions_text: # Only run crew if there's content
        try:
            print(f"Calling run_study_plan_crew with duration: {study_duration_days} days, hours: {study_hours_per_day} per day.")
            print(f"Combined study materials length: {len(combined_study_materials)} characters")
            
            # Log the first 500 characters for debugging
            print(f"First 500 chars of study materials: {combined_study_materials[:500]}...")
            
            # Generate the study plan
            study_plan_result = await run_study_plan_crew(
                study_materials=combined_study_materials,
                days=int(study_duration_days),
                hours_per_day=int(study_hours_per_day)
            )
            
            print("Successfully generated study plan result")
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            error_msg = f"Error calling run_study_plan_crew: {str(e)}\n\nTraceback:\n{error_traceback}"
            print(error_msg)
            study_plan_result = {
                "error": "Failed to generate study plan due to an internal error.", 
                "details": error_msg,
                "type": type(e).__name__
            }
    else:
        study_plan_result = {"message": "No text content extracted from files, skipping study plan generation."}

    # Return the study plan result directly as the main response
    try:
        if study_plan_result:
            logger.info("Study plan generated successfully")
            return {
                "status": "success",
                "raw_plan": study_plan_result.get("raw_plan", ""),
                "structured_plan": study_plan_result.get("structured_plan", {}),
                "frontend_plan": study_plan_result.get("frontend_plan", {})
            }
        else:
            error_msg = "Failed to generate study plan"
            logger.error(f"Error generating study plan: {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "details": ""
            }
    except Exception as e:
        logger.exception("Error processing study plan result:")
        return {
            "status": "error",
            "message": "Failed to process study plan result",
            "details": str(e)
        }

@router.post("/preview")
async def generate_preview(
    notes: list[UploadFile] = File(...), 
    questions: list[UploadFile] = File(None),  # Make questions optional
    study_duration_days: str = Form(...), 
    study_hours_per_day: str = Form(...)
):
    """
    Generate a preview of the study plan based on uploaded materials.
    
    This endpoint creates a preview version of the study plan without permanently storing
    the uploaded files or creating a study session. It's used for the plan preview page.
    """
    try:
        # Create a temporary directory for file uploads
        TEMP_UPLOAD_DIR = Path("./temp_uploads")
        TEMP_UPLOAD_DIR.mkdir(exist_ok=True)
        
        logger.info(f"Generating preview for {study_duration_days} days, {study_hours_per_day} hours per day")
        logger.info(f"Received {len(notes)} note files")
        
        # Check input validation and convert to integers
        try:
            study_duration_days_int = int(study_duration_days)
            study_hours_per_day_int = int(study_hours_per_day)
        except ValueError:
            raise HTTPException(status_code=400, detail="Study duration and hours per day must be valid integers")
            
        if study_duration_days_int < 1 or study_duration_days_int > 14:
            raise HTTPException(status_code=400, detail="Study duration must be between 1 and 14 days")
        
        if study_hours_per_day_int < 1 or study_hours_per_day_int > 24:
            raise HTTPException(status_code=400, detail="Hours per day must be between 1 and 24")
        
        # Extract text from the uploaded files
        notes_text = ""
        questions_text = ""
        
        # Process notes files
        logger.info(f"Processing {len(notes)} notes files")
        for note_file in notes:
            content = await note_file.read()
            temp_path = TEMP_UPLOAD_DIR / note_file.filename
            with open(temp_path, "wb") as f:
                f.write(content)
            
            # Extract text from the file based on its type (simplified for now)
            if temp_path.suffix.lower() in [".txt"]:
                with open(temp_path, "r", encoding="utf-8", errors="ignore") as f:
                    notes_text += f.read() + "\n\n"
            else:
                # For now, just include filename for non-text files
                notes_text += f"Content from {note_file.filename}\n\n"
            
            # Clean up temporary file
            temp_path.unlink(missing_ok=True)
            
        # Process question files if provided
        if questions:
            logger.info(f"Processing {len(questions)} question files")
            for question_file in questions:
                content = await question_file.read()
                temp_path = TEMP_UPLOAD_DIR / question_file.filename
                with open(temp_path, "wb") as f:
                    f.write(content)
                
                # Extract text from the file based on its type (simplified for now)
                if temp_path.suffix.lower() in [".txt"]:
                    with open(temp_path, "r", encoding="utf-8", errors="ignore") as f:
                        questions_text += f.read() + "\n\n"
                else:
                    # For now, just include filename for non-text files
                    questions_text += f"Questions from {question_file.filename}\n\n"
                
                # Clean up temporary file
                temp_path.unlink(missing_ok=True)
        
        # Generate preview study plan
        preview_result = await generate_preview_study_plan(
            study_materials_text=notes_text,
            study_duration_days=study_duration_days_int,
            study_hours_per_day=study_hours_per_day_int,
            questions_text=questions_text if questions and questions_text.strip() else None
        )
        
        # Check for errors
        if preview_result.get("status") == "error":
            error_message = preview_result.get("details", preview_result.get("error", "Unknown error"))
            logger.error(f"Error generating preview: {error_message}")
            raise HTTPException(status_code=500, detail=f"Failed to generate preview: {error_message}")
        
        # Check if we have a partial success (overview but no JSON)
        if preview_result.get("status") == "partial_success":
            logger.warning("Generated preview with partial success (no structured JSON)")
            return {
                "message": "Preview generated with warnings", 
                "preview_plan": preview_result.get("preview_plan"),
                "warnings": preview_result.get("details", "Could not parse structured data")
            }
        
        # Return the preview plan, raw plan text, and simplified JSON if available
        return {
            "message": "Preview generated successfully", 
            "preview_plan": preview_result.get("preview_plan"),
            "raw_plan": preview_result.get("raw_plan"),
            "simplified_json": preview_result.get("simplified_json")
        }
    
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions
        raise http_exc
    
    except Exception as e:
        logger.error(f"Unexpected error in generate_preview: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
    finally:
        # Clean up the temporary directory
        if os.path.exists("./temp_uploads"):
            try:
                shutil.rmtree("./temp_uploads")
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")