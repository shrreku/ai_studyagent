// Study Plan Interfaces for TypeScript

export interface CoreConcept {
  name: string;
  explanation: string;
  importance?: string;
  related_concepts?: string[];
}

export interface StudyResource {
  title: string;
  url?: string;
  type?: string;
  description?: string;
}

export interface StudyItem {
  topic: string;
  description: string;
  duration_minutes: number;
  resource?: (string | StudyResource)[];
  is_completed?: boolean;
}

export interface DailySchedule {
  day: number;
  date?: string;
  focus_area: string;
  study_item: StudyItem[];
  summary: string;
}

export interface KeyFormula {
  name: string;
  formula: string;
  description: string;
}

export interface StructuredStudyPlan {
  overall_goal: string;
  total_study_day: number;
  hour_per_day: number;
  core_concepts: CoreConcept[];
  daily_schedule: DailySchedule[];
  general_tip: string[];
  key_formulas?: KeyFormula[];
}

// Example study plan for reference
export const exampleStudyPlan: StructuredStudyPlan = {
  overall_goal: "Master the fundamental concepts of convection heat and mass transfer, focusing on boundary layer theory, dimensionless parameters, and practical applications.",
  total_study_day: 7,
  hour_per_day: 2.0,
  core_concepts: [
    {
      name: "Boundary Layer Development",
      explanation: "Understanding the development of velocity, thermal, and concentration boundary layers and their significance in convection heat and mass transfer.",
      importance: "Fundamental to analyzing convection processes.",
      related_concepts: ["Convection coefficients", "Laminar vs. turbulent flow"]
    },
    {
      name: "Convection Coefficients",
      explanation: "Local and average convection coefficients (h, hm) and their applications in heat and mass transfer.",
      importance: "Key to quantifying heat and mass transfer rates.",
      related_concepts: ["Boundary layer", "Nusselt number"]
    },
    {
      name: "Dimensionless Parameters",
      explanation: "Key dimensionless numbers (Re, Pr, Sc, Nu, Sh, Le) and their roles in heat and mass transfer.",
      importance: "Essential for scaling and comparing different systems.",
      related_concepts: ["Nusselt number", "Sherwood number"]
    }
  ],
  daily_schedule: [
    {
      day: 1,
      date: null,
      focus_area: "Introduction to Boundary Layers",
      study_item: [
        {
          topic: "Boundary Layer Definition",
          description: "Definition and physical meaning of boundary layers.",
          duration_minutes: 30,
          resource: ["Section 6.1-6.2"],
          is_completed: false
        },
        {
          topic: "Convection Coefficients",
          description: "Local vs. average convection coefficients (h, hm).",
          duration_minutes: 30,
          resource: ["Section 6.1-6.2"],
          is_completed: false
        },
        {
          topic: "Example 6.1",
          description: "Relationship between local and average coefficients.",
          duration_minutes: 30,
          resource: ["Example 6.1"],
          is_completed: false
        }
      ],
      summary: "Introduction to boundary layers and convection coefficients, including practical examples and derivations."
    },
    {
      day: 2,
      date: null,
      focus_area: "Laminar vs. Turbulent Flow",
      study_item: [
        {
          topic: "Flow Characteristics",
          description: "Characteristics of laminar and turbulent flow.",
          duration_minutes: 30,
          resource: ["Section 6.3"],
          is_completed: false
        },
        {
          topic: "Transition Criteria",
          description: "Transition criteria (Rex,c ≈ 5×10^5).",
          duration_minutes: 20,
          resource: ["Section 6.3"],
          is_completed: false
        }
      ],
      summary: "Understanding laminar and turbulent flow characteristics, including transition criteria and practical calculations."
    }
  ],
  general_tip: [
    "Sketch boundary layer development for different scenarios to visualize concepts.",
    "Always identify relevant dimensionless parameters before solving problems.",
    "Create flashcards for key dimensionless parameters and equations."
  ],
  key_formulas: [
    {
      name: "Reynolds Number",
      formula: "Re = ρvL/μ",
      description: "Ratio of inertial forces to viscous forces"
    },
    {
      name: "Nusselt Number",
      formula: "Nu = hL/k",
      description: "Dimensionless heat transfer coefficient"
    },
    {
      name: "Boundary Layer Thickness",
      formula: "δ/x ∝ 1/√(Re_x)",
      description: "Relationship between boundary layer thickness and Reynolds number"
    }
  ]
};
