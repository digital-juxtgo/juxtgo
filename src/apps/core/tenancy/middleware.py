from threading import local

# Thread‑local storage – each request gets its own isolated value
_thread_locals = local()


def get_current_org_id():
    """
    Return the current organization ID from thread‑local storage.
    This function is used by the TenantManager to filter querysets.
    """
    return getattr(_thread_locals, "org_id", None)


class TenancyMiddleware:
    """
    Middleware that reads the active organization ID from the session
    and stores it in thread‑local storage for the duration of the request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        org_id = request.session.get("current_org_id")
        _thread_locals.org_id = org_id
        response = self.get_response(request)
        return response
