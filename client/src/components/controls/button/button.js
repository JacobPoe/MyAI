import React from "react";

import "./button.css";

const Button = (props) => {
    return (
        <button
            id={"button__" + props.id}
            onClick={props.onClickHandler}
            className="btn"
            type={props.type ? props.type : 'button'}
        >
            {props.text ? props.text : 'Click Me'}
        </button>
    )
}

export default Button;