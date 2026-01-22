const glossary = [
    {
        term: 'Real Interest Rate',
        what: 'The nominal interest rate minus expected inflation. Represents the true return on fixed-income investments after accounting for purchasing power erosion.',
        why: 'Gold competes with interest-bearing assets. Higher real rates increase the opportunity cost of holding gold; lower or negative real rates make gold more attractive.',
        today: 'Rising real rates typically pressure gold; falling real rates typically support gold. Watch TIPS yields for a market-implied measure.',
    },
    {
        term: 'DXY (U.S. Dollar Index)',
        what: 'A trade-weighted index measuring the dollar against six major currencies (EUR, JPY, GBP, CAD, SEK, CHF). Euro-heavy (~58% weight).',
        why: 'Gold is priced in dollars globally. A stronger dollar makes gold more expensive for non-U.S. buyers, reducing demand.',
        today: 'DXY above 105 often coincides with gold weakness; DXY below 100 often coincides with gold strength. The relationship is not mechanical but tends to hold.',
    },
    {
        term: 'Breakeven Inflation',
        what: 'The difference between nominal Treasury yields and TIPS yields. Represents the market\'s implied expectation for average CPI inflation over the bond\'s term.',
        why: 'Rising breakevens can support gold if they signal inflation fears. However, if nominal yields rise faster than breakevens, real rates rise and gold may decline.',
        today: 'Breakevens rising while nominal yields stable = bullish for gold. Breakevens rising but nominal yields rising faster = potentially bearish.',
    },
    {
        term: 'VIX (Volatility Index)',
        what: 'A measure of implied volatility on S&P 500 options. Often called the "fear gauge."',
        why: 'Elevated VIX can signal risk-off sentiment, which typically supports gold as a safe haven. However, extreme VIX spikes (>40) can trigger broad deleveraging affecting all assets.',
        today: 'VIX 15-20 = calm. VIX 25-35 = elevated uncertainty, often gold-supportive. VIX >40 = panic, gold can initially rise then decline with deleveraging.',
    },
    {
        term: 'Fed Funds Rate',
        what: 'The target range for overnight interbank lending rates, set by the Federal Reserve. The primary tool of U.S. monetary policy.',
        why: 'Fed rate decisions directly affect short-term rates and influence the entire yield curve. Hawkish surprises (higher rates) strengthen the dollar and raise real rates, pressuring gold.',
        today: 'Watch Fed dot plots and meeting statements. Market pricing via Fed Funds futures indicates expected path.',
    },
    {
        term: 'Gold/Silver Ratio',
        what: 'The number of silver ounces required to buy one ounce of gold. Calculated as gold price / silver price.',
        why: 'Indicates relative valuation between the two metals. Historically oscillates between 40 and 90. High ratios suggest silver is cheap relative to gold.',
        today: 'Ratio >80: silver historically undervalued. Ratio <60: silver historically overvalued. Use as a relative value indicator, not a timing tool.',
    },
];

export default function TerminologyPage() {
    return (
        <div>
            <h1>Terminology</h1>
            <p className="text-[var(--text-muted)] mb-6">
                Definitions, relevance, and interpretation guidance for key terms.
            </p>

            <div className="space-y-6">
                {glossary.map((item, i) => (
                    <div key={i} className="section-card">
                        <h4 className="text-[var(--text-primary)] mb-3">{item.term}</h4>
                        <p className="text-[var(--text-muted)] mb-2">
                            <strong>Definition:</strong> {item.what}
                        </p>
                        <p className="text-[var(--text-muted)] mb-2">
                            <strong>Relevance:</strong> {item.why}
                        </p>
                        <p className="text-[var(--signal-accent)]">
                            <strong>Interpretation:</strong> {item.today}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
}
