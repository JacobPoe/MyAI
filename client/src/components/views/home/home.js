import React, { useState } from "react";
import "../views-base.css";
import "./home.css";
import Chatbot from "../../chatbot/chatbot";
import Header from "../header/header";

const Home = () => {
    const [lightMode, setLightMode] = useState(false);
    const toggleTheme = () => setLightMode(!lightMode);
    const theme = lightMode ? "light-mode" : "dark-mode";

    return (
        <>
            <Header checked={lightMode} theme={theme} toggleTheme={toggleTheme} />
            <div className={`view view__home ${theme}`} data-theme={lightMode ? "light" : "dark"}>
                <div className="view-container container">
                    <section className="home-hero">
                        <h1>Start chatting</h1>
                    </section>

                    <Chatbot id="conversation-root" />
                </div>
            </div>
        </>
    );
};

export default Home;
