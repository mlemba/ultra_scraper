#!/usr/bin/env python3

"""This module contains the scraper class for retrieving results from Ultrasignup web page
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import pickle

import race_writers

header = ['Place', 'First_name', 'Last_name', 'City', 'State', 'Age', 'Gender', 'Gender_placement', 'Time', 'Rank', 'Finish_status']
SQLite_headertype = ['INTEGER', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'INTEGER', 'TEXT', 'INTEGER', 'TEXT', 'REAL', 'TEXT']

class UltraRaceScraper:
    """Scrape results, starting from a race URL, and write them out using an instance from a writing class """
    def __init__(self, race_url, results_writer):
        """Initilize the driver using PhantomJS and retrieve the starting web page"""
        self.driver = webdriver.PhantomJS(executable_path='/home/maris/Documents/Python/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
        self.race_url = race_url
        self.results_writer = results_writer
        
    def scrape_results(self):
        """Find the links to yearly results, click on them, and collect the result table"""
        self.driver.get(self.race_url)

        #The links have a class named 'year_link' which we found by inspecting the DOM
        number_of_years = len(self.driver.find_elements_by_class_name('year_link'))

        for year in range(number_of_years):
            year_page = self.driver.find_elements_by_class_name('year_link')[year]
            results = []
            year_number = year_page.text
            print("Retrieving results from year",year_number)
            finisher_flag = "Finished"
            year_page.click()
            
            #Keep polling the DOM for string "Finishers" to show up in our table up until 10s has passed
            #This is to make sure Ajax loading of the table has completed
            try:
                WebDriverWait(self.driver, 10).until(EC.text_to_be_present_in_element((By.ID,'list'),'results'))
                
                tablerows = self.driver.find_elements_by_xpath("//table[@id='list']/tbody/tr")   #find table with id="list"
                
                for row in tablerows:
                    td_elements = row.find_elements_by_tag_name("td")
                    if len(td_elements) >4 and td_elements[0].text:
                        results.append([elem.text for elem in td_elements[1:-4]]+[finisher_flag])
                    elif "did not finish" in td_elements[0].text.lower():
                        finisher_flag = "DNF"
                    elif "did not start" in td_elements[0].text.lower():
                        finisher_flag = "DNS"
            
                self.results_writer.write(year_number, results)
    
            except TimeoutException:     
                print("Unable to retrieve results for year", year_number)

            
            self.driver.back()


if __name__ == '__main__':
    
    url = "http://ultrasignup.com/register.aspx?did=36209"    #Sample url for White River 50 front page
    
    #Initialize all writers
    csv_writer = race_writers.CSVWriter('test.csv',header)
    dict_writer = race_writers.DictWriter(header)
    sqlite_writer = race_writers.SQLiteWriter('test.sqlite', 'Results', header, SQLite_headertype)
    
    writers = [csv_writer, dict_writer, sqlite_writer]
    
    for results_writer in writers:
        try:
            scraper = UltraRaceScraper(url, results_writer)
        except (IOError, race_writers.sqlite3.OperationalError):   #In case opening a CSV file or SQLLite database file failed
            results_writer = DictWriter(header)
            scraper = UltraRaceScraper(url, results_writer)
        
        scraper.scrape_results()

        results_writer.finish()
        
    pickle.dump(dict_writer.result_tables, open('raceresult_dict','wb'))



