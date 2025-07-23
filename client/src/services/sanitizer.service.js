const sanitizeText = (value) => {
    return value
        .replace(/[\n\t]/g, "")
        .replace(/<[^>]*>/g, "")
        .replace(/[<>&;]/g, "");
};

export const SanitizerService = {
    sanitizeText
}