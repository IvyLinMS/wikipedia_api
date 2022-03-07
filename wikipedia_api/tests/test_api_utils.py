from datetime import datetime
import unittest
from wikipedia_api.pageviews.api_constants import PageViewApiValidDateRange
from wikipedia_api.pageviews.api_exceptions import InputException
from wikipedia_api.pageviews.api_types import AccessMethod, AgentType, Granularity

from wikipedia_api.pageviews.api_utils import (
    parse_start_end_time,
    parse_time_parameter,
    split_time_range_for_legacy_api,
    translate_access_method_to_str,
    translate_agent_type_to_str,
    translate_granularity_to_str,
)


class APIUtilsTests(unittest.TestCase):
    def test_translate_access_method_to_str(self):
        # Test Legacy API
        self.assertEqual(
            translate_access_method_to_str(AccessMethod.ALL, is_legacy=True),
            "all-sites",
        )
        self.assertEqual(
            translate_access_method_to_str(AccessMethod.DESKTOP, is_legacy=True),
            "desktop-site",
        )
        self.assertEqual(
            translate_access_method_to_str(AccessMethod.MOBILE, is_legacy=True),
            "mobile-site",
        )
        self.assertEqual(
            translate_access_method_to_str(AccessMethod.MOBILE_APP, is_legacy=True),
            "mobile-site",
        )
        self.assertEqual(
            translate_access_method_to_str(AccessMethod.MOBILE_WEB, is_legacy=True),
            "mobile-site",
        )
        # test non legacy api
        self.assertEqual(
            translate_access_method_to_str(AccessMethod.ALL, is_legacy=False),
            "all-access",
        )
        self.assertEqual(
            translate_access_method_to_str(AccessMethod.DESKTOP, is_legacy=False),
            "desktop",
        )
        self.assertEqual(
            translate_access_method_to_str(AccessMethod.MOBILE_APP, is_legacy=False),
            "mobile-app",
        )
        self.assertEqual(
            translate_access_method_to_str(AccessMethod.MOBILE_WEB, is_legacy=False),
            "mobile-web",
        )
        with self.assertRaises(InputException):
            translate_access_method_to_str(AccessMethod.MOBILE, is_legacy=False)

    def test_translate_agent_type_to_str(self):
        self.assertEqual(translate_agent_type_to_str(AgentType.ALL), "all-agents")
        self.assertEqual(translate_agent_type_to_str(AgentType.USER), "user")
        self.assertEqual(translate_agent_type_to_str(AgentType.AUTOMATED), "automated")
        self.assertEqual(translate_agent_type_to_str(AgentType.SPIDER), "spider")

    def test_translate_granularity_to_str(self):
        self.assertEqual(translate_granularity_to_str(Granularity.HOURLY), "hourly")
        self.assertEqual(translate_granularity_to_str(Granularity.DAILY), "daily")
        self.assertEqual(translate_granularity_to_str(Granularity.MONTHLY), "monthly")

    def test_parse_time_parameter(self):
        expect_dt = datetime(2020, 1, 1)
        self.assertEqual(parse_time_parameter("20200101"), expect_dt)
        expect_dt_hour = datetime(2020, 1, 1, hour=1)
        self.assertEqual(
            parse_time_parameter("2020010101", support_hour=True), expect_dt_hour
        )

        with self.assertRaises(InputException):
            parse_time_parameter("202001011")

        with self.assertRaises(InputException):
            parse_time_parameter("abc")

        # with hour format but support_hour is False
        with self.assertRaises(InputException):
            parse_time_parameter("2020010101")

    def test_parse_start_end_time(self):
        expect_start = datetime(2020, 1, 1)
        expect_end = datetime(2020, 1, 1, hour=1)
        start, end = parse_start_end_time("20200101", "2020010101", support_hour=True)
        self.assertEqual(start, expect_start)
        self.assertEqual(end, expect_end)
        with self.assertRaises(InputException):
            parse_start_end_time("20201111", "20201101")

        # end time is before new api start date
        start_time = datetime(2008, 1, 1)
        end_time = datetime(2009, 1, 1)
        (
            legacy_api_start_time,
            legacy_api_end_time,
            page_view_api_start_time,
            page_view_api_end_time,
        ) = split_time_range_for_legacy_api(start_time, end_time)
        self.assertEqual(legacy_api_start_time, start_time)
        self.assertEqual(legacy_api_end_time, end_time)
        self.assertIsNone(page_view_api_start_time)
        self.assertIsNone(page_view_api_end_time)

        # start time is after new api start date
        start_time = datetime(2016, 1, 1)
        end_time = datetime(2017, 1, 1)
        (
            legacy_api_start_time,
            legacy_api_end_time,
            page_view_api_start_time,
            page_view_api_end_time,
        ) = split_time_range_for_legacy_api(start_time, end_time)

        self.assertIsNone(legacy_api_start_time)
        self.assertIsNone(legacy_api_end_time)
        self.assertEqual(page_view_api_start_time, start_time)
        self.assertEqual(page_view_api_end_time, end_time)

        # start time overlap the new api start date
        start_time = datetime(2010, 1, 1)
        end_time = datetime(2017, 1, 1)
        (
            legacy_api_start_time,
            legacy_api_end_time,
            page_view_api_start_time,
            page_view_api_end_time,
        ) = split_time_range_for_legacy_api(start_time, end_time)

        self.assertEqual(legacy_api_start_time, start_time)
        self.assertEqual(
            legacy_api_end_time, PageViewApiValidDateRange.PAGEVIEW_API_START_DATE
        )
        self.assertEqual(
            page_view_api_start_time, PageViewApiValidDateRange.PAGEVIEW_API_START_DATE
        )
        self.assertEqual(page_view_api_end_time, end_time)
