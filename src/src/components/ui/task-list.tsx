// /Users/shreyashkumar/coding/projects/studyagent_v2/src/src/components/ui/task-list.tsx
'use client';

import React, { useState, useEffect } from 'react'; // Added useEffect

export interface Task {
  id: string;
  label: string;
  completed: boolean;
  subTasks?: Task[];
  details?: string;
  estimatedTimeHours?: number;
  durationMinutes?: number;
  resources?: any[];
  priority?: string;
  learningObjectives?: string[];
  isSummary?: boolean;
  focusArea?: string;
}

import { StudyPlanDailySchedule, StudyPlanItem, useStudyPlan } from '../../../context/StudyPlanContext'; // Import context and types

interface TaskListProps {
  // tasks: Task[]; // Will be derived from context
  onTaskSelect?: (task: Task) => void; // Renamed from onTaskClick to onTaskSelect to match usage in page.tsx
}

export const TaskList: React.FC<TaskListProps> = ({ onTaskSelect }) => { // Renamed from onTaskClick
  const { studyPlan } = useStudyPlan();
  const [taskList, setTaskList] = useState<Task[]>([]);

  useEffect(() => {
    if (studyPlan && studyPlan.dailyBreakdown) {
      
      const transformedTasks = studyPlan.dailyBreakdown.map((dayItem: any, index: number) => {
        // Get all the study items for this day
        const studyItems = dayItem.items || [];
        
        // Create subtasks for each study item
        const subTasks = studyItems.map((item: any, subIndex: number) => ({
          id: `day-${dayItem.day || index + 1}-topic-${subIndex + 1}`,
          label: item.topic,
          details: item.details,
          estimatedTimeHours: item.estimatedTimeHours,
          durationMinutes: item.durationMinutes,
          resources: item.resources,
          priority: item.priority,
          learningObjectives: item.learningObjectives,
          completed: item.isCompleted || false,
          isSummary: false
        }));
        
        // Add summary as the last task, but only if it doesn't already exist as a topic
        // and if daySummary exists
        if (dayItem.daySummary && !studyItems.some((item: any) => item.topic === 'Summary')) {
          subTasks.push({
            id: `day-${dayItem.day || index + 1}-summary`,
            label: 'Summary',
            details: dayItem.daySummary,
            learningObjectives: dayItem.learningGoals || [],
            completed: false,
            isSummary: true
          });
        }
        
        return {
          id: `day-${dayItem.day || index + 1}`,
          label: `Day ${dayItem.day || index + 1}`,
          focusArea: dayItem.focusArea,
          completed: false, // Initial completion state
          subTasks: subTasks,
        };
      });
      
      setTaskList(transformedTasks);
    }
  }, [studyPlan]);

  const handleToggle = (taskId: string) => {
    const updateTasksRecursive = (items: Task[]): Task[] => {
      return items.map(task => {
        if (task.id === taskId) {
          return { ...task, completed: !task.completed };
        }
        if (task.subTasks) {
          return { ...task, subTasks: updateTasksRecursive(task.subTasks) };
        }
        return task;
      });
    };
    setTaskList(updateTasksRecursive(taskList));
  };

  // No longer needed as we're not using collapsible cards

    // This function is not needed as we're using collapsedDays state

  const renderTasks = (items: Task[], level = 0) => {
    return (
      <ul className={`${level > 0 ? 'ml-4 pl-4 border-l border-slate-700/50 space-y-1' : 'space-y-2'}`}>
        {items.map(task => {
          // Check if this is a day-level task (level 0 and has subtasks)
          const isDayTask = level === 0;
          
          return (
            <li key={task.id} className={`
              ${isDayTask ? 'bg-slate-800/60 rounded-lg border border-slate-700/30 overflow-hidden' : ''}
              ${task.isSummary ? 'mt-2 pt-2 border-t border-slate-700/30' : ''}
            `}>
              <div className={`
                ${isDayTask ? 'p-3' : 'py-1.5'}
                ${task.completed ? 'opacity-80' : ''}
              `}>
                <div className="flex items-center justify-between">
                  {/* Only show checkbox for non-day tasks */}
                  {!isDayTask && (
                    <input
                      type="checkbox"
                      id={task.id}
                      checked={task.completed}
                      onChange={() => handleToggle(task.id)}
                      className="mr-3 h-4 w-4 text-blue-500 bg-slate-800/70 border-slate-600 rounded focus:ring-blue-500/30 focus:ring-offset-slate-800 shrink-0"
                    />
                  )}
                  
                  <span 
                    className={`
                      flex-1 cursor-pointer 
                      ${task.isSummary ? 'text-blue-300 font-medium text-sm' : ''}
                      ${isDayTask ? 'text-blue-300 font-semibold' : 'text-slate-300 text-sm'}
                      ${task.completed && !isDayTask ? 'line-through text-slate-500' : ''}
                    `}
                    onClick={() => onTaskSelect && onTaskSelect(task)}
                  >
                    {task.label}
                    {task.focusArea && <span className="ml-2 text-xs text-blue-400">({task.focusArea})</span>}
                    {task.durationMinutes && <span className="ml-2 text-xs text-gray-400">{task.durationMinutes} min</span>}
                    {task.priority && (
                      <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${
                        task.priority === 'high' 
                          ? 'bg-red-900/50 text-red-200' 
                          : task.priority === 'medium' 
                            ? 'bg-yellow-900/50 text-yellow-200' 
                            : 'bg-green-900/50 text-green-200'
                      }`}>
                        {task.priority}
                      </span>
                    )}
                  </span>
                </div>
              </div>
              
              {/* Always render subtasks */}
              {task.subTasks && task.subTasks.length > 0 && (
                <div className="mt-1">
                  {renderTasks(task.subTasks, level + 1)}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    );
  };

  return <div className="w-full max-h-[calc(100vh-200px)] overflow-y-auto pr-2 pb-6 h-full">{renderTasks(taskList)}</div>;
};

// Example Usage (can be removed or kept for testing):
const SampleTasks: Task[] = [
  {
    id: 'task-1',
    label: 'Chapter 1: Introduction to Heat Transfer',
    completed: false,
    subTasks: [
      { id: 'task-1-1', label: 'Read Sections 1.1-1.3', completed: false },
      { id: 'task-1-2', label: 'Review Key Concepts', completed: false },
    ],
  },
  {
    id: 'task-2',
    label: 'Chapter 2: Conduction',
    completed: false,
    subTasks: [
      { id: 'task-2-1', label: 'Understand Fourier\'s Law', completed: false },
      { id: 'task-2-2', label: 'Solve problems 2.1-2.5', completed: false },
    ],
  },
  {
    id: 'task-3',
    label: 'Chapter 3: Convection',
    completed: true,
  },
];

interface TaskListExampleProps {
  onTaskSelect?: (instruction: string) => void; // Prop to receive the click handler, expects an instruction string
}

export const TaskListExample: React.FC<TaskListExampleProps> = ({ onTaskSelect: onExampleTaskSelect }) => { // Renamed prop to avoid conflict
    const handleExampleTaskClick = (task: Task) => {
        if (onExampleTaskSelect) {
            onExampleTaskSelect(task.label); 
        } else {
            console.log('Task clicked in example (standalone):', task);
            alert(`Task clicked (standalone): ${task.label}. Instruction would be: ${task.label}`);
        }
    };
    return <TaskList onTaskSelect={handleExampleTaskClick} />;
};