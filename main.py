"""
Pipeline for fetching open access data from pubmed  and PMC
"""

import os
from dotenv import load_dotenv
from pubmed_util import get_pubmed_query, get_pubmed_ids, get_web_env_for_pubmed_ids, get_pmc_response, get_pmc_id, \
    get_pmc_tar_link, download_tar_files, get_tar_filename

from pmc_util import pmc_query_result, get_pmc_ids, pmc_tar_link, get_pmc_tar_filename, download_pmc_tar_files, \
    pmc_pdf_link

#  load the env data
load_dotenv()

QUERY = 'multiple myeloma'

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
            download_pmc_tar_files(file)


# This function will fetch data from PMC
def fetch_pmc_data():
    print('data fetching from pmc started......')

    result = pmc_query_result(QUERY)
    ids = get_pmc_ids(result)

    tar_links = pmc_pdf_link(ids)

    for link in tar_links:
        if link != 'None':
            download_pmc_tar_files(link)


# Main function
if __name__ == '__main__':
    fetch_pubmed_data()
    fetch_pmc_data()
