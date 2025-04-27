"""
PMC related utility functions are available here
"""

from typing import Dict, List,  Tuple
from dotenv import load_dotenv
from pubmed_util import convert_xml_to_json
import pandas as pd
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


def pmc_pdf_link(pmc_ids: List[str]) -> Tuple:
    tar_links = []
    oa_pmcs = []
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
            mod_pmc = pmc.replace('PMC', '')
            oa_pmcs.append(mod_pmc)
        except KeyError as e:
            tar_links.append('None')

        #tar_links.append(tar_link)
        #pprint.pprint(data)

    return tar_links, oa_pmcs


def download_pmc_pdf_files(file_link: str, pmcid: str, query: str):
    file_link = file_link.replace('ftp:', 'https:')
    res = requests.get(file_link)
    filename = get_pmc_tar_filename(file_link)

    with open(f'pdf_files/{query}/' + 'PMC' + pmcid + '.pdf', 'wb') as fobj:
        fobj.write(res.content)
        fobj.close()

    print(f'{filename} - file downloaded successful')


def get_pmc_tar_filename(link: str) -> str:
    chunks = link.split('/')
    return chunks[-1]


def get_pmc_webenv(pmcid: str) -> str:
    url = os.getenv('PMC_E_POST_URL')
    pmcid = pmcid.replace('PMC', '')
    res = requests.get(url + pmcid)
    res_json = convert_xml_to_json(res.text)
    web_env = res_json['ePostResult']['WebEnv']
    return web_env


def pmc_efetch_response(webenv: str) -> str:
    url = os.getenv('PMC_E_FETCH_URL')
    url = url + webenv

    res = requests.get(url)
    res_json = convert_xml_to_json(res.text)

    return res_json


def fetch_meta_data_from_pmc_response(res: Dict) -> Dict:
    metadata = {}

    metadata[('PmcId')] = res['pmc-articleset']['article']['front']['article-meta']['article-id'][0]['#text']
    #print(f'fetching metadata for: {metadata['PmcId']}')

    metadata['Doi'] = res['pmc-articleset']['article']['front']['article-meta']['article-id'][2]['#text']
    metadata['Title'] = res['pmc-articleset']['article']['front']['article-meta']['title-group']['article-title']
    metadata['Authors'] = []
    author_list = list(res['pmc-articleset']['article']['front']['article-meta']['contrib-group']['contrib'])

    if len(author_list) > 0:
        for info in author_list:
            author = {}
            author['Surname'] = info['name']['surname']
            author['GivenNames'] = info['name']['given-names']
            metadata['Authors'].append(author)
    else:
        author = {}
        author['Surname'] = author_list['name']['surname']
        author['GivenNames'] = author_list['name']['given-names']
        metadata['Authors'] = author

    metadata['Journal'] = res['pmc-articleset']['article']['front']['journal-meta']['journal-title-group']['journal-title']
    pub_info = res['pmc-articleset']['article']['front']['article-meta']['pub-date']

    for i in pub_info:
        if i['@pub-type'] == 'epub':
            info = {}
            info['day'] = i['day']
            info['month'] = i['month']
            info['year'] = i['year']
            metadata['PublishDate'] = [info]

    return metadata


def write_metadata_to_excel(data: Dict, query: str):
    pmcid = data['PmcId']
    print(f'writing metadata for: {pmcid}')
    filename = 'PMC' + pmcid + '_meta_data.xlsx'
    df = pd.DataFrame.from_dict(data, orient='index')
    df.to_excel('extracted_metadata/' + query + '/' + filename)
    print(f'metadata has written successfully for the id {pmcid}')


def create_query_dir(query: str):
    if not os.path.exists('extracted_metadata/' + query):
        os.makedirs('extracted_metadata/' + query)

    if not os.path.exists('pdf_files/' + query):
        os.makedirs('pdf_files/' + query)