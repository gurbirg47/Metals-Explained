const resources = [
    { name: 'Federal Reserve Economic Data (FRED)', desc: 'Free access to U.S. Treasury yields, inflation breakevens, dollar indices, and economic indicators.' },
    { name: 'TradingView', desc: 'Charting platform for visualizing gold, silver, DXY, and yield time series with technical overlays.' },
    { name: 'CME FedWatch', desc: 'Tool for analyzing market-implied probabilities of Federal Reserve rate decisions.' },
    { name: 'World Gold Council', desc: 'Research and data on gold demand, central bank holdings, and ETF flows.' },
    { name: 'CFTC Commitment of Traders', desc: 'Weekly positioning data for gold and silver futures, useful for understanding speculative flows.' },
    { name: 'Daily Treasury Real Yield Curve Rates', desc: 'Official U.S. Treasury data on TIPS-implied real yields by maturity.' },
];

export default function ResourcesPage() {
    return (
        <div>
            <h1>Resources</h1>
            <p className="text-[var(--text-muted)] mb-6">
                Professional tools and references for continued learning.
            </p>

            <div className="space-y-4 mb-10">
                {resources.map((r, i) => (
                    <div key={i} className="section-card">
                        <h4 className="text-[var(--text-primary)] mb-1">{r.name}</h4>
                        <p className="text-[var(--text-muted)]">{r.desc}</p>
                    </div>
                ))}
            </div>

            <h3 className="border-b border-[var(--text-muted)] pb-2 mb-6">About This Project</h3>

            <p className="text-[var(--text-muted)] leading-relaxed">
                This project is designed to help students understand how macro factors, rates, currencies, and volatility
                interact in precious metals markets. It focuses on explanation and context rather than prediction.
                The goal is to build analytical skills that transfer across asset classes.
            </p>
        </div>
    );
}
