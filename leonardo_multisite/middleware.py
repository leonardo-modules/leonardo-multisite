
from django.conf import settings
from leonardo.module.web.models import Page


class MultiSiteMiddleware(object):

    """activate page filter by request.get_host
    """

    last_current = None

    def process_request(self, request):

        # basic support for multisite
        if getattr(settings, 'MULTISITE_ENABLED', False):

            current = request.get_host()

            if self.last_current != current:
                Page.objects.active_filters.pop('current_site', None)
                Page.objects.add_to_active_filters(
                    lambda queryset: queryset.filter(
                        site__domain=str(current)),
                    key='current_site')
                self.last_current = current
