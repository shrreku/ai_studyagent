'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useStudyPlan } from '../../../context/StudyPlanContext';
import { Loader2 } from 'lucide-react';
import axios from 'axios';

const STORAGE_KEY = 'studyAgent_studyPlan';

const StudySessionLoading: React.FC = () => {
  const { studyPlan, setStudyPlan } = useStudyPlan();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initNavigation = async () => {
      try {
        // Wait for a brief moment to ensure the loading state is visible
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Get the raw plan from localStorage
        const rawPlanResponse = localStorage.getItem('rawStudyPlanResponse');
        
        if (!rawPlanResponse) {
          // If no raw plan, check if we have a structured plan in context or localStorage
          let currentStudyPlan = studyPlan;
          if (!currentStudyPlan) {
            // Try to get from localStorage as fallback
            try {
              const saved = localStorage.getItem(STORAGE_KEY);
              if (saved) {
                currentStudyPlan = JSON.parse(saved);
              }
            } catch (e) {
              console.error('Error reading from localStorage:', e);
            }
          }

          if (!currentStudyPlan) {
            setError('No study plan found. Please generate a study plan first.');
            await new Promise(resolve => setTimeout(resolve, 2000));
            router.replace('/');
            return;
          }

          // Navigate to active session after a short delay
          await new Promise(resolve => setTimeout(resolve, 500));
          router.push('/study-session-active');
          return;
        }
        
        // If we have a raw plan, send it to the structurer
        try {
          console.log('Sending raw plan to structurer...');
          const response = await axios.post('http://localhost:8000/plan/structure-plan', {
            raw_plan: rawPlanResponse
          });
          
          if (response.data && response.data.structured_plan) {
            console.log('Received structured plan:', response.data.structured_plan);
            
            // Store the structured plan in context
            const structuredPlan = response.data.structured_plan;
            
            // Validate the structure has the expected fields
            if (!structuredPlan.overallGoal || !structuredPlan.dailyBreakdown) {
              console.error('Plan structure is not as expected:', structuredPlan);
              throw new Error('Plan structure is invalid or incomplete');
            }
            
            // Store in both context and localStorage
            setStudyPlan(structuredPlan);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(structuredPlan));
            
            // Clean up the raw plan from localStorage
            localStorage.removeItem('rawStudyPlanResponse');
            
            // Add delay to ensure state updates complete
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Navigate to active session
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
          await new Promise(resolve => setTimeout(resolve, 2000));
          router.push('/study-plan-preview');
        }
      } catch (err) {
        console.error('Navigation error:', err);
        setError('Failed to start study session. Please try again.');
        await new Promise(resolve => setTimeout(resolve, 2000));
        router.replace('/');
      } finally {
        setIsLoading(false);
      }
    };

    initNavigation();
  }, [studyPlan, router]);

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-background p-4">
        <div className="text-center text-destructive">
          <p className="text-lg font-medium">{error}</p>
          <p className="text-sm mt-2">Redirecting to home page...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background">
      <div className="flex flex-col items-center space-y-4">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
        <h1 className="text-2xl font-semibold">Preparing your study session...</h1>
        <p className="text-muted-foreground">This will just take a moment</p>
      </div>
    </div>
  );
};

export default StudySessionLoading;
