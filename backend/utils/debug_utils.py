import json
import os
import datetime
from typing import Dict, Any

def save_structured_plan(structured_plan: Dict[str, Any], prefix: str = "plan") -> str:
    """
    Save the structured study plan to a JSON file for debugging and testing.
    
    Args:
        structured_plan: The structured study plan to save
        prefix: Prefix for the filename
        
    Returns:
        Path to the saved file
    """
    # Create directory if it doesn't exist
    test_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_data")
    os.makedirs(test_data_dir, exist_ok=True)
    
    # Generate timestamp for filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.json"
    filepath = os.path.join(test_data_dir, filename)
    
    # Write the plan to file
    with open(filepath, "w") as f:
        json.dump(structured_plan, f, indent=2)
    
    return filepath
