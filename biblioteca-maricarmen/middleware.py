class AllowPopupsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Eliminar la cabecera por completo:
        response.headers.pop('Cross-Origin-Opener-Policy', None)
        # — o — permitir popups específicamente:
        # response['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
        return response