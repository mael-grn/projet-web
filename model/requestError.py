class RequestError(Exception):
    def __init__(self, message, code, details):
        super().__init__(message)  # Appelle Exception avec le message
        self.code = code
        self.details = details