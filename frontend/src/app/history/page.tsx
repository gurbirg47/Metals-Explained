const historySections = [
    {
        title: 'Gold and Inflation: The 1970s Paradigm',
        content: `The 1970s established gold's reputation as an inflation hedge. Following the end of Bretton Woods in 1971 and amid oil shocks, gold rose from $35 to over $800 by 1980. However, this was not merely an inflation story—it was a story of negative real rates. Nominal yields failed to keep pace with inflation, making gold relatively attractive.

When Paul Volcker raised rates aggressively in the early 1980s, real rates turned sharply positive, and gold entered a two-decade bear market. The lesson: gold responds to real rates, not inflation alone.`,
    },
    {
        title: 'The 2000s Bull Market and Dollar Weakness',
        content: `Gold's bull market from 2001 to 2011 coincided with persistent dollar weakness and declining real rates. The Fed cut rates after the dot-com bust and kept them low during the housing boom. Post-2008, quantitative easing further expanded liquidity and suppressed real yields.

Gold peaked above $1,900 in 2011 as real rates reached deeply negative levels. When the Fed began signaling taper in 2013, gold declined sharply—a preview of how sensitive the metal is to policy shifts.`,
    },
    {
        title: 'The 2020 Pandemic Surge',
        content: `Gold reached all-time highs above $2,070 in August 2020 as central banks globally slashed rates and expanded balance sheets in response to COVID-19. Real rates collapsed, the dollar weakened, and uncertainty peaked.

The subsequent pullback in 2021-2022 reflected rising real rates as inflation surged and the Fed began tightening. This demonstrated that even in inflationary environments, gold can decline if real rates rise faster than inflation.`,
    },
    {
        title: 'Silver\'s Industrial Sensitivity',
        content: `Silver\'s 2020-2021 behavior illustrated its dual nature. It rallied with gold during the initial pandemic surge but outperformed as industrial demand recovered. The green energy transition narrative—silver's role in solar panels—provided an additional tailwind.

However, silver's 2022 weakness showed that during aggressive Fed tightening, its industrial beta can dominate, causing it to trade more like a cyclical commodity than a monetary metal.`,
    },
    {
        title: 'Central Bank Demand',
        content: `Post-2022, central bank gold purchases reached multi-decade highs, particularly from emerging market central banks seeking to reduce dollar exposure. This structural demand provided a floor under gold prices even during periods of rising real rates.

This shift suggests the traditional real-rate framework may need adjustment for an era of de-dollarization and geopolitical fragmentation.`,
    },
];

export default function HistoryPage() {
    return (
        <div>
            <h1>What History Tends to Show</h1>
            <p className="text-[var(--text-muted)] mb-6">
                Historical patterns in precious metals markets, with mechanisms explained.
            </p>

            <div className="space-y-8">
                {historySections.map((section, i) => (
                    <div key={i} className="p-6 bg-[rgba(255,255,255,0.02)] rounded-lg">
                        <h3 className="text-[var(--signal-accent)] mb-4 pb-2 border-b border-[rgba(255,255,255,0.1)]">
                            {section.title}
                        </h3>
                        <div className="text-[var(--text-muted)] leading-relaxed whitespace-pre-line">
                            {section.content}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
