import React, { useState } from "react";
import InputCheckbox from "../controls/input.checkbox";
import Chatbot from "../chatbot";

const Home = () => {
    const [lightMode, setLightMode] = useState(true);
    const toggleLightMode = () => setLightMode(!lightMode);

    return (
        <div className={`myai-container ${lightMode ? "light-mode" : "dark-mode"}`}>
            <div className="row">
                <div className="col-12 text-center">
                    <h1>MyAI</h1>
                    <InputCheckbox id={"toggle-theme"} checked={lightMode} onChangeHandler={toggleLightMode} label={"Toggle light/dark mode"} />
                </div>
                <div className="col-12 col-md-8 mx-auto">
                    <Chatbot id={"chatbot-home"} />
                </div>
            </div>
        </div>
    )
}

export default Home;