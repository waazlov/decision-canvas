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
          <h2>Choose a supported analysis question</h2>
        </div>
      </div>

      <div className="question-composer">
        <p className="question-helper">
          Best results come from questions about trends, top or weak segments, drop-offs, comparisons, or anomalies.
        </p>
        <div className="supported-question-types" aria-label="Supported question types">
          <span className="tag">Trends</span>
          <span className="tag">Top segments</span>
          <span className="tag">Underperformance</span>
          <span className="tag">Comparisons</span>
          <span className="tag">Drop-offs</span>
          <span className="tag">Anomalies</span>
        </div>
        <textarea
          placeholder="Example: Which region performs best?"
          rows={4}
          value={question}
          onChange={(event) => onQuestionChange?.(event.target.value)}
        />
        <p className="question-helper question-helper--subtle">
          DecisionCanvas maps your prompt to a supported analysis path. If the question is vague or unsupported, it falls back to a broader overview instead of pretending certainty.
        </p>
        <p className="question-helper question-helper--subtle">
          It does not yet answer arbitrary business questions perfectly, so use the suggested prompts as a guide.
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
