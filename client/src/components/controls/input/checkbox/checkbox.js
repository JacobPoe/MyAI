// import React from "react";
//
// import "./checkbox.css";
//
// const Checkbox = (props) => {
//     return (
//         <div className={`checkbox checkbox__${props.id} ${props.alignment ? props.alignment : ''}`}>
//             <label htmlFor={"input-checkbox--" + props.id} className="checkbox-label">
//                 {props.label ? props.label : ''}
//             </label>
//             <input
//                 id={"input-checkbox--" + props.id}
//                 className={`input-checkbox__${props.id}`}
//                 type="checkbox"
//                 checked={props.checked}
//                 onChange={(e) => props.onChangeHandler(e.target.checked)}
//             />
//         </div>
//     )
// }
//
// export default Checkbox;

import React from "react";
import "./checkbox.css";

/**
 * Props:
 *  - id: string
 *  - checked: boolean
 *  - onChange: (e) => void
 *  - label?: string
 *  - alignRight?: boolean  (adds .right)
 */
const Checkbox = (props) => {
    return (
        <div className={`checkbox checkbox__${props.id} ${props.alignment ? props.alignment : ''}`}>
        <label className={`checkbox ${props.alignment === "right" ? "right" : ""}`} htmlFor={"input-checkbox--" + props.id}>
            {props.label ? <span className="checkbox__label">{props.label}</span> : null}
        </label>
            <input id={`input-checkbox--${props.id}`} type="checkbox" checked={props.checked} onChange={props.onChangeHandler} />
        </div>
    );
};

export default Checkbox;
