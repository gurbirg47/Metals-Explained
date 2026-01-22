'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const tabs = [
    { href: '/', label: 'Today', icon: '◉' },
    { href: '/why-metals', label: 'Why Metals Matter', icon: '◈' },
    { href: '/drivers', label: 'Drivers', icon: '⚙' },
    { href: '/history', label: 'History', icon: '◷' },
    { href: '/terminology', label: 'Terminology', icon: '▤' },
    { href: '/interpretation', label: 'Interpretation', icon: '◎' },
    { href: '/examples', label: 'Examples', icon: '◫' },
    { href: '/resources', label: 'Resources', icon: '◆' },
];

export default function Navigation() {
    const pathname = usePathname();

    return (
        <nav className="nav-tabs">
            {tabs.map((tab) => (
                <Link
                    key={tab.href}
                    href={tab.href}
                    className={`nav-tab ${pathname === tab.href ? 'active' : ''}`}
                >
                    {tab.icon} {tab.label}
                </Link>
            ))}
        </nav>
    );
}
