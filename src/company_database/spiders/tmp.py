import json
from os import path

BASE_DIR = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
company_data_path = path.join(BASE_DIR, 'company_index.json')
error_company_urls = path.join(BASE_DIR, 'error_company_index.json')

print(path.exists(error_company_urls))
