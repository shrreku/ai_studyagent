import { NextResponse } from 'next/server';
import { BACKEND_API_URL } from '@/config/api';

export async function POST(request: Request) {
  try {
    // Parse the request body
    const requestData = await request.json();
    
    // Format the request for the backend API
    const studyPlanRequest = {
      study_materials: requestData.studyMaterials,
      days: requestData.totalDays,
      hours_per_day: requestData.hoursPerDay,
      file_ids: requestData.fileIds || []
    };
    
    // Call the backend API
    const backendUrl = `${BACKEND_API_URL}/study-plan`;
    console.log('Sending request to backend:', backendUrl, studyPlanRequest);
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(studyPlanRequest),
    });
    
    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
    }
    
    // Parse the response from the backend
    const responseData = await response.json();
    
    // Return the structured study plan to the frontend
    return NextResponse.json({
      studyPlan: responseData.frontend_plan,
      rawPlan: responseData.raw_plan,
      success: true
    });
  } catch (error) {
    console.error('Error generating study plan:', error);
    return NextResponse.json(
      { error: 'Failed to generate study plan', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
