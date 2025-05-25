'use client';

import React from 'react';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';

interface FormulaProps {
  formula: string;
  block?: boolean;
  className?: string;
}

/**
 * Formula component for rendering LaTeX formulas
 * Uses KaTeX for rendering
 * 
 * @param formula - The LaTeX formula to render
 * @param block - Whether to render as a block (centered, larger) or inline
 * @param className - Additional CSS classes
 */
const Formula: React.FC<FormulaProps> = ({ formula, block = false, className = '' }) => {
  // Remove any unnecessary escaping that might have been added
  const cleanFormula = formula
    .replace(/\\\\([^\\])/g, '\\$1') // Replace double backslashes with single backslashes
    .trim();

  try {
    return block ? (
      <div className={`my-4 ${className}`}>
        <BlockMath math={cleanFormula} />
      </div>
    ) : (
      <span className={className}>
        <InlineMath math={cleanFormula} />
      </span>
    );
  } catch (error) {
    console.error('Error rendering LaTeX formula:', error);
    return (
      <code className="bg-red-50 text-red-600 px-2 py-1 rounded">
        Error rendering formula: {formula}
      </code>
    );
  }
};

export default Formula;
