from datetime import datetime, timedelta
import pandas as pd
from wikipedia_api.pageviews.api_exceptions import InputException

from wikipedia_api.pageviews.api_types import (
    AccessMethod,
    AgentType,
    AggregatePageViewRequest,
    APIHeader,
    Granularity,
    PerArticlePageViewRequest,
    TopViewedArticleRequest,
    TopViewedCountryRequest,
    TopViewedPerCountryRequest,
)
from wikipedia_api.pageviews.api_constants import (
    PageViewApiEndPoints,
    PageViewApiValidDateRange,
)
from wikipedia_api.pageviews.api_utils import (
    parse_start_end_time,
    rest_api_call,
    split_time_range_for_legacy_api,
    translate_access_method_to_str,
    translate_agent_type_to_str,
    translate_granularity_to_str,
)


class WikipediaPageViewApiClient:
    """
    Wikipedia Page View API client wrapper,
    Save common initialization parameter eg project or api header to avoid passing for 
    each api call, use strong typed parameter to avoid error-prone str typed parameter
    for access or agent or granularity type, do basic validation on user input such as 
    date time format or invalid filter type or date range, and provided two extended 
    functionalities
        -- extend to combine both legacy and current page view api result for aggregated
            page viwe API result, 
        -- extend the top viewed artical per country api to support get result on whole month
    """

    def __init__(self, project: str, api_header: APIHeader) -> None:
        """
        Init WikipediaPageViewApiClient with header and project

        Args:
            api_header (APIHeader): API Header used to call underlying REST API
            project (str): wikipedia project, eg: en.wikipedia.org
        """

        self._project = project
        self._api_header = {
            "User-Agent": api_header.user_agent,
            "From": api_header.call_from,
        }

    @property
    def project(self) -> str:
        return self._project

    def get_aggregated_pageviews(
        self, request: AggregatePageViewRequest
    ) -> pd.DataFrame:
        """
        Given a date range, returns a timeseries of pageview counts. 
        Support filter by access method and/or agent type, and choose between monthly, daily, hourly granularity
        
        if start time specified is between 12/01/2007 and 07/01/2015, legacy API data will be combined with
        new page view API data
        if agent type is set to MOBILE and date range include 07/01/2015, both the mobile-app and mobile-web 
        data will be returned
        
        Args:
            request (AggregatePageViewRequest): Request data for get aggregated page view
        Raises:
            InputException: User input error if start time or end time is invalid or out of supported range

        Returns:
            pd.DataFrame: columns:
                "project": str,
                "access": str,
                "agent": str,
                "granularity": str,
                "timestamp": str,
                "views": int
        """

        start_time, end_time = parse_start_end_time(
            request.start_time, request.end_time, support_hour=True
        )

        # Validate start time
        if start_time < PageViewApiValidDateRange.LEGACY_API_START_DATE:
            raise InputException(f"Data before {request.start_time} is not available")

        (
            legacy_api_start_time,
            legacy_api_end_time,
            page_view_api_start_time,
            page_view_api_end_time,
        ) = split_time_range_for_legacy_api(start_time, end_time)

        legacy_df = pd.DataFrame()
        if legacy_api_start_time is not None:
            legacy_df = self._call_legacy_api(
                request.access,
                request.granularity,
                legacy_api_start_time,
                legacy_api_end_time,
            )

        pageview_df = pd.DataFrame()
        if page_view_api_start_time is not None:
            if request.access == AccessMethod.MOBILE:
                mobile_app_df = self._call_page_view_api(
                    AccessMethod.MOBILE_APP,
                    request.agent,
                    request.granularity,
                    page_view_api_start_time,
                    page_view_api_end_time,
                )
                mobile_web_df = self._call_page_view_api(
                    AccessMethod.MOBILE_WEB,
                    request.agent,
                    request.granularity,
                    page_view_api_start_time,
                    page_view_api_end_time,
                )
                pageview_df = pd.concat(
                    [mobile_app_df, mobile_web_df], ignore_index=True
                )
            else:
                pageview_df = self._call_page_view_api(
                    request.access,
                    request.agent,
                    request.granularity,
                    page_view_api_start_time,
                    page_view_api_end_time,
                )

        return pd.concat([legacy_df, pageview_df], ignore_index=True)

    def get_top_view_per_country(self, request: TopViewedPerCountryRequest):
        """
        Lists the 1000 most viewed articles for a given country and date, across all projects. 
        Support filter by access method. Because of privacy reasons, pageview counts are given 
        in a bounded format and are not reported for certain countries. Furthermore, articles 
        visited by 1000 unique individuals or fewer on the given date will be excluded from the 
        returned data. Also, views produced by agents categorized as bots or web crawlers will 
        be excluded from all calculations, if all-days is specified in the day parameter, all data
        within the specified month will be returned

        Args:
            request (TopViewedPerCountryRequest): Request data for get top page viewed article per country

        Raises:
            InputException: User input error if start time or end time is invalid or out of supported range
            or MOBILE access method is specified as current page view API doesn't support this access type

        Returns:
            pd.DataFrame: columns:
                "country": str,
                "access": str,
                "year": str,
                "month": str,
                "day": str,
                "rank": int,
                "article": str,
                "project": str,
                "views_ceil": int
        """

        if request.access == AccessMethod.MOBILE:
            raise InputException("Current API doesn't support MOBILE access")

        year = request.year
        month = request.month
        day = request.day

        if year <= 0:
            raise InputException(f"Year value {year} should not smaller or equal to 0")

        if month <= 0:
            raise InputException(
                f"Month value {month} should not smaller or equal to 0"
            )

        if month > 12:
            raise InputException(f"Month value {month} should not larger than 12")

        is_all_days = False
        try:
            day = int(day)
        except:
            if day != "all-days":
                raise InputException(f"Day value {day} only accept 1-31 or all-days")
            is_all_days = True

        if is_all_days is not True:
            try:
                date_time = datetime(year, month, day)
                year = date_time.strftime("%Y")
                month = date_time.strftime("%m")
                day = date_time.strftime("%d")
            except:
                raise InputException(f"Invalid date provide:{year}-{month}-{day}")

            # Validate start time
            if (
                date_time
                < PageViewApiValidDateRange.TOP_PER_COUNTRY_PAGEVIEW_API_START_DATE
            ):
                raise InputException(
                    f"Data before {PageViewApiValidDateRange.TOP_PER_COUNTRY_PAGEVIEW_API_START_DATE.strftime('%Y%m%d')} is not available"
                )

            return self._call_top_view_per_country_api(
                request.country, request.access, year, month, day
            )
        else:
            current_date = datetime(year, month, 1)
            # Validate start time
            if (
                current_date
                < PageViewApiValidDateRange.TOP_PER_COUNTRY_PAGEVIEW_API_START_DATE
            ):
                raise InputException(
                    f"Data before {PageViewApiValidDateRange.TOP_PER_COUNTRY_PAGEVIEW_API_START_DATE.strftime('%Y%m%d')} is not available"
                )

            dfs = []
            while True:
                current_year = current_date.strftime("%Y")
                current_month = current_date.strftime("%m")
                current_day = current_date.strftime("%d")
                current_df = self._call_top_view_per_country_api(
                    request.country,
                    request.access,
                    current_year,
                    current_month,
                    current_day,
                )
                dfs.append(current_df)
                current_date = current_date + timedelta(days=1)
                if current_date.month > month:
                    break

            df = pd.concat(dfs, ignore_index=True)
            # group by month to find top 1000 article per month
            aggregated_df = df.groupby(
                ["country", "access", "year", "month", "article", "project"]
            ).agg(views_ceil=("views_ceil", "sum"))
            aggregated_df = (
                aggregated_df.reset_index()
                .sort_values(["views_ceil"], ascending=False)
                .reset_index(drop=True)
                .head(1000)
            )
            aggregated_df["rank"] = aggregated_df.index + 1
            aggregated_df["day"] = "all-days"
            return aggregated_df

    def get_per_article_pageviews(
        self, request: PerArticlePageViewRequest
    ) -> pd.DataFrame:
        """
        Given an article and a date range, returns a daily timeseries of its pageview counts.
        Support filter by access method and/or agent type, and choose between monthly, daily granularity
        
        Args:
            request (PerArticlePageViewRequest): Request data for get page view for a specific artical

        Raises:
            InputException: User input error if start time or end time is invalid or MOBILE access method
            is specified as current page view API doesn't support this access type
        Returns:
            pd.DataFrame: columns:
                "project": str,
                "access": str,
                "article": str,
                "agent": str,
                "granularity": str,
                "timestamp": str,
                "views": int
        """

        start_time, end_time = parse_start_end_time(
            request.start_time, request.end_time, support_hour=True
        )

        # Validate start time
        if start_time < PageViewApiValidDateRange.PAGEVIEW_API_START_DATE:
            raise InputException(
                f"Data before {PageViewApiValidDateRange.PAGEVIEW_API_START_DATE} is not available"
            )

        if request.access == AccessMethod.MOBILE:
            raise InputException(
                "get_per_article_pageviews API doesn't support MOBILE access method"
            )

        if request.granularity == Granularity.HOURLY:
            raise InputException(
                "get_per_article_pageviews API doesn't support hourly granularity"
            )

        params = {
            "project": self._project,
            "access": translate_access_method_to_str(request.access, is_legacy=False),
            "agent": translate_agent_type_to_str(request.agent),
            "article": request.article,
            "granularity": translate_granularity_to_str(request.granularity),
            "start": start_time.strftime("%Y%m%d%H"),
            "end": end_time.strftime("%Y%m%d%H"),
        }

        pageview_data = rest_api_call(
            PageViewApiEndPoints.PER_ARTICLE_PAGEVIEWS, self._api_header, params
        )
        return pd.DataFrame.from_dict(pageview_data["items"])

    def get_top_pageviews(self, request: TopViewedArticleRequest) -> pd.DataFrame:
        """
        Lists the 1000 most viewed articles timespan (month or day), support filter by access method

        Args:
            request (TopViewedArticleRequest): Request data for get top viewed article

        Raises:
            InputException: User input error if start time or end time is invalid or out of supported range

        Returns:
            pd.DataFrame: columns:
                "project": str,
                "access": str,
                "year": str,
                "month": str,
                "day": str,
                "article": str,
                "views": int
                "rank":int,
        """
        if request.access == AccessMethod.MOBILE:
            raise InputException("Current API doesn't support MOBILE access")

        year = request.year
        month = request.month
        day = request.day

        if year <= 0:
            raise InputException(f"Year value {year} should not smaller or equal to 0")

        if month <= 0:
            raise InputException(
                f"Month value {month} should not smaller or equal to 0"
            )

        if month > 12:
            raise InputException(f"Month value {month} should not larger than 12")

        is_all_days = False
        try:
            day = int(day)
        except:
            if day != "all-days":
                raise InputException(f"Day value {day} only accept 1-31 or all-days")
            is_all_days = True

        if is_all_days is not True:
            try:
                date_time = datetime(year, month, day)
                year = date_time.strftime("%Y")
                month = date_time.strftime("%m")
                day = date_time.strftime("%d")
            except:
                raise InputException(f"Invalid date provide:{year}-{month}-{day}")
        else:
            date_time = datetime(year, month, 1)
            year = date_time.strftime("%Y")
            month = date_time.strftime("%m")

        # Validate start time
        if date_time < PageViewApiValidDateRange.PAGEVIEW_API_START_DATE:
            raise InputException(
                f"Data before {PageViewApiValidDateRange.PAGEVIEW_API_START_DATE.strftime('%Y%m%d')} is not available"
            )

        params = {
            "project": self._project,
            "access": translate_access_method_to_str(request.access, is_legacy=False),
            "year": str(year),
            "month": str(month),
            "day": str(day),
        }
        pageview_data = rest_api_call(
            PageViewApiEndPoints.TOP_PAGEVIEWS, self._api_header, params
        )

        articles_df = pd.DataFrame.from_dict(pageview_data["items"][0]["articles"])
        # add the common parameters into the data frame columns
        for key, value in params.items():
            articles_df[key] = value
        return articles_df

    def get_top_viewed_country(self, request: TopViewedCountryRequest) -> pd.DataFrame:
        """
        Lists the pageviews to this project, split by country of origin for a given month. 
        Because of privacy reasons, pageviews are given in a bucketed format, 
        and countries with less than 100 views do not get reported.

        Args:
            request (TopViewedCountryRequest): Request data for get page views split by country

        Raises:
            InputException: User input error if start time or end time is invalid or out of supported range
            or MOBILE access method is specified as current page view API doesn't support this access type

        Returns:
            pd.DataFrame: columns:
                "project": str,
                "access": str,
                "year": str,
                "month": str,
                "country": str,
                "views": int
                "rank":int,
                "views_ceil": int,
        """
        if request.access == AccessMethod.MOBILE:
            raise InputException("Current API doesn't support MOBILE access")

        year = request.year
        month = request.month

        if year <= 0:
            raise InputException(f"Year value {year} should not smaller or equal to 0")

        if month <= 0:
            raise InputException(
                f"Month value {month} should not smaller or equal to 0"
            )

        if month > 12:
            raise InputException(f"Month value {month} should not larger than 12")

        date_time = datetime(year, month, 1)
        # Change year month to correct YYYY and MM format
        year = date_time.strftime("%Y")
        month = date_time.strftime("%m")

        # Validate start time
        if date_time < PageViewApiValidDateRange.TOP_BY_COUNTRY_PAGEVIEW_API_START_DATE:
            raise InputException(
                f"Data before {PageViewApiValidDateRange.TOP_BY_COUNTRY_PAGEVIEW_API_START_DATE.strftime('%Y%m%d')} is not available"
            )

        params = {
            "project": self._project,
            "access": translate_access_method_to_str(request.access, is_legacy=False),
            "year": str(year),
            "month": str(month),
        }
        pageview_data = rest_api_call(
            PageViewApiEndPoints.TOP_VIEW_BY_COUNTRY, self._api_header, params
        )

        df = pd.DataFrame.from_dict(pageview_data["items"][0]["countries"])
        # add the common parameters into the data frame columns
        for key, value in params.items():
            df[key] = value
        return df

    def _call_top_view_per_country_api(
        self, country: str, access: AccessMethod, year: str, month: str, day: str
    ):
        params = {
            "country": country,
            "access": translate_access_method_to_str(access, is_legacy=False),
            "year": str(year),
            "month": str(month),
            "day": str(day),
        }
        pageview_data = rest_api_call(
            PageViewApiEndPoints.TOP_VIEW_PER_COUNTRY, self._api_header, params
        )

        df = pd.DataFrame.from_dict(pageview_data["items"][0]["articles"])
        # add the common parameters into the data frame columns
        for key, value in params.items():
            df[key] = value
        return df

    def _call_legacy_api(
        self,
        access: AccessMethod,
        granularity: Granularity,
        start_time: datetime,
        end_time: datetime,
    ) -> pd.DataFrame:
        params = {
            "project": self._project,
            "access-site": translate_access_method_to_str(access, is_legacy=True),
            "granularity": translate_granularity_to_str(granularity),
            "start": start_time.strftime("%Y%m%d%H"),
            "end": end_time.strftime("%Y%m%d%H"),
        }

        legacy_data = rest_api_call(
            PageViewApiEndPoints.AGGRGATED_PAGEVIEWS_LEGACY, self._api_header, params
        )
        legacy_df = pd.DataFrame.from_dict(legacy_data["items"])
        self._align_legacy_df_to_pageview_df(legacy_df)
        return legacy_df

    def _call_page_view_api(
        self,
        access: AccessMethod,
        agent: AgentType,
        granularity: Granularity,
        start_time: datetime,
        end_time: datetime,
    ) -> pd.DataFrame:
        params = {
            "project": self._project,
            "access": translate_access_method_to_str(access, is_legacy=False),
            "agent": translate_agent_type_to_str(agent),
            "granularity": translate_granularity_to_str(granularity),
            "start": start_time.strftime("%Y%m%d%H"),
            "end": end_time.strftime("%Y%m%d%H"),
        }

        pageview_data = rest_api_call(
            PageViewApiEndPoints.AGGRGATED_PAGEVIEWS, self._api_header, params
        )
        return pd.DataFrame.from_dict(pageview_data["items"])

    def _align_legacy_df_to_pageview_df(self, legacy_df: pd.DataFrame) -> None:
        # rename the column to make it consistent with page view API
        legacy_df.rename(columns={"access-site": "access"}, inplace=True)
        legacy_df.rename(columns={"count": "views"}, inplace=True)
        legacy_df["access"] = legacy_df["access"].replace(
            ["all-sites", "desktop-site"], ["all-access", "desktop"]
        )
        # Legacy API doesn't have agent field, set to default all agents
        legacy_df["agent"] = "all-agents"
