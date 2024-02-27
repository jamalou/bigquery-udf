"""
This script deploys all user defined functions in the
`user_defined_functions` folder to a dataset specified by the user.
How to use:
    python deploy.py --env <env> (--dry_run if you want to print the UDFs instead of deploying them)
    where:
        - project: The name of the project
        - dataset_name: The name of the dataset where the functions will be deployed
"""

import argparse
import logging

from google.cloud import bigquery

from udf_bigquery.src.UDF import UserDefinedFunction
from udf_bigquery.src.udf_utils import get_all_udf_names

def deploy_all_udfs(dry_run=False, **additional_params):
    """
    Deploy all user defined functions in the "user_defined_functions" folder to a dataset.

    :param dry_run: If True, the function will not be deployed, it will only be printed
    :param additional_params: Additional parameters to pass to the UserDefinedFunction class
    """
    bigquery_client = bigquery.Client() if not dry_run else None
    for udf_name in get_all_udf_names():
        udf = UserDefinedFunction(udf_name, **additional_params)
        udf.deploy_to_bq(bigquery_client, dry_run=dry_run)


def main():
    """
    Deploy all user defined functions in the "user_defined_functions" folder to a dataset.
    """
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Deploy user defined functions to a dataset')
    parser.add_argument(
        '--env',
        required=True,
        help='The name of the project',
    )
    parser.add_argument(
        '--dry_run',
        action='store_true',
        help='If True, the function will not be deployed, it will only be printed',
    )
    
    args = parser.parse_args()

    deploy_all_udfs(dry_run=args.dry_run, env=args.env)


if __name__ == '__main__':
    main()
