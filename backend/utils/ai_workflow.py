from curses import raw
from crewai import Agent, Task, Crew, Process
from crewai.crews.crew_output import CrewOutput # Added import
from langchain_openai import ChatOpenAI
import os
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Type
import json
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the LLM for DeepSeek V3 via OpenRouter
# Ensure OPENROUTER_API_KEY and DEEPSEEK_MODEL_NAME are in your .env file
llm = ChatOpenAI(
    model_name=f"openrouter/{os.getenv('DEEPSEEK_MODEL_NAME', 'deepseek/deepseek-coder')}", # Default if not set
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1/",
    temperature=0.7,
)

# --- Pydantic Models for Structured LLM Output ---
class TopicDetail(BaseModel):
    topic_name: str = Field(description="The name of the study topic.")
    priority: int = Field(description="Priority of the topic (e.g., 1 for highest).")
    estimated_hours: float = Field(description="Estimated hours to study this topic.")
    sub_topics: List[str] = Field(description="A list of sub-topics or key concepts within this topic.", default=[])

class TopicListOutput(BaseModel):
    topics: List[TopicDetail] = Field(description="A list of topics with their details including priority, estimated time, and sub-topics.")

# --- Define Agents ---

# Agent 1: Topic Prioritizer & Time Estimator
topic_prioritizer_agent = Agent(
    role='Topic Prioritizer and Time Estimator',
    goal='From the provided study materials, identify core topics and sub-topics. Then, prioritize these topics, ' \
         'estimate study time for each, and structure this information as a JSON object conforming to the TopicListOutput model. ',
    backstory=(
        "You are a meticulous academic planner. You excel at analyzing educational content to extract key learning points. "
        "Given study materials and total study duration, you can identify all relevant topics and sub-topics, assign priorities, "
        "and realistically estimate study time for each. Your output is always a well-formed JSON that adheres to the TopicListOutput schema."
    ),
    verbose=True,
    llm=llm,
    allow_delegation=False,
)

# Agent 2: Study Plan Generator
study_plan_generator_agent = Agent(
    role='Customized Study Plan Generator',
    goal='Generate a human-readable, text-based study plan by populating a given Markdown template with topic details (name, priority, time, sub-topics) from a JSON input. ' \
         'The plan should be comprehensive and follow the structure of the provided template.',
    backstory=(
        "You are an expert curriculum developer with a knack for creating personalized and easy-to-follow study guides. "
        "You take structured JSON data about topics (including names, priorities, estimated study times, and sub-topics) and a markdown template, "
        "then skillfully weave them together to produce a clear, well-organized, and detailed textual study plan. "
        "You pay close attention to formatting instructions within the template."
    ),
    verbose=True,
    llm=llm,
    allow_delegation=False
)

# Agent for Chat Interaction (Placeholder for Task 7)
chat_support_agent = Agent(
    role='AI Study Tutor',
    goal='Provide contextual explanations, answer questions, and offer guidance based on the uploaded study materials and generated study plan.',
    backstory=(
        "You are an interactive AI tutor. Students will ask you questions about concepts from their notes, "
        "seek clarification on topics in their study plan, or ask for help with practice questions. "
        "Your responses must be accurate, contextual, and drawn from the provided materials."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False
)

# --- Define Tasks ---

# Task for Topic Prioritizer
def create_topic_prioritization_task(agent: Agent, study_materials_text: str, total_days: str, hours_per_day: str, output_model: Type[BaseModel]) -> Task:
    return Task(
        description=(
            f"Analyze the following study materials. Identify all core topics and their relevant sub-topics. "
            f"Then, prioritize these topics for a study period of {total_days} days at {hours_per_day} hours per day. "
            f"Estimate the study time (in hours) needed for each main topic. "
            f"Structure your entire output as a single JSON object that strictly conforms to the {output_model} model. "
            f"Ensure all fields in the {output_model} model (topics, topic_name, priority, estimated_hours, sub_topics) are correctly populated.\n\n"
            f"Study Materials:\n```\n{study_materials_text}\n```"
        ),
        expected_output=(
            f"A single JSON string that strictly validates against the {output_model} Pydantic model. "
            f"This JSON will contain a list of 'topics', where each topic has 'topic_name', 'priority', 'estimated_hours', and a list of 'sub_topics'."
        ),
        agent=agent,
        output_pydantic=output_model,
    )

# Task for Study Plan Generator
def create_study_plan_generation_task(agent: Agent, study_plan_template: str, total_days: str, hours_per_day: str) -> Task:
    # The context_topics_json will be implicitly passed from the output of the previous task in a sequential crew.
    return Task(
        description=(
            f"You are tasked with generating a detailed, human-readable study plan in plain text format. "
            f"Use the provided Markdown template and populate it with the topic information received from the previous task's JSON output. "
            f"The study plan is for {total_days} days at {hours_per_day} hours per day.\n\n"
            f"Markdown Template to use:\n```markdown\n{study_plan_template}\n```\n\n"
            f"The JSON data (from the previous step) will contain a list of topics, each with 'topic_name', 'priority', 'estimated_hours', and 'sub_topics'. "
            f"Your goal is to replace placeholders in the template (like '[Topic 1]', '[Total Hours]', '[Primary focus...]', etc.) "
            f"with relevant information derived from this JSON data. The final output MUST be only the populated template as Markdown text. "
            f"Do not include any extra explanations, apologies, or conversational text outside of the generated plan itself. "
            f"Ensure the output is well-formatted Markdown text."
        ),
        expected_output=(
            "A beatifully formatted fully populated study plan in Markdown format. "
            "This text should be ready to be displayed directly to a user."
        ),
        agent=agent,
        # Context is automatically passed from the previous task in a sequential crew.
    )

# --- Crew Definition and Execution ---
def run_study_plan_crew(study_materials_text: str, study_duration_days: str, study_hours_per_day: str) -> Dict[str, Any]:
    logger.info(f"Starting Crew AI workflow with: {study_duration_days} days, {study_hours_per_day} hours/day.")
    
    template_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'template.md'))
    try:
        with open(template_file_path, 'r', encoding='utf-8') as f:
            study_plan_template_content = f.read()
        logger.info(f"Successfully read template file: {template_file_path}")
    except FileNotFoundError:
        logger.error(f"Study plan template file not found at {template_file_path}")
        return {"error": "Configuration error", "details": f"Study plan template file not found at {template_file_path}."}
    except Exception as e:
        logger.error(f"Error reading template file {template_file_path}: {str(e)}", exc_info=True)
        return {"error": "File reading error", "details": f"Could not read template: {str(e)}"}

    if not os.getenv("OPENROUTER_API_KEY") or not os.getenv("DEEPSEEK_MODEL_NAME"):
        error_message = "Error: API keys (OPENROUTER_API_KEY or DEEPSEEK_MODEL_NAME) not configured in .env file."
        logger.error(error_message)
        return {"error": "API Key Configuration Error", "details": error_message}

    try:
        task_prioritize = create_topic_prioritization_task(
            agent=topic_prioritizer_agent,
            study_materials_text=study_materials_text,
            total_days=study_duration_days,
            hours_per_day=study_hours_per_day,
            output_model=TopicListOutput
        )

        task_generate_plan = create_study_plan_generation_task(
            agent=study_plan_generator_agent,
            study_plan_template=study_plan_template_content,
            total_days=study_duration_days,
            hours_per_day=study_hours_per_day
        )
        task_generate_plan.context = [task_prioritize] # Explicitly set context

        study_crew = Crew(
            agents=[topic_prioritizer_agent, study_plan_generator_agent],
            tasks=[task_prioritize, task_generate_plan],
            process=Process.sequential,
            verbose=True # Explicitly set to boolean True
        )

        logger.info("Kicking off the study crew...")
        # The result of kickoff() is the output of the last task (task_generate_plan's text output).
        text_plan_output = study_crew.kickoff()
        logger.info(f"Crew execution finished. Raw output type: {type(text_plan_output)}. Output (first 200 chars): {str(text_plan_output)[:200]}...")

        # Ensure text_plan_output is a string
        actual_text_plan = ""
        if isinstance(text_plan_output, str):
            actual_text_plan = text_plan_output
            logger.info("text_plan_output is already a string.")
        elif isinstance(text_plan_output, CrewOutput):
            logger.info("text_plan_output is a CrewOutput object. Attempting to extract text.")
            # Try .raw first, as it's often the direct text output
            if hasattr(text_plan_output, 'raw') and isinstance(text_plan_output.raw, str) and text_plan_output.raw.strip():
                logger.info("Using .raw attribute from CrewOutput.")
                actual_text_plan = text_plan_output.raw
            else: # Fallback to str() conversion, which logs show works
                logger.info("CrewOutput .raw attribute not suitable, empty, or not found. Falling back to str(CrewOutput).")
                actual_text_plan = str(text_plan_output)
                if not actual_text_plan.strip(): # Check if str() result is empty or whitespace
                     logger.warning(f"str(CrewOutput) resulted in a falsy or whitespace-only value: '{actual_text_plan}'. Original object (first 200 chars): {str(text_plan_output)[:200]}")
        elif hasattr(text_plan_output, 'raw_output') and isinstance(text_plan_output.raw_output, str):
            logger.info("Accessing .raw_output attribute from object for text plan.")
            actual_text_plan = text_plan_output.raw_output
        elif hasattr(text_plan_output, '__str__'): # General fallback for other types
            logger.info(f"Object is not str or CrewOutput, but has __str__. Type: {type(text_plan_output)}. Attempting str() conversion.")
            try:
                actual_text_plan = str(text_plan_output)
                if not actual_text_plan.strip(): # Check if str() result is empty or whitespace
                    logger.warning(f"str() conversion of {type(text_plan_output)} resulted in a falsy or whitespace-only value: '{actual_text_plan}'")
            except Exception as e:
                logger.error(f"Could not convert {type(text_plan_output)} to string using __str__: {e}")
        
        # Retrieve the JSON output from the first task (task_prioritize)
        topics_json_string = ""
        if task_prioritize.output:
            if isinstance(task_prioritize.output, BaseModel):
                # If output_pydantic is used, task.output is the Pydantic model instance
                topics_json_output_object = task_prioritize.output
                topics_json_string = topics_json_output_object.model_dump_json(indent=2)
            elif hasattr(task_prioritize.output, 'raw_output') and isinstance(task_prioritize.output.raw_output, str):
                 # Fallback if raw_output contains the JSON string (older CrewAI versions or different configs)
                topics_json_string = task_prioritize.output.raw_output
                try: # Validate this string is JSON
                    json.loads(topics_json_string)
                except json.JSONDecodeError as e:
                    logger.error(f"Topic prioritization task (raw_output) was a string but not valid JSON: {topics_json_string}. Error: {e}")
                    return {"error": "Invalid topic list format from AI (raw string)", "details": str(e)}
            else:
                logger.error(f"Unexpected output type from topic prioritization task: {type(task_prioritize.output)}. Value: {task_prioritize.output}")
                return {"error": "Failed to get topic list from AI", "details": "Topic prioritization task did not produce expected Pydantic model or raw string output."}
        else:
            logger.error("Could not retrieve output from topic prioritization task (task.output is None).")
            return {"error": "Failed to get topic list from AI", "details": "Topic prioritization task output is missing."}
        
        # This check replaces the one above and uses actual_text_plan
        # Ensure actual_text_plan is not just whitespace
        if not actual_text_plan or not actual_text_plan.strip(): 
            logger.error(f"Failed to extract a usable text plan. Original type: {type(text_plan_output)}, Processed actual_text_plan: '{actual_text_plan}', Original object state for context (first 500 chars): {str(text_plan_output)[:500]}")
            return {"error": "Invalid study plan format from AI", "details": f"Expected a text plan, got {type(text_plan_output)} and failed to convert to a non-empty string."}

        logger.info(f"Successfully generated. Topics JSON (first 200): {topics_json_string[:200]}... Text Plan (first 200): {actual_text_plan[:200]}...")
        return {
            "text_plan": actual_text_plan,
            "topic_list_json": topics_json_string
        }

    except Exception as e:
        logger.error(f"Error in run_study_plan_crew: {str(e)}", exc_info=True)
        return {"error": "An unexpected error occurred in AI workflow", "details": str(e)}


# Example usage (for testing purposes):
if __name__ == '__main__':
    if not os.getenv("OPENROUTER_API_KEY") or not os.getenv("DEEPSEEK_MODEL_NAME"):
        print("Error: OPENROUTER_API_KEY or DEEPSEEK_MODEL_NAME environment variable not set. Please set it in .env to run this test.")
    else:
        print("OPENROUTER_API_KEY and DEEPSEEK_MODEL_NAME are set. Running test...")
        sample_materials = """
        Chapter 1: Introduction to Quantum Physics
        - Wave-particle duality
        - Photoelectric effect
        - Compton scattering
        - De Broglie wavelength
        Chapter 2: Schrödinger Equation
        - Time-dependent and time-independent forms
        - Wave functions and probability density
        - Expectation values
        - Operators for position, momentum, energy
        Chapter 3: Potential Wells
        - Infinite square well
        - Finite square well
        - Quantum tunneling
        - Harmonic oscillator
        Key Formulas:
        - E = hf
        - p = h/lambda
        - Schrödinger Eq: Hψ = Eψ
        This course covers fundamental concepts in quantum mechanics. Students should understand both the mathematical formalism and the physical interpretations.
        Prioritize understanding the Schrödinger equation and its applications to simple systems like potential wells.
        Wave-particle duality is a foundational concept.
        """
        days = "5"
        hours = "3"
        
        print(f"Running study plan generation for {days} days, {hours} hours/day...")
        result = run_study_plan_crew(sample_materials, days, hours)
        
        if "error" in result:
            print(f"\nError generating study plan: {result['error']}")
            if "details" in result:
                print(f"Details: {result['details']}")
        else:
            print("\n--- Generated Study Plan (Text) ---")
            print(result.get("text_plan"))
            print("\n--- Topic List (JSON) ---")
            print(result.get("topic_list_json"))
            try:
                json_data = json.loads(result.get("topic_list_json"))
                print("\nTopic List JSON is valid.")
                # Optional: Validate with Pydantic model
                # parsed_topics = TopicListOutput(**json_data)
                # print("Topic List JSON conforms to Pydantic model TopicListOutput.")
            except Exception as e:
                print(f"\nError validating/parsing Topic List JSON: {e}")