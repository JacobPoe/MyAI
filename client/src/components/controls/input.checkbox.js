import React from "react";

const InputCheckbox = (props) => {
    return (
        <label>
            {props.label ? props.label : ''}
            <input
                id={"input-checkbox--" + props.id ? props.id : ''}
                type="checkbox"
                checked={props.checked}
                onChange={(e) => props.onChangeHandler(e.target.checked)}
            />
        </label>
    )
}

export default InputCheckbox;