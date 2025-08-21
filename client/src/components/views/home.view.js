import React, { useState } from "react";

import Checkbox from "../controls/input/checkbox/checkbox";
import Chatbot from "../chatbot/chatbot";

const Home = () => {
    const [lightMode, setLightMode] = useState(true);
    const toggleLightMode = () => setLightMode(!lightMode);

    return (
        <div className={`myai-container ${lightMode ? "light-mode" : "dark-mode"}`}>
                <div className="text-center">
                    <h1>MyAI</h1>
                    <Checkbox id={"toggle-theme"} checked={lightMode} onChangeHandler={toggleLightMode} label={"Toggle light/dark mode"} />
                </div>
                <div className="">
                    <Chatbot id={"chatbot-home"} />
                </div>
        </div>
    )
}

export default Home;