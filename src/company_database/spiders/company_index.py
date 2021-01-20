import scrapy


class CompanyIndexSpider(scrapy.Spider):
    name = 'company_index'
    allowed_domains = ['www.adapt.io']
    start_urls = [
        'https://www.adapt.io/directory/industry/telecommunications/A-1']

    def parse(self, response):
        company_index_page_A_to_Z = response.xpath(
            "//ul[@class='alphabet-nav-list']//a")

        for company_index_page in company_index_page_A_to_Z:
            link = company_index_page.xpath(".//@href").get()
            yield response.follow(url=link, callback=self.parse_index_page)

    def parse_index_page(self, response):
        company_list = response.xpath("//div[@class='list-item']/a")
        for company in company_list:
            name = company.xpath(".//text()").get()
            link = company.xpath(".//@href").get()

            yield {
                "company_name": name,
                "source_url": link
            }
