'use client';

import React, { useState, useEffect, useRef, FormEvent } from 'react';
import { useStudyPlan } from '../../../context/StudyPlanContext';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { TaskList } from '@/components/ui/task-list';
import KeyFormulasDisplay from '@/components/ui/key-formulas-display';
import DebugPanel from '@/components/ui/debug-utils';
import axios from 'axios';
// Import API configuration
import { getApiUrl, API_ENDPOINTS } from '@/config/api';
// Import the sample plan for testing
import samplePlanData from '../../data/sample_plan.json';

interface ChatMessage {
  id?: string;
  sender: 'user' | 'ai';
  message: string;
  timestamp?: Date;
  isError?: boolean;
  isStreaming?: boolean;
}

// Custom day navigation button component
const DayButton: React.FC<{
  day: number;
  isActive: boolean;
  onClick: () => void;
  focusArea?: string;
  completed?: boolean;
  totalDays?: number;
}> = ({ day, isActive, onClick, focusArea, completed = false, totalDays = 7 }) => {
  // Calculate the width based on total days (ensure it's responsive)
  const getButtonClass = () => {
    if (isActive) return 'bg-blue-600 text-white border-2 border-blue-400';
    if (completed) return 'bg-green-700/40 text-green-200 border border-green-600/30';
    return 'bg-slate-700/40 text-slate-300 hover:bg-slate-700/60 border border-slate-600/30';
  };
  
  return (
    <button
      className={`flex flex-col items-center justify-center p-2 rounded-lg transition-all ${getButtonClass()}`}
      onClick={onClick}
    >
      <span className="text-sm font-bold">Day {day}</span>
      {focusArea && <span className="text-xs mt-1 opacity-80 text-center">{focusArea}</span>}
      {completed && (
        <span className="mt-1 text-xs bg-green-600/30 px-2 py-0.5 rounded-full text-green-200">
          Completed
        </span>
      )}
    </button>
  );
};

const StudySessionActivePage = () => {
  const { studyPlan, setStudyPlan } = useStudyPlan();
  const router = useRouter();
  const [activeDay, setActiveDay] = useState<number>(0);
  const [activeTopic, setActiveTopic] = useState<number>(0);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { 
      id: 'welcome',
      sender: 'ai', 
      message: `Welcome to your study session! I'm here to help you with your studies. You can ask me questions about the topics you're learning, request explanations, or get help with practice problems.`,
      timestamp: new Date()
    }
  ]);
  const [messageInput, setMessageInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [sessionId, setSessionId] = useState<string>('');
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    console.log('StudySessionActivePage loaded with studyPlan:', studyPlan);
    
    if (!studyPlan) {
      console.warn('No study plan found, redirecting to home');
      router.replace('/');
    } else {
      // Log the structure to help with debugging
      console.log('Study Plan Structure:', {
        hasOverallGoal: !!studyPlan.overallGoal,
        totalDays: studyPlan.totalStudyDays,
        hoursPerDay: studyPlan.hoursPerDay,
        conceptsCount: studyPlan.keyConcepts?.length || 0,
        daysCount: studyPlan.dailyBreakdown?.length || 0,
        hasKeyFormulas: !!studyPlan.keyFormulas && studyPlan.keyFormulas.length > 0,
        hasGeneralTips: !!studyPlan.generalTips && studyPlan.generalTips.length > 0
      });
      
      // Generate a session ID if not already set
      if (!sessionId) {
        setSessionId(`session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`);
      }
      
      // Add a welcome message if there are no messages yet
      if (chatMessages.length === 0) {
        setChatMessages([{ 
          id: 'welcome-message',
          sender: 'ai', 
          message: `Welcome to your study session! I'm here to help you with your studies. You can ask me questions about the topics you're learning, request explanations, or get help with practice problems.`,
          timestamp: new Date()
        }]);
      }
    }
  }, [studyPlan, router, sessionId, chatMessages.length]);

  // Get current day content
  const currentDay = studyPlan?.dailyBreakdown?.[activeDay];
  const currentTopic = currentDay?.items?.[activeTopic];
  
  // Initialize navigation when study plan loads
  useEffect(() => {
    if (studyPlan && studyPlan.dailyBreakdown && studyPlan.dailyBreakdown.length > 0) {
      // Initialize with first day and topic
      setActiveDay(0);
      setActiveTopic(0);
    }
  }, [studyPlan]);
  
  // Scroll to bottom of chat when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
    // Debug log to track chat message updates
    console.log('Chat messages updated:', chatMessages);
  }, [chatMessages]);

  const handleEndSession = () => {
    setStudyPlan(null);
    router.push('/');
  };

  const handleTaskSelect = (task: any) => {
    console.log('Selected task:', task);
    
    // Extract day and topic indices from the task ID
    const taskIdParts = task.id.split('-');
    if (taskIdParts[0] === 'day') {
      const dayIndex = parseInt(taskIdParts[1]) - 1;
      
      // If it's a day task
      if (taskIdParts.length === 2) {
        setActiveDay(dayIndex);
        setActiveTopic(0); // Reset to first topic
      } 
      // If it's a topic task
      else if (taskIdParts[2] === 'topic') {
        const topicIndex = parseInt(taskIdParts[3]) - 1;
        setActiveDay(dayIndex);
        setActiveTopic(topicIndex);
      }
      // If it's a summary task
      else if (taskIdParts[2] === 'summary') {
        setActiveDay(dayIndex);
        // Set to the last topic (which is the summary)
        const lastTopicIndex = (studyPlan?.dailyBreakdown?.[dayIndex]?.items?.length || 0);
        setActiveTopic(lastTopicIndex);
      }
    }
  };
  
  // Helper function to navigate to the next or previous day
  const navigateDay = (direction: 'next' | 'prev') => {
    if (!studyPlan) return;
    
    const totalDays = studyPlan.dailyBreakdown.length;
    
    if (direction === 'next' && activeDay < totalDays - 1) {
      setActiveDay(activeDay + 1);
      setActiveTopic(0); // Reset to first topic
    } else if (direction === 'prev' && activeDay > 0) {
      setActiveDay(activeDay - 1);
      setActiveTopic(0); // Reset to first topic
    }
  };
  
  // Helper function to navigate to the next or previous topic
  const navigateTopic = (direction: 'next' | 'prev') => {
    if (!studyPlan || !currentDay) return;
    
    const totalTopics = currentDay.items.length;
    
    if (direction === 'next' && activeTopic < totalTopics - 1) {
      setActiveTopic(activeTopic + 1);
    } else if (direction === 'prev' && activeTopic > 0) {
      setActiveTopic(activeTopic - 1);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (messageInput.trim() && !isLoading) {
      handleSendMessage(messageInput);
      setMessageInput('');
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;
    
    // Add user message to chat
    const userMessage: ChatMessage = {
      sender: 'user',
      message: text,
      timestamp: new Date()
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setMessageInput('');
    setIsLoading(true);
    
    try {
      // Prepare study materials context
      let studyMaterialsContext = '';
      if (currentTopic && currentTopic.details) {
        studyMaterialsContext = currentTopic.details;
      }
      
      // Prepare study plan context - focus on current day and topic
      let studyPlanContext = '';
      if (currentDay && currentTopic) {
        studyPlanContext = JSON.stringify({
          currentDay: {
            day: activeDay + 1,
            focusArea: currentDay.focusArea,
            currentTopic: currentTopic
          },
          overallGoal: studyPlan?.overallGoal,
          keyFormulas: studyPlan?.keyFormulas,
          keyConcepts: studyPlan?.keyConcepts
        });
      }
      
      // Create a placeholder message for response
      const messageId = `msg-${Date.now()}`;
      const initialMessage: ChatMessage = {
        id: messageId,
        sender: 'ai',
        message: '',
        timestamp: new Date(),
        isStreaming: true
      };
      
      setChatMessages(prev => [...prev, initialMessage]);
      
      // Decide whether to use streaming or regular response
      const useStreaming = true; // Set to false to disable streaming
      
      if (useStreaming) {
        // Use streaming for a more interactive experience
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_query: text,
            session_id: sessionId,
            study_materials_context: studyMaterialsContext,
            study_plan_context: studyPlanContext,
            stream: true
          }),
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const contentType = response.headers.get('Content-Type') || '';
        
        // Check if we got a streaming response or a regular JSON response
        console.log('Response content type:', contentType);
        if (contentType.includes('text/event-stream')) {
          // Process the streaming response
          const reader = response.body?.getReader();
          if (!reader) throw new Error('Response body is not readable');
          
          let fullMessage = '';
          
          try {
            // Read the stream
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              
              // Convert the chunk to text
              const chunk = new TextDecoder().decode(value);
              console.log('Received chunk:', chunk); // Debug log
              
              // Split by newlines and process each line
              const lines = chunk.split('\n').filter(line => line.trim());
              
              // Process each line (each line is a JSON object)
              for (const line of lines) {
                try {
                  const data = JSON.parse(line);
                  console.log('Parsed data:', data); // Debug log
                  
                  if (data.chunk) {
                    // Append the chunk to the full message
                    fullMessage += data.chunk + ' ';
                    
                    // Update the streaming message
                    setChatMessages(prev => prev.map(msg => 
                      msg.id === messageId 
                        ? { ...msg, message: fullMessage.trim() }
                        : msg
                    ));
                  }
                  
                  // If this is the last chunk, mark the message as complete
                  if (data.done) {
                    console.log('Stream complete, final message:', fullMessage.trim());
                    setChatMessages(prev => prev.map(msg => 
                      msg.id === messageId 
                        ? { ...msg, isStreaming: false }
                        : msg
                    ));
                  }
                } catch (e) {
                  console.error('Error parsing streaming response line:', line, e);
                }
              }
            }
          } catch (e) {
            console.error('Error reading stream:', e);
            // If there's an error in streaming, make sure we still show the message
            setChatMessages(prev => prev.map(msg => 
              msg.id === messageId 
                ? { ...msg, message: fullMessage.trim() || 'Error receiving complete response', isStreaming: false, isError: !fullMessage.trim() }
                : msg
            ));
          }
        } else {
          // We got a regular JSON response instead of a stream
          console.log('Received regular JSON response instead of stream');
          const jsonData = await response.json();
          console.log('Response data:', jsonData);
          
          // For debugging - log all chat messages
          console.log('Current chat messages:', chatMessages);
          
          // Check if we have a valid AI response
          if (jsonData && jsonData.ai_response) {
            // Replace the placeholder message with the actual response
            setChatMessages(prev => prev.map(msg => 
              msg.id === messageId 
                ? { 
                    ...msg, 
                    message: jsonData.ai_response, 
                    isStreaming: false
                  }
                : msg
            ));
            
            // Log the updated messages for debugging
            console.log('Updated chat messages with AI response');
          } else {
            // Handle error case
            setChatMessages(prev => prev.map(msg => 
              msg.id === messageId 
                ? { 
                    ...msg, 
                    message: 'No response received from AI assistant', 
                    isStreaming: false,
                    isError: true
                  }
                : msg
            ));
          }
        }
      } else {
        // Use regular axios for non-streaming response
        const response = await axios.post('/api/chat', {
          user_query: text,
          session_id: sessionId,
          study_materials_context: studyMaterialsContext,
          study_plan_context: studyPlanContext,
          stream: false
        });
        
        // Update the message with the response
        setChatMessages(prev => prev.map(msg => 
          msg.id === messageId 
            ? { 
                ...msg, 
                message: response.data.ai_response || 'No response received', 
                isStreaming: false,
                isError: !response.data.ai_response
              }
            : msg
        ));
      }
    } catch (error) {
      console.error('Error sending message to AI:', error);
      
      // Add error message to chat
      const errorMessage: ChatMessage = {
        sender: 'ai',
        message: 'Sorry, I encountered an error processing your request. Please try again later.',
        timestamp: new Date(),
        isError: true
      };
      
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate the daily breakdown for a more convenient access
  const dailyBreakdown = studyPlan?.dailyBreakdown || [];

  return (
    <div className="min-h-screen bg-slate-900 text-white pb-20">
      <header className="bg-slate-800/90 backdrop-blur-sm sticky top-0 z-10 border-b border-slate-700/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-bold text-blue-300">Study Session</h1>
              {currentDay && currentDay.focusArea && (
                <h2 className="text-lg font-medium text-white bg-blue-600/30 px-3 py-1 rounded-md">
                  {currentDay.focusArea}
                </h2>
              )}
            </div>
            <div className="flex space-x-2">
              <Button 
                onClick={() => {
                  // Load the sample plan data for testing
                  // Type cast to handle any potential format differences
                  const typedSamplePlan = samplePlanData as any;
                  setStudyPlan(typedSamplePlan);
                  console.log('Loaded sample plan data for testing');
                }} 
                variant="secondary" 
                size="sm"
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                Load Sample Data
              </Button>
              <Button 
                onClick={handleEndSession} 
                variant="outline" 
                size="sm"
                className="border-red-500/50 text-red-300 hover:bg-red-900/20"
              >
                End Session
              </Button>
            </div>
          </div>
          
          {/* Simple Day Counter */}
          <div className="flex justify-center mb-3">
            <span className="text-sm text-white bg-blue-600/40 px-4 py-1.5 rounded-full">
              Day {activeDay + 1} of {studyPlan?.totalStudyDays || 0}
            </span>
          </div>
          
          {/* Day Navigation Bar - Center Aligned */}
          <div className="flex justify-center gap-2 overflow-x-auto pb-4 hide-scrollbar">
            {/* Only show days up to the totalStudyDays value */}
            {studyPlan?.dailyBreakdown?.slice(0, studyPlan?.totalStudyDays || studyPlan?.dailyBreakdown?.length).map((day, index) => (
              <DayButton 
                key={index}
                day={day.day || index + 1}
                isActive={index === activeDay}
                onClick={() => {
                  setActiveDay(index);
                  setActiveTopic(0);
                }}
                focusArea={day.focusArea}
                completed={index < activeDay}
                totalDays={studyPlan?.totalStudyDays || 0}
              />
            ))}

          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Panel - Tasks */}
        <div className="lg:col-span-3 bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden flex flex-col border border-slate-700/50 shadow-lg">
          <div className="p-4 border-b border-slate-700/50">
            <h2 className="text-lg font-semibold text-blue-300">Study Tasks</h2>
          </div>
          <div className="flex-1 overflow-auto p-4">
            {studyPlan ? (
              <TaskList onTaskSelect={handleTaskSelect} />
            ) : (
              <div className="text-center p-4 text-slate-400">
                <p>No study plan loaded.</p>
                <p className="mt-2">Please try regenerating your study plan.</p>
              </div>
            )}
          </div>
        </div>

        {/* Center Panel - Content */}
        <div className="lg:col-span-6 flex flex-col space-y-4">
          {/* Day Content */}
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden flex flex-col border border-slate-700/50 shadow-lg">
            <div className="p-4 border-b border-slate-700/50 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-blue-300">
                {currentDay?.daySummary || `Day ${activeDay + 1}`}
              </h2>
            </div>
            <div className="flex-1 overflow-auto p-6">
              {/* Current Topic Content */}
              {currentTopic && (
                <div className="mb-6 space-y-4">
                  <div className="flex justify-between items-center mb-2">
                    <h2 className="text-xl font-semibold text-blue-300">{currentTopic.topic}</h2>
                    <div className="flex space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => navigateTopic('prev')}
                        disabled={activeTopic === 0}
                      >
                        Previous
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => navigateTopic('next')}
                        disabled={!currentDay || activeTopic >= (currentDay.items.length - 1)}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                  
                  {/* Topic Details */}
                  <div className="p-4 bg-slate-800/40 rounded-lg border border-slate-700/50">
                    {/* Duration and Priority */}
                    {(currentTopic.durationMinutes || currentTopic.priority) && (
                      <div className="flex items-center mb-3 space-x-3">
                        {currentTopic.durationMinutes && (
                          <span className="px-3 py-1 bg-slate-700/60 rounded-full text-xs text-blue-200">
                            {currentTopic.durationMinutes} minutes
                          </span>
                        )}
                        {currentTopic.priority && (
                          <span className={`px-3 py-1 rounded-full text-xs ${
                            currentTopic.priority === 'high' 
                              ? 'bg-red-900/50 text-red-200' 
                              : currentTopic.priority === 'medium' 
                                ? 'bg-yellow-900/50 text-yellow-200' 
                                : 'bg-green-900/50 text-green-200'
                          }`}>
                            {currentTopic.priority} priority
                          </span>
                        )}
                      </div>
                    )}
                    
                    {/* Description */}
                    <div className="mb-4">
                      <h3 className="text-md font-medium text-blue-300 mb-2">Description</h3>
                      <p className="text-slate-200">{currentTopic.details}</p>
                    </div>
                    
                    {/* Learning Objectives */}
                    {currentTopic.learningObjectives && currentTopic.learningObjectives.length > 0 && (
                      <div className="mb-4">
                        <h3 className="text-md font-medium text-blue-300 mb-2">Learning Objectives</h3>
                        <ul className="list-disc pl-5 space-y-1 text-slate-200">
                          {currentTopic.learningObjectives.map((objective, idx) => (
                            <li key={idx}>{objective}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* Resource Links */}
                    {currentTopic.resources && currentTopic.resources.length > 0 && (
                      <div>
                        <h3 className="text-md font-medium text-blue-300 mb-2">Resources</h3>
                        <ul className="list-disc pl-5 space-y-1">
                          {currentTopic.resources.map((resource, idx) => {
                            // Handle both string resources and resource objects
                            const resourceTitle = typeof resource === 'string' ? resource : resource.title;
                            const resourceUrl = typeof resource === 'string' ? resource : resource.url;
                            const resourceDesc = typeof resource === 'string' ? null : resource.description;
                            
                            return (
                              <li key={idx} className="text-slate-300">
                                {resourceUrl ? (
                                  <a 
                                    href={resourceUrl} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-blue-400 hover:text-blue-300 transition-colors duration-200 hover:underline"
                                  >
                                    {resourceTitle}
                                  </a>
                                ) : (
                                  <span className="text-blue-300">{resourceTitle}</span>
                                )}
                                {resourceDesc && (
                                  <p className="text-xs text-slate-400 mt-1">{resourceDesc}</p>
                                )}
                              </li>
                            );
                          })}
                        </ul>
                      </div>
                    )}
                    
                    {/* Summary Section (if this is the summary item) */}
                    {currentTopic.isSummary && currentDay && currentDay.learningGoals && currentDay.learningGoals.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-slate-700/50">
                        <h3 className="text-md font-medium text-blue-300 mb-2">Learning Goals for Today</h3>
                        <ul className="list-disc pl-5 space-y-1 text-slate-200">
                          {currentDay.learningGoals.map((goal, idx) => (
                            <li key={idx}>{goal}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Chat Interface */}
          <div className="bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden flex flex-col h-96 border border-slate-700/50 shadow-lg">
            <div className="p-4 border-b border-slate-700/50">
              <h2 className="text-lg font-semibold text-blue-300">Study Assistant</h2>
            </div>
            <div className="flex-1 overflow-auto p-4 space-y-4" ref={chatContainerRef}>
              {chatMessages.map((msg, i) => (
                <div key={i} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div 
                    className={`max-w-[80%] rounded-2xl p-3 ${msg.sender === 'user' 
                      ? 'bg-blue-600/80 text-white border border-blue-500/30' 
                      : msg.isError 
                        ? 'bg-red-900/30 text-red-200 border border-red-800/30'
                        : 'bg-slate-700/80 text-slate-200 border border-slate-600/30'}`}
                  >
                    <p className="whitespace-pre-line">{msg.message}</p>
                    
                    <div className="flex justify-between items-center mt-1">
                      {/* Show typing indicator for streaming messages */}
                      {msg.isStreaming && (
                        <div className="flex space-x-1">
                          <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></div>
                          <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                          <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                      )}
                      
                      {/* Timestamp */}
                      {msg.timestamp && (
                        <p className="text-xs text-slate-300 text-right opacity-70 ml-auto">
                          {new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] rounded-2xl p-3 bg-slate-700/80 text-slate-200 border border-slate-600/30">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce"></div>
                      <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div className="p-4 border-t border-slate-700/50 bg-slate-800/40">
              <form onSubmit={handleSubmit} className="flex space-x-2">
                <input
                  type="text"
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1 bg-slate-700/60 text-white rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500/50 border border-slate-600/50"
                />
                <Button 
                  type="submit" 
                  disabled={isLoading || !messageInput.trim()}
                  className="rounded-full bg-blue-600/80 hover:bg-blue-500 text-white border-none"
                >
                  Send
                </Button>
              </form>
            </div>
          </div>
        </div>

        {/* Right Panel - Key Formulas and Points */}
        <div className="lg:col-span-3 bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden flex flex-col border border-slate-700/50 shadow-lg">
          <div className="p-4 border-b border-slate-700/50">
            <h2 className="text-lg font-semibold text-blue-300">Key Information</h2>
          </div>
          <div className="flex-1 p-4">
            <KeyFormulasDisplay />
          </div>
        </div>
      </main>
    </div>
  );
};

export default StudySessionActivePage;
