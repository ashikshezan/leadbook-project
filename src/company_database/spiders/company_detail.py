from genericpath import exists
from json.decoder import JSONDecodeError
import scrapy
import json
from urllib.parse import urljoin
from os import path

BASE_DIR = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


class CompanyDetailSpider(scrapy.Spider):
    name = 'company_detail'
    allowed_domains = ['www.adapt.io']
    handle_httpstatus_list = [200, 410]
    number_of_http = set()

    def __init__(self):
        self.company_index_list = []
        self.company_index_path = path.join(BASE_DIR, 'company_index.json')

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
        print('-----------Failed attempt: ', len(self.company_index_list))
        print('=======Http responses: ', self.number_of_http)
        if path.exists(self.company_index_path):
            with open(self.company_index_path, 'w') as file:
                file.write(json.dumps(self.company_index_list))

    def start_requests(self):
        for company in self.company_index_list:
            url = urljoin('https://www.adapt.io', company['source_url'])
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        # just looking up the number http response I am getting
        self.number_of_http.add(response.status)

        if response.status == 410:
            error_company_index = response.url.split("https://www.adapt.io")[1]
            self.company_index_list = [
                i for i in self.company_index_list if not i['source_url'] == error_company_index]

        elif response.status == 200:
            error_company_index = response.url.split("https://www.adapt.io")[1]
            self.company_index_list = [
                i for i in self.company_index_list if not i['source_url'] == error_company_index]

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
                "url": error_company_index,
                "company name": company_name,
                "company_location": location,
                "company_website": web_site,
                "company_webdomain": web_domain,
                "company_industry": industry_name,
                "company_employee_size": employee_size,
                "company_revenue": revenue,
            }
