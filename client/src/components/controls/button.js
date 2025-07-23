import React from "react";

const Button = (props) => {
    return (
        <button id={props.id ? props.id : ''} onClick={props.onClickHandler} className="btn">
            Send
        </button>
    )
}

export default Button;