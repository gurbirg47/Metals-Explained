export default function WhyMetalsPage() {
    return (
        <div>
            <h1>Why Gold & Silver Matter</h1>

            <div className="text-[var(--text-muted)] leading-relaxed space-y-6 mt-6">
                <p>
                    Gold and silver occupy a unique position in global markets. Unlike equities, which represent claims on corporate earnings,
                    or bonds, which represent claims on future cash flows, precious metals are real assets with no counterparty risk.
                    They cannot default, and their value does not depend on any institution's solvency.
                </p>

                <p>
                    This makes gold, in particular, a preferred store of value during periods of monetary uncertainty, geopolitical tension,
                    or financial system stress. Central banks hold gold as a reserve asset. Institutional investors use gold to hedge against
                    tail risks. Retail investors buy gold when they lose confidence in paper currencies.
                </p>

                <p>
                    Silver shares some of gold's monetary characteristics but also has significant industrial applications—electronics,
                    solar panels, medical devices. This dual nature makes silver more volatile and more sensitive to economic cycles.
                </p>

                <h3 className="mt-8 mb-4">Why Students Should Understand Metals</h3>

                <p>
                    Understanding precious metals markets teaches several important concepts:
                </p>

                <ul className="list-disc list-inside space-y-2 ml-4">
                    <li>How real interest rates affect asset valuations</li>
                    <li>The relationship between the U.S. dollar and dollar-denominated commodities</li>
                    <li>How inflation expectations manifest in market prices</li>
                    <li>The role of safe-haven flows during market stress</li>
                    <li>How central bank policy transmits through financial markets</li>
                </ul>

                <p>
                    These concepts apply broadly across asset classes. Mastering them through metals analysis builds a foundation for
                    understanding fixed income, currencies, and macro trading more generally.
                </p>
            </div>

            <h3 className="mt-10 mb-6 border-b border-[var(--text-muted)] pb-2">Mental Model</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-6 rounded-lg border border-[rgba(255,215,0,0.3)] bg-[rgba(255,215,0,0.1)] text-center">
                    <h4 className="text-[#FFD700] mb-3">GOLD</h4>
                    <p className="mono text-[var(--text-muted)]">
                        Real rates ↑ → Gold ↓<br />
                        Dollar ↑ → Gold ↓<br />
                        Fear ↑ → Gold ↑
                    </p>
                </div>

                <div className="p-6 rounded-lg border border-[rgba(192,192,192,0.3)] bg-[rgba(192,192,192,0.1)] text-center">
                    <h4 className="text-[#C0C0C0] mb-3">SILVER</h4>
                    <p className="mono text-[var(--text-muted)]">
                        Gold direction + industrial demand<br />
                        More volatile than gold<br />
                        Higher beta to risk sentiment
                    </p>
                </div>
            </div>
        </div>
    );
}
