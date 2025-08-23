import React from "react";

import "./checkbox.css";

const Checkbox = (props) => {
    return (
        <>
            {props.action && (<h6>{props.action}</h6>)}
            <div className={`checkbox checkbox__${props.id} ${props.alignment ? props.alignment : ''}`}>
                <label htmlFor={"input-checkbox--" + props.id} className="checkbox-label sr-only">
                    {props.label ? props.label : ''}
                </label>
                <input
                    id={"input-checkbox--" + props.id}
                    className={`input-checkbox__${props.id}`}
                    type="checkbox"
                    checked={props.checked}
                    onChange={(e) => props.onChangeHandler(e.target.checked)}
                />

                <span className="checkbox__box" aria-hidden="true"/>
            </div>
        </>
    )
}

export default Checkbox;