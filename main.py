import requests
from dotenv import load_dotenv
import os
import random


def check_error(response, method):
    if 'error' in response:
        raise requests.HTTPError(f'{response["error"]["error_msg"]} in method {method}')


def check_is_empty(response, funk):
    if response['photo'] == '[]':
        raise requests.HTTPError(f'Parameter "photo" is empty in function {funk}')


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
    response = response.json()
    download_photo(response['img'], filename)
    caption = response['alt']
    return caption


def get_address(payload, api_url):
    method = 'photos.getWallUploadServer'
    response = requests.get(f'{api_url}{method}', params=payload)
    response.raise_for_status()
    response = response.json()
    check_error(response, method)
    upload_url = response['response']['upload_url']
    return upload_url


def upload_to_server(upload_url, filename):
    with open(filename, 'rb') as photo:
        file = {
            'photo': photo
        }
        response = requests.post(upload_url, files=file)
    response.raise_for_status()
    response = response.json()
    check_error(response, 'send_file')
    check_is_empty(response, 'send_file')
    photo_config = response['photo']
    server = response['server']
    hash_param = response['hash']
    return photo_config, server, hash_param


def save_the_result(api_url, payload):
    method = 'photos.saveWallPhoto'
    response = requests.post(f'{api_url}{method}', params=payload)
    response.raise_for_status()
    response = response.json()
    check_error(response, method)
    media_id = response['response'][0]['id']
    owner_id_attachments = response['response'][0]['owner_id']
    return media_id, owner_id_attachments


def post_comic(api_url, payload):
    method = 'wall.post'
    response = requests.post(f'{api_url}{method}', params=payload)
    response.raise_for_status()
    response = response.json()
    check_error(response, method)
    return response['response']['post_id']


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
        photo_config, server, hash_param = upload_to_server(upload_url, filename)
        saving_result_payload = {
            'group_id': group_id,
            'photo': photo_config,
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
