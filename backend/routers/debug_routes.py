from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/sample_plan")
async def get_sample_plan():
    """
    Returns a sample study plan for testing purposes.
    """
    try:
        # Get the path to the sample plan
        sample_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "test_data", 
            "sample_frontend_plan.json"
        )
        
        # Check if the file exists
        if not os.path.exists(sample_path):
            logger.error(f"Sample plan file not found at {sample_path}")
            raise HTTPException(status_code=404, detail="Sample plan file not found")
            
        # Return the file
        return FileResponse(
            path=sample_path,
            media_type="application/json",
            filename="sample_frontend_plan.json"
        )
        
    except Exception as e:
        logger.error(f"Error serving sample plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to serve sample plan: {str(e)}")
