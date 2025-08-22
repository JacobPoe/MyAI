import React from "react";
import "./header.css";

const Header = ({ checked, theme, toggleTheme }) => {
    const heroText = "PhÖebe";

    return (
        <header className={`header ${theme} z-header`}>
            <div className="header__inner">
                <div className="header__brand">
                    <span>✨</span>
                    <span>{heroText}</span>
                </div>

                <div className="header__actions">
                    <button
                        type="button"
                        className="theme-toggle"
                        role="switch"
                        aria-checked={checked}
                        aria-label={checked ? "Switch to dark mode" : "Switch to light mode"}
                        onClick={toggleTheme}
                    >
                        <span className="theme-toggle__thumb" aria-hidden="true" />
                    </button>
                </div>
            </div>
        </header>
    );
};

export default Header;
