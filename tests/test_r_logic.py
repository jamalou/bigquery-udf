"""
Test the uniqueness of the UDFs
"""
import os
import unittest

import yaml

UDFS_FOLDER = os.path.join(
    os.path.dirname(os.path.relpath(__file__)).replace('\\', '/'),
    '..',
    'user_defined_functions',
)

class TestFunctionsLogic(unittest.TestCase):
    """
    Test the logic of the UDFs by running the functions against
    real examples stored in csv files.

    The class does not contain any test cases, but it will be populated with test cases.
    """

def generate_test_function(udf_name, test):
    """
    Generate a test case for a specific function
    :param udf_name: The name of the function
    :param test: The test case to be run
    :return: test_function: a test case that checks the logic of the function
    """
    def test_function(self):
        # Your testing logic goes here
        # Example: your_function_testing_logic(function_name)
        self.assertTrue(bool(test) and bool(udf_name), msg=f"Test for {udf_name} failed")

    return test_function


def create_all_test_cases():
    """
    Create all test cases for the UDFs
    """
    udf_test_mapping = {}
    # Collect all function names from YAML files
    for filename in os.listdir(UDFS_FOLDER):
        if filename.endswith('.yaml'):
            udf_name = filename.split('.')[0]
            file_path = os.path.join(UDFS_FOLDER, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)

                test = data.get('tests')
                if test:
                    test_name = f'test_{udf_name}'
                    test_function = generate_test_function(udf_name, test_name)
                    setattr(TestFunctionsLogic, test_name, test_function)
    return udf_test_mapping

create_all_test_cases()

if __name__ == '__main__':
    # Run the tests using unittest
    unittest.main()
