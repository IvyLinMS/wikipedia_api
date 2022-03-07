"""
Wikipedia Page View API request related enumeration and class

Enum:
    AccessMethod
    AgentType
    Granularity

Classes:
    APIHeader
    AggregatePageViewRequest
    PerArticlePageViewRequest
    TopViewedArticleRequest
    TopViewedByCountryRequest
    TopViewedPerCountryRequest
"""
from enum import Enum
from typing import NamedTuple, Union


class AccessMethod(Enum):
    """
    Enum for different Access Method for page view
    """

    # All access include from both desktop and mobile (include app and web),
    # repsent 'all-access' for page view api and 'all-sites' for legacy page view api
    ALL = 0
    # Access from desktop, represent 'desktop' for page view api and 'desktop-site' for legacy page view api
    DESKTOP = 1
    # Access from mobile, represent 'mobile-app' and 'mobile-web' for page view api and
    # 'mobile-site' for legacy page view api,
    MOBILE = 2
    # Access from mobile app, represent 'mobile-app' for page view api
    MOBILE_APP = 3
    # Access from mobile web, prepresent 'mobile-web' for page view api
    MOBILE_WEB = 4


class AgentType(Enum):
    """
    Enum for User Agent type
    """

    # All user agent type, represent 'all-agents' for page view api
    ALL = 0
    # Agent type from User, represent 'user' for page view api
    USER = 1
    # Agent type from spider, represent 'spider' for page view api
    SPIDER = 2
    # Agent type from automated, represent 'automated' for page view api
    AUTOMATED = 3


class Granularity(Enum):
    """
    The time unit for the response data
    """

    HOURLY = 0
    DAILY = 1
    MONTHLY = 2


class APIHeader(NamedTuple):
    """
    API Header needed to access the RESTful API
    """

    user_agent: str
    call_from: str


class AggregatePageViewRequest(NamedTuple):
    """
    Request for aggregated page view API, works for both page view api and legacy api
    """

    # Access Method to filter page view data
    access: AccessMethod
    # Agent Type to filter page view data
    agent: AgentType
    # Granularity level of page view data, support HOURLY, DAILY, MONTHLY
    granularity: Granularity
    # Start date of page view data in string format of YYYYMMDD or YYYYMMDDHH,
    # support start date later than 12/01/2027,
    start_time: str
    # End date of page view data in string format of YYYYMMDD or YYYYMMDDHH
    end_time: str


class PerArticlePageViewRequest(NamedTuple):
    """
    Request for per article page view API
    """

    # Access Method to filter page view data
    access: AccessMethod
    # Agent Type to filter page view data
    agent: AgentType
    # The title of any article in the specified project.
    # Any spaces should be replaced with underscores. It also should be URI-encoded
    article: str
    # Granularity level of page view data, support HOURLY, DAILY, MONTHLY
    granularity: Granularity
    # Start date of page view data in string format of YYYYMMDD or YYYYMMDDHH
    start_time: str
    # End date of page view data in string format of YYYYMMDD or YYYYMMDDHH
    end_time: str


class TopViewedArticleRequest(NamedTuple):
    """
    Request for top viewed artical page view API
    """

    # Access Method to filter page view data
    access: AccessMethod
    # The year of the date for which to retrieve top articles
    year: int
    # The month of the date for which to retrieve top articles
    month: int
    # The day of the date for which to retrieve top articles, can be all-days to
    # get the top articles of a whole month
    day: Union[int, str]


class TopViewedCountryRequest(NamedTuple):
    """
    Request for top viewed country api
    """

    # Access Method to filter page view data
    access: AccessMethod
    # The year of the date for which to retrieve top countries
    year: int
    # The month of the date for which to retrieve top countries
    month: int


class TopViewedPerCountryRequest(NamedTuple):
    """
    Request for top viewed artical per country api
    """

    # The ISO 3166-1 alpha-2 code of a country for which to retrieve top articles, like 'FR' or 'IN'.
    country: str
    # Access Method to filter page view data
    access: AccessMethod
    # The year of the date for which to retrieve top countries
    year: int
    # The month of the date for which to retrieve top countries
    month: int
    # The day of the date for which to retrieve top articles, can be all-days to
    # get the top articles of a whole month
    day: Union[int, str]
