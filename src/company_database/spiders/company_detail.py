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

    # Some custom variables for debugging purposes
    http_410 = []
    http_503_count = 0

    def __init__(self):
        self.company_index_list = []
        self.company_index_path = path.join(BASE_DIR, 'company_index.json')
        self.company_index_of_http410_path = path.join(
            BASE_DIR, 'company_index_http_410.json')

        # taking the company_index file
        if path.exists(self.company_index_path):
            with open(self.company_index_path, 'r') as file:
                try:
                    self.company_index_list = json.load(file)
                except:
                    raise Exception('Please provide a valid JSON file')
        else:
            raise FileNotFoundError(
                "'company_index.json' file is needed to run the spider")

    def __del__(self):
        print('\n\n\n')
        print(
            f'{len(self.company_index_list)} companies still to be crawled ________________')
        print(f'HTTP 503 retuned: {self.http_503_count} ______________')
        print(f'HTTP 410 retuned: {len(self.http_410)} ______________')

        # Updating the company_index.json file by excluding the company that info
        # successfully scraped already
        if path.exists(self.company_index_path):
            with open(self.company_index_path, 'w') as file:
                file.write(json.dumps(self.company_index_list))

        # Creating a new file for the companty index that returned HTTP 410
        with open(self.company_index_of_http410_path, 'a') as file:
            file.write(json.dumps(self.http_410))

    def start_requests(self):
        for company in self.company_index_list:
            url = urljoin('https://www.adapt.io', company['source_url'])
            yield scrapy.Request(url=url, callback=self.parse)

    def update_company_index_list(self, to_be_excluded_url):
        '''
        A method to keep up-to-date the company urls list by excluding
        the urls that returned response successfully from self.company_index_list.
        Finally, at the end the self.company_index_list remains with the company urls list that
        the spider could not scrap because of HTTP 503 error.
        '''
        company_index = to_be_excluded_url.split(
            "https://www.adapt.io")[1]
        self.company_index_list = [
            i for i in self.company_index_list if not i['source_url'] == company_index]

    def parse(self, response):
        # just looking up the number http response I am getting
        if response.status == 410:
            self.http_410.append(response.url)
            self.update_company_index_list(response.url)

        elif response.status == 200:
            self.update_company_index_list(response.url)

            company_profile = get_company_profile(response)
            company_contact_list = get_company_contacts(response)

            company_profile['contact_details'] = company_contact_list

            yield company_profile

        elif response.status == 503:
            self.http_503_count += 1
