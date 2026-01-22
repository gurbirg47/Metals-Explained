const drivers = [
    {
        title: 'Real Interest Rates',
        what: 'The nominal yield on Treasury securities minus expected inflation, typically measured using TIPS breakevens or survey-based inflation expectations.',
        why: 'Gold pays no yield. When real rates rise, the opportunity cost of holding gold increases, making interest-bearing assets more attractive. When real rates fall or turn negative, gold becomes relatively more appealing as a store of value.',
        signal: 'Rising real rates tend to pressure gold; falling real rates tend to support gold.',
    },
    {
        title: 'U.S. Dollar (DXY)',
        what: 'A trade-weighted index of the U.S. dollar against a basket of major currencies, dominated by the euro.',
        why: 'Gold is priced in dollars globally. A stronger dollar makes gold more expensive for foreign buyers, reducing demand. A weaker dollar makes gold cheaper internationally and often reflects monetary easing, which supports gold.',
        signal: 'Rising DXY tends to pressure gold; falling DXY tends to support gold.',
    },
    {
        title: 'Inflation Expectations',
        what: 'Market-implied or survey-based measures of expected future inflation, often derived from breakeven rates.',
        why: 'Gold is historically viewed as an inflation hedge. When investors expect purchasing power to erode, they may allocate to gold as a store of value. However, the relationship is nuanced—gold responds more to real rates than nominal inflation alone.',
        signal: 'Rising inflation expectations can support gold, especially if nominal yields do not rise commensurately.',
    },
    {
        title: 'Risk Sentiment',
        what: 'The aggregate willingness of market participants to take risk, often proxied by equity volatility (VIX), credit spreads, or flows into safe-haven assets.',
        why: 'During periods of market stress, investors seek assets perceived as safe. Gold has historically served this function. Silver is more ambiguous—it can act as a safe haven but also sells off with risk assets due to its industrial exposure.',
        signal: 'Rising fear typically supports gold; equity selloffs may initially support gold before broader deleveraging affects all assets.',
    },
    {
        title: 'Central Bank Policy',
        what: 'The stance of major central banks, particularly the Federal Reserve, regarding interest rates and balance sheet policy.',
        why: 'Hawkish policy (rate hikes, QT) tends to strengthen the dollar and raise real rates, pressuring gold. Dovish policy (rate cuts, QE) tends to weaken the dollar and lower real rates, supporting gold.',
        signal: 'Fed pivot expectations often drive gold rallies; unexpected hawkishness can trigger sharp corrections.',
    },
];

export default function DriversPage() {
    return (
        <div>
            <h1>What Moves Gold & Silver</h1>
            <p className="text-[var(--text-muted)] mb-6">
                Understanding the macroeconomic forces that influence precious metals prices.
            </p>

            <div className="space-y-6">
                {drivers.map((driver, i) => (
                    <div key={i} className="section-card">
                        <h4 className="text-[var(--text-primary)] mb-3">{driver.title}</h4>
                        <p className="text-[var(--text-muted)] mb-2">
                            <strong>Definition:</strong> {driver.what}
                        </p>
                        <p className="text-[var(--text-muted)] mb-2">
                            <strong>Mechanism:</strong> {driver.why}
                        </p>
                        <p className="text-[var(--signal-accent)]">
                            <strong>Market Signal:</strong> {driver.signal}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
}
