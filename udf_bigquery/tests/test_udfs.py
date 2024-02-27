"""
This module contains the test cases for the UDFs.
Tests are generated dynamically based on the `json` test files
found in the "user_defined_functions" folder.
"""
import os
import unittest
from google.cloud import bigquery

from udf_bigquery.src.udf_utils import get_all_udf_names
from udf_bigquery.src.UDF import UserDefinedFunction

class TestUDFConfig(unittest.TestCase):
    """
    Test the UDF against the test cases
    the class does not contain any test cases, but it will be populated with test cases
    depending on the UDFs YAML files that are found in the "user_defined_functions" folder.
    """

def create_all_test_cases():
    """
    Generate test cases for all UDFs
    """
    bq_client = bigquery.Client()
    env = os.environ.get('_ENV', 'dev')
    for udf_name in get_all_udf_names():

        udf = UserDefinedFunction(udf_name, env=env)

        for test in udf.tests:
            test_name = f"test_{test['path'].stem}"
            test_case = udf.generate_test_case(test, bq_client)
            setattr(TestUDFConfig, test_name, test_case)

# Create the test cases for all UDFs in the TestUDFConfig class
create_all_test_cases()

if __name__ == '__main__':
    unittest.main()
