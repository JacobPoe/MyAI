import React from "react";
import "./button.css";

const Button = ({
                    type = "button",
                    variant = "primary",
                    text = "Click",
                    onClickHandler,
                    className = "",
                    disabled = false,
                    ...rest
                }) => {
    const isIcon = type === "icon";
    const htmlType = isIcon ? "button" : type;

    const cls = [
        "btn",
        variant === "primary" && "btn--primary",
        variant === "ghost" && "btn--ghost",
        variant === "danger" && "btn--danger",
        variant === "success" && "btn--success",
        isIcon && "btn--icon",
        className
    ]
        .filter(Boolean)
        .join(" ");

    return (
        <button
            type={htmlType}
            className={cls}
            onClick={onClickHandler}
            disabled={disabled}
            {...rest}
        >
            {text}
        </button>
    );
};

export default Button;
