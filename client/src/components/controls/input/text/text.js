import React from "react";
import "./text.css";
import { SanitizerService } from "../../../../services/sanitizer.service";

const Text = ({ id, value, placeholder = "Type your message here...", onChange }) => {
    const handleChange = (e) => {
        const cleaned = SanitizerService.sanitizeText(e.target.value);
        onChange?.({ ...e, target: { ...e.target, value: cleaned } });
    };

    return (
        <div className="text-input">
            <input
                id={id}
                type="text"
                className="input input--lg"
                placeholder={placeholder}
                value={value}
                onChange={handleChange}
                aria-label={placeholder}
                autoComplete="off"
            />
        </div>
    );
};

export default Text;
