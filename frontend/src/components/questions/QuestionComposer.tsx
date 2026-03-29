import type { ExampleQuestion } from "../../types/ui";

interface QuestionComposerProps {
  question: string;
  exampleQuestions: ExampleQuestion[];
  isSubmitting?: boolean;
  onQuestionChange?: (question: string) => void;
  onSubmit?: () => void;
}

export function QuestionComposer({
  question,
  exampleQuestions,
  isSubmitting = false,
  onQuestionChange,
  onSubmit,
}: QuestionComposerProps) {
  return (
    <section className="surface-card">
      <div className="section-heading">
        <div>
          <p className="section-heading__eyebrow">Step 2</p>
          <h2>Ask a business question</h2>
        </div>
      </div>

      <div className="question-composer">
        <p className="question-helper">
          Ask about trends, top segments, drop-offs, or anomalies.
        </p>
        <textarea
          placeholder="Why did conversion drop last month?"
          rows={4}
          value={question}
          onChange={(event) => onQuestionChange?.(event.target.value)}
        />
        <p className="question-helper question-helper--subtle">
          DecisionCanvas routes your question into a specific analysis path and falls back to an overview when confidence is low.
        </p>

        <div className="preset-list">
          {exampleQuestions.map((item) => (
            <button
              className="preset-chip"
              key={item.id}
              type="button"
              onClick={() => onQuestionChange?.(item.label)}
            >
              {item.label}
            </button>
          ))}
        </div>

        <button className="button button--primary" disabled={isSubmitting} type="button" onClick={onSubmit}>
          {isSubmitting ? "Generating dashboard..." : "Generate dashboard"}
        </button>
      </div>
    </section>
  );
}
