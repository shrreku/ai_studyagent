'use client';

import React, { useState, useEffect } from 'react';
import { useStudyPlan, StudyPlanKeyFormula } from '../../../context/StudyPlanContext';
import Formula from './formula'; // Import the LaTeX formula component

interface FormulaItem {
  id: string;
  name: string;
  equation: string; // LaTeX string or plain text
  description?: string;
  isKeyConcept?: boolean;
  variables?: Record<string, string> | undefined;
}

interface KeyFormulasDisplayProps {
  title?: string;
}

const KeyFormulasDisplay: React.FC<KeyFormulasDisplayProps> = ({ 
  title = "Key Formulas & Concepts"
}) => {
  const { studyPlan } = useStudyPlan();
  const [formulas, setFormulas] = useState<FormulaItem[]>([]);

  // Convert study plan data to formula items
  useEffect(() => {
    if (studyPlan && studyPlan.keyFormulas && Array.isArray(studyPlan.keyFormulas)) {
      const transformedFormulas = studyPlan.keyFormulas.map((formula: StudyPlanKeyFormula, index: number) => ({
        id: `formula-${index + 1}`,
        name: formula.formula_name || formula.name || 'Formula',
        equation: formula.formula || formula.description || '', // First try formula field, then description
        description: formula.usage_context || formula.description || '', // First try usage_context, then description
        variables: formula.variables || {}
      }));
      
      // Also add key concepts as formulas for display
      let allItems = [...transformedFormulas];
      
      if (studyPlan.keyConcepts && Array.isArray(studyPlan.keyConcepts)) {
        const conceptFormulas = studyPlan.keyConcepts.map((concept, index) => ({
          id: `concept-${index + 1}`,
          name: concept.concept || 'Concept',
          equation: '', // No equation for concepts
          description: concept.explanation || '',
          isKeyConcept: true,
          variables: {} // Add empty variables object to match the interface
        }));
        
        allItems = [...allItems, ...conceptFormulas];
      }
      
      setFormulas(allItems);
    } else {
      setFormulas([]); // Clear formulas if no plan or no keyFormulas
    }
  }, [studyPlan]);

  // No longer needed as we're not using collapsible cards

  if (!formulas || formulas.length === 0) {
    return (
      <div className="p-4 bg-slate-800/40 rounded-lg border border-slate-700/30 backdrop-blur-sm">
        <h3 className="text-md font-semibold text-blue-300 mb-2">{title}</h3>
        <p className="text-sm text-slate-400">No key formulas available for this topic yet.</p>
      </div>
    );
  }

  // Group formulas by type (formulas vs concepts)
  const keyFormulas = formulas.filter(f => !f.isKeyConcept);
  const keyConcepts = formulas.filter(f => f.isKeyConcept);
  
  return (
    <div className="space-y-6 max-h-[calc(100vh-200px)] overflow-y-auto pr-2 pb-6 h-full">
      {/* Key Formulas Section */}
      {keyFormulas.length > 0 && (
        <div>
          <h3 className="text-md font-semibold text-blue-300 mb-3 border-b border-blue-500/30 pb-1 sticky top-0 bg-slate-900/90 backdrop-blur-sm z-10">Key Formulas</h3>
          <div className="space-y-4">
            {keyFormulas.map((formula) => (
              <div key={formula.id} className="bg-slate-700/50 rounded-lg p-4 border border-slate-600/50">
                <h3 className="text-blue-300 font-medium mb-3">{formula.name}</h3>
                
                <div className="bg-slate-800/70 rounded p-3 border border-slate-700/50 overflow-x-auto">
                  <Formula formula={formula.equation} block={true} />
                </div>
                
                {formula.description && (
                  <p className="mt-2 text-slate-300 text-sm">{formula.description}</p>
                )}
                
                {formula.variables && Object.keys(formula.variables).length > 0 && (
                  <div className="mt-3 pt-2 border-t border-slate-700/30">
                    <p className="text-xs font-medium text-blue-300 mb-1">Variables:</p>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(formula.variables).map(([key, value]) => (
                        <div key={key} className="text-xs">
                          <span className="text-blue-200 font-mono">{key}</span>: <span className="text-slate-300">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Key Concepts Section */}
      {keyConcepts.length > 0 && (
        <div>
          <h3 className="text-md font-semibold text-blue-300 mb-3 border-b border-blue-500/30 pb-1 sticky top-0 bg-slate-900/90 backdrop-blur-sm z-10 mt-6">Key Concepts</h3>
          <div className="space-y-3">
            {keyConcepts.map((concept) => (
              <div key={concept.id} className="p-4 bg-slate-800/40 rounded-lg border border-slate-700/30 backdrop-blur-sm transition-all duration-200 hover:border-blue-500/30 hover:bg-slate-800/60">
                <p className="text-sm font-medium text-blue-300 mb-2">{concept.name}</p>
                {concept.description && (
                  <p className="text-sm text-slate-300 leading-relaxed">{concept.description}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Show message if no formulas or concepts */}
      {formulas.length === 0 && (
        <div className="p-4 bg-slate-800/40 rounded-lg border border-slate-700/30 backdrop-blur-sm h-full flex items-center justify-center">
          <p className="text-sm text-slate-400">No key formulas or concepts available for this topic yet.</p>
        </div>
      )}
    </div>
  );
};

export default KeyFormulasDisplay;