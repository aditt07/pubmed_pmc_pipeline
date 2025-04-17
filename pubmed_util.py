"""
pubmed related utils are available here
"""

import os
import requests
import xmltodict
from typing import List, Dict
from dotenv import load_dotenv

import pprint

"""
todos:
1. Get the query from the user with API and utilise e_query_url and get the pubmed ids  - DONE
2. Get the webEnv key for the pubmed ID and use e_post_url - DONE
3. Check if PMCID is present in the response once you use e_fetch_url. if not ignore that pubmed ID - DONE
4. Get the tar.gz link from the response of pmc_url by passing the pmcid as query parameter - TODO
"""

load_dotenv()

COMMERCIAL_USE = ['CC0', 'CC BY', 'CC BY-SA', 'CC BY-ND']
NON_COMMERCIAL_USE = ['CC BY-NC', 'CC BY-NC-SA', 'CC BY-NC-ND']


def get_pubmed_query(query: str) -> Dict:
    query_url = os.getenv('E_SEARCH_URL')
    query = formatted_query(query)
    query_url = f'{query_url}{query}&usehistroy=y'
    res = requests.get(query_url)
    data = convert_xml_to_json(res.text)
    return data


def get_pubmed_ids(data: Dict) -> List[str]:
    result_count = os.getenv('RESULT_COUNT')
    return data['eSearchResult']['IdList']['Id'][0:int(result_count)]


def get_web_env_for_pubmed_ids(pubmed_ids: List[str]) -> List[str]:
    web_envs = []
    key_url = os.getenv('E_POST_URL')
    for p_id in pubmed_ids:
        endpoint = f'{key_url}{p_id}'
        res = requests.get(endpoint)
        data = convert_xml_to_json(res.text)
        web_envs.append(data['ePostResult']['WebEnv'])

    return web_envs


# Warning: Consider BigO performance (multiple for loops)
def get_pmc_id(data: List) -> List[str]:
    pmc_ids = []
    for l1 in data:
        for l2 in l1:
            if l2['@IdType'] == 'pmc':
                pmc_ids.append(l2['#text'])
    return pmc_ids


def get_pmc_response(webenv: str) -> List:
    fetch_url = os.getenv('E_FETCH_URL')
    endpoint = f'{fetch_url}{webenv}'
    res = requests.get(endpoint)
    data = convert_xml_to_json(res.text)
    return data


def is_licensed(lcs: str) -> bool:
    """
        returns false if it is not licensed
    """
    return lcs in COMMERCIAL_USE


def get_pmc_tar_link(pmc_ids: List[str]) -> List[str]:
    tar_links = []
    # TODO: Need to fetch the tar link if the license is allowed.   verify that in the existing codebase
    for pmc in pmc_ids:
        pmc_url = os.getenv('PMC_URL')
        endpoint = f'{pmc_url}{pmc}'

        res = requests.get(endpoint)
        data = convert_xml_to_json(res.text)
        #pprint.pprint(data)
        if not is_licensed(data['OA']['records']['record']['@license']):
            tar_link = data['OA']['records']['record']['link'][0]['@href']
            tar_links.append(tar_link)

    return tar_links


def download_tar_files(file_link: str):
    file_link = file_link.replace('ftp:', 'https:')
    res = requests.get(file_link)
    filename = get_tar_filename(file_link)

    with open('tar_files/' + filename, 'wb') as fobj:
        fobj.write(res.content)
        fobj.close()

    print(f'{filename} - file downloaded successful')


# Helper functions
def formatted_query(query: str) -> str:
    query_list = query.split(' ')

    if len(query_list) > 1:
        return query.replace(' ', '+')

    return query


def convert_xml_to_json(xml: str) -> str:
    return xmltodict.parse(xml)


def get_tar_filename(link: str) -> str:
    chunks = link.split('/')
    return chunks[-1]

