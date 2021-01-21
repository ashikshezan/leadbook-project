from typing import Dict, List
from urllib.parse import urljoin, urlparse


def get_company_profile(response) -> Dict:
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
    # extracting the company web domain name from the website url
    if web_site:
        web_domain = company_web_domain_exptractor(
            web_site)
    return {
        "company_name": company_name,
        "company_location": location,
        "company_website": web_site,
        "company_webdomain": web_domain,
        "company_industry": industry_name,
        "company_employee_size": employee_size,
        "company_revenue": revenue,
    }


def get_company_contacts(response) -> List:
    contact_list = []
    contact_items = response.xpath(
        "//div[@class='top-contact-item']")
    for contact in contact_items:
        name = contact.xpath('.//a//text()').get()
        link = contact.xpath('.//a//@href').get()
        job_title = contact.xpath(
            ".//p[@class='contact-role']//text()").get()
        email_domain = contact.xpath(
            ".//span[@itemprop='email']//text()").get().strip()
        # extracting the domain name only
        email_domain = contact_email_domain_exptractor(
            email_domain)
        contact_list.append(
            {
                "contact_name": name,
                "contact_jobtitle": job_title,
                "contact_email_domain": email_domain,
                "contact_profile_link": link,
            }
        )
    return contact_list


def contact_email_domain_exptractor(email: str) -> str:
    return email.split('@')[-1]


def company_web_domain_exptractor(website: str) -> str:
    domain = urlparse(website).netloc
    domain_parts = domain.split('.')
    domain_name = '.'.join(domain_parts[1:])
    return domain_name


if __name__ == "__main__":
    pass
