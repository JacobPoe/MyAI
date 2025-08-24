const baseUrl = 'http://localhost:1587';
const defaultHeaders = {};

const post = async (props) => {
    const requestUrl = buildRequestUrl(props);
    let headers = props.headers || defaultHeaders;

    const response = await fetch(requestUrl, {
        method: "POST",
        body: props.body,
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