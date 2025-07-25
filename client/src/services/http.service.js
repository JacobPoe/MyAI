const baseUrl = 'http://localhost:1587';
const defaultHeaders = {};

const post = async (props) => {
    const requestUrl = buildRequestUrl(props);

    // Handle form data if provided
    let body = props.body;
    let headers = props.headers || defaultHeaders;

    if (props.formData) {
        const formData = new FormData();
        Object.entries(props.formData).forEach(([key, value]) => {
            formData.append(key, value);
        });
        body = formData;
    }

    const response = await fetch(requestUrl, {
        method: "POST",
        body: body,
        headers: headers,
    });
    return await response.json();
};

const buildRequestUrl = (props) => {
    const params = props.params
        ? `?${new URLSearchParams(props.params).toString()}`
        : '';
    return  `${props.baseUrl || baseUrl}/${props.endpoint || ''}${params}`;
};

export const HTTPService = {
    post
};