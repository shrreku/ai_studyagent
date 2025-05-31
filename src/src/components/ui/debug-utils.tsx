'use client';

import React from 'react';
import { useStudyPlan } from '../../../context/StudyPlanContext';
import { Button } from './button';
import { useRouter } from 'next/navigation';
import { samplePlan } from '../../utils/sample-data-utils';

export const DebugPanel: React.FC<{ showText?: boolean; variant?: 'full' | 'compact' }> = ({ 
  showText = false, 
  variant = 'compact' 
}) => {
  const { setStudyPlan } = useStudyPlan();
  const router = useRouter();
  
  const loadSampleData = () => {
    try {
      // Use the imported type-safe sample data
      console.log('Loading sample study plan');
      
      // Set the sample data in the context
      setStudyPlan(samplePlan);
      
      // Also store in localStorage for persistence
      localStorage.setItem('intelliStudy_studyPlan', JSON.stringify(samplePlan));
      
      // Navigate to the study session active page
      router.push('/study-session-active');
    } catch (error: unknown) {
      console.error('Error loading sample data:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      alert(`Failed to load sample data: ${errorMessage}`);
    }
  };
  
  return (
    <div className={`${variant === 'full' ? '' : 'fixed bottom-4 right-4 z-50'}`}>
      <Button 
        onClick={loadSampleData}
        variant={variant === 'full' ? 'default' : 'outline'}
        size={variant === 'full' ? 'default' : 'sm'}
        className={variant === 'full' 
          ? 'bg-indigo-600 hover:bg-indigo-700 text-white w-full' 
          : 'bg-slate-800 text-white hover:bg-slate-700 border-slate-600 flex items-center gap-2'
        }
      >
        {showText ? 'Try with Sample Data' : 'Sample Data'}
      </Button>
    </div>
  );
};

export default DebugPanel;
