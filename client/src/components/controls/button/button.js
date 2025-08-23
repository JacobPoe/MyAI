import React from "react";

import "./button.css";

const Button = (props) => {
    return (
        <>
            {props.label && (
                <label htmlFor={"button__" + props.id} className="button-label sr-only">
                    {props.label}
                </label>
            )}
            <button
                id={"button__" + props.id}
                onClick={props.onClickHandler}
                className="btn"
                type={props.type ? props.type : 'button'}
                >
                <span>{props.text}</span>
            </button>
        </>
    )
}

export default Button;