'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';

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
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isMobile, setIsMobile] = useState(false);

    // Detect mobile viewport
    useEffect(() => {
        const checkMobile = () => setIsMobile(window.innerWidth < 768);
        checkMobile();
        window.addEventListener('resize', checkMobile);
        return () => window.removeEventListener('resize', checkMobile);
    }, []);

    // Close menu when route changes
    useEffect(() => {
        setIsMenuOpen(false);
    }, [pathname]);

    // Prevent body scroll when menu is open
    useEffect(() => {
        if (isMenuOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => { document.body.style.overflow = ''; };
    }, [isMenuOpen]);

    const currentTab = tabs.find(tab => tab.href === pathname);

    // Mobile Navigation
    if (isMobile) {
        return (
            <>
                {/* Mobile Header Bar */}
                <nav className="mobile-nav-header">
                    <button
                        className="hamburger-btn"
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        aria-label="Toggle menu"
                    >
                        <span className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></span>
                        <span className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></span>
                        <span className={`hamburger-line ${isMenuOpen ? 'open' : ''}`}></span>
                    </button>
                    <span className="mobile-nav-title">
                        {currentTab?.icon} {currentTab?.label || 'Metals, Explained'}
                    </span>
                </nav>

                {/* Overlay */}
                {isMenuOpen && (
                    <div
                        className="menu-overlay"
                        onClick={() => setIsMenuOpen(false)}
                    />
                )}

                {/* Slide-in Drawer */}
                <div className={`mobile-drawer ${isMenuOpen ? 'open' : ''}`}>
                    <div className="drawer-header">
                        <span className="drawer-title">Navigation</span>
                        <button
                            className="close-btn"
                            onClick={() => setIsMenuOpen(false)}
                            aria-label="Close menu"
                        >
                            ✕
                        </button>
                    </div>
                    <div className="drawer-content">
                        {tabs.map((tab) => (
                            <Link
                                key={tab.href}
                                href={tab.href}
                                className={`drawer-link ${pathname === tab.href ? 'active' : ''}`}
                                onClick={() => setIsMenuOpen(false)}
                            >
                                <span className="drawer-icon">{tab.icon}</span>
                                <span className="drawer-label">{tab.label}</span>
                                {pathname === tab.href && (
                                    <span className="drawer-active-indicator">●</span>
                                )}
                            </Link>
                        ))}
                    </div>
                </div>
            </>
        );
    }

    // Desktop Navigation (unchanged behavior)
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
