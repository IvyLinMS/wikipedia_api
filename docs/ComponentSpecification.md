## Software Components

### Component 1: (get_aggregated_pageviews)
        Given a date range, returns a timeseries of pageview counts.
        Support filter by access method and/or agent type, and choose between
        monthly, daily, hourly granularity
        if start time specified is between 12/01/2007 and 07/01/2015, legacy
        API data will be combined with new page view API data if agent type
        is set to MOBILE and date range include 07/01/2015, both the
        mobile-app and mobile-web data will be returned
        Args:
            request (AggregatePageViewRequest): Request data for get
            aggregated page view
        Raises:
            InputException: User input error if start time or end time is
            invalid or out of supported range

        Returns:
            pd.DataFrame: columns:
                "project": str,
                "access": str,
                "agent": str,
                "granularity": str,
                "timestamp": str,
                "views": int 

### Component 2: (get_top_view_per_country)
        Lists the 1000 most viewed articles for a given country and date,
        across all projects. Support filter by access method. Because of
        privacy reasons, pageview counts are given in a bounded format and
        are not reported for certain countries. Furthermore, articles visited
        by 1000 unique individuals or fewer on the given date will be excluded
        from the returned data. Also, views produced by agents categorized as
        bots or web crawlers will be excluded from all calculations, if
        all-days is specified in the day parameter, all data within the
        specified month will be returned

        Args:
            request (TopViewedPerCountryRequest): Request data for get top
            page viewed article per country

        Raises:
            InputException: User input error if start time or end time is
            invalid or out of supported range or MOBILE access method is
            specified as current page view API doesn't support this access type

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

### Component 3: (get_per_article_pageviews)  
        Given an article and a date range, returns a daily timeseries of its
        pageview counts. Support filter by access method and/or agent type,
        and choose between monthly, daily granularity

        Args:
            request (PerArticlePageViewRequest): Request data for get page
            view for a specific artical
        Raises:
            InputException: User input error if start time or end time is
            invalid or MOBILE access method is specified as current page view
            API doesn't support this access type
        Returns:
            pd.DataFrame: columns:
                "project": str,
                "access": str,
                "article": str,
                "agent": str,
                "granularity": str,
                "timestamp": str,
                "views": int
                
### Component 4: (get_top_pageviews)
        Lists the 1000 most viewed articles timespan (month or day), support
        filter by access method

        Args:
            request (TopViewedArticleRequest): Request data for get top viewed
            article

        Raises:
            InputException: User input error if start time or end time is
            invalid or out of supported range

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

### Component 5: (get_top_viewed_country)
        Lists the pageviews to this project, split by country of origin for a
        given month. Because of privacy reasons, pageviews are given in a
        bucketed format, and countries with less than 100 views do not get
        reported.

        Args:
            request (TopViewedCountryRequest): Request data for get page views
            split by country

        Raises:
            InputException: User input error if start time or end time is
            invalid or out of supported range or MOBILE access method is
            specified as current page view API doesn't support this access type

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
                
### Components Private: (_call_top_view_per_country_api, _call_legacy_api, _call_page_view_api, _align_legacy_df_to_pageview_df)
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

### Component Diagram Example
Component <b>get_top_view_per_country</b>
     +  Lists the 1000 most viewed articles for a given country and date, across all projects. 
        Support filter by access method. Because of privacy reasons, pageview counts are given 
        in a bounded format and are not reported for certain countries. Furthermore, articles 
        visited by 1000 unique individuals or fewer on the given date will be excluded from the 
        returned data. Also, views produced by agents categorized as bots or web crawlers will 
        be excluded from all calculations, if all-days is specified in the day parameter, all data
        within the specified month will be returned
     (./diagram/GetTopViewed.png)


---
### Components interaction
1. get_aggregated_pageviews calls _call_legacy_api and _call_page_view_api
2. get_top_view_per_country calls _call_top_view_per_country_ap
3. _call_legacy_api calls _align_legacy_df_to_pageview_df

---
### Example for Call get_aggregated_pageviews
Reference to Example Folder https://github.com/IvyLinMS/wikipedia_api/blob/main/examples/wikipedia_api_examples.ipynb
