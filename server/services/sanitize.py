class Sanitize:
    @staticmethod
    def decode_headers(data):
        headers = {}
        query_string = data.decode("utf-8")
        if query_string:
            pairs = query_string.split("&")
            for pair in pairs:
                key, value = pair.split("=")
                headers[key] = value
        return headers
