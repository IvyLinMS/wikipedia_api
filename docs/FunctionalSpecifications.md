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
<li>Choosing the instance which will return results as quickly as possible given a budgetary constraint
  <ol>
    <li>USER: Enters a budgetary constraint, say $100.</li>
    <li>USER: Provides location of algorithm file to be run</li>
    <li>USER: Provides location of data</li>
    <li>PROGRAM: Runs benchmark on user’s computer</li>
    <li>PROGRAM: Runs algorithm with small proportion of data</li>
    <li>OUTPUT: Suggested best instance for this use case</li>
  </ol>
</li>
<li>Choosing the instance which will return results within a time window.
  <ol>
    <li>USER: Enters a time constraint.</li>
    <li>USER: Provides location of algorithm file to be run</li>
    <li>USER: Provides location of data</li>
    <li>PROGRAM: Runs benchmark on user’s computer</li>
    <li>PROGRAM: Runs algorithm with small proportion of data</li>
    <li>OUTPUT: Suggested best instance for this use case</li>
  </ol>
</li>
</ol>
