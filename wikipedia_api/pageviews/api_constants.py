from datetime import datetime


class PageViewApiEndPoints:
    """
    Wikipedia Page view RESTful API Endpoint templates
    """
    AGGRGATED_PAGEVIEWS_LEGACY = "https://wikimedia.org/api/rest_v1/metrics/legacy/pagecounts/aggregate/{project}/{access-site}/{granularity}/{start}/{end}"
    AGGRGATED_PAGEVIEWS = "https://wikimedia.org/api/rest_v1/metrics/pageviews/aggregate/{project}/{access}/{agent}/{granularity}/{start}/{end}"
    PER_ARTICLE_PAGEVIEWS = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{project}/{access}/{agent}/{article}/{granularity}/{start}/{end}"
    TOP_PAGEVIEWS = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/{project}/{access}/{year}/{month}/{day}"
    TOP_VIEW_BY_COUNTRY = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top-by-country/{project}/{access}/{year}/{month}"
    TOP_VIEW_PER_COUNTRY = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top-per-country/{country}/{access}/{year}/{month}/{day}"
    
class PageViewApiValidDateRange:
    # Date that old legacy API have data
    LEGACY_API_START_DATE: datetime = datetime(2007, 12, 1)
    # Date that new page view API have data
    PAGEVIEW_API_START_DATE: datetime = datetime(2015, 7, 1)
    # Date that top viewed country page view API have data
    TOP_BY_COUNTRY_PAGEVIEW_API_START_DATE: datetime = datetime(2015, 5, 1)
    # Date that top artical per country page view API have data
    TOP_PER_COUNTRY_PAGEVIEW_API_START_DATE: datetime = datetime(2021, 1, 1)

