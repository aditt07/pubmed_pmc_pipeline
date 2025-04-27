"""
Pipeline for fetching open access data from pubmed  and PMC
"""

import os
import pprint

from dotenv import load_dotenv
from pubmed_util import get_pubmed_query, get_pubmed_ids, get_web_env_for_pubmed_ids, get_pmc_response, get_pmc_id, \
    get_pmc_tar_link, download_tar_files

from pmc_util import pmc_query_result, get_pmc_ids, write_metadata_to_excel, \
    pmc_pdf_link, get_pmc_webenv, pmc_efetch_response, fetch_meta_data_from_pmc_response, download_pmc_pdf_files, \
    create_query_dir

#  load the env data
load_dotenv()

QUERY = 'breast cancer'


# This test function will fetch records from pubmed
def fetch_pubmed_data():
    print('data fetching from pubmed started.....')

    data = get_pubmed_query(QUERY)  # xml is converted to Dict    API-1
    pubmed_ids = get_pubmed_ids(data)  # This will return pubmed Ids from Dict   API-2

    print(f'DEBUG: printing pubmed IDS for {len(pubmed_ids)}')
    print(pubmed_ids)

    web_envs = get_web_env_for_pubmed_ids(pubmed_ids)  # API-3
    print(f'DEBUG: printing web envs for {len(web_envs)}')
    print(web_envs)

    article_list = []
    for env in web_envs:
        data = get_pmc_response(env)
        data = data['PubmedArticleSet']['PubmedArticle']['PubmedData']['ArticleIdList']
        article_list.append(data['ArticleId'])

    print('DEBUG: printing PMC IDS')
    pmc_ids = get_pmc_id(article_list)

    print(f'DEBUG: Total PMC IDs fetched from the given pubmedId: {len(pmc_ids)}')
    print(pmc_ids)

    tar_files = get_pmc_tar_link(pmc_ids)
    print('DEBUG: Tar files link which is non-commercial.....')
    print(tar_files)

    for file in tar_files:
        if file != 'None':
            download_tar_files(file)


# This function will fetch data from PMC
def fetch_pmc_data(query: str):
    print('data fetching from pmc started......')

    create_query_dir(query)

    result = pmc_query_result(query)
    ids = get_pmc_ids(result)
    print("ids:", ids)
    pdf_links, oa_pmc = pmc_pdf_link(ids)
    pdf_links = [l for l in pdf_links if l != 'None']

    print('pdf_links:', pdf_links)
    print('oa pmc ids:', oa_pmc)

    print('length of open access pdf links: ',len(pdf_links))
    print('length of open access pmc IDS: ', len(oa_pmc))

    print('Downloading PDF files.....')
    for link, pmc in zip(pdf_links, oa_pmc):
        download_pmc_pdf_files(link, pmc, query)

    print('Metadata extraction started.........')
    for pmc in oa_pmc:
        print('fetching PMC metadata response for: ', pmc)
        envkey = get_pmc_webenv(pmc)
        res = pmc_efetch_response(envkey)
        data = fetch_meta_data_from_pmc_response(res)
        write_metadata_to_excel(data, query)


# Main function
if __name__ == '__main__':
    #fetch_pubmed_data()
    '''
        TODO:  query is hardcoded. Query has to come from the DB. and this 
        function has to be iterated
    '''
    fetch_pmc_data(QUERY)
