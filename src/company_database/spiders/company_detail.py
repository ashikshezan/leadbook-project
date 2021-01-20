import scrapy
import json
from urllib.parse import urljoin
from os import path

BASE_DIR = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


class CompanyDetailSpider(scrapy.Spider):
    name = 'company_detail'
    allowed_domains = ['www.adapt.io']

    handle_httpstatus_list = [200, 410]

    # Some custom variables for debugging purposes
    http_410 = []

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
        print(
            f'{len(self.company_index_list)} companies still to be crawled ________________')
        print(f'HTTP 410 retuned: {len(self.http_410)} ______________')

        # Updating the company_index.json file by excluding the company that info
        # successfully scraped already
        if path.exists(self.company_index_path):
            with open(self.company_index_path, 'w') as file:
                file.write(json.dumps(self.company_index_list))

        # Creating a new file for the companty index that returned HTTP 410
        with open(self.company_index_of_http410_path, 'w') as file:
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

    def catch_410_error_list(self, url):
        error_company_index = url.split(
            "https://www.adapt.io")[1]
        self.http_410.append(error_company_index)

    def parse(self, response):

        # just looking up the number http response I am getting
        if response.status == 410:
            self.catch_410_error_list(response.url)
            self.update_company_index_list(response.url)

        elif response.status == 200:
            self.update_company_index_list(response.url)
            company_name = response.xpath(
                "//div[@class='info-wrapper']//h1//text()").get()
            location = response.xpath(
                "//div[@class='info-wrapper']//li//span[text()='Location']//following-sibling::node()[2]/text()").get()
            web_site = response.xpath(
                "//div[@class='info-wrapper']//span[@class='website-url']/text()").get()
            web_domain = web_site
            industry_name = response.xpath(
                "//div[@class='info-wrapper']//li//span[text()='Industry']//following-sibling::node()[2]/text()").get()
            employee_size = response.xpath(
                "//div[@class='info-wrapper']//li//span[text()='Head Count']//following-sibling::node()[2]/text()").get()
            revenue = response.xpath(
                "//div[@class='info-wrapper']//li//span[text()='Revenue']//following-sibling::node()[2]/text()").get()

            yield {
                "company name": company_name,
                "company_location": location,
                "company_website": web_site,
                "company_webdomain": web_domain,
                "company_industry": industry_name,
                "company_employee_size": employee_size,
                "company_revenue": revenue,
            }
