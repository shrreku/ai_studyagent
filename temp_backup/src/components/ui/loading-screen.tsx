'use client';

import React from 'react';

interface LoadingScreenProps {
  message?: string;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message = 'Processing your study plan...'
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-800 to-slate-600 text-white flex flex-col items-center justify-center p-8">
      <div className="flex flex-col items-center">
        <div className="mb-6">
          <div className="relative w-16 h-16">
            <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <div className="absolute top-2 left-2 w-12 h-12 border-4 border-cyan-300 border-t-transparent rounded-full animate-spin"></div>
          </div>
        </div>
        <h2 className="text-2xl font-semibold mb-2">Please Wait</h2>
        <p className="text-slate-300 text-center max-w-md">{message}</p>
        <p className="text-slate-400 text-sm mt-8">This may take a few moments...</p>
      </div>
    </div>
  );
};

export default LoadingScreen;
