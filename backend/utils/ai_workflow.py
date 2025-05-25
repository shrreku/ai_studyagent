from crewai import Agent, Task, Crew, Process
from crewai.crews.crew_output import CrewOutput
from langchain_openai import ChatOpenAI
import os
import sys
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import logging
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the LLM for DeepSeek V3 via OpenRouter
llm = ChatOpenAI(
    model_name=f"openrouter/{os.getenv('DEEPSEEK_MODEL_NAME', 'deepseek/deepseek-coder')}",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.7,
    max_tokens=16000,  # Increased token limit for more comprehensive analysis
    streaming=True
)

llm2 = ChatOpenAI(
    model_name=f"openrouter/{os.getenv('DEEPSEEK_MODEL_NAME', 'deepseek/deepseek-coder')}",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.1,
    max_tokens=16000,  # Increased token limit for more comprehensive analysis
    streaming=True
)

# Chat Support Agent for interactive study sessions
chat_support_agent = Agent(
    role='AI Study Tutor',
    goal='Provide contextual explanations, answer questions, and offer guidance based on the uploaded study materials and generated study plan.',
    backstory=(
        "You are an interactive AI tutor. Students will ask you questions about concepts from their notes, "
        "seek clarification on topics in their study plan, or ask for help with practice questions. "
        "Your responses must be accurate, contextual, and drawn from the provided materials."
    ),
    llm=llm,  # Using the lower temperature model for more focused responses
    verbose=True,
    allow_delegation=False
)


# --- Define Pydantic Models for Output Validation ---
class CoreConcept(BaseModel):
    name: str = Field(description="Name of the core concept.")
    explanation: str = Field(description="Brief explanation of the core concept.")
    importance: str = Field(description="Importance level: high/medium/low.", default="medium")
    related_concepts: List[str] = Field(description="List of related concepts.", default_factory=list)
    examples: List[str] = Field(description="Examples of the concept.", default_factory=list)
    difficulty_level: str = Field(description="Difficulty level: basic/intermediate/advanced.", default="intermediate")

class Resource(BaseModel):
    title: str = Field(description="Title of the resource.")
    type: str = Field(description="Type of resource (textbook, video, article, etc.).", default="textbook")
    url: Optional[str] = Field(description="URL of the resource if available.", default=None)
    description: str = Field(description="Brief description of the resource.")

class StudyPlanItem(BaseModel):
    topic: str = Field(description="The topic or concept to study.")
    description: str = Field(description="Brief description of what to study.")
    duration_minutes: int = Field(description="Duration in minutes for this study item.")
    resource: List[Resource] = Field(description="List of resources or materials to use.", default_factory=list)
    is_completed: bool = Field(description="Whether this item has been completed.", default=False)
    learning_objectives: List[str] = Field(description="Learning objectives for this item.", default_factory=list)
    priority: str = Field(description="Priority level: high/medium/low.", default="medium")

class DailySchedule(BaseModel):
    day: int = Field(description="Day number in the study plan.")
    date: Optional[str] = Field(description="Optional date for the study day.", default=None)
    focus_area: str = Field(description="Main focus area for this day.")
    study_item: List[StudyPlanItem] = Field(description="List of study items for this day.")
    summary: str = Field(description="Brief summary of the day's study goals.")
    learning_goals: List[str] = Field(description="Learning goals for this day.", default_factory=list)
    review_topics: List[str] = Field(description="Topics to review from previous days.", default_factory=list)

class StructuredStudyPlanOutput(BaseModel):
    overall_goal: str = Field(description="The main objective of the study plan.")
    total_study_days: int = Field(description="Total number of study days.")
    hours_per_day: float = Field(description="Number of study hours per day.")
    core_concepts: List[CoreConcept] = Field(description="List of core concepts to be covered.")
    daily_schedules: List[DailySchedule] = Field(description="Detailed daily study schedules.")
    general_tips: List[str] = Field(description="General study tips and strategies.", default_factory=list)

# Preview Study Plan model - follows the format from star_plan_20250524_192631.json
class PreviewStudyPlan(BaseModel):
    overall_goal: str = Field(description="The main objective of the study plan.")
    total_study_day: int = Field(description="Total number of study days.")
    hour_per_day: float = Field(description="Number of study hours per day.")
    core_concepts: List[CoreConcept] = Field(description="List of core concepts to be covered.")
    daily_schedule: List[DailySchedule] = Field(description="Detailed daily study schedules.")
    general_tips: List[str] = Field(description="General study tips and strategies.", default_factory=list)

# Study Plan Template
STUDY_PLAN_TEMPLATE = """# Study Plan: {subject}

## Overview
{overview}

## Key Concepts
{key_concepts}

## Daily Schedule
{daily_schedule}

## Study Tips
{study_tips}
"""

def create_study_plan_agent() -> Agent:
    """Create the study plan agent."""
    return Agent(
        role="Expert Study Planner",
        goal="Create a detailed study plan with clear structure and comprehensive coverage",
        backstory=(
            "You are an expert study planner with years of experience in educational psychology "
            "and curriculum development. You excel at creating personalized study plans "
            "that maximize learning efficiency while balancing comprehension and retention. "
            "You are particularly skilled at identifying core concepts, creating logical daily schedules, "
            "and providing practical learning resources."
        ),
        llm=llm,
        verbose=True
    )

def create_study_plan_task(agent: Agent, materials: str, days: int, hours_per_day: int, questions: str = None):
    """
    Create a task for generating a study plan.
    
    Args:
        agent: The agent to assign the task to
        materials: The study materials to base the plan on
        days: Number of days for the study plan
        hours_per_day: Hours per day to study
        questions: Optional questions to focus on during study
        
    Returns:
        Task: A CrewAI Task object for the study plan generation
    """
    task_desc = (
        f"Create a detailed study plan overview based on the following materials and constraints.\n"
        f"Study Duration: {days} days, {hours_per_day} hours per day\n\n"
        f"Study Materials (Notes):\n```\n{materials}\n```\n\n"
    )
    
    if questions:
        task_desc += f"Study Questions:\n```\n{questions}\n```\n\n"
    
    task_desc += (
        f"Provide a structured overview of a study plan with the following sections:\n\n"
        f"1. OVERVIEW: A brief paragraph describing the overall goal and approach of the study plan.\n\n"
        f"2. CORE CONCEPTS: List 5-10 core concepts that are essential to understand, with a brief explanation of each.\n\n"
        f"3. DAILY BREAKDOWN: For each of the {days} days, provide:\n"
        f"   - Day focus area/theme\n"
        f"   - 3-5 main topics to study\n"
        f"   - Estimated time allocation (total should be {hours_per_day} hours per day)\n\n"
        f"4. KEY FORMULAS: If applicable, list 5-10 important formulas that should be memorized.\n\n"
        f"5. STUDY TIPS: Provide 3-5 general tips for studying this material effectively.\n\n"
        f"This overview will be shown to the user before generating the full structured plan.\n\n"
        f"ALSO provide a simplified JSON structure with the key information that will help a structurer agent create a full plan:\n"
        f"```json\n"
        f"{{\n"
        f"  \"overall_goal\": \"[concise goal statement]\",\n"
        f"  \"core_concepts\": [\n"
        f"    {{\n"
        f"      \"name\": \"[concept name]\",\n"
        f"      \"explanation\": \"[brief explanation]\",\n"
        f"      \"importance\": \"[high/medium/low]\"\n"
        f"    }}\n"
        f"  ],\n"
        f"  \"daily_focus\": [\n"
        f"    {{\n"
        f"      \"day\": 1,\n"
        f"      \"focus_area\": \"[main focus]\",\n"
        f"      \"topics\": [\"[topic 1]\", \"[topic 2]\"],\n"
        f"      \"subtopics\": {{\"[topic 1]\": [\"[subtopic 1.1]\", \"[subtopic 1.2]\"]}}\n"
        f"    }}\n"
        f"  ],\n"
        f"  \"key_formulas\": [\n"
        f"    {{\n"
        f"      \"name\": \"[formula name]\",\n"
        f"      \"formula\": \"[formula]\",\n"
        f"      \"description\": \"[what it's used for]\"\n"
        f"    }}\n"
        f"  ]\n"
        f"}}\n"
        f"```\n\n"
        f"Make the overview engaging, informative, and well-structured to help the user understand the learning journey. "
        f"Extract as much relevant information as possible from the study materials including summaries of topics, "
        f"subtopics, key formulas, key concepts, and any other information that would be helpful for creating a "
        f"comprehensive study plan."
    )
    
    return Task(
        description=task_desc,
        agent=agent,
        expected_output=(
            "A comprehensive study plan in markdown format with clear sections for overview, "
            "key concepts, daily schedule, and study tips."
        )
    )

def create_study_plan_structurer_agent() -> Agent:
    """Create the study plan structurer agent."""
    return Agent(
        role="Study Plan Structurer",
        goal="Convert the study plan into a structured JSON format",
        backstory=(
            "You are an expert at converting natural language study plans into "
            "structured data formats while maintaining all important information."
        ),
        llm=llm2,
        verbose=True
    )

def create_structuring_task(agent: Agent, study_plan_text: str) -> Task:
    """Create a task for structuring the study plan."""
    return Task(
        description=(
            f"Convert the following study plan into a structured JSON format. "
            f"Extract all key information including daily schedules, topics, and study items.\n\n"
            f"Study Plan:\n```\n{study_plan_text}\n```\n\n"
            f"Your response MUST be a valid JSON object with no additional text. "
            f"Do not include markdown formatting in your response. "
            f"The JSON should match the exact field names from the input: "
            f"'overall_goal', 'total_study_day', 'hour_per_day', 'core_concepts', 'daily_schedule', 'general_tips'."
        ),
        agent=agent,
        expected_output=(
            "A structured JSON object containing all the study plan details, "
            "including daily schedules, topics, and study items."
        ),
        output_pydantic=StructuredStudyPlanOutput
    )

async def generate_preview_study_plan(
    study_materials_text: str,
    study_duration_days: int,
    study_hours_per_day: int,
    questions_text: str = None
) -> Dict[str, Any]:
    """
    Generate a preview study plan using the AI agent.
    
    Args:
        study_materials_text: The study materials to base the plan on
        study_duration_days: Number of days for the study plan
        study_hours_per_day: Number of hours per day for studying
        questions_text: Optional questions to include in the study plan
        
    Returns:
        dict: A structured preview study plan following the PreviewStudyPlan format
    """
    try:
        logger.info(f"Generating preview study plan for {study_duration_days} days, {study_hours_per_day} hours/day")
        
        # Create the study plan agent and task
        study_plan_agent = create_study_plan_agent()
        
        # Prepare materials section with both notes and questions if available
        materials_section = f"Study Materials (Notes):\n```\n{study_materials_text}\n```\n"
        
        # Add questions section if questions are provided
        if questions_text and len(questions_text.strip()) > 0:
            materials_section += f"\nStudy Questions:\n```\n{questions_text}\n```\n"
            logger.info("Including questions text in study plan generation")
        
        # Build a task description that focuses on generating a human-readable overview
        # and extracting comprehensive information for the structurer agent
        task_description = f"""# Agent: Expert Study Planner
## Task: Create a detailed study plan overview based on the following materials and constraints.
Study Duration: {study_duration_days} days, {study_hours_per_day} hours per day

{materials_section}

Provide a structured overview of a study plan with the following sections:

1. OVERVIEW: A detailed paragraph describing the overall goal and approach of the study plan.

2. CORE CONCEPTS: List 5-10 core concepts that are essential to understand, with a brief explanation of each, their importance, and related concepts.

3. DAILY BREAKDOWN: For each of the {study_duration_days} days, provide:
   - Day focus area/theme
   - 3-5 main topics to study
   - Important subtopics for each main topic
   - Estimated time allocation (total should be {study_hours_per_day} hours per day)

4. KEY FORMULAS: If applicable, list 5-10 important formulas that should be memorized, with explanations of their application.

5. STUDY TIPS: Provide 3-5 general tips for studying this material effectively.

This overview will be shown to the user before generating the full structured plan.

EXTRACT as much relevant information as possible from the study materials including summaries of topics, subtopics, key formulas, key concepts, and any other information that would be helpful for creating a comprehensive study plan.

This overview will be shown to the user before generating the full structured plan.

ALSO provide a simplified JSON structure with the key information that will help a structurer agent create a full plan:
```json
{{
  "overall_goal": "[concise goal statement]",
  "core_concepts": [
    {{
      "name": "[concept name]",
      "explanation": "[brief explanation]",
      "importance": "[high/medium/low]",
      "related_concepts": ["[related concept 1]", "[related concept 2]"],
      "examples": ["[example 1]", "[example 2]"]
    }}
  ],
  "daily_focus": [
    {{
      "day": 1,
      "focus_area": "[main focus]",
      "topics": ["[topic 1]", "[topic 2]"],
      "subtopics": {{
        "[topic 1]": ["[subtopic 1.1]", "[subtopic 1.2]"],
        "[topic 2]": ["[subtopic 2.1]", "[subtopic 2.2]"]
      }},
      "time_allocation": {{
        "[topic 1]": "[time in minutes]",
        "[topic 2]": "[time in minutes]"
      }}
    }}
  ],
  "key_formulas": [
    {{
      "name": "[formula name]",
      "formula": "[formula]",
      "description": "[what it's used for]",
      "application": "[example application]"
    }}
  ],
  "study_tips": [
    "[study tip 1]",
    "[study tip 2]",
    "[study tip 3]"
  ]
}}
```

Make the overview engaging, informative, and well-structured to help the user understand the learning journey.
"""
        
        study_plan_task = Task(
            description=task_description,
            agent=study_plan_agent,
            expected_output=(
                "A comprehensive study plan in the exact JSON format specified, with all fields properly populated."
            )
        )
        
        # Create and run the study plan crew
        study_plan_crew = Crew(
            agents=[study_plan_agent],
            tasks=[study_plan_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Run the crew and get the result
        crew_output = study_plan_crew.kickoff()
        
        if isinstance(crew_output, CrewOutput):
            # If we got a valid crew output, process it
            full_output = crew_output.raw
            logger.info(f"Successfully generated preview study plan, output length: {len(full_output)}")
            
            # Extract the overview text and JSON part
            try:
                # Extract human-readable overview - everything before the JSON block
                import re
                overview_text = re.sub(r'```json\s*\{[\s\S]*?\}\s*```\s*$', '', full_output).strip()
                
                # Extract JSON content between triple backticks
                json_match = re.search(r'```(?:json)?\s*({[\s\S]*?})\s*```', full_output)
                
                # If we found JSON content, parse it
                simplified_json = {}
                if json_match:
                    json_text = json_match.group(1)
                    simplified_json = json.loads(json_text.strip())
                    logger.info("Successfully extracted JSON data from agent output")
                
                # Save the full output and extracted data for debugging
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                os.makedirs('test_data', exist_ok=True)
                
                # Save the full output
                with open(f'test_data/preview_full_output_{timestamp}.txt', 'w') as f:
                    f.write(full_output)
                
                # Save the extracted JSON
                if simplified_json:
                    with open(f'test_data/preview_simplified_json_{timestamp}.json', 'w') as f:
                        json.dump(simplified_json, f, indent=2)
                
                # Create a plan object that contains both the overview and the simplified JSON
                # This will be displayed to the user in the preview page
                preview_plan = {
                    "overview": overview_text,
                    "overall_goal": simplified_json.get("overall_goal", "Master the subject material"),
                    "core_concepts": simplified_json.get("core_concepts", []),
                    "daily_focus": simplified_json.get("daily_focus", []),
                    "key_formulas": simplified_json.get("key_formulas", []),
                    "study_days": study_duration_days,
                    "hours_per_day": study_hours_per_day
                }
                
                return {
                    "status": "success",
                    "preview_plan": preview_plan,
                    "raw_plan": full_output,  # Pass the full output for structuring later
                    "simplified_json": simplified_json  # Pass the simplified JSON for the structurer
                }
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Failed to parse data from crew output: {e}")
                # Return the raw text for troubleshooting, but still provide the overview text if available
                overview_text = full_output
                
                # Try to clean up the overview by removing any partial JSON
                json_start = overview_text.find('```json')
                if json_start > 0:
                    overview_text = overview_text[:json_start].strip()
                
                return {
                    "status": "partial_success",
                    "error": "Failed to parse JSON data",
                    "details": str(e),
                    "preview_plan": {
                        "overview": overview_text,
                        "study_days": study_duration_days,
                        "hours_per_day": study_hours_per_day
                    },
                    "raw_plan": full_output
                }
        else:
            logger.error(f"Unexpected crew output type: {type(crew_output)}")
            return {
                "status": "error",
                "error": "Failed to generate preview plan",
                "details": f"Unexpected output type: {type(crew_output)}"
            }
    except Exception as e:
        error_traceback = traceback.format_exc()
        error_msg = f"Error in generate_preview_study_plan: {str(e)}\n\nTraceback:\n{error_traceback}"
        logger.error(error_msg)
        return {
            "status": "error", 
            "error": "An unexpected error occurred", 
            "details": error_msg
        }

def run_study_plan_crew(
    materials_text: str,
    study_duration_days: str,
    study_hours_per_day: str,
    notes: str = None,
    questions: str = None
) -> Dict[str, Any]:
    """Run the simplified study plan generation workflow.
    
    Args:
        materials_text: The study materials to base the plan on
        study_duration_days: Number of days for the study plan
        study_hours_per_day: Number of study hours per day
        notes: Optional additional notes
        questions: Optional questions to answer

    Returns:
        dict: Contains the generated study plan and any errors
    """
    try:
        # Create agents
        study_plan_agent = create_study_plan_agent()
        structurer_agent = create_study_plan_structurer_agent()
        
        # Combine all input materials
        combined_materials = materials_text
        if notes:
            combined_materials += f"\n\nAdditional Notes:\n{notes}"
        if questions:
            combined_materials += f"\n\nQuestions to Answer:\n{questions}"
        
        # Create tasks
        generate_task = create_study_plan_task(
            agent=study_plan_agent,
            materials=combined_materials,
            days=int(study_duration_days),
            hours_per_day=float(study_hours_per_day)
        )
        
        # Create and execute the crew
        crew = Crew(
            agents=[study_plan_agent, structurer_agent],
            tasks=[generate_task],
            process=Process.sequential,
            verbose=True
        )
        
        logger.info("Starting study plan generation...")
        result = crew.kickoff()
        
        # If we have a text result, structure it
        if isinstance(result, str):
            structure_task = create_structuring_task(
                agent=structurer_agent,
                study_plan_text=result
            )
            
            structure_crew = Crew(
                agents=[structurer_agent],
                tasks=[structure_task],
                process=Process.sequential,
                verbose=True
            )
            
            logger.info("Structuring study plan...")
            structured_result = structure_crew.kickoff()
            
            if hasattr(structured_result, 'dict'):
                return {
                    "status": "success",
                    "study_plan": result,
                    "structured_plan": structured_result.dict()
                }
        
        return {
            "status": "success",
            "study_plan": str(result),
            "structured_plan": None
        }
        
    except Exception as e:
        error_msg = f"Error in study plan generation: {str(e)}"
        logger.error(error_msg, exc_info=True)
        import traceback
        return {
            "status": "error",
            "error": "Generation Error",
            "details": error_msg,
            "traceback": traceback.format_exc()
        }
    # Create the structuring task (will be used in full mode)
    task_structure_plan = create_study_plan_structuring_task(
        agent=study_plan_structurer_agent,
        text_study_plan="{text_plan_output}", # Placeholder, will be replaced by actual output
        output_model=StructuredStudyPlanOutput
    )

    # Create and execute the crew for part 1 (always needed)
    study_crew_part1 = Crew(
        agents=[topic_prioritizer_agent, study_plan_generator_agent],
        tasks=[task_prioritize, task_generate_plan],
        process=Process.sequential,
        verbose=True
    )

    logger.info("Kicking off Part 1 of the study crew (Prioritization & Text Plan Generation)...")
    part1_result = study_crew_part1.kickoff(inputs={
        'original_materials': study_materials,
        'study_duration_days': study_duration_days,
        'study_hours_per_day': study_hours_per_day
    })

    # Extract outputs from Part 1
    # Robustly extract topics_json_string from task_prioritize.output
    topics_json_string = None
    raw_topics_output = task_prioritize.output
    
    if isinstance(raw_topics_output, CrewOutput):
        # If output is CrewOutput, try to get the raw string or export
        if raw_topics_output.raw:
            topics_json_string = raw_topics_output.raw
        elif hasattr(raw_topics_output, 'pydantic_output') and raw_topics_output.pydantic_output is not None:
            topics_json_string = raw_topics_output.pydantic_output.model_dump_json()
    elif hasattr(raw_topics_output, 'model_dump_json'):
        # If it's a Pydantic model directly
        topics_json_string = raw_topics_output.model_dump_json()
    elif isinstance(raw_topics_output, str):
        topics_json_string = raw_topics_output
    
    if not topics_json_string:
        logger.error(f"Failed to extract topics JSON from task_prioritize.output: {raw_topics_output}")
        return {"error": "AI Workflow Error", "details": "Failed to extract topics list from the prioritization task."}
    
    # Get the text plan output
    text_plan_output = task_generate_plan.output
    if isinstance(text_plan_output, CrewOutput):
        if text_plan_output.raw:
            actual_text_plan = text_plan_output.raw
        else:
            actual_text_plan = str(text_plan_output)
    else:
        actual_text_plan = str(text_plan_output)
    
    if not actual_text_plan or not actual_text_plan.strip():
        logger.error(f"Failed to get a valid text plan from the generator. Output: {actual_text_plan}")
        return {"error": "AI Workflow Error", "details": "Failed to generate a valid text study plan."}
    
    # For preview mode, we're done
    if stage == "preview":
        logger.info(f"Crew Part 1 execution finished. Preview mode completed.")
        return {
            "text_plan": actual_text_plan,
            "topic_list_json": topics_json_string
        }

        # Log the completion of part 1
        logger.info("Crew Part 1 execution finished successfully.")

    # For full mode, we need to generate the structured plan
    logger.info("Generating structured study plan...")
    
    # Update the structuring task with the actual text plan
    task_structure_plan.description = task_structure_plan.description.replace("{text_plan_output}", actual_text_plan)
    
    # Update checksum in description
    new_checksum = hashlib.sha256(actual_text_plan.encode('utf-8')).hexdigest()
    checksum_part = task_structure_plan.description.split("checksum of the input text plan is ")[1].split(".")[0]
    task_structure_plan.description = task_structure_plan.description.replace(checksum_part, new_checksum)

    # Create and execute the crew for part 2 (structuring)
    study_crew_part2 = Crew(
        agents=[study_plan_structurer_agent],
        tasks=[task_structure_plan],
        process=Process.sequential,
        verbose=True
    )

    logger.info("Kicking off the study crew (Part 2: Plan Structuring)...")
    structured_plan_output_obj = study_crew_part2.kickoff()
    logger.info(f"Crew Part 2 execution finished. Raw output type: {type(structured_plan_output_obj)}. Output: {str(structured_plan_output_obj)[:200]}...")

    # Log the start of part 2
    logger.info("Starting Part 2: Generating structured study plan...")

    # Process the structured plan output
    structured_plan = None
    if structured_plan_output_obj:
        if isinstance(structured_plan_output_obj, BaseModel):
            structured_plan = json.loads(structured_plan_output_obj.model_dump_json())
        elif isinstance(structured_plan_output_obj, CrewOutput):
            if hasattr(structured_plan_output_obj, 'pydantic_output') and structured_plan_output_obj.pydantic_output is not None:
                structured_plan = json.loads(structured_plan_output_obj.pydantic_output.model_dump_json())
            elif hasattr(structured_plan_output_obj, 'raw') and isinstance(structured_plan_output_obj.raw, str):
                try:
                    structured_plan = json.loads(structured_plan_output_obj.raw)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse structured plan JSON: {e}. Raw: {structured_plan_output_obj.raw[:200]}...")
                    return {"error": "Invalid JSON in structured plan", "details": f"Failed to parse JSON: {e}"}
        elif hasattr(structured_plan_output_obj, 'model_dump_json'):
            structured_plan = json.loads(structured_plan_output_obj.model_dump_json())
        elif isinstance(structured_plan_output_obj, str):
            try:
                structured_plan = json.loads(structured_plan_output_obj)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse structured plan string as JSON: {e}")
                return {"error": "Invalid JSON in structured plan", "details": f"Failed to parse string as JSON: {e}"}
    
    if not structured_plan:
        logger.error(f"Failed to extract structured plan from output: {structured_plan_output_obj}")
        return {"error": "AI Workflow Error", "details": "Failed to generate a valid structured study plan."}
    
    # Parse the topics JSON if it's a string
    topics_data = None
    try:
        if isinstance(topics_json_string, str):
            topics_data = json.loads(topics_json_string)
        else:
            topics_data = topics_json_string
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse topics JSON: {e}. JSON: {topics_json_string[:200]}...")
        return {"error": "Invalid topics JSON", "details": f"Failed to parse topics: {e}"}
    
    # Log completion of the structured plan generation
    logger.info("Successfully generated structured study plan.")
    
    # Log the successful generation with sample data
    logger.info(f"Successfully generated. Topics JSON (first 200): {topics_json_string[:200]}... Text Plan (first 200): {actual_text_plan[:200]}...")
    
    try:
        # Convert the structured plan to match frontend StudyPlan interface
        if structured_plan and "error" not in structured_plan:
            # Transform the structured plan to match frontend interface
            study_plan_response = {
                "overallGoal": structured_plan.get("title", "Complete study plan"),
                "totalStudyDays": int(study_duration_days),
                "hoursPerDay": float(study_hours_per_day),
                "keyConcepts": [
                    {
                        "concept": concept.get("name", ""),
                        "explanation": concept.get("explanation", "")
                    } for concept in structured_plan.get("core_concepts", [])
                ],
                "dailyBreakdown": [
                    {
                        "day": day_plan.get("day", 1),
                        "daySummary": day_plan.get("focus", ""),
                        "items": [
                            {
                                "topic": activity,
                                "details": f"Focus on {activity}",
                                "estimatedTimeHours": float(study_hours_per_day) / max(1, len(day_plan.get("activities", [activity]))),
                                "resources": []
                            } for activity in day_plan.get("activities", [day_plan.get("focus", "Study")])
                        ]
                    } for day_plan in structured_plan.get("condensed_study_plan", [])
                ],
                "keyFormulas": [
                    {
                        "formula_name": formula.get("formula", ""),
                        "description": formula.get("description", ""),
                        "usage_context": "Study reference"
                    } for formula in structured_plan.get("key_formulas", [])
                ],
                "generalTips": [
                    "Review key concepts daily",
                    "Practice problems regularly",
                    "Take breaks between study sessions",
                    structured_plan.get("conclusion", "Stay consistent with your study schedule")
                ]
            }
            return study_plan_response
        else:
            # Fallback: create a basic study plan structure
            return {
                "overallGoal": "Complete your study plan",
                "totalStudyDays": int(study_duration_days),
                "hoursPerDay": float(study_hours_per_day),
                "keyConcepts": [
                    {
                        "concept": "Core Study Material",
                        "explanation": "Focus on understanding the main concepts from your uploaded materials"
                    }
                ],
                "dailyBreakdown": [
                    {
                        "day": i + 1,
                        "daySummary": f"Day {i + 1} Study Session",
                        "items": [
                            {
                                "topic": "Study Session",
                                "details": "Review uploaded materials and practice problems",
                                "estimatedTimeHours": float(study_hours_per_day),
                                "resources": []
                            }
                        ]
                    } for i in range(int(study_duration_days))
                ],
                "keyFormulas": [],
                "generalTips": [
                    "Review your notes regularly",
                    "Practice active recall",
                    "Take regular breaks"
                ]
            }

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        error_msg = f"Error in run_study_plan_crew: {str(e)}\n\nTraceback:\n{error_traceback}"
        logger.error(error_msg)
        return {
            "error": "An unexpected error occurred in AI workflow", 
            "details": error_msg,
            "type": type(e).__name__
        }
async def structure_raw_plan(raw_plan_text: str, simplified_json: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Process a raw text study plan into a structured format for the frontend.
    
    Args:
        raw_plan_text: The raw study plan text to structure
        simplified_json: Optional simplified JSON data to help with structuring
        
    Returns:
        dict: A structured study plan in the format expected by the frontend,
              or an error message if processing fails
    """
    try:
        logger.info(f"Structuring raw plan of length {len(raw_plan_text)} characters")
        
        # Create the study plan structurer agent and task
        structurer_agent = create_study_plan_structurer_agent()
        
        # Create a template for the full study plan structure
        template_path = os.path.join(os.path.dirname(__file__), '../templates/study_plan_template.json')
        template_content = "{}"
        
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
        except Exception as e:
            logger.warning(f"Could not read template file: {e}")
        
        # Extract information from simplified_json if available
        context = """Here's the overview of the study plan:

""" + raw_plan_text
        
        if simplified_json:
            # Add the simplified JSON to provide additional context
            context += "\n\nHere's the simplified data extracted from the overview:\n"
            context += json.dumps(simplified_json, indent=2)

        # Create a task description that instructs the agent to create a structured plan
        structuring_task = Task(
            description=(
                f"You are an AI study plan structurer. Your task is to create a detailed, structured study plan in JSON format "
                f"based on the following overview and simplified data. The final output must strictly follow the JSON template provided.\n\n"
                f"{context}\n\n"
                f"Use this template format for your response (fill in the placeholders with actual content):\n"
                f"```json\n{template_content}\n```\n\n"
                f"Make sure your response is ONLY the valid JSON with no additional text.\n"
                f"The JSON must include:\n"
                f"1. An overall goal\n"
                f"2. The number of study days and hours per day\n"
                f"3. At least 3 core concepts with explanations, importance levels, and related concepts\n"
                f"4. A daily schedule with focus areas, study items, and timing that matches the days and hours\n"
                f"5. General tips for effective studying\n"
            ),
            expected_output=(
                "A valid JSON document that strictly follows the template structure. "
                "It should include all required fields populated with relevant content extracted from the study materials."
            ),
            agent=structurer_agent
        )
        
        # Create and run the structuring crew
        structuring_crew = Crew(
            agents=[structurer_agent],
            tasks=[structuring_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Run the crew and get the result
        crew_output = structuring_crew.kickoff()
        
        if isinstance(crew_output, CrewOutput):
            # If we got a valid crew output, parse it to get the structured plan
            structured_text = crew_output.raw
            logger.info(f"Successfully generated structured plan, output length: {len(structured_text)}")
            
            # Extract JSON from the agent's response if it's wrapped in markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*({[\s\S]*?})\s*```', structured_text)
            if json_match:
                structured_text = json_match.group(1)
            
            try:
                # Import the adapter utility for proper transformation
                from utils.adapter_utils import transform_backend_to_frontend
                
                # Parse the structured output as JSON
                plan_data = json.loads(structured_text)
                
                # Save the structured data for debugging
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                os.makedirs('test_data', exist_ok=True)
                with open(f'test_data/structured_input_{timestamp}.json', 'w') as f:
                    json.dump(plan_data, f, indent=2)
                
                # Use the adapter utils to transform the data to frontend format
                transformed_plan = transform_backend_to_frontend(plan_data)
                
                # Save the transformed data for debugging
                with open(f'test_data/structured_output_{timestamp}.json', 'w') as f:
                    json.dump(transformed_plan, f, indent=2)
                
                logger.info("Successfully transformed plan to frontend format")
                return transformed_plan
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse structured plan as JSON: {e}")
                return {
                    "error": "Could not parse structured plan",
                    "details": f"JSON parsing error: {str(e)}",
                    "raw_output": structured_text
                }
        else:
            # Handle the case where we didn't get a valid crew output
            logger.error(f"Unexpected crew output type: {type(crew_output)}")
            return {
                "error": "Unexpected output from structuring agent",
                "details": f"Got {type(crew_output)} instead of CrewOutput"
            }
    except Exception as e:
        logger.error(f"Error in structuring raw plan: {e}")
        return {
            "error": "Failed to structure study plan",
            "details": str(e)
        }

if __name__ == '__main__':
    if not os.getenv("OPENROUTER_API_KEY") or not os.getenv("DEEPSEEK_MODEL_NAME"):
        print("Error: Please set OPENROUTER_API_KEY and DEEPSEEK_MODEL_NAME environment variables")
        exit(1)
        
    test_materials = """
    Linear Algebra
    - Vectors and spaces
    - Matrix transformations
    - Eigenvalues and eigenvectors
    - Dot products and cross products
    - Linear transformations
    
    Calculus
    - Limits and continuity
    - Derivatives and differentiation rules
    - Integrals and the Fundamental Theorem of Calculus
    - Applications of derivatives and integrals
    - Multivariable calculus
    
    Probability and Statistics
    - Basic probability concepts
    - Random variables and distributions
    - Hypothesis testing
    - Statistical inference
    - Regression analysis
    """
    
    result = run_study_plan_crew(
        materials_text=test_materials,
        study_duration_days="14",
        study_hours_per_day="2",
        notes="Focus on practical applications and problem-solving.",
        questions="What are the most important concepts to focus on for a machine learning course?"
    )
    
    if result.get("status") == "success":
        print("\n=== Study Plan ===\n")
        print(result["study_plan"])
        print("\n=== Structured Plan ===\n")
        print(json.dumps(result.get("structured_plan"), indent=2, ensure_ascii=False))
    else:
        print("\n=== Error ===\n")
        print(f"Error: {result.get('error')}")
        print(f"Details: {result.get('details')}")
        if "traceback" in result:
            print("\nTraceback:")
            print(result["traceback"])