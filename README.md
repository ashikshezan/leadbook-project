# Application Architecture

The application is designed on top of the Scrapy framework. I created 2 basic spiders to crawl the required data which I will explain in the later part of this documentation. After crawling all the pages I store that data in a MongoDB that has 2 collections `company_index` & `company_profile` 

## Part One: First Spider

Firstly all the company urls (A-Z) had to be crawled from the site. I created a spider called `company_index.py` which crawled `1128` company urls and stored the data in a file called `company_index.json`  in the Scrapy root directory which is `/src/` After successfully scraping all the company urls the the `company_index.json` file must be copied into the `collected_data/` directory because later when the second spider will run, the data of `src/company_index.json` file will be deleted.

The command to run this spider `scrapy crawl company_index -o company_index.json`

## Part Two: Second Spider

In the testing phase when I was crawling the profiles of `1128` companies, I was getting 3 types of HTTP responses. 

- `HTTP 200` the ones with successful response with the desired company information. 
- `HTTP 503` which means the targeted server is unable to handle the request at that time. But it can be crawled after some time
- `HTTP 410` which means the page I am looking for is not available anymore.

So I designed the spider in such a way that it stores all the successful response data in a JSON file and keeps record of all the company pages that returns `HTTP 503` response in a file so that it can crawl the data next time. The spider keeps records of the `HTTP 410` response and blacklisted those urls into a separate file as well. In this way, the spider has to be run again and again until there is no more `HTTP 503` response url in the list. I got `1045` company profile and got `83` `HTTP 410` response out of `1128` company urls after running the spider ~4 times <br>

The second spider is this one `src/company_database/spiders/company_detail.py` It requires the `company_index.json` file which was produced by the first spider to get all the company urls. After each time the second spider is run, it overrides the `src/company_index.json` with the urls that return `HTTP 503` until the `src/company_index.json` file is empty which means it successfully crawled all of the available company pages(1045). And it also creates a file which holds the urls of unavailable company pages that returns `HTTP 410` response. <br>

The command to run this spider `scrapy crawl company_detail -o company_profiles.json`

## Part Three: Load the data into a database

After successfully getting the `src/company_profiles.json` file produced by the second spider its time to load the data into the database. I pick MongoDB as my database choice for this application. I wrote a python script in a Jupyter Notebook which located in `collected_data/company_data_analysis.ipynb`<br>

I used `pymongo` library to create the library and the details code is documented in the notebook

# Why I Chose MongoDB

Actually there are 2 reasons to choose MongoDB. First one is, before this project I had no hands-on experience with MongoDB or any type of noSQL database system. In the technical interview I was asked If am willing to learn MongoDB in the future if I was chosen for the job. So I decided to learn MongoDB to use it in this very project. <br>

Second reason is, MongoDB is more suitable for this kind of data. The company information I collected in this project doesn't require any complex relational model. It is more simple and easy to design the database in a documented way that noSQL database system does. For example, the way I stored the data in database like this one,

```
{
    "_id" : "A+ Conferencing",
    "company_location" : "Houston, Texas",
    "company_website" : "http://www.aplusconferencing.com",
    "company_webdomain" : "aplusconferencing.com",
    "company_industry" : "Telecommunications",
    "company_employee_size" : "25 - 100",
    "company_revenue" : "$100 - 250M",
    "contact_details" : [ 
        {
            "contact_name" : "Mike Burns",
            "contact_jobtitle" : "Owner",
            "contact_email_domain" : "aplusconferencing.com",
            "contact_profile_link" : "https://www.adapt.io/contact/mike-burns/71611468"
        }
    ]
}
```

Where I was able to keep the `contact_details` as a list which was never be possible in a Relational Database Management System. I had to create another table for contact details then connect it with a foreign key to the company profile table and so on. But in MongoDB it is like storing data as a JSON file which is more flexible, easy to work with, much faster and scalable. So, not that I learned MongoDB to use it as the database for this project, I would always choose mongodb for this project if I did have working experience with MongoDB at the first place.