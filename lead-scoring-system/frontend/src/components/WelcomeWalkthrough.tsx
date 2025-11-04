import { useState, useEffect } from "react";

interface WalkthroughStep {
  title: string;
  description: string;
  target?: string; // CSS selector for element to highlight
}

interface WelcomeWalkthroughProps {
  role: "sales_rep" | "manager" | "admin";
  onComplete: () => void;
}

export function WelcomeWalkthrough({ role, onComplete }: WelcomeWalkthroughProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  const steps: Record<string, WalkthroughStep[]> = {
    sales_rep: [
      {
        title: "Welcome to LeadScore AI!",
        description:
          "Let's take a quick tour of your dashboard. You can upload leads, view AI scores, and manage your pipeline all in one place.",
      },
      {
        title: "Upload Leads",
        description:
          "Click 'Upload Leads' to add leads via CSV or enter them individually. All leads are automatically scored with AI.",
        target: "[data-walkthrough='upload-button']",
      },
      {
        title: "Your Statistics",
        description:
          "See your total leads, hot/warm/cold breakdown, and average score at a glance. These update automatically as you add leads.",
        target: "[data-walkthrough='stats']",
      },
      {
        title: "Leads Table",
        description:
          "View all your leads in one place. Sort by score, status, or date. Click on any lead to see detailed information.",
        target: "[data-walkthrough='leads-table']",
      },
      {
        title: "You're All Set!",
        description:
          "Start uploading leads to see AI scoring in action. Need help? Check the documentation or contact support.",
      },
    ],
    manager: [
      {
        title: "Welcome to LeadScore AI!",
        description:
          "As a manager, you have oversight of your entire team. Let's explore what you can do.",
      },
      {
        title: "Team Statistics",
        description:
          "See overall team performance, total leads, and team averages. Monitor how your team is doing at a glance.",
        target: "[data-walkthrough='team-stats']",
      },
      {
        title: "Sales Rep Performance",
        description:
          "Compare all your sales reps side-by-side. See who's performing best and identify top performers.",
        target: "[data-walkthrough='reps-table']",
      },
      {
        title: "You're Ready!",
        description:
          "Use this dashboard to track team performance and help your reps succeed. All data updates in real-time.",
      },
    ],
    admin: [
      {
        title: "Welcome to LeadScore AI!",
        description:
          "As the owner, you have complete system access. Let's see what you can do with your dashboard.",
      },
      {
        title: "System Overview",
        description:
          "See complete system statistics including total users, leads, and conversion rates across your entire dealership.",
        target: "[data-walkthrough='system-stats']",
      },
      {
        title: "Top Performers",
        description:
          "Track which sales reps are performing best. Use this data to recognize top performers and identify training opportunities.",
        target: "[data-walkthrough='top-performers']",
      },
      {
        title: "Source Analytics",
        description:
          "See where your leads are coming from. Use this to optimize your marketing and lead generation efforts.",
        target: "[data-walkthrough='sources']",
      },
      {
        title: "You're All Set!",
        description:
          "Use this dashboard to make data-driven decisions and grow your dealership. Everything updates in real-time.",
      },
    ],
  };

  const roleSteps = steps[role] || steps.sales_rep;
  const step = roleSteps[currentStep];

  const handleNext = () => {
    if (currentStep < roleSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const handleComplete = () => {
    setIsVisible(false);
    // Mark walkthrough as completed in localStorage
    localStorage.setItem("walkthrough_completed", "true");
    localStorage.setItem("walkthrough_role", role);
    onComplete();
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="relative w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
        <button
          onClick={handleSkip}
          className="absolute right-4 top-4 text-slate-400 hover:text-slate-600"
          aria-label="Close"
        >
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="mb-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-2xl font-bold text-slate-900">{step.title}</h2>
            <span className="text-sm text-slate-500">
              {currentStep + 1} / {roleSteps.length}
            </span>
          </div>
          <p className="text-slate-600">{step.description}</p>
        </div>

        {/* Progress bar */}
        <div className="mb-6 h-2 w-full rounded-full bg-slate-200">
          <div
            className="h-2 rounded-full bg-navy-600 transition-all duration-300"
            style={{ width: `${((currentStep + 1) / roleSteps.length) * 100}%` }}
          />
        </div>

        {/* Navigation buttons */}
        <div className="flex justify-between">
          <button
            onClick={handleSkip}
            className="rounded-lg px-4 py-2 text-slate-600 hover:bg-slate-100"
          >
            Skip Tour
          </button>
          <div className="flex gap-2">
            {currentStep > 0 && (
              <button
                onClick={() => setCurrentStep(currentStep - 1)}
                className="rounded-lg border border-slate-300 px-4 py-2 text-slate-700 hover:bg-slate-50"
              >
                Previous
              </button>
            )}
            <button
              onClick={handleNext}
              className="rounded-lg bg-navy-600 px-4 py-2 font-semibold text-white hover:bg-navy-700"
            >
              {currentStep === roleSteps.length - 1 ? "Get Started" : "Next"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

