import React, { useState } from "react";

import "../views-base.css";
import "./home.css";

import Chatbot from "../../chatbot/chatbot";
import Header from "../header/header";

const Home = () => {
    const [lightMode, setLightMode] = useState(false);
    const toggleTheme = () => setLightMode(!lightMode);

    return (
        <>
            <Header checked={lightMode} theme={lightMode ? "light-mode" : "dark-mode"} toggleTheme={toggleTheme} />
            <div className={`view view__home ${lightMode ? "light-mode" : "dark-mode"}`}>
                <div className={"view-container"}>
                    <Chatbot id={"conversation-root"} checked={lightMode} />
                </div>
            </div>
        </>
    )
}

export default Home;