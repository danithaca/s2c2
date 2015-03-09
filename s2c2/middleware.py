from django.utils.cache import patch_cache_control


class DisableBrowserCacheMiddleware(object):
    """ When DEBUG=False, django would add HTTP HEADER Cache-Control, and mess up caching things """

    def process_response(self, request, response):
        patch_cache_control(response, no_cache=True, no_store=True, must_revalidate=True, cache_timeout=-1)
        return response
