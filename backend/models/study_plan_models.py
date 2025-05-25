from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union

class CoreConcept(BaseModel):
    """Core concept to master in the study plan"""
    name: str = Field(..., description="Name of the concept")
    explanation: str = Field(..., description="Explanation of the concept")
    importance: Optional[str] = Field(None, description="Why this concept is important")
    related_concepts: Optional[List[str]] = Field(None, description="List of related concepts")
    examples: Optional[List[str]] = Field(None, description="Examples illustrating this concept")
    difficulty_level: Optional[str] = Field(None, description="Difficulty level of the concept (basic, intermediate, advanced)")

class Resource(BaseModel):
    """Study resource"""
    title: str = Field(..., description="Title or name of the resource")
    type: Optional[str] = Field(None, description="Type of resource (textbook, video, article, exercise)")
    url: Optional[str] = Field(None, description="URL for the resource, if available")
    description: Optional[str] = Field(None, description="Brief description of the resource")

class StudyItem(BaseModel):
    """Study item within a day"""
    topic: str = Field(..., description="Topic to study")
    description: str = Field(..., description="Description of what to study")
    duration_minutes: int = Field(..., description="Duration in minutes")
    resource: Optional[Union[List[str], List[Resource]]] = Field(None, description="Resources to use (either simple strings or detailed resources)")
    is_completed: bool = Field(False, description="Whether this item is completed")
    learning_objectives: Optional[List[str]] = Field(None, description="Specific learning objectives for this study item")
    priority: Optional[str] = Field(None, description="Priority of this study item (high, medium, low)")

    @validator('resource', pre=True)
    def convert_string_resources(cls, v):
        """Convert string resources to Resource objects if provided as strings"""
        if isinstance(v, list) and v and isinstance(v[0], str):
            return [Resource(title=r) for r in v]
        return v

class DailySchedule(BaseModel):
    """Daily schedule in a study plan"""
    day: int = Field(..., description="Day number")
    date: Optional[str] = Field(None, description="Date for this day if available")
    focus_area: str = Field(..., description="Main focus area for this day")
    study_item: List[StudyItem] = Field(..., description="List of study items for this day")
    summary: str = Field(..., description="Summary of what will be covered this day")
    learning_goals: Optional[List[str]] = Field(None, description="Learning goals for this day")
    review_topics: Optional[List[str]] = Field(None, description="Topics to review from previous days")

class KeyFormula(BaseModel):
    """Key formula to remember"""
    name: str = Field(..., description="Name of the formula")
    formula: str = Field(..., description="The formula expression")
    description: str = Field(..., description="Description of what the formula represents")
    usage_context: Optional[str] = Field(None, description="When and how to use this formula")
    variables: Optional[Dict[str, str]] = Field(None, description="Definition of variables used in the formula")
    examples: Optional[List[str]] = Field(None, description="Example applications of the formula")

class LearningResource(BaseModel):
    """General learning resource for the entire study plan"""
    title: str = Field(..., description="Title of the resource")
    type: str = Field(..., description="Type of resource (book, video, website, etc.)")
    url: Optional[str] = Field(None, description="URL for the resource, if available")
    description: str = Field(..., description="Description of the resource")
    relevance: Optional[str] = Field(None, description="Relevance to the study plan")

class Assessment(BaseModel):
    """Assessment method for testing knowledge"""
    name: str = Field(..., description="Name of the assessment")
    description: str = Field(..., description="Description of the assessment")
    type: str = Field(..., description="Type of assessment (quiz, project, problem set)")
    topics_covered: List[str] = Field(..., description="Topics covered by this assessment")

class StructuredStudyPlan(BaseModel):
    """Complete structured study plan"""
    overall_goal: str = Field(..., description="Overall goal of the study plan")
    total_study_day: int = Field(..., description="Total number of study days")
    hour_per_day: float = Field(..., description="Hours per day to study")
    
    @validator('total_study_day')
    def validate_study_days(cls, v, values):
        """Ensure that total_study_day matches user input"""
        # This validator will be enforced during data validation
        # The actual value will be set from user input in the workflow
        if v <= 0:
            raise ValueError(f"Total study days must be positive, got {v}")
        return v
        
    @validator('hour_per_day')
    def validate_hours_per_day(cls, v, values):
        """Ensure that hour_per_day matches user input"""
        # This validator will be enforced during data validation
        # The actual value will be set from user input in the workflow
        if v <= 0:
            raise ValueError(f"Hours per day must be positive, got {v}")
        return v

    core_concepts: List[CoreConcept] = Field(..., description="List of core concepts to master")
    daily_schedule: List[DailySchedule] = Field(..., description="Daily breakdown of the study plan")
    general_tip: List[str] = Field(..., description="General tips for studying")
    key_formulas: Optional[List[KeyFormula]] = Field(None, description="Key formulas to remember")
    resources: Optional[List[LearningResource]] = Field(None, description="General resources for the entire study plan")
    assessments: Optional[List[Assessment]] = Field(None, description="Assessments to test knowledge")
    prerequisites: Optional[List[str]] = Field(None, description="Prerequisites for this study plan")
    difficulty_level: Optional[str] = Field(None, description="Overall difficulty level of the study plan")
    estimated_completion_time: Optional[float] = Field(None, description="Estimated total time to complete in hours")
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_goal": "Master the fundamental concepts of [SUBJECT], focusing on [KEY_AREA_1], [KEY_AREA_2], and [KEY_AREA_3].",
                "total_study_day": 7,
                "hour_per_day": 2.0,
                "core_concepts": [
                    {
                        "name": "[CONCEPT_NAME]",
                        "explanation": "[DETAILED_EXPLANATION_OF_CONCEPT]",
                        "importance": "[WHY_THIS_CONCEPT_IS_IMPORTANT]",
                        "related_concepts": ["[RELATED_CONCEPT_1]", "[RELATED_CONCEPT_2]"],
                        "examples": ["[EXAMPLE_1_ILLUSTRATING_CONCEPT]", "[EXAMPLE_2_ILLUSTRATING_CONCEPT]"],
                        "difficulty_level": "basic"
                    }
                ],
                "daily_schedule": [
                    {
                        "day": 1,
                        "date": None,
                        "focus_area": "[MAIN_FOCUS_FOR_DAY_1]",
                        "study_item": [
                            {
                                "topic": "[SPECIFIC_TOPIC_TO_STUDY]",
                                "description": "[DETAILED_DESCRIPTION_OF_WHAT_TO_STUDY]",
                                "duration_minutes": 30,
                                "resource": [
                                    {
                                        "title": "[RESOURCE_TITLE]",
                                        "type": "textbook",
                                        "url": None,
                                        "description": "[RESOURCE_DESCRIPTION]"
                                    }
                                ],
                                "is_completed": False,
                                "learning_objectives": ["[SPECIFIC_LEARNING_OBJECTIVE_1]", "[SPECIFIC_LEARNING_OBJECTIVE_2]"],
                                "priority": "high"
                            }
                        ],
                        "summary": "[SUMMARY_OF_DAY'S_LEARNING]",
                        "learning_goals": ["[LEARNING_GOAL_1_FOR_DAY]", "[LEARNING_GOAL_2_FOR_DAY]"],
                        "review_topics": ["[TOPIC_TO_REVIEW_FROM_PREVIOUS_DAYS]"]
                    }
                ],
                "general_tip": ["[GENERAL_STUDY_TIP_1]", "[GENERAL_STUDY_TIP_2]", "[GENERAL_STUDY_TIP_3]"],
                "key_formulas": [
                    {
                        "name": "[FORMULA_NAME]",
                        "formula": "[ACTUAL_FORMULA_EXPRESSION]",
                        "description": "[WHAT_THE_FORMULA_REPRESENTS]",
                        "usage_context": "[WHEN_AND_HOW_TO_USE_FORMULA]",
                        "variables": {"[VARIABLE_1]": "[DEFINITION_OF_VARIABLE_1]", "[VARIABLE_2]": "[DEFINITION_OF_VARIABLE_2]"},
                        "examples": ["[EXAMPLE_APPLICATION_OF_FORMULA_1]", "[EXAMPLE_APPLICATION_OF_FORMULA_2]"]
                    }
                ],
                "resources": [
                    {
                        "title": "[GENERAL_RESOURCE_TITLE]",
                        "type": "[RESOURCE_TYPE]",
                        "url": "[RESOURCE_URL]",
                        "description": "[RESOURCE_DESCRIPTION]",
                        "relevance": "[RELEVANCE_TO_STUDY_PLAN]"
                    }
                ],
                "assessments": [
                    {
                        "name": "[ASSESSMENT_NAME]",
                        "description": "[ASSESSMENT_DESCRIPTION]",
                        "type": "[ASSESSMENT_TYPE]",
                        "topics_covered": ["[TOPIC_1]", "[TOPIC_2]"]
                    }
                ],
                "prerequisites": ["[PREREQUISITE_1]", "[PREREQUISITE_2]"],
                "difficulty_level": "intermediate",
                "estimated_completion_time": 14.0
            }
        }
