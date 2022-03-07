import unittest
import json
from unittest.mock import MagicMock, patch

import pandas as pd

from wikipedia_api.pageviews.api_client import WikipediaPageViewApiClient
from wikipedia_api.pageviews.api_exceptions import InputException
from wikipedia_api.pageviews.api_types import (
    APIHeader,
    AccessMethod,
    AgentType,
    AggregatePageViewRequest,
    Granularity,
    PerArticlePageViewRequest,
    TopViewedArticleRequest,
    TopViewedCountryRequest,
    TopViewedPerCountryRequest,
)


class WikipediaPageViewApiClientTest(unittest.TestCase):
    def setUp(self):
        self._project: str = "en.wikipedia"
        self._user_agent = "test agent"
        self._call_from = "test@test.com"
        self._api_header = APIHeader(self._user_agent, self._call_from)

    def test_init(self):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        self.assertEqual(client.project, self._project)

    def test_get_per_article_pageviews(self):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        request = PerArticlePageViewRequest(
            access=AccessMethod.ALL,
            agent=AgentType.USER,
            article="Main",
            granularity=Granularity.DAILY,
            start_time="20201110",
            end_time="20201111",
        )
        df = client.get_per_article_pageviews(request)
        expected_columns = set(
            [
                "project",
                "access",
                "article",
                "agent",
                "granularity",
                "timestamp",
                "views",
            ]
        )
        self.assertEqual(set(df.columns), expected_columns)

    def test_get_per_article_pageviews_input_validation(self):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        # invalid start time
        request = PerArticlePageViewRequest(
            access=AccessMethod.ALL,
            agent=AgentType.USER,
            article="Main",
            granularity=Granularity.DAILY,
            start_time="20201110x",
            end_time="20201111",
        )
        with self.assertRaises(InputException):
            client.get_per_article_pageviews(request)

        # invalid end time
        request = PerArticlePageViewRequest(
            access=AccessMethod.ALL,
            agent=AgentType.USER,
            article="Main",
            granularity=Granularity.DAILY,
            start_time="20201110",
            end_time="20201141",
        )
        with self.assertRaises(InputException):
            client.get_per_article_pageviews(request)

        # start_time not in valid range
        request = PerArticlePageViewRequest(
            access=AccessMethod.ALL,
            agent=AgentType.USER,
            article="Main",
            granularity=Granularity.DAILY,
            start_time="20141112",
            end_time="20201111",
        )
        with self.assertRaises(InputException):
            client.get_per_article_pageviews(request)

        # start_time > end_time
        request = PerArticlePageViewRequest(
            access=AccessMethod.ALL,
            agent=AgentType.USER,
            article="Main",
            granularity=Granularity.DAILY,
            start_time="20201112",
            end_time="20201111",
        )
        with self.assertRaises(InputException):
            client.get_per_article_pageviews(request)

        # AccessMethod=MOBILE
        request = PerArticlePageViewRequest(
            access=AccessMethod.MOBILE,
            agent=AgentType.USER,
            article="Main",
            granularity=Granularity.DAILY,
            start_time="20201110",
            end_time="20201111",
        )
        with self.assertRaises(InputException):
            client.get_per_article_pageviews(request)

        # Granularity=HOURLY
        request = PerArticlePageViewRequest(
            access=AccessMethod.MOBILE,
            agent=AgentType.USER,
            article="Main",
            granularity=Granularity.HOURLY,
            start_time="20201110",
            end_time="20201111",
        )
        with self.assertRaises(InputException):
            client.get_per_article_pageviews(request)

    def test_get_aggregated_pageviews_input_validation(self):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        # start time not in valid range
        request = AggregatePageViewRequest(
            access=AccessMethod.ALL,
            agent=AgentType.USER,
            granularity=Granularity.DAILY,
            start_time="20061110",
            end_time="20201111",
        )
        with self.assertRaises(InputException):
            client.get_aggregated_pageviews(request)

    @patch(
        "wikipedia_api.pageviews.api_client.WikipediaPageViewApiClient._call_legacy_api"
    )
    @patch(
        "wikipedia_api.pageviews.api_client.WikipediaPageViewApiClient._call_page_view_api"
    )
    def test_get_aggregated_pageviews_include_both_legacy_and_new_data_and_mobile(
        self, page_view_api_mock: MagicMock, legacy_api_mock: MagicMock
    ):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        request = AggregatePageViewRequest(
            access=AccessMethod.MOBILE,
            agent=AgentType.USER,
            granularity=Granularity.DAILY,
            start_time="20101110",
            end_time="20201111",
        )
        page_view_api_mock.return_value = pd.DataFrame()
        legacy_api_mock.return_value = pd.DataFrame()
        client.get_aggregated_pageviews(request)
        legacy_api_mock.assert_called_once()
        self.assertEqual(page_view_api_mock.call_count, 2)

    @patch(
        "wikipedia_api.pageviews.api_client.WikipediaPageViewApiClient._call_legacy_api"
    )
    @patch(
        "wikipedia_api.pageviews.api_client.WikipediaPageViewApiClient._call_page_view_api"
    )
    def test_get_aggregated_pageviews_include_both_legacy_and_new_data_non_mobile(
        self, page_view_api_mock: MagicMock, legacy_api_mock: MagicMock
    ):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        request = AggregatePageViewRequest(
            access=AccessMethod.ALL,
            agent=AgentType.USER,
            granularity=Granularity.DAILY,
            start_time="20101110",
            end_time="20201111",
        )
        page_view_api_mock.return_value = pd.DataFrame()
        legacy_api_mock.return_value = pd.DataFrame()
        client.get_aggregated_pageviews(request)
        legacy_api_mock.assert_called_once()
        page_view_api_mock.assert_called_once()

    def test_get_aggregated_pageview(self):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        request = AggregatePageViewRequest(
            access=AccessMethod.ALL,
            agent=AgentType.USER,
            granularity=Granularity.MONTHLY,
            start_time="20101110",
            end_time="20201111",
        )
        df = client.get_aggregated_pageviews(request)
        expected_columns = set(
            ["project", "access", "agent", "granularity", "timestamp", "views",]
        )
        self.assertEqual(set(df.columns), expected_columns)

    def test_get_aggregated_pageview_legacy_range_only(self):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        request = AggregatePageViewRequest(
            access=AccessMethod.ALL,
            agent=AgentType.USER,
            granularity=Granularity.MONTHLY,
            start_time="20101110",
            end_time="20121111",
        )
        df = client.get_aggregated_pageviews(request)
        expected_columns = set(
            ["project", "access", "agent", "granularity", "timestamp", "views",]
        )
        self.assertEqual(set(df.columns), expected_columns)

    def test_get_top_pageviews_validation(self):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        # MOBILE access not support
        request = TopViewedArticleRequest(
            access=AccessMethod.MOBILE, year=2020, month=1, day=1,
        )
        with self.assertRaises(InputException):
            client.get_top_pageviews(request)

        request = TopViewedArticleRequest(
            access=AccessMethod.ALL, year=-2020, month=1, day=1,
        )
        with self.assertRaises(InputException):
            client.get_top_pageviews(request)

        request = TopViewedArticleRequest(
            access=AccessMethod.ALL, year=2020, month=-1, day=1,
        )
        with self.assertRaises(InputException):
            client.get_top_pageviews(request)
            
        request = TopViewedArticleRequest(
            access=AccessMethod.ALL, year=2020, month=13, day=1,
        )
        with self.assertRaises(InputException):
            client.get_top_pageviews(request)

        request = TopViewedArticleRequest(
            access=AccessMethod.ALL, year=2020, month=1, day=-1,
        )
        with self.assertRaises(InputException):
            client.get_top_pageviews(request)

        request = TopViewedArticleRequest(
            access=AccessMethod.ALL, year=2020, month=1, day="all",
        )
        with self.assertRaises(InputException):
            client.get_top_pageviews(request)

        request = TopViewedArticleRequest(
            access=AccessMethod.ALL, year=2015, month=6, day="all-days",
        )
        with self.assertRaises(InputException):
            client.get_top_pageviews(request)

    def test_get_top_pageviews(self):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        request = TopViewedArticleRequest(
            access=AccessMethod.MOBILE_APP, year=2020, month=1, day=1,
        )
        df = client.get_top_pageviews(request)
        expected_columns = set(
            ["project", "access", "year", "month", "day", "article", "views", "rank",]
        )
        self.assertEqual(set(df.columns), expected_columns)

    def test_get_top_viewed_country_validation(self):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        # MOBILE access not support
        request = TopViewedCountryRequest(
            access=AccessMethod.MOBILE, year=2020, month=1,
        )
        with self.assertRaises(InputException):
            client.get_top_viewed_country(request)

        request = TopViewedCountryRequest(access=AccessMethod.ALL, year=-2020, month=1,)
        with self.assertRaises(InputException):
            client.get_top_viewed_country(request)

        request = TopViewedCountryRequest(access=AccessMethod.ALL, year=2020, month=-1,)
        with self.assertRaises(InputException):
            client.get_top_viewed_country(request)

        request = TopViewedCountryRequest(access=AccessMethod.ALL, year=2020, month=13,)
        with self.assertRaises(InputException):
            client.get_top_viewed_country(request)

    def test_get_top_viewed_country(self):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        request = TopViewedCountryRequest(
            access=AccessMethod.MOBILE_APP, year=2020, month=1,
        )
        df = client.get_top_viewed_country(request)
        expected_columns = set(
            [
                "project",
                "access",
                "year",
                "month",
                "country",
                "views",
                "rank",
                "views_ceil",
            ]
        )
        self.assertEqual(set(df.columns), expected_columns)

    def test_get_top_view_per_country_validation(self):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        # MOBILE access not support
        request = TopViewedPerCountryRequest(
            country="US", access=AccessMethod.MOBILE, year=2020, month=1, day=1,
        )
        with self.assertRaises(InputException):
            client.get_top_view_per_country(request)

        request = TopViewedPerCountryRequest(
            country="US", access=AccessMethod.ALL, year=-2020, month=1, day=1,
        )
        with self.assertRaises(InputException):
            client.get_top_view_per_country(request)

        request = TopViewedPerCountryRequest(
            country="US", access=AccessMethod.ALL, year=2020, month=-1, day=1,
        )
        with self.assertRaises(InputException):
            client.get_top_view_per_country(request)

        request = TopViewedPerCountryRequest(
            country="US", access=AccessMethod.ALL, year=2020, month=1, day=-1,
        )
        with self.assertRaises(InputException):
            client.get_top_view_per_country(request)

        request = TopViewedPerCountryRequest(
            country="US", access=AccessMethod.ALL, year=2020, month=1, day="all",
        )
        with self.assertRaises(InputException):
            client.get_top_view_per_country(request)

        request = TopViewedPerCountryRequest(
            country="US", access=AccessMethod.ALL, year=2020, month=12, day=31,
        )
        with self.assertRaises(InputException):
            client.get_top_view_per_country(request)

    def test_get_top_view_per_country(self):
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        request = TopViewedPerCountryRequest(
            country="US", access=AccessMethod.ALL, year=2021, month=1, day=1,
        )
        df = client.get_top_view_per_country(request)
        expected_columns = set(
            [
                "country",
                "access",
                "year",
                "month",
                "day",
                "rank",
                "article",
                "project",
                "views_ceil",
            ]
        )
        self.assertEqual(set(df.columns), expected_columns)

    @patch(
        "wikipedia_api.pageviews.api_client.rest_api_call"
    )
    def test_get_top_view_per_country_all_days(self, rest_api_call_mock: MagicMock):

        mock_data1 = """
        {
            "items": [
                {
                "country": "US",
                "access": "mobile-app",
                "year": "2021",
                "month": "12",
                "day": "01",
                "articles": [
                    {
                    "article": "Deaths_in_2021",
                    "project": "en.wikipedia",
                    "views_ceil": 1000,
                    "rank": 1
                    },
                    {
                    "article": "Thank_You/en",
                    "project": "thankyou.wikipedia",
                    "views_ceil": 900,
                    "rank": 2
                    }
                ]
                }
            ]
            }
        """
        mock_data2 = """
        {
            "items": [
                {
                "country": "US",
                "access": "mobile-app",
                "year": "2021",
                "month": "12",
                "day": "02",
                "articles": [
                    {
                    "article": "Deaths_in_2021",
                    "project": "en.wikipedia",
                    "views_ceil": 500,
                    "rank": 1
                    },
                    {
                    "article": "Thank_You/en",
                    "project": "thankyou.wikipedia",
                    "views_ceil": 1000,
                    "rank": 2
                    }
                ]
                }
            ]
            }
        """
        empty_mock_data = """
        {
            "items": [
                {
                "country": "US",
                "access": "mobile-app",
                "year": "2021",
                "month": "12",
                "day": "03",
                "articles": []
                }
            ]
        }
        """
        return_values = [json.loads(mock_data1), json.loads(mock_data2)]
        # return empty result from remaining 29 days
        for _ in range(29):
            return_values.append(json.loads(empty_mock_data))
        rest_api_call_mock.side_effect = return_values
        client = WikipediaPageViewApiClient(self._project, self._api_header)
        request = TopViewedPerCountryRequest(
            country="US", access=AccessMethod.ALL, year=2021, month=1, day="all-days",
        )
        df = client.get_top_view_per_country(request)
        expected_columns = set(
            [
                "country",
                "access",
                "year",
                "month",
                "day",
                "rank",
                "article",
                "project",
                "views_ceil",
            ]
        )
        self.assertEqual(set(df.columns), expected_columns)
        self.assertEqual(rest_api_call_mock.call_count, 31)
        self.assertEqual(df["article"][0], "Thank_You/en")
        self.assertEqual(df["views_ceil"][0], 1900)
        self.assertEqual(df["article"][1], "Deaths_in_2021")
        self.assertEqual(df["views_ceil"][1], 1500)

