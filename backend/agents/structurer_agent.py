import json
import os
import re
import logging
from typing import Dict, Any, List, Optional
from langchain_community.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from models.study_plan_models import StructuredStudyPlan
from utils.file_utils import save_structured_output
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class StructurerAgent:
    """
    Agent responsible for structuring raw study plans into a consistent JSON format
    that follows the StructuredStudyPlan Pydantic model.
    """
    
    def __init__(self, model_name: str = "deepseek/deepseek-chat-v3-0324:free", temperature: float = 0.7):
        """
        Initialize the structurer agent.
        
        Args:
            model_name: The model to use (default: deepseek/deepseek-chat-v3-0324:free via OpenRouter)
            temperature: The temperature for generation
        """
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not found")
            
        # Initialize with OpenRouter
        self.model = ChatOpenAI(
            model=model_name,
            temperature=temperature,  # Use the provided temperature for more creative responses
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=openrouter_api_key,
            max_tokens=4000  # Reduced max tokens to avoid truncation issues
        )
        self.output_parser = PydanticOutputParser(pydantic_object=StructuredStudyPlan)
        
        # Load the template
        template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     "templates", "study_plan_template.json")
        try:
            with open(template_path, "r") as f:
                self.template = json.load(f)
                logger.info("Successfully loaded study plan template from %s", template_path)
        except FileNotFoundError:
            # Fallback to a basic template if file not found
            logger.warning("Template file not found at %s, using fallback template", template_path)
            self.template = {
                "overall_goal": "Master the fundamental concepts of [SUBJECT], focusing on [KEY_AREA_1], [KEY_AREA_2], and [KEY_AREA_3].",
                "total_study_day": "[TOTAL_STUDY_DAYS]",
                "hour_per_day": "[HOURS_PER_DAY]",
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
            
        # Create the system prompt with instructions and format requirements
        self.system_prompt = self._create_system_prompt()
        
    def _create_system_prompt(self):
        """Create the system prompt for the structurer agent."""
        # Convert the template to a pretty-printed JSON string
        template_json = json.dumps(self.template, indent=2)
        
        # Create the system prompt
        return f"""You are an expert study plan structurer. Your task is to convert a raw study plan into a structured JSON format.
        
        The output must strictly follow this JSON template structure:
        ```json
        {template_json}
        ```
        
        CRITICAL REQUIREMENTS:
        1. You MUST preserve the exact number of study days provided in the user input
        2. You MUST preserve the exact number of hours per day provided in the user input
        3. NEVER modify the total_study_day or hour_per_day values under any circumstances
        4. If the raw plan has a different timeline, adjust the content to fit the required days/hours
        
        Important rules:
        1. Follow the EXACT structure of the template, including all fields and nested objects.
        2. Replace placeholder values (like [CONCEPT_NAME]) with appropriate content from the raw study plan.
        3. Maintain the same data types as shown in the template.
        4. Ensure all JSON is valid and properly formatted.
        5. Be comprehensive but concise in filling out each section.
        6. If information for a field is not available in the raw plan, make a reasonable inference based on the context.
        7. Your output should ONLY contain the JSON object, nothing else.
        8. Keep your response within reasonable length to avoid truncation.
        9. Limit the number of study items per day to 3-4 maximum.
        10. Limit the number of core concepts to 5 maximum.
        
        Your response must be a single, valid JSON object that follows the template structure exactly."""

    def _enforce_user_constraints(self, structured_plan: Dict[str, Any], user_days: int = None, user_hours: float = None, is_sync: bool = False) -> Dict[str, Any]:
        """
        Enforce user-specified days and hours in the structured plan.
        
        Args:
            structured_plan: The structured plan to enforce constraints on
            user_days: User-specified number of study days
            user_hours: User-specified hours per day
            is_sync: Whether this is being called from the sync method
            
        Returns:
            The structured plan with enforced constraints
        """
        sync_label = " (sync)" if is_sync else ""
        
        if user_days is not None:
            logger.info(f"Enforcing user-specified days: {user_days}{sync_label}")
            structured_plan['total_study_day'] = user_days
            
            # Make sure we have exactly the right number of days in daily_schedule
            if 'daily_schedule' in structured_plan and structured_plan['daily_schedule']:
                if len(structured_plan['daily_schedule']) > user_days:
                    # Truncate to the requested number of days
                    logger.info(f"Truncating from {len(structured_plan['daily_schedule'])} to {user_days} days{sync_label}")
                    structured_plan['daily_schedule'] = structured_plan['daily_schedule'][:user_days]
                elif len(structured_plan['daily_schedule']) < user_days:
                    # Add additional days if needed
                    logger.info(f"Adding days to reach {user_days} days (current: {len(structured_plan['daily_schedule'])}){sync_label}")
                    last_day = structured_plan['daily_schedule'][-1] if structured_plan['daily_schedule'] else None
                    
                    while len(structured_plan['daily_schedule']) < user_days:
                        day_num = len(structured_plan['daily_schedule']) + 1
                        # Create a new day based on the last day or a template
                        if last_day:
                            new_day = dict(last_day)
                            new_day['day'] = day_num
                            new_day['focus_area'] = f"Additional study for day {day_num}"
                            new_day['summary'] = f"Additional study day {day_num}"
                        else:
                            new_day = {
                                "day": day_num,
                                "date": None,
                                "focus_area": f"Study day {day_num}",
                                "study_item": [],
                                "summary": f"Study activities for day {day_num}"
                            }
                        structured_plan['daily_schedule'].append(new_day)
        
        if user_hours is not None:
            logger.info(f"Enforcing user-specified hours per day: {user_hours}{sync_label}")
            structured_plan['hour_per_day'] = user_hours
            
        return structured_plan
        
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from text using multiple parsing strategies.
        
        Args:
            text: The text to extract JSON from
            
        Returns:
            The extracted JSON as a dictionary, or None if extraction fails
        """
        # First, try to parse the entire response as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.debug("Direct JSON parsing failed, trying pattern matching")
        
        # Try to extract JSON using regex pattern matching
        try:
            # Look for JSON between triple backticks
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
            if json_match:
                json_str = json_match.group(1).strip()
                return json.loads(json_str)
            
            # Try to find JSON without backticks
            json_match = re.search(r'(\{[\s\S]*\})', text)
            if json_match:
                json_str = json_match.group(1).strip()
                return json.loads(json_str)
        except Exception as pattern_error:
            logger.debug(f"Pattern matching parsing failed: {str(pattern_error)}")
        
        # If all parsing attempts fail, return None
        return None
        
    async def structure_plan(self, raw_plan: str, save_output: bool = True, output_filename: str = None, 
                            user_days: int = None, user_hours: float = None) -> Dict[str, Any]:
        """
        Structure a raw study plan into a structured JSON format.
        
        Args:
            raw_plan: The raw study plan to structure
            save_output: Whether to save the output
            output_filename: The filename to save the output to (without extension)
            user_days: Explicitly specified number of study days
            user_hours: Explicitly specified hours per day
        
        Returns:
            The structured study plan as a dictionary
        """
        try:
            # Log the explicitly passed user days and hours if provided
            if user_days is not None:
                logger.info(f"Using explicitly specified days: {user_days}")
            if user_hours is not None:
                logger.info(f"Using explicitly specified hours per day: {user_hours}")
                
            # If not explicitly provided, try to extract from the raw_plan
            if user_days is None or user_hours is None:
                # Extract user_days and user_hours from the raw_plan if present
                user_days_match = re.search(r'\b(\d+)\s*(?:days?|study days)\b', raw_plan, re.IGNORECASE)
                user_hours_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:hours?|hour per day|hours? per day)\b', raw_plan, re.IGNORECASE)
                
                if user_days is None and user_days_match:
                    user_days = int(user_days_match.group(1))
                    logger.info(f"Extracted user-specified days: {user_days}")
                
                if user_hours is None and user_hours_match:
                    user_hours = float(user_hours_match.group(1))
                    logger.info(f"Extracted user-specified hours per day: {user_hours}")
            
            response_text = ""
            structured_plan = None
            error_message = None
            
            # Break down the task into smaller chunks to avoid truncation issues
            # First, generate the core structure with essential fields
            core_prompt = """First, create the core structure of the study plan with these essential fields:
            1. overall_goal
            2. total_study_day
            3. hour_per_day
            4. core_concepts (limit to 5 max)
            5. general_tip
            
            Do not include daily_schedule or key_formulas yet. Keep your response concise and focused.
            Return a valid JSON object with just these fields."""
            
            # Create the messages for the core structure
            core_messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Here is the raw study plan to structure:\n\n{raw_plan}\n\n{core_prompt}")
            ]
            
            # Get the core structure response
            core_response = await self.model.ainvoke(core_messages)
            core_text = core_response.content
            
            # Parse the core structure
            core_structure = self._extract_json(core_text)
            if not core_structure:
                raise ValueError("Failed to generate core structure")
            
            logger.info("Successfully generated core structure")
            
            # Now generate the daily schedule separately
            schedule_prompt = """Now, create only the daily_schedule array for the study plan.
            Limit each day to 3-4 study items maximum to keep the response concise.
            Include focus_area, study_item, summary, learning_goals, and review_topics for each day.
            Return a valid JSON array containing just the daily schedule."""
            
            # Create the messages for the daily schedule
            schedule_messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Here is the raw study plan:\n\n{raw_plan}\n\n{schedule_prompt}")
            ]
            
            # Get the daily schedule response
            schedule_response = await self.model.ainvoke(schedule_messages)
            schedule_text = schedule_response.content
            
            # Parse the daily schedule
            daily_schedule = self._extract_json(schedule_text)
            if not daily_schedule:
                # Try to extract just the array
                array_match = re.search(r'\[\s*\{[\s\S]*?\}\s*\]', schedule_text)
                if array_match:
                    try:
                        daily_schedule = json.loads(array_match.group(0))
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse daily schedule array")
                        daily_schedule = []
                else:
                    logger.warning("Failed to extract daily schedule")
                    daily_schedule = []
            
            # If we got an object with a daily_schedule field, extract it
            if isinstance(daily_schedule, dict) and 'daily_schedule' in daily_schedule:
                daily_schedule = daily_schedule['daily_schedule']
            
            logger.info(f"Successfully generated daily schedule with {len(daily_schedule)} days")
            
            # Finally, generate the key formulas separately
            formulas_prompt = """Finally, create only the key_formulas array for the study plan.
            Include name, formula, description, and usage_context for each formula.
            Return a valid JSON array containing just the key formulas."""
            
            # Create the messages for the key formulas
            formulas_messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Here is the raw study plan:\n\n{raw_plan}\n\n{formulas_prompt}")
            ]
            
            # Get the key formulas response
            formulas_response = await self.model.ainvoke(formulas_messages)
            formulas_text = formulas_response.content
            
            # Parse the key formulas
            key_formulas = self._extract_json(formulas_text)
            if not key_formulas:
                # Try to extract just the array
                array_match = re.search(r'\[\s*\{[\s\S]*?\}\s*\]', formulas_text)
                if array_match:
                    try:
                        key_formulas = json.loads(array_match.group(0))
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse key formulas array")
                        key_formulas = []
                else:
                    logger.warning("Failed to extract key formulas")
                    key_formulas = []
            
            # If we got an object with a key_formulas field, extract it
            if isinstance(key_formulas, dict) and 'key_formulas' in key_formulas:
                key_formulas = key_formulas['key_formulas']
            
            logger.info(f"Successfully generated key formulas with {len(key_formulas)} formulas")
            
            # Combine all parts into the final structured plan
            structured_plan = core_structure
            structured_plan['daily_schedule'] = daily_schedule
            structured_plan['key_formulas'] = key_formulas
            
            # Enforce user constraints
            structured_plan = self._enforce_user_constraints(structured_plan, user_days, user_hours, is_sync=False)
            
            # Combine all responses for logging
            response_text = f"CORE:\n{core_text}\n\nSCHEDULE:\n{schedule_text}\n\nFORMULAS:\n{formulas_text}"
            
            # If we have a structured plan, validate and save it
            if structured_plan:
                try:
                    # Validate against the Pydantic model
                    validated_plan = StructuredStudyPlan(**structured_plan)
                    result = validated_plan.dict()
                    
                    # Save both raw and structured outputs if requested
                    if save_output:
                        logger.info("Saving structured output to test_data directory")
                        raw_path = save_structured_output(
                            {"raw_response": response_text, "structured_output": result},
                            filename=output_filename or "structured_output_raw_and_processed.json",
                            directory="test_data"
                        )
                        
                        # Also save just the structured output in a clean format
                        clean_filename = (output_filename.replace(".json", "_clean.json") 
                                          if output_filename and ".json" in output_filename 
                                          else (output_filename + "_clean.json" if output_filename else "structured_output_clean.json"))
                        clean_path = save_structured_output(
                            result,
                            filename=clean_filename,
                            directory="test_data"
                        )
                        logger.info(f"Saved raw output to {raw_path} and clean output to {clean_path}")
                    
                    return result
                except Exception as validation_error:
                    logger.error(f"Validation error: {str(validation_error)}")
                    error_result = {
                        "error": "Failed to validate structured plan",
                        "details": str(validation_error),
                        "parsed_json": structured_plan,
                        "raw_response": response_text
                    }
                    
                    if save_output:
                        save_structured_output(
                            {"raw_response": response_text, "error": error_result},
                            filename=output_filename or "structured_output_validation_error.json",
                            directory="test_data"
                        )
                    
                    return error_result
            else:
                # If all parsing attempts failed
                error_result = {
                    "error": "Failed to structure the study plan", 
                    "details": error_message or "Unknown parsing error", 
                    "raw_response": response_text
                }
                
                if save_output:
                    save_structured_output(
                        {"raw_response": response_text, "error": error_result},
                        filename=output_filename or "structured_output_parsing_error.json",
                        directory="test_data"
                    )
                
                return error_result
                
        except Exception as e:
            logger.error(f"Error in structurer agent: {str(e)}")
            
            # Try a retry with explicit instructions if we don't have a structured plan yet
            if structured_plan is None:
                try:
                    logger.warning("Initial parsing attempts failed. Trying again with explicit JSON-only instructions.")
                    
                    retry_prompt = f"""
                    Your previous response could not be parsed as valid JSON. Please try again.
                    
                    Here is the raw study plan:
                    
                    {raw_plan}
                    
                    Return ONLY a valid JSON object following the schema. 
                    NO explanations, NO markdown formatting (no ```), NO additional text.
                    Just the raw JSON object starting with {{.
                    
                    Make sure all strings are properly quoted and all JSON syntax is valid.
                    """
                    
                    retry_messages = [
                        SystemMessage(content=self.system_prompt),
                        HumanMessage(content=retry_prompt)
                    ]
                    
                    retry_response = await self.model.ainvoke(retry_messages)
                    retry_text = retry_response.content
                    
                    logger.info("Retry response from structurer agent: %s", retry_text)
                    
                    try:
                        structured_plan = json.loads(retry_text)
                        logger.info("Successfully parsed JSON from retry")
                        response_text = retry_text
                    except json.JSONDecodeError as e:
                        # One last attempt - try to extract any JSON-like content from retry
                        json_pattern = re.search(r'({.*})', retry_text, re.DOTALL)
                        if json_pattern:
                            potential_json = json_pattern.group(1).strip()
                            try:
                                structured_plan = json.loads(potential_json)
                                logger.info("Successfully parsed JSON from retry pattern matching")
                                response_text = retry_text
                            except json.JSONDecodeError as e2:
                                error_message = f"All parsing attempts failed. Final error: {str(e2)}"
                                logger.error(error_message)
                        else:
                            error_message = f"All parsing attempts failed. Final error: {str(e)}"
                            logger.error(error_message)
                            
                    # If we have a structured plan from the retry, validate and return it
                    if structured_plan:
                        try:
                            validated_plan = StructuredStudyPlan(**structured_plan)
                            result = validated_plan.dict()
                            
                            if save_output:
                                logger.info("Saving structured output from retry to test_data directory")
                                raw_path = save_structured_output(
                                    {"raw_response": response_text, "structured_output": result},
                                    filename=output_filename or "structured_output_raw_and_processed_retry.json",
                                    directory="test_data"
                                )
                                
                                clean_filename = (output_filename.replace(".json", "_clean_retry.json") 
                                                if output_filename and ".json" in output_filename 
                                                else (output_filename + "_clean_retry.json" if output_filename else "structured_output_clean_retry.json"))
                                clean_path = save_structured_output(
                                    result,
                                    filename=clean_filename,
                                    directory="test_data"
                                )
                                logger.info(f"Saved retry output to {raw_path} and clean output to {clean_path}")
                            
                            return result
                        except Exception as validation_error:
                            logger.error(f"Validation error for retry: {str(validation_error)}")
                            error_result = {
                                "error": "Failed to validate structured plan from retry",
                                "details": str(validation_error),
                                "parsed_json": structured_plan,
                                "raw_response": response_text
                            }
                            
                            if save_output:
                                save_structured_output(
                                    {"raw_response": response_text, "error": error_result},
                                    filename=output_filename or "structured_output_validation_error_retry.json",
                                    directory="test_data"
                                )
                            
                            return error_result
                except Exception as retry_error:
                    logger.error(f"Error during retry attempt: {str(retry_error)}")
                    error_message = f"Initial error: {str(e)}. Retry error: {str(retry_error)}"
            
            # If we reach here, all attempts have failed
            error_result = {
                "error": "Failed to structure the study plan", 
                "details": error_message or str(e),
                "raw_response": response_text if response_text else "No response received"
            }
            
            if save_output:
                save_structured_output(
                    {"error": error_result},
                    filename=output_filename or "structured_output_exception.json",
                    directory="test_data"
                )
            
            return error_result
    
    def structure_plan_sync(self, raw_plan: str, save_output: bool = True, output_filename: str = None, 
                         user_days: int = None, user_hours: float = None) -> Dict[str, Any]:
        """
        Synchronous version of structure_plan.
        
        Args:
            raw_plan: The raw study plan to structure
            save_output: Whether to save the output
            output_filename: The filename to save the output to (without extension)
        
        Returns:
            The structured study plan as a dictionary
        """
        try:
            # Log the explicitly passed user days and hours if provided
            if user_days is not None:
                logger.info(f"Using explicitly specified days: {user_days} (sync)")
            if user_hours is not None:
                logger.info(f"Using explicitly specified hours per day: {user_hours} (sync)")
                
            # If not explicitly provided, try to extract from the raw_plan
            if user_days is None or user_hours is None:
                # Extract user_days and user_hours from the raw_plan if present
                user_days_match = re.search(r'\b(\d+)\s*(?:days?|study days)\b', raw_plan, re.IGNORECASE)
                user_hours_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:hours?|hour per day|hours? per day)\b', raw_plan, re.IGNORECASE)
                
                if user_days is None and user_days_match:
                    user_days = int(user_days_match.group(1))
                    logger.info(f"Extracted user-specified days: {user_days} (sync)")
                
                if user_hours is None and user_hours_match:
                    user_hours = float(user_hours_match.group(1))
                    logger.info(f"Extracted user-specified hours per day: {user_hours} (sync)")
            
            logger.info(f"Structuring study plan with {self.model.model_name} (sync)")
            prompt = f"""
            Here is a raw study plan:
            
            {raw_plan}
            
            Convert this raw study plan into a structured JSON format following the schema provided.
            Focus on creating a COMPLETE and COMPREHENSIVE study plan.
            Return ONLY valid JSON without any explanations, markdown formatting, or non-JSON text.
            """
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            # First attempt
            response = self.model.invoke(messages)
            response_text = response.content
            
            # Log the raw response for debugging
            logger.info("Raw response from structurer agent (sync): %s", response_text)
            
            # Multiple parsing attempts with increasingly aggressive cleanup
            structured_plan = None
            error_message = None
            
            # Attempt 1: Direct JSON parsing
            try:
                structured_plan = json.loads(response_text)
                logger.info("Successfully parsed JSON directly (sync)")
            except json.JSONDecodeError as e:
                error_message = f"Direct parsing failed (sync): {str(e)}"
                logger.warning(error_message)
            
            # Attempt 2: Extract from code blocks
            if structured_plan is None:
                json_match = re.search(r'```(?:json)?(.*?)```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                    try:
                        structured_plan = json.loads(json_str)
                        logger.info("Successfully parsed JSON from code block (sync)")
                    except json.JSONDecodeError as e:
                        error_message = f"Code block parsing failed (sync): {str(e)}"
                        logger.warning(error_message)
            
            # Attempt 3: Find any JSON-like content
            if structured_plan is None:
                # Look for content that looks like JSON object (starts with { and ends with })
                json_pattern = re.search(r'({.*})', response_text, re.DOTALL)
                if json_pattern:
                    potential_json = json_pattern.group(1).strip()
                    try:
                        structured_plan = json.loads(potential_json)
                        logger.info("Successfully parsed JSON from pattern matching (sync)")
                    except json.JSONDecodeError as e:
                        error_message = f"Pattern matching parsing failed (sync): {str(e)}"
                        logger.warning(error_message)
            
            # Attempt 4: If still failing, try a retry with explicit instructions
            if structured_plan is None:
                logger.warning("Initial parsing attempts failed. Trying again with explicit JSON-only instructions (sync).")
                
                retry_prompt = f"""
                Your previous response could not be parsed as valid JSON. Please try again.
                
                Here is the raw study plan:
                
                {raw_plan}
                
                Return ONLY a valid JSON object following the schema. 
                NO explanations, NO markdown formatting (no ```), NO additional text.
                Just the raw JSON object starting with {{.
                
                Make sure all strings are properly quoted and all JSON syntax is valid.
                """
                
                retry_messages = [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=retry_prompt)
                ]
                
                retry_response = self.model.invoke(retry_messages)
                retry_text = retry_response.content
                
                logger.info("Retry response from structurer agent (sync): %s", retry_text)
                
                try:
                    structured_plan = json.loads(retry_text)
                    logger.info("Successfully parsed JSON from retry (sync)")
                except json.JSONDecodeError as e:
                    # One last attempt - try to extract any JSON-like content from retry
                    json_pattern = re.search(r'({.*})', retry_text, re.DOTALL)
                    if json_pattern:
                        potential_json = json_pattern.group(1).strip()
                        try:
                            structured_plan = json.loads(potential_json)
                            logger.info("Successfully parsed JSON from retry pattern matching (sync)")
                        except json.JSONDecodeError as e2:
                            error_message = f"All parsing attempts failed. Final error (sync): {str(e2)}"
                            logger.error(error_message)
                    else:
                        error_message = f"All parsing attempts failed. Final error (sync): {str(e)}"
                        logger.error(error_message)
            
            # If we have a structured plan, validate and save it
            if structured_plan:
                try:
                    # Validate against the Pydantic model
                    validated_plan = StructuredStudyPlan(**structured_plan)
                    result = validated_plan.dict()
                    
                    # Save both raw and structured outputs if requested
                    if save_output:
                        logger.info(f"Saving structured output to test_data directory (sync)")
                        raw_path = save_structured_output(
                            {"raw_response": response_text, "structured_output": result},
                            filename=output_filename or "structured_output_raw_and_processed_sync.json",
                            directory="test_data"
                        )
                        
                        # Also save just the structured output in a clean format
                        clean_filename = (output_filename.replace(".json", "_clean_sync.json") 
                                          if output_filename and ".json" in output_filename 
                                          else (output_filename + "_clean_sync.json" if output_filename else "structured_output_clean_sync.json"))
                        clean_path = save_structured_output(
                            result,
                            filename=clean_filename,
                            directory="test_data"
                        )
                        logger.info(f"Saved raw output to {raw_path} and clean output to {clean_path} (sync)")
                    
                    return result
                except Exception as validation_error:
                    logger.error(f"Validation error (sync): {str(validation_error)}")
                    error_result = {
                        "error": "Failed to validate structured plan",
                        "details": str(validation_error),
                        "parsed_json": structured_plan,
                        "raw_response": response_text
                    }
                    
                    if save_output:
                        save_structured_output(
                            {"raw_response": response_text, "error": error_result},
                            filename=output_filename or "structured_output_validation_error_sync.json",
                            directory="test_data"
                        )
                    
                    return error_result
            else:
                # If all parsing attempts failed
                error_result = {
                    "error": "Failed to structure the study plan (sync)", 
                    "details": error_message or "Unknown parsing error", 
                    "raw_response": response_text
                }
                
                if save_output:
                    save_structured_output(
                        {"raw_response": response_text, "error": error_result},
                        filename=output_filename or "structured_output_parsing_error_sync.json",
                        directory="test_data"
                    )
                
                return error_result
        
        except Exception as e:
            logger.error("Error in structurer agent (sync): %s", str(e))
            error_result = {
                "error": "Failed to structure the study plan (sync)", 
                "details": str(e),
                "raw_response": response_text if 'response_text' in locals() else "No response received"
            }
            
            if save_output:
                save_structured_output(
                    {"error": str(e)},
                    filename=output_filename or "structured_output_exception_sync.json",
                    directory="test_data"
                )
            
            return error_result
