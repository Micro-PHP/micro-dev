#!/usr/bin/env python3

import requests

def to_ssh(func):
    def wrapper(package, *args, **kwargs):
        url = func(package, *args, **kwargs)
        if url.startswith('https://github.com/'):
            url = url.replace('https://github.com/', 'git@github.com:')
            if url.endswith('.git'):
                return url
            else:
                return url + '.git'
        return url
    return wrapper

@to_ssh
def get_repository_link(package):
    response = requests.get(f'https://repo.packagist.org/p2/{package}.json')
    return response.json()['packages'][package][0]['source']['url']

