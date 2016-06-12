# ultra_scraper

race_scraper.py is a Python module to retrieve race data from [Ultrasignup web site](https://ultrasignup.com/). 
UltraSignup (as of now) uses Ajax to generate the result pages, and the UltraRaceScraper class in race_scraper.py uses selenium and PhantomJS to retrieve the results.

The race_writers.py module is a module that contains three classes of writers for the race data: 1) to store it in a dictionary, 2) to write it out as a csv file, 3) and to write it out as sqlite file.

# Usage

Input to the main scraper class is the url of the particular race web page (e.g. Western States, etc).
See the code at the bottom of file race_scraper.py for detailed example of usage.

