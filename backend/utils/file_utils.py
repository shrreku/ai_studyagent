import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def save_structured_output(data, filename=None, directory="test_data"):
    """
    Save structured output to a file for future testing and refinement.
    
    Args:
        data: The data to save (will be converted to JSON)
        filename: Optional custom filename, if None a timestamp will be used
        directory: Directory to save the file in
    
    Returns:
        str: Path to the saved file
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Generate filename with timestamp if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"structured_output_{timestamp}.json"
        
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename += '.json'
            
        # Full path to save file
        filepath = os.path.join(directory, filename)
        
        # Save the data
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Structured output saved to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving structured output: {str(e)}")
        return None
