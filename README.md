# wikipedia_api
[![Build Status](https://app.travis-ci.com/IvyLinMS/wikipedia_api.svg?branch=main)](https://app.travis-ci.com/IvyLinMS/wikipedia_api)

## Project Motivation

+ Wikipedia provide a set of RESTful APIs to get Wikipedia's page view data. Users of these APIs can provide different Wikipedia projects they are interested in and specify date range as well as different filters such as access method, agent type etc. but there are some issues with the APIs.
  + Most of the parameters are in string format, such as the access method or agent type, which is error prone as typo or mis capitalization could happen
  + Some of the API could set hourly, daily, monthly granularity, but the date format specified required to pass in hour information even user didn't specify to get the data at hourly granularity level
  + Aggregated page view API has two version, one for legacy data from 12/01/2007 to 07/01/2015, while another API provide data after 07/01/2015, if user need to get data from after 12/01/2007 to a date after 07/01/2015, user will have to explicit call the two API separately and provide different set of parameters for access method or agent type
  + Top viewed article per country API only support daily granularity without monthly level support
 
