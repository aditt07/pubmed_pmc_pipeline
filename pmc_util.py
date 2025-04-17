"""
PMC related utility functions are available here
"""

from typing import Dict, List
from dotenv import load_dotenv
from pubmed_util import convert_xml_to_json, get_pubmed_ids
import os
import requests

load_dotenv()


def pmc_query_result(query: str) -> Dict:
    query_url = os.getenv('PMC_QUERY_URL')
    query_url = f'{query_url}{query}&usehistory=y'
    res = requests.get(query_url)
    data = convert_xml_to_json(res.text)
    #print(data)
    return data


def pmc_response(pmc_id: str) -> List:
    fetch_url = os.getenv('PMC_DOWNLOAD_URL')
    endpoint = f'{fetch_url}{pmc_id}'
    res = requests.get(endpoint)
    data = convert_xml_to_json(res.text)
    return data


def get_pmc_ids(data: Dict) -> List[str]:
    result_count = os.getenv('RESULT_COUNT')
    return data['eSearchResult']['IdList']['Id'][0:int(result_count)]


def pmc_tar_link(pmc_ids: List[str]) -> List[str]:
    tar_links = []
    # TODO: Need to fetch the tar link if the license is allowed.   verify that in the existing codebase
    for pmc in pmc_ids:
        pmc_url = os.getenv('PMC_DOWNLOAD_URL')
        endpoint = f'{pmc_url}{pmc}'

        res = requests.get(endpoint)
        data = convert_xml_to_json(res.text)

        try:
            tar_link = data['OA']['records']['record']['link'][0]['@href']
            tar_link = tar_link.replace('ftp://', 'https://')
            tar_links.append(tar_link)
        except KeyError as e:
            tar_links.append('None')

        #tar_links.append(tar_link)
        #pprint.pprint(data)

    return tar_links


def pmc_pdf_link(pmc_ids: List[str]) -> List[str]:
    tar_links = []
    # TODO: Need to fetch the tar link if the license is allowed.   verify that in the existing codebase
    for pmc in pmc_ids:
        pmc_url = os.getenv('PMC_DOWNLOAD_URL')
        endpoint = f'{pmc_url}{pmc}'

        res = requests.get(endpoint)
        data = convert_xml_to_json(res.text)

        try:
            tar_link = data['OA']['records']['record']['link'][1]['@href']  # Index 0 -> tarfile, 1 -> PDF
            tar_link = tar_link.replace('ftp://', 'https://')
            tar_links.append(tar_link)
        except KeyError as e:
            tar_links.append('None')

        #tar_links.append(tar_link)
        #pprint.pprint(data)

    return tar_links


def download_pmc_pdf_files(file_link: str):
    file_link = file_link.replace('ftp:', 'https:')
    res = requests.get(file_link)
    filename = get_pmc_tar_filename(file_link)

    with open('pdf_files_from_pmc/' + filename, 'wb') as fobj:
        fobj.write(res.content)
        fobj.close()

    print(f'{filename} - file downloaded successful')


def get_pmc_tar_filename(link: str) -> str:
    chunks = link.split('/')
    return chunks[-1]

