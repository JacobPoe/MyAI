const baseUrl = 'http://localhost:1587';
const defaultHeaders = {
    "Content-Type": "application/json",
};

const post = async (props) => {
    const response = await fetch(`${props.baseUrl || baseUrl}/${props.endpoint}`, {
        method: "POST",
        body: props.body,
        headers: props.headers || defaultHeaders,
    });
    return await response.json();
}

export const HTTPService = {
    post
};