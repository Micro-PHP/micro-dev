#!/usr/bin/env python3

import requests

def get_repository_link(package):
    response = requests.get(f'https://repo.packagist.org/p2/{package}.json')
    return response.json()['packages'][package][0]['source']['url']

