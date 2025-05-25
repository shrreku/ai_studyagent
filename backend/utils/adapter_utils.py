from typing import Dict, Any, List, Optional

def transform_backend_to_frontend(structured_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms the backend structured study plan to match the frontend expected format.
    
    Backend format (from study_plan_models.py):
    - overall_goal, total_study_day, hour_per_day
    - core_concepts, daily_schedule, general_tip, key_formulas
    
    Frontend format (enhanced for better UI/UX):
    - overallGoal, totalStudyDays, hoursPerDay
    - keyConcepts, dailyBreakdown, generalTips, keyFormulas
    - Enhanced with focus areas, learning objectives, priorities, etc.
    
    Args:
        structured_plan: The backend structured study plan
        
    Returns:
        The transformed plan in frontend format
    """
    # Skip transformation if there's an error
    if "error" in structured_plan:
        return {
            "error": structured_plan["error"],
            "details": structured_plan.get("details", "Unknown error")
        }
    
    try:
        # Create base structure with camelCase keys
        frontend_plan = {
            "overallGoal": structured_plan.get("overall_goal", "Study effectively"),
            "totalStudyDays": structured_plan.get("total_study_day", 1),
            "hoursPerDay": structured_plan.get("hour_per_day", 2.0),
            "keyConcepts": [],
            "dailyBreakdown": [],
            "generalTips": structured_plan.get("general_tip", []),
        }
        
        # Transform core_concepts to keyConcepts
        if "core_concepts" in structured_plan and structured_plan["core_concepts"]:
            frontend_plan["keyConcepts"] = [
                {
                    "concept": concept.get("name", ""),
                    "explanation": concept.get("explanation", "")
                }
                for concept in structured_plan["core_concepts"]
            ]
        
        # Transform daily_schedule to dailyBreakdown with enhanced information
        if "daily_schedule" in structured_plan and structured_plan["daily_schedule"]:
            frontend_plan["dailyBreakdown"] = []
            
            for day_schedule in structured_plan["daily_schedule"]:
                day_data = {
                    "day": day_schedule.get("day", 1),
                    "daySummary": day_schedule.get("summary", ""),
                    "focusArea": day_schedule.get("focus_area", "Day Study"),  # Added focus_area for day navigation
                    "learningGoals": day_schedule.get("learning_goals", []),  # Added learning goals
                    "reviewTopics": day_schedule.get("review_topics", []),    # Added review topics
                    "items": []
                }
                
                # Add study items for the day
                if "study_item" in day_schedule and day_schedule["study_item"]:
                    study_items = day_schedule["study_item"]
                    
                    # Process regular study items
                    for item in study_items:
                        # Convert duration from minutes to hours
                        duration_hours = item.get("duration_minutes", 60) / 60
                        
                        # Process resources (could be strings or objects)
                        resources = []
                        if "resource" in item and item["resource"]:
                            for resource in item["resource"]:
                                if isinstance(resource, str):
                                    resources.append({
                                        "title": resource,
                                        "type": "text",
                                        "url": None
                                    })
                                elif isinstance(resource, dict) and "title" in resource:
                                    # Keep the full resource object with additional fields
                                    res_obj = {
                                        "title": resource.get("title", ""),
                                        "type": resource.get("type", "text"),
                                        "url": resource.get("url", None),
                                        "description": resource.get("description", None)
                                    }
                                    resources.append(res_obj)
                        
                        # Create enhanced study item with all available information
                        study_item = {
                            "topic": item.get("topic", "Study topic"),
                            "details": item.get("description", ""),
                            "durationMinutes": item.get("duration_minutes", 60),  # Keep original minutes
                            "estimatedTimeHours": duration_hours,                  # Also provide hours
                            "resources": resources,
                            "isCompleted": item.get("is_completed", False),
                            "learningObjectives": item.get("learning_objectives", []),
                            "priority": item.get("priority", "medium")
                        }
                        
                        day_data["items"].append(study_item)
                    
                    # Add summary as the last item for better UI representation
                    if day_schedule.get("summary"):
                        summary_item = {
                            "topic": "Summary",
                            "details": day_schedule.get("summary", ""),
                            "durationMinutes": 10,
                            "estimatedTimeHours": 10/60,
                            "resources": [],
                            "isCompleted": False,
                            "learningObjectives": day_schedule.get("learning_goals", []),
                            "priority": "high"
                        }
                        day_data["items"].append(summary_item)
                
                frontend_plan["dailyBreakdown"].append(day_data)
        
        # Transform key_formulas to keyFormulas with enhanced information
        if "key_formulas" in structured_plan and structured_plan["key_formulas"]:
            frontend_plan["keyFormulas"] = []
            
            for formula in structured_plan["key_formulas"]:
                # Create enhanced formula object with all available information
                formula_obj = {
                    "formula_name": formula.get("name", ""),
                    "formula": formula.get("formula", ""),  # The actual formula expression
                    "description": formula.get("description", ""),
                    "usage_context": formula.get("usage_context", ""),
                    "variables": formula.get("variables", {}),
                    "examples": formula.get("examples", [])
                }
                
                frontend_plan["keyFormulas"].append(formula_obj)
        
        return frontend_plan
    
    except Exception as e:
        print(f"Error transforming plan: {e}")
        # Return a minimal valid structure if transformation fails
        return {
            "overallGoal": structured_plan.get("overall_goal", "Study effectively"),
            "totalStudyDays": 1,
            "hoursPerDay": 2.0,
            "keyConcepts": [],
            "dailyBreakdown": [
                {
                    "day": 1,
                    "daySummary": "Error occurred while processing the study plan",
                    "items": [
                        {
                            "topic": "Please regenerate your study plan",
                            "details": f"An error occurred: {str(e)}",
                            "estimatedTimeHours": 1.0,
                            "resources": []
                        }
                    ]
                }
            ],
            "generalTips": ["Try regenerating your study plan"],
            "error": str(e)
        }
