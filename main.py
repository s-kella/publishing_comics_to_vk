import requests
from dotenv import load_dotenv
import os
import random


def check_error(response):
    if 'error' in response:
        return response['error']['error_msg']


def download_photo(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)


def find_random_comic():
    last_comic_url = 'http://xkcd.com/info.0.json'
    response = requests.get(last_comic_url)
    response.raise_for_status()
    last_comic_num = response.json()['num']
    comic_number = random.randint(1, last_comic_num)
    return comic_number


def download_comic(filename, comic_number):
    comic_url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(comic_url)
    response.raise_for_status()
    response_data = response.json()
    download_photo(response_data['img'], filename)
    caption = response_data['alt']
    return caption


def get_address(payload, api_url):
    method = 'photos.getWallUploadServer'
    response = requests.get(f'{api_url}{method}', params=payload)
    response.raise_for_status()
    response_data = response.json()
    error = check_error(response_data)
    if error is not None:
        raise requests.HTTPError(f'{error} in method {method}')
    upload_url = response_data['response']['upload_url']
    return upload_url


def send_file(upload_url, filename):
    with open(filename, 'rb') as photo:
        file = {
            'photo': photo
        }
        response = requests.post(upload_url, files=file)
    response.raise_for_status()
    response_data = response.json()
    photo_json = response_data['photo']
    server = response_data['server']
    hash_param = response_data['hash']
    return photo_json, server, hash_param


def save_the_result(api_url, payload):
    method = 'photos.saveWallPhoto'
    response = requests.post(f'{api_url}{method}', params=payload)
    response.raise_for_status()
    response_data = response.json()
    error = check_error(response_data)
    if error is not None:
        raise requests.HTTPError(f'{error} in method {method}')
    media_id = response_data['response'][0]['id']
    owner_id_attachments = response_data['response'][0]['owner_id']
    return media_id, owner_id_attachments


def post_comic(api_url, payload):
    method = 'wall.post'
    response = requests.post(f'{api_url}{method}', params=payload)
    response.raise_for_status()
    response_data = response.json()
    error = check_error(response_data)
    if error is not None:
        raise requests.HTTPError(f'{error} in method {method}')
    return response_data['response']['post_id']


if __name__ == '__main__':
    load_dotenv()
    filename = 'comic.jpg'
    comic_number = find_random_comic()
    caption = download_comic(filename, comic_number)
    try:
        api_url = 'https://api.vk.com/method/'
        vk_token = os.getenv('ACCESS_TOKEN_VK')
        group_id = os.getenv('GROUP_ID')
        api_version = '5.130'
        getting_address_payload = {
            'access_token': vk_token,
            'v': api_version,
            'group_id': group_id
        }
        upload_url = get_address(getting_address_payload, api_url)
        photo_json, server, hash_param = send_file(upload_url, filename)
        saving_result_payload = {
            'group_id': group_id,
            'photo': photo_json,
            'server': server,
            'hash': hash_param,
            'access_token': vk_token,
            'v': api_version
        }
        media_id, owner_id_attachments = save_the_result(api_url, saving_result_payload)
        owner_id = f'-{group_id}'
        attachments = f'photo{owner_id_attachments}_{media_id}'
        posting_payload = {
            'from_group': True,
            'attachments': attachments,
            'owner_id': owner_id,
            'access_token': vk_token,
            'v': api_version,
            'message': caption
        }
        post_id = post_comic(api_url, posting_payload)
    finally:
        os.remove(filename)
