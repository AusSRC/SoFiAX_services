def handle_navigation(request, queryset, idx, url_base, url_params):
    """Navigation without changing the queryset

    """
    url = None
    body = dict(request.POST)
    if 'Next' in body['action']:
        new_idx = idx + 1
        if new_idx >= len(queryset):
            new_idx = len(queryset) - 1
        url = f"{url_base}?{url_params}{queryset[new_idx].id}"
    if 'Previous' in body['action']:
        new_idx = idx - 1
        if new_idx <= 0:
            new_idx = 0
        url = f"{url_base}?{url_params}{queryset[new_idx].id}"
    if 'Go to index' in body['action']:
        if (request.POST['index'] == ''):
            return f"{url_base}?{url_params}{queryset[0].id}"
        idx = int(request.POST['index'])
        if idx >= len(queryset):
            idx = len(queryset)
        url = f"{url_base}?{url_params}{queryset[idx-1].id}"
    if 'First' in body['action']:
        url = f"{url_base}?{url_params}{queryset[0].id}"
    if 'Last' in body['action']:
        idx = len(queryset) - 1
        url = f"{url_base}?{url_params}{queryset[idx].id}"
    return url


def handle_next(request, queryset, idx, url_base, url_params):
    """Handle next where queryset changes.

    """
    if len(queryset) == 1:
        return '/admin/survey/run'
    new_idx = idx + 1
    if new_idx >= len(queryset) - 1:
        new_idx = idx - 1
    url = f"{url_base}?{url_params}{queryset[new_idx].id}"
    return url