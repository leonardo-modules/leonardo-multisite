
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import Q
from leonardo.module.web.models import Page
from constance import config


class MultiSiteMiddleware(object):

    """activate page filter by request.get_host
    """

    last_current = None

    @property
    def fallback_site(self):
        """Return fallback site
        """

        try:
            fallback_site = Site.objects.get(domain=config.MULTISITE_FALLBACK)
        except Site.DoesNotExist:
            pass
        else:
            return fallback_site

    def process_request(self, request):

        if getattr(settings, 'MULTISITE_ENABLED', False):

            current = request.get_host()
            # don't hit DB if is same as last

            if self.last_current != current:

                aliases = config.MULTISITE_ALIASES
                domains = [{
                    site.domain: aliases.get(site.domain, [])}
                    for site in Site.objects.all()]

                current_site = None

                if current in domains:
                    current_site = domains[current]
                else:
                    for _aliases in domains.values():
                        if current in _aliases:
                            current_site = domains[current]

                if not current_site:
                    current_site = self.fallback_site

                if current_site:
                    Page.objects.active_filters.pop('current_site', None)
                    Page.objects.add_to_active_filters(Q(site=current_site),
                                                       key='current_site')
                    # patch settings which is used for feincms cache keys
                    settings.SITE_ID = current_site.id
                    settings.SITE_NAME = current_site.name

                self.last_current = current
