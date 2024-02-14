import argparse
import logging
import os

import yaml
import jinja2

from google.cloud import bigquery

TEMPLATE_FOLDER = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/') + '/templates'


def deploy_udf(udf_name, project, dataset_name, bigquery_client):
    """
    Deploy a user defined function to a dataset.
    The information of the function is stored in a yaml file in the "user_defined_functions" folder.

    :param udf_name: The name of the user defined function
    :param project: The name of the project
    :param dataset_name: The name of the dataset
    :param bigquery_client: The bigquery client object
    """
    
    filename = f'user_defined_functions/{udf_name}.yaml'

    fully_qualified_udf = f'`{project}`.`{dataset_name}`.{udf_name}'
    fully_qualified_dataset = f'`{project}`.`{dataset_name}`'
    
    # load the configuration of the udf from the yaml file
    with open(filename, 'r', encoding='utf-8') as file:
        conf = yaml.safe_load(file)

    conf['name'] = udf_name
    conf['dataset'] = fully_qualified_dataset

    template_file = os.path.join(TEMPLATE_FOLDER, f'{conf["type"]}.sql')
    
    with open(template_file, 'r', encoding='utf-8') as file:
        template = jinja2.Template(file.read())

    query = template.render(**conf)
    return query
    # execute the query to create the udf
    logging.info(f'Creating function {udf_name} in dataset {fully_qualified_dataset}')
    bigquery_client.query(query).result()
    logging.info(f'successfully created {fully_qualified_udf}')


def deploy_all_udfs(project, dataset_name):
    """
    Deploy all user defined functions in the "user_defined_functions" folder to a dataset.

    :param project: The name of the project
    :param dataset_name: The name of the dataset
    """
    bigquery_client = bigquery.Client(project)

    for filename in os.listdir('user_defined_functions'):
        if filename.endswith('.yaml'):
            udf_name = filename.replace('.yaml', '')
            print(deploy_udf(udf_name, project, dataset_name, bigquery_client))


def main():
    """
    Deploy all user defined functions in the "user_defined_functions" folder to a dataset.
    """
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Deploy user defined functions to a dataset')
    parser.add_argument('project', help='The name of the project')
    parser.add_argument('dataset_name', help='The name of the dataset where the functions will be deployed')

    args = parser.parse_args()

    deploy_all_udfs(args.project, args.dataset_name)


if __name__ == '__main__':
    main()
