'use client';

import samplePlanRaw from '../data/sample_plan.json';
import { StudyPlan, StudyPlanKeyFormula } from '../../context/StudyPlanContext';

// Helper function to fix any type compatibility issues in the sample data
export function prepareSamplePlan(): StudyPlan {
  // Deep clone the sample data to avoid modifying the original
  const sampleData = JSON.parse(JSON.stringify(samplePlanRaw)) as any;
  
  // Fix keyFormulas compatibility issues if present
  if (sampleData.keyFormulas) {
    sampleData.keyFormulas = sampleData.keyFormulas.map((formula: any) => {
      // Create a new formula object that matches the StudyPlanKeyFormula interface
      const newFormula: StudyPlanKeyFormula = {
        formula_name: formula.formula_name,
        formula: formula.formula,
        description: formula.description,
        usage_context: formula.usage_context
      };
      
      // Handle variables safely by creating a proper Record<string, string>
      if (formula.variables) {
        newFormula.variables = {};
        Object.keys(formula.variables).forEach(key => {
          if (newFormula.variables) {
            newFormula.variables[key] = formula.variables[key] || '';
          }
        });
      }
      
      return newFormula;
    });
  }
  
  return sampleData as StudyPlan;
}

// Export the processed sample plan
export const samplePlan = prepareSamplePlan();
