import re

import markdown
import msal
import requests
from quarter_lib.akeyless import get_secrets
from quarter_lib.logging import setup_logging

logger = setup_logging(__file__)

AUTHORITY_URL = "https://login.microsoftonline.com/consumers/"

SCOPES = ["Files.ReadWrite.All", "Files.Read.All", "Notes.ReadWrite", "Notes.ReadWrite.All", "Notes.Read.All",
          "User.Read"]

CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, TENANT_ID = get_secrets(
    ["microsoft/client_id", "microsoft/client_secret", "microsoft/refresh_token", "microsoft/tenant_id"])

client_instance = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY_URL
)

global ACCESS_TOKEN


def get_access_token():
    token = client_instance.acquire_token_by_refresh_token(
        refresh_token=REFRESH_TOKEN,
        scopes=SCOPES)

    return token['access_token']


def get_notebooks(access_token):
    url = 'https://graph.microsoft.com/v1.0/me/onenote/notebooks'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        logger.info(f'Error getting notebooks: {response.status_code} {response.text}')
        return []


def get_sections(notebook_id, access_token):
    url = f'https://graph.microsoft.com/v1.0/me/onenote/notebooks/{notebook_id}/sections'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        logger.info(f'Error getting sections: {response.status_code} {response.text}')
        return []


def get_pages(section_id, access_token):
    url = f'https://graph.microsoft.com/v1.0/me/onenote/sections/{section_id}/pages?$select=title,contentUrl,id'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        logger.info(f'Error getting pages: {response.status_code} {response.text}')
        return []


def duplicate_page(page_id, section_id, access_token):
    url = f'https://graph.microsoft.com/beta/me/onenote/pages/{page_id}/copyToSection'
    body = {
        'id': section_id,
    }
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=body)
    logger.info(response)
    if response.status_code == 202:
        logger.info('Page duplicated successfully.')
        return response.json()
    else:
        logger.info(f'Error getting page content: {response.status_code} {response.text}')


def get_new_page_id(duplicate_response, access_token):
    url = f"https://graph.microsoft.com/v1.0/me/onenote/operations/{duplicate_response['id']}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response_json = response.json()
    logger.info(response_json)
    if response_json['status'] != 'Completed':
        logger.info('Operation not completed.')
        return None
    return response.json()['resourceLocation'].split('/')[-1]


def add_formatted_text_to_page(page_id, text, title, access_token):
    url = f'https://graph.microsoft.com/v1.0/me/onenote/pages/{page_id}/content'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL).strip()
    text = markdown.markdown(text)  # Uncomment this line if text uses Markdown formatting
    formatted_text = text.replace('\n', '<br>')

    content = f'''
    <div>
        <p style="font-size:72px;color:black;">{formatted_text}</p>
    </div>
    '''

    payload = {
        'target': 'body',
        'action': 'append',
        'position': 'before',
        'content': content
    }

    another_payload = {
        'target': 'title',
        'action': 'replace',
        'content': title
    }
    
    response = requests.patch(url, headers=headers, json=[payload, another_payload])
    logger.info(response.text)
    if response.status_code == 204:
        logger.info('Formatted text added successfully.')
        return response
    else:
        logger.info(f'Error adding formatted text: {response.status_code} {response.text}')
        return None
