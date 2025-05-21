from fastapi import APIRouter, File, UploadFile, HTTPException
import shutil
import os
from utils.file_parser import extract_text_from_file
from utils.ai_workflow import run_study_plan_crew # Import the crew runner

router = APIRouter()

UPLOAD_DIR = "./uploads"

@router.post("/upload")
async def upload_files(notes: UploadFile = File(...), questions: UploadFile = File(...), study_duration_days: str = "7", study_hours_per_day: str = "2"):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    notes_filename = getattr(notes, 'filename', 'notes_default_name')
    questions_filename = getattr(questions, 'filename', 'questions_default_name')

    notes_path = os.path.join(UPLOAD_DIR, notes_filename)
    questions_path = os.path.join(UPLOAD_DIR, questions_filename)

    try:
        with open(notes_path, "wb") as buffer:
            shutil.copyfileobj(notes.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save notes file: {e}")
    finally:
        if hasattr(notes, 'file') and notes.file:
            notes.file.close()

    try:
        with open(questions_path, "wb") as buffer:
            shutil.copyfileobj(questions.file, buffer)
    except Exception as e:
        # Clean up notes file if questions file fails
        if os.path.exists(notes_path):
            os.remove(notes_path)
        raise HTTPException(status_code=500, detail=f"Could not save questions file: {e}")
    finally:
        if hasattr(questions, 'file') and questions.file:
            questions.file.close()

    # Extract text from uploaded files
    extracted_notes_text = ""
    extracted_questions_text = ""
    try:
        extracted_notes_text = extract_text_from_file(notes_path)
        extracted_questions_text = extract_text_from_file(questions_path)
    except HTTPException as e:
        # Clean up files if text extraction fails
        if os.path.exists(notes_path):
            os.remove(notes_path)
        if os.path.exists(questions_path):
            os.remove(questions_path)
        raise e # Re-raise the HTTPException from text extraction
    except Exception as e:
        # Clean up files if text extraction fails with a generic error
        if os.path.exists(notes_path):
            os.remove(notes_path)
        if os.path.exists(questions_path):
            os.remove(questions_path)
        raise HTTPException(status_code=500, detail=f"Error during text extraction: {e}")
    finally:
        # Clean up uploaded files after processing
        if os.path.exists(notes_path):
            os.remove(notes_path)
        if os.path.exists(questions_path):
            os.remove(questions_path)

    # Combine extracted texts for the crew
    combined_study_materials = f"Class Notes:\n{extracted_notes_text}\n\nPractice Questions:\n{extracted_questions_text}"

    study_plan_result = None
    if extracted_notes_text or extracted_questions_text: # Only run crew if there's content
        try:
            print(f"Calling run_study_plan_crew with duration: {study_duration_days} days, hours: {study_hours_per_day} per day.")
            study_plan_result = run_study_plan_crew(
                study_materials_text=combined_study_materials,
                study_duration_days=study_duration_days,
                study_hours_per_day=study_hours_per_day
            )
        except Exception as e:
            print(f"Error calling run_study_plan_crew: {e}")
            # study_plan_result will remain None or could be set to an error dict
            study_plan_result = {"error": "Failed to generate study plan due to an internal error.", "details": str(e)}
    else:
        study_plan_result = {"message": "No text content extracted from files, skipping study plan generation."}

    return {
        "message": "Files processed. Study plan generation attempted.",
        "notes_filename": notes_filename,
        "questions_filename": questions_filename,
        "extracted_notes_text_preview": extracted_notes_text[:500] + "..." if extracted_notes_text else "", # Preview to keep response size manageable
        "extracted_questions_text_preview": extracted_questions_text[:500] + "..." if extracted_questions_text else "", # Preview
        "study_plan_result": study_plan_result
    }