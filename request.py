import os
import requests
from dotenv import load_dotenv


def request(auth_token, api_url, params, path):
    """Make a request and return the response as a JSON"""

    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }

    response = requests.get(f"{api_url}/{path}", headers=headers, params=params)
    return response.json()


def get_festivals(api_url, auth_token):
    """Get the list of festivals"""

    params = {
        'sort': 'name:asc',
        'pagination[withCount]': 'false',
        'pagination[page]': '0',
        'pagination[pageSize]': '25',
        'locale': 'ES'
    }
    
    return request(auth_token, api_url, params, 'festivals')


def main():
    load_dotenv()

    API_URL = os.getenv("API_URL")
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")

    result = get_festivals(API_URL, AUTH_TOKEN)
    print(result)


if __name__ == "__main__":
    main()