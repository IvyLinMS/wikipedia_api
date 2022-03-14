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

### Component 5: (get_top_viewed_country)
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
                
### Component 5: (get_top_viewed_country)
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

### Components Private: (_call_top_view_per_country_api, _call_legacy_api, _call_page_view_api, _align_legacy_df_to_pageview_df)
Input(Dataframe with time and cost estimates per instance, generated by Component 5: recommender)
Final results output:  
Output (A sortable HTML table consisting of instances with their associated costs and times).
---
![components_map](./components-interaction-map.PNG)

---
### Components interaction
1. User passes string that will be used to call the user's algorithm. String contains data_loc = <data csv path>, target_loc = <target csv path>, and any other parameters.
2. algo_runner takes in the string. Subsets the data and target into small fractions and run user's algorithm on small sets of data. algo_runner returns the fractions of data used to run, and their respective runtime.
3. total_time takes in this information and fit a curve through the data points. This is used to estimate the time user's algorithm will take to run at 100% of the data. total_time_component returns this estimate.
4. Meanwhile, benchmark_runnner runs a predetermined menchmark test on user's computer. benchmark_runner retuns runtime of this benchmark test on user's computer.
5. Meanwhile, aws_pricing crawls Amazon AWS API for spot and on demand prices at that moment.
6. recommender takes in the output from total_time_component(3), benchmark_runner(4), and aws_pricing(5) to merge them all into one dataframe together with our own benchmark dataset on various AWS instance tpyes. This dataframe is passed to the report_generator.
7. report_generator takes the dataframe and builds a table of estimated time and cost to run uset's algorithm on various AWS instance types. This table is then returned as a HTML wile which allows users to sort and filter according to user's constraints.

---
### The Output
The HTML file created by report_generator:
![sample_reccommendation](./sample-recommendation.PNG)
