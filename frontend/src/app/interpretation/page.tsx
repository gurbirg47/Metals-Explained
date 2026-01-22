const steps = [
    {
        step: 1,
        title: 'Identify the Price Move',
        desc: 'Start by quantifying what happened in the market.',
        detail: 'Before explaining why gold moved, establish how much it moved and in what direction. Use precise percentages and dollar amounts. Distinguish between intraday noise (<0.3%) and meaningful moves (>0.5%).',
    },
    {
        step: 2,
        title: 'Check the Macro Inputs',
        desc: 'Review rates, dollar, and volatility for corroborating signals.',
        detail: 'Look at 10-year yields, DXY, and VIX. Are they moving in a direction consistent with the gold move? If yields rose and gold fell, the move is explicable. If yields rose and gold rose, there may be an offsetting factor worth identifying.',
    },
    {
        step: 3,
        title: 'Rank the Drivers',
        desc: 'Determine which macro factor had the largest move.',
        detail: 'The driver with the largest relative move is usually the primary explanation. A 10bp move in 10-year yields is typically more significant than a 0.2% move in DXY. Weight by typical sensitivity.',
    },
    {
        step: 4,
        title: 'Check for Conflicts',
        desc: 'Note when drivers are sending divergent signals.',
        detail: 'If yields rose (bearish for gold) but dollar fell (bullish for gold), the outcome depends on which driver dominated. Conflicts make explanation harder and suggest caution in drawing strong conclusions.',
    },
    {
        step: 5,
        title: 'Formulate the Narrative',
        desc: 'Construct a coherent story linking cause and effect.',
        detail: 'The narrative should follow: "Gold moved [direction] by [amount]. The primary driver appears to be [factor], as evidenced by [data]. This is consistent with the mechanism that [explanation]."',
    },
    {
        step: 6,
        title: 'Acknowledge Uncertainty',
        desc: 'Recognize the limits of single-day analysis.',
        detail: 'Markets are noisy. A single day\'s move may not have a clean explanation. Use language like "appears to reflect" or "is consistent with" rather than "was caused by." Avoid false precision.',
    },
];

const principles = [
    {
        title: 'Correlation is Not Causation',
        content: 'Just because yields and gold moved together today does not prove a causal link. Look for mechanism plausibility and pattern consistency over time.',
    },
    {
        title: 'Size Matters',
        content: 'Small moves (<0.3% for gold, <3bp for yields) are often noise. Reserve explanatory effort for meaningful moves where attribution is more likely to be correct.',
    },
    {
        title: 'Context Matters',
        content: 'A 0.5% gold move on a quiet day is different from a 0.5% move on FOMC day. Consider what information arrived and whether the move is proportionate to the news.',
    },
    {
        title: 'Humility in Hindsight',
        content: 'It is always easier to explain moves after they happen than to predict them. Resist the temptation to retrofit narratives with excessive confidence.',
    },
];

const mistakes = [
    'Insisting on a single explanation when drivers are conflicting.',
    'Using causal language when only correlation is observed.',
    'Ignoring that small moves may be noise rather than signal.',
    'Assuming yesterday\'s driver is today\'s driver without verification.',
    'Confusing what gold "should" do with what it actually did.',
    'Treating correlations during crises as reliable for normal periods.',
    'Ignoring positioning and technical factors in short-term moves.',
];

export default function InterpretationPage() {
    return (
        <div>
            <h1>How to Interpret the Charts</h1>
            <p className="text-[var(--text-muted)] mb-6">
                A disciplined analytical framework for market interpretation.
            </p>

            <h3 className="mt-8 mb-6 border-b border-[var(--text-muted)] pb-2">Analytical Framework</h3>

            <div className="space-y-6">
                {steps.map((step) => (
                    <div key={step.step} className="p-5 bg-[rgba(255,255,255,0.02)] rounded-lg flex gap-4">
                        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-[var(--signal-accent)] text-[var(--bg-void)] font-bold flex items-center justify-center font-['Barlow_Condensed'] text-lg">
                            {step.step}
                        </div>
                        <div>
                            <h4 className="text-[var(--text-primary)] mb-2">{step.title}</h4>
                            <p className="text-[var(--text-muted)] mb-2">{step.desc}</p>
                            <p className="text-[var(--text-muted)] text-sm leading-relaxed">{step.detail}</p>
                        </div>
                    </div>
                ))}
            </div>

            <h3 className="mt-10 mb-6 border-b border-[var(--text-muted)] pb-2">Interpretation Principles</h3>

            <div className="space-y-4">
                {principles.map((p, i) => (
                    <div key={i} className="section-card border-l-[var(--signal-macro)]">
                        <h4 className="text-[var(--signal-macro)] mb-2">{p.title}</h4>
                        <p className="text-[var(--text-muted)]">{p.content}</p>
                    </div>
                ))}
            </div>

            <h3 className="mt-10 mb-6 border-b border-[var(--text-muted)] pb-2">Common Analytical Errors</h3>

            <ul className="space-y-2">
                {mistakes.map((m, i) => (
                    <li key={i} className="text-[var(--signal-down)]">✗ {m}</li>
                ))}
            </ul>
        </div>
    );
}
