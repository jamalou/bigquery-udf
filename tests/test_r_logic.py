"""
Test the uniqueness of the UDFs
"""
from collections import defaultdict
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
    """
    pass

def generate_test_function(udf_name, test):
    # Generate a test case for each function
    def test_function(self):
        # Your testing logic goes here
        # Example: your_function_testing_logic(function_name)
        self.assertTrue(1)

    return test_function


def create_all_test_cases():
    udf_test_mapping = dict()
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