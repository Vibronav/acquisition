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

def download_file(file_id, destination_name):

    url = "https://drive.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(url, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)
    
    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(url, params=params, stream=True)

    save_response_content(response, os.path.join(os.path.dirname(__file__), destination_name))
    
