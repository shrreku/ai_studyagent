'use client';

import React from 'react';
import { useStudyPlan } from '../../../context/StudyPlanContext';
import { Button } from './button';

export const DebugPanel: React.FC = () => {
  const { setStudyPlan } = useStudyPlan();
  
  const loadSampleData = async () => {
    try {
      // Fetch the sample data from our backend
      const response = await fetch('http://localhost:8000/debug/sample_plan');
      if (!response.ok) {
        throw new Error(`Failed to fetch sample data: ${response.status}`);
      }
      
      const sampleData = await response.json();
      console.log('Loaded sample study plan:', sampleData);
      
      // Set the sample data in the context
      setStudyPlan(sampleData);
      
      // Also store in localStorage for persistence
      localStorage.setItem('studyAgent_studyPlan', JSON.stringify(sampleData));
      
      alert('Sample study plan loaded successfully!');
    } catch (error: unknown) {
      console.error('Error loading sample data:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      alert(`Failed to load sample data: ${errorMessage}`);
    }
  };
  
  return (
    <div className="fixed bottom-4 right-4 z-50">
      <Button 
        onClick={loadSampleData}
        variant="outline" 
        size="sm"
        className="bg-slate-800 text-white hover:bg-slate-700 border-slate-600"
      >
        Load Sample Plan
      </Button>
    </div>
  );
};

export default DebugPanel;
