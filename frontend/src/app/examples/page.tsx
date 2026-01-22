const scenarios = [
    {
        title: 'Classic Rate-Driven Selloff',
        charts: 'Gold -1.2%, 10Y Yield +12bp, DXY +0.4%',
        explanation: 'This is the textbook bearish scenario for gold. Rising yields increase the opportunity cost of holding non-yielding assets. The stronger dollar compounds the pressure by making gold more expensive for international buyers. Both drivers are aligned, making the gold decline explicable and mechanistically coherent. No single factor is sufficient, but together they form a consistent narrative.',
    },
    {
        title: 'Risk-Off Rally',
        charts: 'Gold +1.5%, 10Y Yield -8bp, DXY -0.3%, VIX +15%',
        explanation: 'A flight to safety. Equity volatility surged, investors sold risk assets, and capital flowed into safe havens. Yields fell as traders bought Treasuries; the dollar weakened on risk-off flows; gold rallied as the preferred hard-asset hedge. All macro inputs align with a fear-driven narrative. The magnitude of the gold move is proportionate to the volatility spike.',
    },
    {
        title: 'Conflict Between Drivers',
        charts: 'Gold +0.4%, 10Y Yield +5bp, DXY -0.6%',
        explanation: 'Here the drivers diverge. Rising yields are typically gold-negative, but the falling dollar is gold-positive. Gold rose modestly, suggesting the dollar move dominated—or other factors (positioning, technical levels) contributed. This scenario calls for humility. The explanation is less clean, and the move may reflect cross-currents rather than a single theme.',
    },
    {
        title: 'Fed Pivot Speculation',
        charts: 'Gold +2.1%, 10Y Yield -15bp, DXY -1.0%',
        explanation: 'A large, coordinated move across all inputs consistent with expectations for easier monetary policy. Perhaps weak economic data or dovish Fed commentary sparked speculation of rate cuts. Gold surged on falling real rates and a weaker dollar. This is a high-conviction day—the narrative is clear and the magnitude of moves is proportionate across assets.',
    },
    {
        title: 'Low-Conviction Noise',
        charts: 'Gold +0.1%, 10Y Yield +2bp, DXY -0.1%',
        explanation: 'On days like this, there is no story. All moves are within noise bands. Attempting to explain a 0.1% gold move is an exercise in false precision. The correct interpretation is: nothing meaningful happened. Markets traded sideways. Wait for a larger move before constructing narratives.',
    },
];

export default function ExamplesPage() {
    return (
        <div>
            <h1>Example Scenarios</h1>
            <p className="text-[var(--text-muted)] mb-6">
                Educational case studies demonstrating analytical reasoning.
            </p>

            <div className="space-y-6">
                {scenarios.map((s, i) => (
                    <div key={i} className="p-6 bg-[rgba(255,255,255,0.03)] rounded-lg border border-[rgba(255,255,255,0.1)]">
                        <h4 className="text-[var(--signal-accent)] mb-3">{s.title}</h4>
                        <p className="mono text-sm text-[var(--text-muted)] mb-4">
                            <em>Observable Conditions: {s.charts}</em>
                        </p>
                        <p className="text-[var(--text-primary)] leading-relaxed">{s.explanation}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
