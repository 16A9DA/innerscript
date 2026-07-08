class SecurityHeadersMiddleware:
    """Deny unused browser features and drop version-disclosure headers.

    A fronting proxy should also strip Server, since the WSGI server re-adds it.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=(), usb=(), "
            "magnetometer=(), gyroscope=(), interest-cohort=()"
        )
        for header in ("Server", "X-Powered-By"):
            if header in response:
                del response[header]
        return response
