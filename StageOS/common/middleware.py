class RLSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        from django.db import connection
        org_id = getattr(getattr(request, 'user', None), 'organisation_id', None)
        if org_id:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT set_config('app.current_org_id', %s, TRUE)",
                    [str(org_id)]
                )
