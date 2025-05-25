'use client';

import React, { useState, ChangeEvent, useEffect } from 'react';
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { useStudyPlan } from "../../../context/StudyPlanContext";
import { getApiUrl, API_ENDPOINTS } from '@/config/api';

const InputForm: React.FC = () => {
  const router = useRouter();
  const { setStudyPlan } = useStudyPlan();

  // Form state
  const [totalDays, setTotalDays] = useState<string>('7'); // Default to 5 days
  const [hoursPerDay, setHoursPerDay] = useState<string>('2'); // Default to 2 hours per day
  const [notesFiles, setNotesFiles] = useState<FileList | null>(null);
  const [questionFiles, setQuestionFiles] = useState<FileList | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState<boolean>(false);
  const [previewData, setPreviewData] = useState<StudyPlan | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Constants
  const MAX_FILE_SIZE_MB = 10; // Maximum file size in MB
  const ALLOWED_FILE_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
  const ALLOWED_FILE_EXTENSIONS = ['.pdf', '.docx', '.txt'];

  // Define interfaces for the study plan structure
  interface StudyPlanItem {
    topic: string;
    details: string;
    estimatedTimeHours: number;
    resources: string[];
  }

  interface StudyPlanDay {
    day: number;
    daySummary: string;
    focusArea: string;
    items: StudyPlanItem[];
  }

  interface KeyConcept {
    concept: string;
    explanation: string;
  }

  interface KeyFormula {
    formula_name: string;
    description: string;
    usage_context: string;
  }

  interface StudyPlan {
    totalStudyDays: number;
    hoursPerDay: number;
    overallGoal: string;
    dailyBreakdown: StudyPlanDay[];
    keyConcepts: KeyConcept[];
    generalTips: string[];
    keyFormulas?: KeyFormula[];
  }

  const handleTotalDaysChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Allow empty string or positive integers between 1 and 7
    if (value === '' || (/^\d+$/.test(value) && parseInt(value, 10) >= 1 && parseInt(value, 10) <= 7)) {
      setTotalDays(value);
    }
  };

  const handleHoursPerDayChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Allow empty string or integers between 1 and 24
    if (value === '' || (/^\d+$/.test(value) && parseInt(value, 10) >= 1 && parseInt(value, 10) <= 24)) {
      setHoursPerDay(value);
    }
  };

  const validateFiles = (files: FileList): { validFiles: File[], invalidFiles: string[] } => {
    const validFiles: File[] = [];
    const invalidFiles: string[] = [];

    Array.from(files).forEach(file => {
      if (!ALLOWED_FILE_TYPES.includes(file.type)) {
        invalidFiles.push(`${file.name} (type: ${file.type || 'unknown'})`);
      } else if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        invalidFiles.push(`${file.name} (size: ${Math.round(file.size / (1024 * 1024))}MB - exceeds ${MAX_FILE_SIZE_MB}MB)`);
      } else {
        validFiles.push(file);
      }
    });

    return { validFiles, invalidFiles };
  };

  const handleNotesFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFileError(null); // Clear previous errors
      const { validFiles, invalidFiles } = validateFiles(e.target.files);

      if (invalidFiles.length > 0) {
        setFileError(`Invalid notes file(s): ${invalidFiles.join(', ')}. Allowed types: PDF, DOCX, TXT. Max size: ${MAX_FILE_SIZE_MB}MB.`);
        // Create a new FileList from valid files only, or clear if all are invalid
        const dataTransfer = new DataTransfer();
        validFiles.forEach(file => dataTransfer.items.add(file));
        setNotesFiles(dataTransfer.files.length > 0 ? dataTransfer.files : null);
        e.target.value = ''; // Clear the input field to allow re-selection of the same file if needed after error
      } else {
        setNotesFiles(e.target.files);
      }
    }
  };

  const handleQuestionFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFileError(null); // Clear previous errors
      const { validFiles, invalidFiles } = validateFiles(e.target.files);

      if (invalidFiles.length > 0) {
        setFileError(`Invalid question file(s): ${invalidFiles.join(', ')}. Allowed types: PDF, DOCX, TXT. Max size: ${MAX_FILE_SIZE_MB}MB.`);
        // Create a new FileList from valid files only, or clear if all are invalid
        const dataTransfer = new DataTransfer();
        validFiles.forEach(file => dataTransfer.items.add(file));
        setQuestionFiles(dataTransfer.files.length > 0 ? dataTransfer.files : null);
        e.target.value = ''; // Clear the input field to allow re-selection of the same file if needed after error
      } else {
        setQuestionFiles(e.target.files);
      }
    }
  };

  const calculateTotalHours = () => {
    const numTotalDays = parseInt(totalDays, 10);
    const numHoursPerDay = parseInt(hoursPerDay, 10);
    if (!isNaN(numTotalDays) && !isNaN(numHoursPerDay) && numTotalDays > 0 && numHoursPerDay > 0) {
      return numTotalDays * numHoursPerDay;
    }
    return 0;
  };

  // Function to prepare form data for submission
  const prepareFormData = async (): Promise<FormData | null> => {
    if (!totalDays || !hoursPerDay) {
      alert('Please fill in Total Study Days and Hours Per Day.');
      return null;
    }

    if (fileError) {
      alert('Please resolve file errors before continuing.');
      return null;
    }

    if (!notesFiles || notesFiles.length === 0) {
      alert('Please upload at least one notes file.');
      return null;
    }

    const formData = new FormData();
    
    // Convert string values to integers for the backend
    formData.append('study_duration_days', parseInt(totalDays, 10).toString());
    formData.append('study_hours_per_day', parseInt(hoursPerDay, 10).toString());

    // Add notes files
    Array.from(notesFiles).forEach(file => {
      formData.append('notes', file);
    });

    // Add question files if any
    if (questionFiles && questionFiles.length > 0) {
      Array.from(questionFiles).forEach(file => {
        formData.append('questions', file);
      });
    }

    return formData;
  };

  // Handle preview button click - generate a plan preview and redirect to preview page
  const handlePreview = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();

    const formData = await prepareFormData();
    if (!formData) return;

    try {
      setIsLoading(true);
      
      console.log('Generating study plan preview from backend...');
      console.log('Form data:', {
        study_duration_days: formData.get('study_duration_days'),
        study_hours_per_day: formData.get('study_hours_per_day'),
        notes: formData.getAll('notes').map((file: any) => file.name)
      });
      
      // Call the preview endpoint to generate a study plan preview
      const response = await axios.post(getApiUrl(API_ENDPOINTS.PREVIEW), formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      console.log('Response received:', response.data);
      
      if (response.data && response.data.raw_plan) {
        console.log('Preview generated successfully');
        
        // Store the raw plan in localStorage for the preview page to access
        localStorage.setItem('rawStudyPlanResponse', response.data.raw_plan);
        
        // Navigate to the preview page
        router.push('/study-plan-preview');
      } else {
        throw new Error('No raw plan returned from backend');
      }
    } catch (error) {
      console.error('Error generating preview:', error);
      let errorMessage = 'Failed to generate preview. Please try again.';
      
      if (axios.isAxiosError(error) && error.response) {
        errorMessage = `Error: ${error.response.data?.detail || error.message}`;
      }
      
      alert(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle direct start session button click - upload files, generate plan, and go directly to study session
  const handleStartSession = async () => {
    const formData = await prepareFormData();
    if (!formData) return;
    
    try {
      setIsLoading(true);
      
      // Upload files and generate complete study plan
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (response.data && response.data.frontend_plan) {
        // Save the study plan to context
        setStudyPlan(response.data.frontend_plan);
        
        // Navigate directly to the active study session page
        router.push('/study-session-active');
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('Failed to generate study plan. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form className="space-y-8 p-4 md:p-8 bg-white shadow-lg rounded-lg max-w-lg mx-auto">
      <div className="space-y-4">
        <div>
          <Label htmlFor="totalDays" className="block text-sm font-medium text-gray-700 mb-1">Total Study Days</Label>
          <Input
            type="number"
            id="totalDays"
            name="totalDays"
            value={totalDays}
            onChange={handleTotalDaysChange}
            min="1"
            max="7"
            placeholder="e.g., 7"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            required
          />
        </div>
        <div>
          <Label htmlFor="hoursPerDay" className="block text-sm font-medium text-gray-700 mb-1">Hours Per Day</Label>
          <Input
            type="number"
            id="hoursPerDay"
            name="hoursPerDay"
            value={hoursPerDay}
            onChange={handleHoursPerDayChange}
            min="1"
            max="24"
            placeholder="e.g., 3"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            required
          />
        </div>
      </div>
      <div className="space-y-4">
        <div>
          <Label htmlFor="notesFiles" className="block text-sm font-medium text-gray-700 mb-1">Study Notes (Required)</Label>
          <Input
            type="file"
            id="notesFiles"
            name="notesFiles"
            onChange={handleNotesFilesChange}
            multiple
            className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            required
          />
          <p className="text-xs text-gray-500 mt-1">Upload your study materials (PDF, DOCX, TXT). Max size: {MAX_FILE_SIZE_MB}MB per file.</p>
        </div>

        <div>
          <Label htmlFor="questionFiles" className="block text-sm font-medium text-gray-700 mb-1">Practice Questions (Optional)</Label>
          <Input
            type="file"
            id="questionFiles"
            name="questionFiles"
            onChange={handleQuestionFilesChange}
            multiple
            className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <p className="text-xs text-gray-500 mt-1">Upload practice questions or exercises (PDF, DOCX, TXT). Max size: {MAX_FILE_SIZE_MB}MB per file.</p>
        </div>

        {fileError && (
          <p className="mt-2 text-xs text-red-600">{fileError}</p>
        )}

        {/* Display selected notes files */}
        {notesFiles && notesFiles.length > 0 && !fileError && (
          <div className="mt-2 text-xs text-gray-500 p-2 bg-gray-50 rounded">
            <p className="font-medium">Study Notes ({notesFiles.length} file{notesFiles.length !== 1 ? 's' : ''}):</p>
            <ul className="list-disc pl-5 mt-1">
              {Array.from(notesFiles).map((file, index) => (
                <li key={`notes-${index}`}>- {file.name} ({Math.round(file.size / 1024)} KB)</li>
              ))}
            </ul>
          </div>
        )}

        {/* Display selected question files */}
        {questionFiles && questionFiles.length > 0 && !fileError && (
          <div className="mt-2 text-xs text-gray-500 p-2 bg-gray-50 rounded">
            <p className="font-medium">Practice Questions ({questionFiles.length} file{questionFiles.length !== 1 ? 's' : ''}):</p>
            <ul className="list-disc pl-5 mt-1">
              {Array.from(questionFiles).map((file, index) => (
                <li key={`questions-${index}`}>- {file.name} ({Math.round(file.size / 1024)} KB)</li>
              ))}
            </ul>
          </div>
        )}
      </div>
      { (totalDays && hoursPerDay) && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm font-medium text-blue-700">
            Total Study Hours: <span className="font-bold">{calculateTotalHours()} hours</span>
          </p>
        </div>
      )}
      <div>
        <button
          type="button" // Important: type="button" to prevent form submission
          onClick={handlePreview}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          disabled={!totalDays || !hoursPerDay || !!fileError}
        >
          Preview Plan
        </button>
      </div>

    </form>
  );
};

export default InputForm;