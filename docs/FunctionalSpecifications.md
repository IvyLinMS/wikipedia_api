## Functional Specifications

### Background.
Last quarter I had a class called "DATA 512 A Au 21: Human-Centered Data Science", we did a lot of projects using WikiPedia data, then I found the WikiPedia API is not very convenient to use for our research. Since we learned a lot of Software Design in Data512, so I decided to create a Python package to make an easy to use class for accessing Wikipedia page view API by providing unified API for page view aggregated data with set only once common parameters such as User-Agent and hide the detail of HTTP request construction, also provide top result per country on monthly level API which currently the Wikipedia API only support daily level.

### User profile.
- Researchers
- Students
- Corporate Dev/Data Engineers
The users are someone who are using WikiPedia data to doing some research.

### Data source:
Wikipedia traffic from 2008-2021

### Data acquisition:
- Wikimedia Foundation REST API terms of use: https://www.mediawiki.org/wiki/REST_API#Terms_and_conditions
- The Legacy Pagecounts API (https://wikitech.wikimedia.org/wiki/Analytics/AQS/Legacy_Pagecounts) provides access to desktop and mobile traffic data from December 2007 through July 2016.
- The Pageviews API (https://wikitech.wikimedia.org/wiki/Analytics/AQS/Pageviews) provides access to desktop, mobile web, and mobile app traffic data from July 2015 through last month.

### Use cases. 
<ol>
<li>Listing the 1000 most viewed articles for a given country and date, across all projects. 
  <ol>
    <li>USER Enter1: access=AccessMethod.ALL, year=2015, month=6, day=20</li>
    <li>USER Enter2: access=AccessMethod.ALL, year=2020, month=1, day="all"</li>
    <li>PROGRAM: Runs rest_api_call(PageViewApiEndPoints.TOP_VIEW_BY_COUNTRY</li>
    <li>PROGRAM: Repeat rest_api_call then convert and append to dataframe</li>
    <li>OUTPUT: Top 1000 most viewed articles for a single day or the whole month</li>
  </ol>
</li>
<li>Given a date range, returns a timeseries of pageview counts.
  <ol>
    <li>USER Enter: access=AccessMethod.MOBILE, agent=AgentType.USER, granularity=Granularity.DAILY, start_time="20101110", end_time="20201111",</li>
    <li>PROGRAM: Runs get_aggregated_pageviews to rest_api_call https://wikimedia.org/api/rest_v1/metrics/pageviews/aggregate/all-projects </li>
    <li>OUTPUT: returns a timeseries of pageview counts for access method and Daily/Monthly</li>
  </ol>
</li>
</ol>

### Unit Test.

Reference to test folder https://github.com/IvyLinMS/wikipedia_api/tree/main/wikipedia_api/tests.
