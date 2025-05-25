import { NextResponse } from 'next/server';
import { BACKEND_API_URL, API_ENDPOINTS } from '@/config/api';

interface ChatRequest {
  user_query: string;
  session_id: string;
  study_materials_context?: string;
  study_plan_context?: string;
  stream?: boolean;
}

export async function POST(request: Request) {
  try {
    // Parse the request body
    const requestData = await request.json();
    
    // Check if streaming is requested
    const isStreaming = requestData.stream === true;
    
    // Format the request for the backend API
    const chatRequest: ChatRequest = {
      user_query: requestData.user_query,
      session_id: requestData.session_id,
      study_materials_context: requestData.study_materials_context,
      study_plan_context: requestData.study_plan_context,
      stream: isStreaming
    };
    
    // The backend router path for chat is '/chat'
    const backendUrl = `${BACKEND_API_URL}/chat`;
    
    // For streaming responses, we need to proxy the stream directly
    if (isStreaming) {
      console.log('Streaming request to backend:', chatRequest);
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(chatRequest),
      });
      
      if (!response.ok) {
        throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
      }
      
      const contentType = response.headers.get('Content-Type') || '';
      console.log('Backend response content type:', contentType);
      
      // Check if we got a streaming response or a regular JSON response
      if (contentType.includes('text/event-stream')) {
        // Return the streaming response directly
        return new Response(response.body, {
          headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache, no-transform',
            'Connection': 'keep-alive',
            'Transfer-Encoding': 'chunked'
          },
        });
      } else {
        // We got a regular JSON response even though we requested streaming
        // Parse it and return it as a regular JSON response
        console.log('Got regular JSON response instead of stream');
        const data = await response.json();
        return NextResponse.json(data);
      }
    }
    
    // For non-streaming responses, handle as before
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(chatRequest),
    });
    
    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
    }
    
    // Parse the response from the backend
    const responseData = await response.json();
    
    // Return the AI response to the frontend
    return NextResponse.json({
      ai_response: responseData.ai_response,
      session_id: responseData.session_id,
      debug_info: responseData.debug_info
    });
  } catch (error) {
    console.error('Error processing chat message:', error);
    return NextResponse.json(
      { error: 'Failed to process message', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
