'use client';

import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';

// Define the interfaces for the study plan data, aligned with backend Pydantic models
export interface StudyPlanCoreConcept {
  concept: string;
  explanation: string;
}

// Resource interface for more detailed resource information
export interface StudyPlanResource {
  title: string;
  type?: string | null;
  url?: string | null;
  description?: string | null;
}

export interface StudyPlanItem {
  topic: string;
  details: string;
  estimatedTimeHours?: number;
  durationMinutes?: number;
  resources?: (string | StudyPlanResource)[];
  isCompleted?: boolean;
  learningObjectives?: string[];
  priority?: string;
  isSummary?: boolean;
}

export interface StudyPlanDailySchedule {
  day: number;
  daySummary?: string;
  focusArea?: string;
  learningGoals?: string[];
  reviewTopics?: string[] | null;
  items: StudyPlanItem[];
}

export interface StudyPlanKeyFormula {
  formula_name?: string;
  name?: string;
  formula?: string;
  description: string;
  usage_context?: string;
  variables?: Record<string, string>;
  examples?: string[];
}

export interface StudyPlan {
  overallGoal: string;
  totalStudyDays: number;
  hoursPerDay: number;
  keyConcepts: StudyPlanCoreConcept[];
  dailyBreakdown: StudyPlanDailySchedule[];
  keyFormulas?: StudyPlanKeyFormula[];
  generalTips?: string[];
  // Additional fields for enhanced plans
  difficulty_level?: string;
  estimated_completion_time?: number;
  prerequisites?: string[];
}

export interface StudyPlanContextType {
  studyPlan: StudyPlan | null;
  setStudyPlan: (plan: StudyPlan | null) => void;
}

const STORAGE_KEY = 'intelliStudy_studyPlan';

const StudyPlanContext = createContext<StudyPlanContextType | undefined>(undefined);

export const StudyPlanProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [studyPlan, setStudyPlanState] = useState<StudyPlan | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setStudyPlanState(JSON.parse(saved));
      }
    } catch (error) {
      console.error('Failed to load study plan from localStorage:', error);
    } finally {
      setIsInitialized(true);
    }
  }, []);

  const setStudyPlan = (plan: StudyPlan | null) => {
    try {
      setStudyPlanState(plan);
      if (plan) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(plan));
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    } catch (error) {
      console.error('Failed to save study plan to localStorage:', error);
    }
  };

  // Don't render children until we've loaded from localStorage
  if (!isInitialized) {
    return null;
  }

  return (
    <StudyPlanContext.Provider value={{ studyPlan, setStudyPlan }}>
      {children}
    </StudyPlanContext.Provider>
  );
};

export const useStudyPlan = (): StudyPlanContextType => {
  const context = useContext(StudyPlanContext);
  if (context === undefined) {
    throw new Error('useStudyPlan must be used within a StudyPlanProvider')
  }
  return context;
};