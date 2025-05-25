import json
import re
from typing import Dict, Any, List, Optional, Union

# Import pydantic models for structured data
try:
    from models.study_plan_models import StructuredStudyPlan, CoreConcept, DailySchedule, StudyItem, KeyFormula
except ImportError:
    # Define models inline if the import fails
    from pydantic import BaseModel, Field
    
    class CoreConcept(BaseModel):
        name: str
        explanation: str
        importance: Optional[str] = None
        related_concepts: Optional[List[str]] = None
    
    class StudyItem(BaseModel):
        topic: str
        description: str
        duration_minutes: int
        resource: Optional[str] = None
        is_completed: bool = False
    
    class DailySchedule(BaseModel):
        day: int
        date: Optional[str] = None
        focus_area: Optional[str] = None
        study_items: List[StudyItem]
        summary: Optional[str] = None
    
    class KeyFormula(BaseModel):
        name: str
        formula: str
        description: Optional[str] = None
    
    class StructuredStudyPlan(BaseModel):
        overall_goal: str
        total_study_day: int
        hour_per_day: int
        core_concepts: List[CoreConcept] = Field(default_factory=list)
        daily_schedule: List[DailySchedule] = Field(default_factory=list)
        general_tip: Optional[List[str]] = None
        key_formulas: Optional[List[KeyFormula]] = None

def generate_structured_study_plan(raw_plan: str, days: int, hours_per_day: int) -> StructuredStudyPlan:
    """
    Generate a structured study plan from the raw LLM output.
    
    Args:
        raw_plan: The raw study plan text from the LLM
        days: Total number of study days
        hours_per_day: Hours per day for study
        
    Returns:
        A structured study plan object
    """
    # Extract the overall goal from the raw plan
    overall_goal = extract_overall_goal(raw_plan)
    
    # Extract core concepts
    core_concepts_data = extract_core_concepts(raw_plan)
    core_concepts = [CoreConcept(**concept) for concept in core_concepts_data]
    
    # Extract daily schedule
    daily_schedule_data = extract_daily_schedule(raw_plan, days)
    daily_schedule = [DailySchedule(**day_data) for day_data in daily_schedule_data]
    
    # Extract general tips
    general_tips = extract_general_tips(raw_plan)
    
    # Extract key formulas
    key_formulas_data = extract_key_formulas(raw_plan)
    key_formulas = [KeyFormula(**formula) for formula in key_formulas_data] if key_formulas_data else None
    
    # Create and return the structured study plan
    return StructuredStudyPlan(
        overall_goal=overall_goal,
        total_study_day=days,
        hour_per_day=hours_per_day,
        core_concepts=core_concepts,
        daily_schedule=daily_schedule,
        general_tip=general_tips,
        key_formulas=key_formulas
    )

def extract_overall_goal(raw_plan: str) -> str:
    """
    Extract the overall goal from the raw study plan.
    
    Args:
        raw_plan: The raw study plan text
        
    Returns:
        The overall goal as a string
    """
    # Try to find an explicit goal statement
    goal_matches = re.search(r'(?:##\s*Goal|##\s*Overall\s*Goal)\s*(.+?)(?=##|$)', raw_plan, re.DOTALL | re.IGNORECASE)
    if goal_matches:
        return goal_matches.group(1).strip()
    
    # If no explicit goal, try to extract from introduction
    intro_matches = re.search(r'(?:##\s*Introduction|##\s*Overview)\s*(.+?)(?=##|$)', raw_plan, re.DOTALL | re.IGNORECASE)
    if intro_matches:
        intro_text = intro_matches.group(1).strip()
        # Take the first paragraph as the goal
        paragraphs = intro_text.split('\n\n')
        if paragraphs:
            return paragraphs[0].strip()
    
    # Default goal if nothing is found
    return f"Master the study materials over {days} days with {hours_per_day} hours per day."

def extract_core_concepts(raw_plan: str) -> List[Dict[str, Any]]:
    """
    Extract core concepts from the raw study plan.
    
    Args:
        raw_plan: The raw study plan text
        
    Returns:
        A list of core concept dictionaries
    """
    concepts = []
    # Look for sections that might contain core concepts
    concept_sections = re.findall(r'(?:##\s*Core\s*Concepts|##\s*Key\s*Concepts|##\s*Fundamental\s*Concepts).*?(?=##|$)', 
                                 raw_plan, re.DOTALL | re.IGNORECASE)
    
    if not concept_sections:
        # Try to find concepts in bullet points
        bullets_match = re.findall(r'(?:Key|Core|Important)\s+Concepts[:\n](.*?)(?=##|$)', raw_plan, re.DOTALL | re.IGNORECASE)
        if bullets_match:
            for match in bullets_match:
                bullet_points = re.findall(r'[*\-+]\s*([^\n]+)', match)
                for point in bullet_points:
                    concepts.append({
                        "name": point.strip(),
                        "explanation": f"Important concept: {point.strip()}"
                    })
    else:
        # Process the sections that contain concepts
        for section in concept_sections:
            # Try to extract concepts with explanations (in format: Concept - Explanation)
            concept_items = re.findall(r'[*\-+]\s*([^:\n]+)(?::\s*|\s*-\s*)([^\n]+)', section)
            
            # If we found structured concept items
            if concept_items:
                for name, explanation in concept_items:
                    concepts.append({
                        "name": name.strip(),
                        "explanation": explanation.strip()
                    })
            else:
                # Just extract bullet points as concept names
                bullet_points = re.findall(r'[*\-+]\s*([^\n]+)', section)
                for point in bullet_points:
                    concepts.append({
                        "name": point.strip(),
                        "explanation": f"Important concept in the study material."
                    })
    
    # If we still don't have concepts, create some default ones
    if not concepts:
        concepts = [
            {"name": "Core Concept 1", "explanation": "No specific concepts were identified in the study plan."}
        ]
    
    return concepts

def extract_daily_schedule(raw_plan: str, total_days: int) -> List[Dict[str, Any]]:
    """
    Extract the daily schedule from the raw study plan.
    
    Args:
        raw_plan: The raw study plan text
        total_days: Total number of study days
        
    Returns:
        A list of daily schedule dictionaries
    """
    daily_schedule = []
    
    # Try to find day sections
    day_sections = re.findall(r'##\s*Day\s*(\d+)[^#]*', raw_plan, re.DOTALL)
    day_contents = re.split(r'##\s*Day\s*\d+', raw_plan)[1:] # Skip the text before first day
    
    # If we found day sections
    if day_sections and len(day_sections) == len(day_contents):
        for i, (day_num, day_content) in enumerate(zip(day_sections, day_contents)):
            # Extract focus area if available
            focus_area_match = re.search(r'Focus\s*(?:Area|Topic)s?[:\s]([^\n]+)', day_content, re.IGNORECASE)
            focus_area = focus_area_match.group(1).strip() if focus_area_match else f"Day {day_num} Studies"
            
            # Extract summary if available
            summary_match = re.search(r'Summary[:\s]([^\n]+)', day_content, re.IGNORECASE)
            summary = summary_match.group(1).strip() if summary_match else None
            
            # Extract study items
            study_items = []
            
            # First, look for structured time allocations
            time_allocations = re.findall(r'[*\-+]\s*([^\n:]+)\s*(?:\(|:)\s*(\d+)\s*(?:hours|hour|hrs|hr|min|minutes)\s*(?:\)|,|;)\s*([^\n]*)', day_content, re.IGNORECASE)
            
            if time_allocations:
                for topic, duration, details in time_allocations:
                    # Convert hours to minutes if needed
                    duration_value = int(duration)
                    if 'hour' in details.lower() or 'hr' in details.lower():
                        duration_value *= 60
                        
                    study_items.append({
                        "topic": topic.strip(),
                        "description": details.strip() if details.strip() else f"Study {topic.strip()}",
                        "duration_minutes": duration_value,
                        "resource": None,
                        "is_completed": False
                    })
            else:
                # If no structured time allocations, look for bullet points
                topics = re.findall(r'[*\-+]\s*([^\n]+)', day_content)
                
                # Calculate approximate minutes per topic to match the day's total hours
                total_minutes = 240  # Default to 4 hours if not specified
                minutes_per_topic = total_minutes // len(topics) if topics else 60
                
                for topic in topics:
                    study_items.append({
                        "topic": topic.strip(),
                        "description": f"Study {topic.strip()}",
                        "duration_minutes": minutes_per_topic,
                        "resource": None,
                        "is_completed": False
                    })
            
            # If no study items were found, create a default one
            if not study_items:
                study_items = [{
                    "topic": f"Day {day_num} Studies",
                    "description": f"Complete studies for day {day_num}",
                    "duration_minutes": 240,  # Default to 4 hours
                    "resource": None,
                    "is_completed": False
                }]
            
            # Add the day to the schedule
            daily_schedule.append({
                "day": int(day_num),
                "date": None,
                "focus_area": focus_area,
                "study_items": study_items,
                "summary": summary
            })
    
    # If we couldn't extract the daily schedule, create a default one
    if not daily_schedule:
        for day in range(1, total_days + 1):
            daily_schedule.append({
                "day": day,
                "date": None,
                "focus_area": f"Day {day} Studies",
                "study_items": [{
                    "topic": f"Day {day} Studies",
                    "description": f"Complete studies for day {day}",
                    "duration_minutes": 240,  # Default to 4 hours
                    "resource": None,
                    "is_completed": False
                }],
                "summary": None
            })
    
    return daily_schedule

def extract_general_tips(raw_plan: str) -> List[str]:
    """
    Extract general study tips from the raw plan.
    
    Args:
        raw_plan: The raw study plan text
        
    Returns:
        A list of general tips
    """
    tips = []
    
    # Look for sections that might contain general tips
    tip_sections = re.findall(r'(?:##\s*General\s*Tips|##\s*Study\s*Tips|##\s*Tips).*?(?=##|$)', 
                             raw_plan, re.DOTALL | re.IGNORECASE)
    
    if tip_sections:
        for section in tip_sections:
            # Extract bullet points as tips
            bullet_points = re.findall(r'[*\-+]\s*([^\n]+)', section)
            tips.extend([point.strip() for point in bullet_points])
    
    # If no tips were found, provide some default ones
    if not tips:
        tips = [
            "Break your study sessions into 25-minute focused intervals with 5-minute breaks (Pomodoro Technique).",
            "Review your notes and key concepts regularly to reinforce learning.",
            "Get adequate sleep and exercise to optimize your learning capacity.",
            "Connect new information to concepts you already understand.",
            "Teach what you've learned to someone else to identify gaps in your understanding."
        ]
    
    return tips

def extract_key_formulas(raw_plan: str) -> List[Dict[str, Any]]:
    """
    Extract key formulas from the raw plan.
    
    Args:
        raw_plan: The raw study plan text
        
    Returns:
        A list of key formula dictionaries
    """
    formulas = []
    
    # Look for sections that might contain formulas
    formula_sections = re.findall(r'(?:##\s*Key\s*Formulas|##\s*Formulas|##\s*Equations).*?(?=##|$)', 
                                 raw_plan, re.DOTALL | re.IGNORECASE)
    
    if formula_sections:
        for section in formula_sections:
            # Try to extract structured formulas (Name: Formula - Description)
            formula_items = re.findall(r'[*\-+]\s*([^:\n]+)\s*:\s*([^\n]+?)(?:\s*-\s*|\s*:\s*)([^\n]+)?', section)
            
            if formula_items:
                for name, formula, description in formula_items:
                    formulas.append({
                        "name": name.strip(),
                        "formula": formula.strip(),
                        "description": description.strip() if description else f"Formula for {name.strip()}"
                    })
            else:
                # Just extract bullet points as formula names
                bullet_points = re.findall(r'[*\-+]\s*([^\n]+)', section)
                for point in bullet_points:
                    # Try to split the point into formula and description
                    parts = point.split(':', 1)
                    if len(parts) == 2:
                        name = parts[0].strip()
                        formula_text = parts[1].strip()
                        formulas.append({
                            "name": name,
                            "formula": formula_text,
                            "description": f"Formula for {name}"
                        })
                    else:
                        formulas.append({
                            "name": f"Formula {len(formulas) + 1}",
                            "formula": point.strip(),
                            "description": "Important formula from the study material."
                        })
    
    return formulas