import os
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination_name, chunk_size=32768):
    with open(destination_name, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)

def download_file(url, destination_name):

    session = requests.Session()
    response = session.get(url, stream=True)
    token = get_confirm_token(response)

    if token:
        parsed = urlunparse(url)
        query = parse_qs(parsed.query)
        query['confirm'] = token
        new_query = urlencode({k: v[0] if isinstance(v, list) else v for k, v in query.items()})
        url = urlunparse(parsed._replace(query=new_query))
        response = session.get(url, stream=True)

    save_response_content(response, os.path.join(os.path.dirname(__file__), destination_name))
    
