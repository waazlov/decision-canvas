interface BrandMarkProps {
  mode?: "icon" | "lockup";
}

export function BrandMark({ mode = "lockup" }: BrandMarkProps) {
  const icon = (
    <svg
      aria-hidden="true"
      className="brandmark-icon"
      viewBox="0 0 48 48"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="brandmark-gradient" x1="8" x2="40" y1="8" y2="40">
          <stop offset="0%" stopColor="var(--accent)" />
          <stop offset="100%" stopColor="var(--accent-violet)" />
        </linearGradient>
      </defs>
      <rect
        fill="rgba(255,255,255,0.8)"
        height="36"
        rx="12"
        stroke="rgba(15,23,42,0.08)"
        width="36"
        x="6"
        y="6"
      />
      <path
        d="M16 16H32M16 24H32M16 32H32M16 16V32M24 16V32M32 16V32"
        opacity="0.14"
        stroke="var(--text-strong)"
        strokeWidth="1.2"
      />
      <path
        d="M14 29L21 24L26 26L34 17"
        fill="none"
        stroke="url(#brandmark-gradient)"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="3"
      />
      <circle cx="34" cy="17" fill="var(--accent-violet)" r="3.5" />
    </svg>
  );

  if (mode === "icon") {
    return <span className="brandmark brandmark--icon-only">{icon}</span>;
  }

  return (
    <span className="brandmark">
      {icon}
      <span className="brandmark-wordmark">
        <span className="brandmark-wordmark__name">DecisionCanvas</span>
        <span className="brandmark-wordmark__tag">Analytics copilot</span>
      </span>
    </span>
  );
}
