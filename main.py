import requests
from dotenv import load_dotenv
import os
import random


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
    download_photo(response.json()['img'], filename)
    caption = response.json()['alt']
    return caption


def get_address(payload, api_url):
    method = 'photos.getWallUploadServer'
    response = requests.get(api_url + method, params=payload)
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']
    return upload_url


def file_transfer(upload_url, filename):
    with open(filename, 'rb') as photo:
        file = {
            'photo': photo
        }
        response = requests.post(upload_url, files=file)
        response.raise_for_status()
        photo_json = response.json()['photo']
        server = response.json()['server']
        hash = response.json()['hash']
    return photo_json, server, hash


def save_the_result(api_url, payload):
    method = 'photos.saveWallPhoto'
    response = requests.post(api_url + method, params=payload)
    response.raise_for_status()
    media_id = response.json()['response'][0]['id']
    owner_id_attachments = response.json()['response'][0]['owner_id']
    return media_id, owner_id_attachments


def post_comic(api_url, payload):
    method = 'wall.post'
    response = requests.post(api_url + method, params=payload)
    response.raise_for_status()
    return response.json()['response']['post_id']


if __name__ == '__main__':
    load_dotenv()
    filename = 'comic.jpg'
    comic_number = find_random_comic()
    caption = download_comic(filename, comic_number)
    api_url = 'https://api.vk.com/method/'
    vk_token = os.getenv("ACCESS_TOKEN_VK")
    group_id = os.getenv('GROUP_ID')
    api_version = '5.130'
    getting_address_payload = {
        'access_token': vk_token,
        'v': api_version,
        'group_id': group_id
    }
    upload_url = get_address(getting_address_payload, api_url)
    photo_json, server, hash = file_transfer(upload_url, filename)
    saving_result_payload = {
        'group_id': group_id,
        'photo': photo_json,
        'server': server,
        'hash': hash,
        'access_token': vk_token,
        'v': api_version
    }
    media_id, owner_id_attachments = save_the_result(api_url, saving_result_payload)
    owner_id = '-'+group_id
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
    print(f'Post number {post_id} published')
    os.remove(filename)
