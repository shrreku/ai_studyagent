from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging
import os
import asyncio

from crewai import Agent, Task, Crew, Process
from crewai.crews.crew_output import CrewOutput

# Assuming ai_workflow.py is in utils and contains the llm and chat_support_agent
from utils.ai_workflow import llm, chat_support_agent # Corrected import for running from backend/

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request and response
class ChatRequest(BaseModel):
    user_query: str = Field(..., description="The user's query or message.")
    session_id: str = Field(..., description="A unique session identifier to track conversation history or context.")
    study_materials_context: Optional[str] = Field(None, description="Context from uploaded study materials.")
    study_plan_context: Optional[str] = Field(None, description="Optional context from the current study plan.")
    stream: Optional[bool] = Field(False, description="Whether to stream the response or return it as a single JSON object.")

class ChatResponse(BaseModel):
    ai_response: str = Field(..., description="The AI's response to the user's query.")
    session_id: str = Field(..., description="The session identifier, echoed back from the request.")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Optional debugging information.")

# --- Define Task for Chat Agent --- (Subtask 7.2)
def create_chat_interaction_task(agent: Agent, user_query: str, study_materials: Optional[str], study_plan: Optional[str]) -> Task:
    context_summary = []
    if study_materials:
        context_summary.append(f"Reference Study Materials (first 200 chars):\n{study_materials[:200]}...")
    if study_plan:
        context_summary.append(f"Reference Study Plan (first 200 chars):\n{study_plan[:200]}...")
    
    full_context_description = "\n\n".join(context_summary)
    if not full_context_description:
        full_context_description = "No specific reference material provided beyond the user's query."

    return Task(
        description=(
            f"You are an AI Study Tutor. A student has sent the following query: '{user_query}'.\n"
            f"Use the following reference material to inform your answer. If the material is not directly relevant, focus on the user's query directly.\n\n"
            f"Reference Material:\n{full_context_description}\n\n"
            f"Your primary goal is to provide a helpful, concise, and accurate response to the student's query. "
            f"If the query is a greeting, respond politely. If it's a question, answer it clearly. If it's a request for explanation, provide one based on the reference material if relevant."
        ),
        expected_output=(
            "A clear, helpful, and contextually relevant textual response to the student's query. "
            "The response should directly address what the student asked, using the provided reference material if applicable."
        ),
        agent=agent,
    )

import asyncio # Added for asyncio.to_thread

# --- Crew Definition and Execution for Chat --- (Subtask 7.2 & 7.3)
async def run_chat_crew(user_query: str, study_materials_context: Optional[str], study_plan_context: Optional[str]) -> Dict[str, Any]:
    logger.info(f"Starting ASYNC Chat Crew AI workflow for query: {user_query[:50]}...")

    if not os.getenv("OPENROUTER_API_KEY") or not os.getenv("DEEPSEEK_MODEL_NAME"):
        error_message = "Critical Error: API keys (OPENROUTER_API_KEY or DEEPSEEK_MODEL_NAME) are not configured in the environment (.env file). The AI service cannot be reached."
        logger.error(error_message)
        raise HTTPException(status_code=503, detail=error_message) # 503 Service Unavailable

    try:
        # Ensure the chat_support_agent is correctly initialized (it's imported from ai_workflow)
        if not chat_support_agent:
            logger.error("Chat support agent is not initialized.")
            raise HTTPException(status_code=500, detail="Chat support agent not available.")

        chat_task = create_chat_interaction_task(
            agent=chat_support_agent,
            user_query=user_query,
            study_materials=study_materials_context,
            study_plan=study_plan_context
        )

        chat_crew = Crew(
            agents=[chat_support_agent],
            tasks=[chat_task],
            process=Process.sequential,
            verbose=True # Set to False in production if too noisy
        )

        logger.info("Kicking off the chat crew asynchronously...")
        # Run the blocking kickoff in a separate thread
        crew_result = await asyncio.to_thread(chat_crew.kickoff)
        logger.info(f"Async chat crew execution finished. Raw output type: {type(crew_result)}. Output (first 200 chars): {str(crew_result)[:200]}...")

        ai_response_text = ""
        if isinstance(crew_result, str):
            ai_response_text = crew_result
        elif isinstance(crew_result, CrewOutput) and hasattr(crew_result, 'raw') and isinstance(crew_result.raw, str):
            ai_response_text = crew_result.raw
        elif hasattr(crew_result, '__str__'): # Fallback for other CrewOutput structures or direct string-like objects
            ai_response_text = str(crew_result)
        else:
            ai_response_text = "Sorry, I encountered an unexpected issue processing your request with the AI crew."
            logger.warning(f"Unexpected crew_result type: {type(crew_result)}. Could not extract string response. Full result: {crew_result}")

        if not ai_response_text.strip():
             ai_response_text = "I'm sorry, I couldn't generate a specific response for that. Could you try rephrasing or providing more context?"
             logger.warning(f"Chat crew returned an empty or whitespace-only response. Original output: {str(crew_result)[:200]}")

        return {"ai_response": ai_response_text.strip(), "debug_info": {"crew_raw_output_type": str(type(crew_result))}}

    except HTTPException as http_exc: # Re-raise HTTPExceptions to be handled by FastAPI
        raise http_exc
    except Exception as e:
        logger.error(f"Error during chat crew execution: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat request with AI: {str(e)}")

from fastapi.responses import StreamingResponse
import json

@router.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """
    Handles a user's chat message, processes it with the Chat Crew AI,
    and returns an AI-generated response. Supports both streaming and non-streaming responses.
    """
    logger.info(f"Received chat request: Query='{request.user_query}', SessionID='{request.session_id}', Stream={request.stream}")

    try:
        # If streaming is requested, handle it differently
        if request.stream:
            return StreamingResponse(
                content=stream_chat_response(request),
                media_type="text/event-stream"
            )
        
        # Standard non-streaming response
        crew_response_data = await run_chat_crew(
            user_query=request.user_query,
            study_materials_context=request.study_materials_context,
            study_plan_context=request.study_plan_context
        )
        
        return ChatResponse(
            ai_response=crew_response_data["ai_response"],
            session_id=request.session_id,
            debug_info=crew_response_data.get("debug_info")
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unhandled error in handle_chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")

async def stream_chat_response(request: ChatRequest):
    """
    Generator function that streams the AI response chunk by chunk.
    """
    try:
        # Send initial message to confirm connection
        yield json.dumps({"status": "processing"}) + "\n"
        
        # Call the async chat crew execution function
        crew_response_data = await run_chat_crew(
            user_query=request.user_query,
            study_materials_context=request.study_materials_context,
            study_plan_context=request.study_plan_context
        )
        
        # Get the full response
        full_response = crew_response_data["ai_response"]
        
        # For empty responses, send a fallback message
        if not full_response or not full_response.strip():
            full_response = "I'm sorry, I couldn't generate a specific response for that. Could you try rephrasing your question?"
            yield json.dumps({"chunk": full_response}) + "\n"
            yield json.dumps({"done": True}) + "\n"
            return
        
        # Stream the response in small chunks - adaptive chunk size based on response length
        total_length = len(full_response)
        
        # Use smaller chunks for shorter responses, larger for longer ones
        if total_length < 100:
            chunk_size = 5  # Very small chunks for short responses
        elif total_length < 500:
            chunk_size = 10  # Small chunks for medium responses
        else:
            chunk_size = 15  # Larger chunks for long responses
        
        # Add a small initial delay to make it feel more natural
        await asyncio.sleep(0.2)
        
        # Stream the response
        for i in range(0, total_length, chunk_size):
            chunk = full_response[i:i+chunk_size]
            # Format as JSON and add newline (required for event stream parsing)
            yield json.dumps({"chunk": chunk}) + "\n"
            
            # Adaptive delay - slower at punctuation for more natural reading
            if chunk and chunk[-1] in ['.', '!', '?', ':', ';']:
                await asyncio.sleep(0.1)  # Longer pause at sentence breaks
            else:
                await asyncio.sleep(0.05)  # Standard delay
        
        # Add a small delay before completion
        await asyncio.sleep(0.2)
        
        # Signal completion
        yield json.dumps({"done": True}) + "\n"
        
    except HTTPException as http_exc:
        logger.error(f"HTTP error in streaming response: {http_exc.detail}", exc_info=True)
        # Send formatted error message
        yield json.dumps({"error": f"Error: {http_exc.detail}"}) + "\n"
        yield json.dumps({"done": True}) + "\n"
    except Exception as e:
        logger.error(f"Unexpected error in streaming response: {str(e)}", exc_info=True)
        # Send error message
        yield json.dumps({"error": f"An unexpected error occurred: {str(e)}"}) + "\n"
        yield json.dumps({"done": True}) + "\n"