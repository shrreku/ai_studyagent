'use client';

import React from 'react';
import { Loader2 } from 'lucide-react';

const PreviewGenerationAnimation: React.FC = () => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full">
        <div className="flex flex-col items-center text-center">
          <Loader2 className="h-12 w-12 text-indigo-600 animate-spin mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Generating Study Plan</h3>
          
          <div className="space-y-2 w-full">
            <div className="relative pt-1">
              <div className="flex mb-2 items-center justify-between">
                <div>
                  <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-indigo-600 bg-indigo-100">
                    Processing your materials
                  </span>
                </div>
              </div>
              <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-indigo-100">
                <div className="animate-pulse w-full h-full bg-indigo-500 opacity-75"></div>
              </div>
            </div>
          </div>
          
          <div className="mt-4 text-sm text-gray-600">
            <p>Our AI expert is analyzing your materials and crafting a personalized study plan...</p>
            <div className="mt-3 flex flex-col space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-indigo-600 animate-pulse"></div>
                <span>Extracting key concepts</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-indigo-600 animate-pulse delay-150"></div>
                <span>Organizing learning materials</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-indigo-600 animate-pulse delay-300"></div>
                <span>Creating daily schedule</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-indigo-600 animate-pulse delay-500"></div>
                <span>Finalizing your study plan</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PreviewGenerationAnimation;
