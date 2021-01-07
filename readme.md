# Hacker rank 
----
[Hacker rank](https://www.hackerrank.com/) is a platform to learn all things programming. 
The purpose is to get all the successful submission in one go. Currently this fetches all the problems under python and saves it up. 


Example usage 
----

> python hackerrank.py


Dependencies
----

The Requests, selenium and Beautiful Soup libraries are required beyond the standard Python libraries. These can be usually be installed using your standard package manager or pip:

Download the [chromedriver](https://chromedriver.chromium.org/) depending on your version of Google Chrome installed 

Development
----
Basically uses the request and bs4 library to hit the end points and scrape the data. 
Request library does most of the heavy lifting suck as downloading files, api calls 
Bs4 is used to scrape avilable learning path 
Selenium library is used to load all the session data. 