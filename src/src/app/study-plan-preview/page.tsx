'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useStudyPlan } from '../../../context/StudyPlanContext';
import { Button } from '@/components/ui/button';
import LoadingScreen from '@/components/ui/loading-screen';
import { DebugPanel } from '@/components/ui/debug-utils';
import axios from 'axios';
import { getApiUrl, API_ENDPOINTS } from '@/config/api';

const StudyPlanPreviewPage: React.FC = () => {
  const router = useRouter();
  const { studyPlan, setStudyPlan } = useStudyPlan();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // This represents the raw response from the study planning agent
  const [rawPlanResponse, setRawPlanResponse] = useState<string | null>(null);

  // Get the raw plan response from the URL query parameters or localStorage on component mount
  React.useEffect(() => {
    // Try to get the raw plan from localStorage (it would have been set by the input form)
    const storedRawPlan = localStorage.getItem('rawStudyPlanResponse');
    if (storedRawPlan) {
      setRawPlanResponse(storedRawPlan);
    }
  }, []);

  const handleStartStructuring = async () => {
    if (!rawPlanResponse) {
      setError('No study plan response to structure.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Send the raw plan to the structurer agent
      const response = await axios.post(getApiUrl(API_ENDPOINTS.STRUCTURE_PLAN), {
        raw_plan: rawPlanResponse
      });

      if (response.data && response.data.structured_plan) {
        // Store the structured plan in the StudyPlanContext
        setStudyPlan(response.data.structured_plan);
        
        // Log the plan for debugging
        console.log('Received structured plan:', response.data.structured_plan);
        
        // Navigate to the active study session page
        router.push('/study-session-active');
      } else {
        throw new Error('Failed to receive structured plan from server');
      }
    } catch (error: any) {
      console.error('Error during plan structuring:', error);
      let errorMessage = 'An unexpected error occurred while structuring the plan.';
      if (axios.isAxiosError(error)) {
        if (error.response) {
          errorMessage = `Server error: ${error.response.data?.message || error.message}`;
        } else if (error.request) {
          errorMessage = 'Network error: No response received from server.';
        }
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToForm = () => {
    router.push('/');
  };

  if (isLoading) {
    return <LoadingScreen message="Structuring your study plan... Please wait." />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-800 to-slate-600 text-white">
      <div className="container mx-auto p-6">
        <div className="max-w-4xl mx-auto bg-slate-900 rounded-lg shadow-xl p-6">
          <h1 className="text-2xl font-bold mb-6 border-b border-slate-700 pb-2">
            Study Plan Preview
          </h1>
          
          {error && (
            <div className="bg-red-900/30 border border-red-500 text-red-200 rounded-md p-4 mb-6">
              <p className="font-semibold">Error:</p>
              <p>{error}</p>
            </div>
          )}

          <div className="mb-6">
            <p className="text-slate-300 mb-4">
              This is the raw response from the study planning agent. Review it before proceeding.
            </p>
            
            <div className="bg-slate-950 rounded-md p-4 overflow-auto max-h-[60vh]">
              {rawPlanResponse ? (
                <pre className="text-slate-300 whitespace-pre-wrap break-words text-sm">
                  {rawPlanResponse}
                </pre>
              ) : (
                <p className="text-slate-400 italic">No study plan response available.</p>
              )}
            </div>
          </div>

          <div className="space-y-6">
            <div className="border-t border-slate-700 pt-4">
              <p className="text-slate-300 mb-4">Not happy with this plan? Try our sample study plan instead:</p>
              <DebugPanel showText={true} variant="full" />
            </div>
            
            <div className="flex space-x-4 justify-end">
              <Button
                onClick={handleBackToForm}
                variant="outline"
                className="border-slate-500 text-slate-300 hover:bg-slate-700"
              >
                Back to Form
              </Button>
              <Button
                onClick={handleStartStructuring}
                className="bg-blue-600 hover:bg-blue-700 text-white"
                disabled={!rawPlanResponse}
              >
                Structure Plan & Start Session
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudyPlanPreviewPage;
