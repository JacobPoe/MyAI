import {SanitizerService} from "../../../../services/sanitizer.service";
import React from "react";

const Text = (props) => {
    return (
        <input
            type="text"
            value={props.text}
            onChange={(e) => props.onChangeHandler(SanitizerService.sanitizeText(e.target.value))}
            className="form-control"
            placeholder={props.placeholder? props.placeholder : "Type your message here..."}
        />
    )
}

export default Text;