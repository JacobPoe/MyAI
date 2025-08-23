import React from "react";
import Checkbox from "../../controls/input/checkbox/checkbox";

import "./header.css";

const Header = (props) => {
    const heroText = "PhÖebe";
    const toggleLightModeMsg = "Toggle between light and dark mode.";

    return (
        <div className={`header header__${props.theme}`}>
            <h1>{heroText}</h1>
            <div className={`row-right header__theme-toggle`}>
                <h6 className={"header__theme-toggle--light"}>☉</h6>
                <Checkbox
                    id={"toggle-theme"}
                    alignment={"right"}
                    type={"toggle-theme"}
                    checked={props.checked}
                    onChangeHandler={props.toggleTheme}
                    label={toggleLightModeMsg}
                />
                <h6 className={"header__theme-toggle--dark"}>☾</h6>
            </div>
        </div>
        )
    };

export default Header;