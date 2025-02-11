import os
import requests
from dotenv import load_dotenv


def get_festivals(api_url, auth_token):
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {auth_token}'
    }
    
    params = {
        'sort': 'name:asc',
        'pagination[withCount]': 'false',
        'pagination[page]': '0',
        'pagination[pageSize]': '25',
        'locale': 'ES'
    }
    
    response = requests.get(f"{api_url}/festivals", headers=headers, params=params)
    return response.text


def main():
    load_dotenv()

    API_URL = os.getenv("API_URL")
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")

    result = get_festivals(API_URL, AUTH_TOKEN)
    print(result)


if __name__ == "__main__":
    main()