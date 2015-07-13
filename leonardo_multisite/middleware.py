
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import Q
from leonardo.module.web.models import Page


class MultiSiteMiddleware(object):

    """activate page filter by request.get_host
    """

    last_current = None

    def process_request(self, request):

        if getattr(settings, 'MULTISITE_ENABLED', False):

            current = request.get_host()
            # don't hit DB if is same as last
            if self.last_current != current:
                current_site = Site.objects.get(domain=current)
                Page.objects.active_filters.pop('current_site', None)
                Page.objects.add_to_active_filters(Q(site=current_site),
                                                   key='current_site')
                self.last_current = current
                # patch settings which is used for feincms cache keys
                settings.SITE_ID = current_site.id
