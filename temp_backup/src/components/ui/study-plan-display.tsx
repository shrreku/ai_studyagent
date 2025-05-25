// /Users/shreyashkumar/coding/projects/studyagent_v2/src/src/components/ui/study-plan-display.tsx

import React from 'react';
// Correctly import StudyPlan and other necessary types from the context
import { StudyPlan, StudyPlanCoreConcept, StudyPlanDailySchedule, StudyPlanItem, StudyPlanKeyFormula } from '../../../context/StudyPlanContext';

interface StudyPlanDisplayProps {
  plan: StudyPlan | null; // Use StudyPlan from context
}

export const StudyPlanDisplay: React.FC<StudyPlanDisplayProps> = ({ plan }) => {
  if (!plan) {
    return <p className="text-slate-500 italic">Loading study plan or no plan available...</p>;
  }

  return (
    <div className="prose prose-slate max-w-none dark:prose-invert">
      <h2 className="text-2xl font-bold text-slate-800 mb-4">Study Plan: {plan.overallGoal}</h2>

      <section className="mb-6">
        <h3 className="text-xl font-semibold text-slate-700 mb-2">Overall Goal</h3>
        <p className="text-sm text-gray-700">{plan.overallGoal}</p>
      </section>

      <section className="mb-6">
        <h3 className="text-xl font-semibold text-slate-700 mb-2">Key Concepts</h3>
        {plan.keyConcepts?.length > 0 ? (
          <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
            {plan.keyConcepts.map((concept: StudyPlanCoreConcept, index: number) => (
              <li key={`concept-${index}`}>
                <strong>{concept.concept}:</strong> {concept.explanation}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-600 italic">No key concepts provided.</p>
        )}
      </section>

      <section className="mb-6">
        <h3 className="text-xl font-semibold text-slate-700 mb-2">Daily Breakdown ({plan.totalStudyDays} Days, ~{plan.hoursPerDay} hrs/day)</h3>
        {plan.dailyBreakdown?.length > 0 ? (
          <div className="space-y-3">
            {plan.dailyBreakdown.map((dayPlan: StudyPlanDailySchedule, index: number) => (
              <div key={`day-${index}`} className="p-3 border rounded-md bg-slate-50">
                <h4 className="font-semibold text-slate-600">Day {dayPlan.day}</h4>
                {dayPlan.daySummary && <p className="text-xs text-gray-500 mb-1 italic">{dayPlan.daySummary}</p>}
                <ul className="list-disc pl-5 mt-1 space-y-1 text-sm text-gray-700">
                  {dayPlan.items.map((item: StudyPlanItem, itemIndex: number) => (
                    <li key={`item-${index}-${itemIndex}`}>
                      <strong>{item.topic}:</strong> {item.details} (Est: {item.estimatedTimeHours}h)
                      {item.resources && item.resources.length > 0 && (
                        <ul className="list-circle pl-5 text-xs text-gray-600">
                          {item.resources.map((resource: string, rIndex: number) => (
                            <li key={`resource-${index}-${itemIndex}-${rIndex}`}>{resource}</li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-600 italic">Daily breakdown not available.</p>
        )}
      </section>

      {plan.keyFormulas && plan.keyFormulas.length > 0 && (
        <section className="mb-6">
          <h3 className="text-xl font-semibold text-slate-700 mb-2">Key Formulas & Concepts</h3>
          <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
            {plan.keyFormulas.map((formula: StudyPlanKeyFormula, index: number) => (
              <li key={`formula-${index}`}>
                <strong>{formula.formula_name}:</strong> {formula.description}
                {formula.usage_context && <span className="text-xs italic"> (Usage: {formula.usage_context})</span>}
              </li>
            ))}
          </ul>
        </section>
      )}

      {plan.generalTips && plan.generalTips.length > 0 && (
        <section className="mb-6">
          <h3 className="text-xl font-semibold text-slate-700 mb-2">General Tips</h3>
          <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
            {plan.generalTips.map((tip: string, index: number) => (
              <li key={`tip-${index}`}>{tip}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
};