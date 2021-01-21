from os import path
import scrapy
import json
from urllib.parse import urljoin, urlparse
from typing import Dict, List

from .helper_tools import get_company_profile, get_company_contacts

BASE_DIR = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


class CompanyDetailSpider(scrapy.Spider):
    name = 'company_detail'
    allowed_domains = ['www.adapt.io']

    handle_httpstatus_list = [200, 410, 503]

    # variables for later debugging
    http_410 = []
    http_503_count = 0

    def __init__(self):
        self.company_index_list = []
        self.company_index_path = path.join(BASE_DIR, 'company_index.json')

        self.load_url_from_json_file(self.company_index_path)

    def __del__(self):
        self.update_http_503_company_list()
        self.update_http410_company_list()
        self.print_report()

    def start_requests(self):
        for company in self.company_index_list:
            url = urljoin('https://www.adapt.io', company['source_url'])
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        if response.status == 410:
            self.http_410.append(response.url)
            self.update_company_index_list(response.url)

        elif response.status == 503:
            self.http_503_count += 1

        elif response.status == 200:
            self.update_company_index_list(response.url)

            company_profile = get_company_profile(response)
            company_contact_list = get_company_contacts(response)

            # adding company_contacts into company_profile
            company_profile['contact_details'] = company_contact_list

            yield company_profile

    def update_company_index_list(self, url: str) -> None:
        '''
        This method uodate the company_index_list after every
        successful http 200 response by excluding the successfull url
        from the company_index_list. So at the end only faild http responses
        remain at the list. 
        '''
        company_index = url.split(
            "https://www.adapt.io")[1]
        self.company_index_list = [
            i for i in self.company_index_list if not i['source_url'] == company_index]

    def load_url_from_json_file(self, file_path: str) -> None:
        '''
        This method loads the urls from the 'company_index.json' file into 
        a list called 'self.company_index_list'
        '''
        if path.exists(file_path):
            with open(file_path, 'r') as file:
                try:
                    self.company_index_list = json.load(file)
                except:
                    raise Exception('Please provide a valid JSON file')
        else:
            raise FileNotFoundError(
                "'company_index.json' file is needed to run the spider")

    def print_report(self) -> None:
        print('\n\n')

        if self.company_index_list:
            print(f'HTTP 503 response count: {self.http_503_count}')
            print(f'HTTP 410 response count: {len(self.http_410)}')
            print(
                f'Companies still to be crawled: {len(self.company_index_list)}')
            print('Run this command: "crawl company_detail -o company_profiles.json"')

        else:
            print("Successfully crawled all the companies!")

    def update_http_503_company_list(self) -> None:
        '''
        This method update the 'company_index.json' file with the ursl
        which returns http 503 response so that those can be scrapped 
        successfully next time the spider is run.
        '''
        if path.exists(self.company_index_path):
            with open(self.company_index_path, 'w') as file:
                file.write(json.dumps(self.company_index_list))

    def update_http410_company_list(self) -> None:
        '''
        This method creates a file called 'unavailable_companies.json'
        The file contains the list of company that returned http 410 responses
        which means data is not available
        '''
        path_410 = path.join(
            BASE_DIR, 'unavailable_companies.json')

        with open(path_410, 'a') as file:
            file.write(json.dumps(self.http_410))
