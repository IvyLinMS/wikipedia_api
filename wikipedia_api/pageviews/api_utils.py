from typing import Optional, Tuple
from datetime import datetime
from wikipedia_api.pageviews.api_constants import PageViewApiValidDateRange
from wikipedia_api.pageviews.api_exceptions import InputException
from wikipedia_api.pageviews.api_types import AccessMethod, AgentType, Granularity
import requests


def translate_access_method_to_str(
    access: AccessMethod, is_legacy: bool = False
) -> str:
    """
    Translate the AccessMethod enum to str format, special handling if is_legacy flag is true
    """
    if is_legacy:
        if access == AccessMethod.ALL:
            return "all-sites"
        elif access == AccessMethod.DESKTOP:
            return "desktop-site"
        elif access in (
            AccessMethod.MOBILE,
            AccessMethod.MOBILE_APP,
            AccessMethod.MOBILE_WEB,
        ):
            return "mobile-site"
    else:
        if access == AccessMethod.ALL:
            return "all-access"
        elif access == AccessMethod.DESKTOP:
            return "desktop"
        elif access == AccessMethod.MOBILE_APP:
            return "mobile-app"
        elif access == AccessMethod.MOBILE_WEB:
            return "mobile-web"

    raise InputException("Unexpected MOBILE AccessMethod when using non legacy API")


def translate_agent_type_to_str(agent: AgentType) -> str:
    """
    Translate AgentType enum to str format
    """
    if agent == AgentType.ALL:
        return "all-agents"
    elif agent == AgentType.USER:
        return "user"
    elif agent == AgentType.SPIDER:
        return "spider"
    elif agent == AgentType.AUTOMATED:
        return "automated"


def translate_granularity_to_str(granularity: Granularity) -> str:
    """
    Translate Granularity enum to str format
    """
    if granularity == Granularity.HOURLY:
        return "hourly"
    elif granularity == Granularity.DAILY:
        return "daily"
    elif granularity == Granularity.MONTHLY:
        return "monthly"


def parse_time_parameter(time_str: str, support_hour: bool = False) -> datetime:
    try:
        dt = datetime.strptime(time_str, "%Y%m%d")
    except:
        if support_hour:
            try:
                dt = datetime.strptime(time_str, "%Y%m%d%H")
            except:
                raise InputException(f"{time_str} is invalid datetime string")
        else:
            raise InputException(f"{time_str} is invalid datetime string")

    return dt


def parse_start_end_time(
    start_time_str: str, end_time_str: str, support_hour: bool = False
) -> Tuple[datetime, datetime]:
    start_time = parse_time_parameter(start_time_str, support_hour=support_hour)
    end_time = parse_time_parameter(end_time_str, support_hour=support_hour)
    if start_time > end_time:
        raise InputException("start time should not later than end time")
    return start_time, end_time


def split_time_range_for_legacy_api(
    start_time: datetime, end_time: datetime
) -> Tuple[
    Optional[datetime], Optional[datetime], Optional[datetime], Optional[datetime]
]:
    legacy_api_start_time = None
    legacy_api_end_time = None
    page_view_api_start_time = None
    page_view_api_end_time = None

    if start_time < PageViewApiValidDateRange.PAGEVIEW_API_START_DATE:
        legacy_api_start_time = start_time
        if end_time < PageViewApiValidDateRange.PAGEVIEW_API_START_DATE:
            legacy_api_end_time = end_time
        elif end_time > PageViewApiValidDateRange.PAGEVIEW_API_START_DATE:
            legacy_api_end_time = PageViewApiValidDateRange.PAGEVIEW_API_START_DATE
            page_view_api_start_time = PageViewApiValidDateRange.PAGEVIEW_API_START_DATE
            page_view_api_end_time = end_time

    else:
        page_view_api_start_time = start_time
        page_view_api_end_time = end_time

    return (
        legacy_api_start_time,
        legacy_api_end_time,
        page_view_api_start_time,
        page_view_api_end_time,
    )


def rest_api_call(endpoint: str, api_header: dict, parameters: dict):
    call = requests.get(endpoint.format(**parameters), headers=api_header)
    response = call.json()
    return response
