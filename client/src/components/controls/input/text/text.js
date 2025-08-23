import {SanitizerService} from "../../../../services/sanitizer.service";
import React from "react";

import "./text.css";

const Text = (props) => {
    return (
        <input
            type="text"
            id={"input-text__" + props.id}
            value={props.text}
            onChange={(e) => props.onChangeHandler(SanitizerService.sanitizeText(e.target.value))}
            className="input__text"
            placeholder={props.placeholder? props.placeholder : "Type your message here..."}
        />
    )
}

export default Text;