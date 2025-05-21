'use client';

import React, { useState, ChangeEvent, useEffect } from 'react';
import { Input } from '@/components/ui/input'; // Assuming Shadcn UI structure
import { Label } from '@/components/ui/label';   // Assuming Shadcn UI structure
import { Button } from '@/components/ui/button'; // Assuming Shadcn UI structure
import { useRouter } from 'next/navigation'; // Import useRouter

// Define a basic structure for the study plan
const InputForm: React.FC = () => {
  const router = useRouter(); // Initialize router
  const [totalDays, setTotalDays] = useState<string>(''); // Store as string to allow empty input
  const [hoursPerDay, setHoursPerDay] = useState<string>(''); // Store as string to allow empty input
  const [studyMaterials, setStudyMaterials] = useState<FileList | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState<boolean>(false);
  const [previewData, setPreviewData] = useState<StudyPlan | null>(null);

  // Define a basic structure for the study plan
  interface StudyPlanTopic {
    name: string;
    estimatedHours: number;
    resources: string[];
  }

  interface StudyPlanDay {
    day: number;
    topics: StudyPlanTopic[];
    dailySummary?: string;
  }

  interface StudyPlan {
    totalStudyDays: number;
    hoursPerDay: number;
    overallGoal: string;
    schedule: StudyPlanDay[];
    generalTips?: string[];
  }

  const ALLOWED_FILE_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
  const MAX_FILE_SIZE_MB = 5;

  const handleTotalDaysChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Allow empty string or positive integers
    if (value === '' || (/^\d+$/.test(value) && parseInt(value, 10) >= 1)) {
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFileError(null); // Clear previous errors
      const files = e.target.files;
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

      if (invalidFiles.length > 0) {
        setFileError(`Invalid file(s): ${invalidFiles.join(', ')}. Allowed types: PDF, DOCX, TXT. Max size: ${MAX_FILE_SIZE_MB}MB.`);
        // Create a new FileList from valid files only, or clear if all are invalid
        const dataTransfer = new DataTransfer();
        validFiles.forEach(file => dataTransfer.items.add(file));
        setStudyMaterials(dataTransfer.files.length > 0 ? dataTransfer.files : null);
        e.target.value = ''; // Clear the input field to allow re-selection of the same file if needed after error
      } else {
        setStudyMaterials(files);
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

  const handlePreview = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault(); // Prevent form submission if it's part of a form
    // Basic validation before showing preview
    if (!totalDays || !hoursPerDay) {
      alert('Please fill in Total Study Days and Hours Per Day before previewing.');
      return;
    }
    if (fileError) {
      alert('Please resolve file errors before previewing.');
      return;
    }
    setShowPreview(true);
    // Later, this will trigger fetching/generating the plan
    // For now, let's set some mock data for preview
    const numTotalDays = parseInt(totalDays, 10) || 0;
    const numHoursPerDay = parseInt(hoursPerDay, 10) || 0;

    const mockPlan: StudyPlan = {
      totalStudyDays: numTotalDays,
      hoursPerDay: numHoursPerDay,
      overallGoal: "Successfully master the provided study materials.",
      schedule: [
        {
          day: 1,
          topics: [
            { name: "Introduction to Topic A", estimatedHours: numHoursPerDay > 0 ? numHoursPerDay / 2 : 0, resources: ["Chapter 1 of PDF1.pdf"] },
            { name: "Deep Dive into Topic B", estimatedHours: numHoursPerDay > 0 ? numHoursPerDay / 2 : 0, resources: ["Section 2 of Notes.docx"] },
          ],
          dailySummary: "Covered foundational concepts and an initial deep dive."
        },
        // Add more days as needed for a more complete mock preview
      ],
      generalTips: ["Take regular breaks.", "Review notes daily."]
    };
    setPreviewData(mockPlan);
  };

  const handleStartSession = () => {
    // Basic validation before attempting to start session
    if (!totalDays || !hoursPerDay) {
      alert('Please fill in Total Study Days and Hours Per Day.');
      return;
    }
    if (fileError) {
      alert('Please resolve file errors before starting a session.');
      return;
    }
    if (!previewData) {
      alert('Please preview the plan before starting a session.');
      return;
    }
    // Later, this will handle form submission to backend and navigation
    // alert('Form submitted (mock)! Navigating to study session page (mock)...');
    // Example: router.push('/study-session'); // Requires Next.js router
    // For now, we'll just navigate to a placeholder route
    router.push('/study-session-active'); // Navigate to the new page
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
      <div>
        <Label htmlFor="studyMaterials" className="block text-sm font-medium text-gray-700 mb-1">Study Materials (Optional)</Label>
        <Input
          type="file"
          id="studyMaterials"
          name="studyMaterials"
          onChange={handleFileChange}
          multiple
          className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        {fileError && (
          <p className="mt-2 text-xs text-red-600">{fileError}</p>
        )}
        {studyMaterials && studyMaterials.length > 0 && !fileError && (
          <div className="mt-2 text-xs text-gray-500">
            <p>{studyMaterials.length} file(s) selected:</p>
            <ul>
              {Array.from(studyMaterials).map((file, index) => (
                <li key={index}>- {file.name} ({Math.round(file.size / 1024)} KB)</li>
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
      {showPreview && previewData && (
        <div className="mt-8 p-4 border border-gray-200 rounded-md bg-gray-50">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Study Plan Preview:</h3>
          
          <div className="space-y-3 text-sm">
            <p><span className="font-semibold">Overall Goal:</span> {previewData.overallGoal}</p>
            <p><span className="font-semibold">Total Study Days:</span> {previewData.totalStudyDays}</p>
            <p><span className="font-semibold">Hours Per Day:</span> {previewData.hoursPerDay}</p>
          </div>

          <div className="mt-6">
            <h4 className="text-md font-semibold text-gray-700 mb-2">Daily Schedule:</h4>
            {previewData.schedule.map((dayPlan) => (
              <div key={dayPlan.day} className="mb-4 p-3 border border-gray-300 rounded-md bg-white">
                <h5 className="font-semibold text-gray-700">Day {dayPlan.day}</h5>
                <ul className="list-disc list-inside ml-4 mt-1 space-y-1 text-xs text-gray-600">
                  {dayPlan.topics.map((topic, index) => (
                    <li key={index}>
                      {topic.name} ({topic.estimatedHours} hrs)
                      {topic.resources && topic.resources.length > 0 && (
                        <ul className="list-circle list-inside ml-4 text-gray-500">
                          {topic.resources.map((resource, rIndex) => (
                            <li key={rIndex}>{resource}</li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
                {dayPlan.dailySummary && (
                  <p className="mt-2 text-xs italic text-gray-500">Summary: {dayPlan.dailySummary}</p>
                )}
              </div>
            ))}
          </div>

          {previewData.generalTips && previewData.generalTips.length > 0 && (
            <div className="mt-6">
              <h4 className="text-md font-semibold text-gray-700 mb-2">General Tips:</h4>
              <ul className="list-disc list-inside ml-4 space-y-1 text-sm text-gray-600">
                {previewData.generalTips.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>
            </div>
          )}
          <div className="mt-6">
            <button
              type="button" // Or type="submit" if this button submits the form
              onClick={handleStartSession}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              disabled={!previewData} // Disabled until plan is previewed
            >
              Start Study Session
            </button>
          </div>
        </div>
      )}
    </form>
  );
};

export default InputForm;