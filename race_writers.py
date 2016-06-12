"""This module contains the writer classes for producing a dictionary,
csv file, and sqllite database of results"""


import csv
import sqlite3

class WritingError(Exception):
    pass

class MatchError(WritingError):
    pass


class Writer:
    """ Define superclass for writing scraping results"""
    def __init__(self, headerlist):
        self.header = headerlist
    def finish(self):
        pass

class CSVWriter(Writer):
    """Write scraping results to a CSV file """
    def __init__(self, filename, headerlist):
        self.header = ['Year'] + headerlist
        self.f = open(filename, 'a+', encoding = "utf-8")
        self.resultswriter = csv.writer(self.f)
        self.resultswriter.writerow(self.header)
    def write(self, year_number, table):
        for row in table:
            row.insert(0, year_number)
            self.resultswriter.writerow(row)
    def finish(self):
        self.f.close()


class SQLiteWriter(Writer):
    """Write scraping results to a SQLLite file"""
    def __init__(self, database_file, table_name, headerlist, headertype):
        if len(headerlist) != len(headertype):
            raise MatchError('Length of header and headertype lists not equal')
        self.header = ['Year'] + headerlist
        self.headertype = ['INTEGER'] + headertype
        self.table_name = table_name
        headerzipped = zip(self.header, self.headertype)
        table_columns = ', '.join([' '.join(i) for i in headerzipped])
        self.conn = sqlite3.connect(database_file)
        self.cur = self.conn.cursor()
        self.cur.execute('CREATE TABLE IF NOT EXISTS ' + table_name + ' ('+ table_columns + ');')
    def write(self, year_number, table):        
        try:
            for row in table:
                row.insert(0, year_number)
                if len(row) != len(self.header):
                    raise MatchError('Length of row and header not equal')
            converted_table = [tuple(i) for i in table]
            self.cur.executemany('INSERT INTO ' + self.table_name + ' VALUES (' + ', '.join(['?']*len(self.header)) + ')', converted_table)
            self.conn.commit()
        except WritingError():
            print("Encountered problems with writing data for year", year_number)
    def finish(self):
        self.conn.close()
            

class DictWriter(Writer):
    """Store scraping results in a dictionary, where the keys are year numbers """
    def __init__(self, headerlist):
        self.result_tables = {}   #Create a result table where keys are year numbers and values are nested list of results
        self.result_tables['Header'] = headerlist
    def write(self, year_number, table):
        self.result_tables[year_number] = table

            
