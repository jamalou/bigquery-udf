"""
Test the validity of the UDFs configuration.
"""
import os
import unittest

from udf_bigquery.src.udf_utils import UDFS_FOLDER
from .config_validation_utils import (
    generate_config_completeness_test,
    generate_types_validity_test,
    generate_test_values_validity,
    VALIDITY_MAP,
)


class TestUDFConfig(unittest.TestCase):
    """
    test the completeness the UDFs configuration.
    test the validity of the UDFs configuration.
    the class does not contain any test cases, but it will be populated with test cases
    depending on the UDFs YAML files that are found in the "user_defined_functions" folder.
    """

def create_all_test_cases():
    """
    Generate test cases for all UDFs
    """
    for filename in os.listdir(UDFS_FOLDER):
        if not filename.endswith('.yaml'):
            continue

        udf_name = filename.split('.')[0]
        udf_file_path = os.path.join(UDFS_FOLDER, filename)

        # Add a test case for the completeness of the UDF's configuration
        completeness_test_name = f'test_{udf_name}_completeness'
        test_config_completeness = generate_config_completeness_test(
            udf_name,
            udf_file_path,
            VALIDITY_MAP
        )
        setattr(TestUDFConfig, completeness_test_name, test_config_completeness)

        # Add a test case for the validity of the UDF's configuration types
        validity_test_name = f'test_{udf_name}_validity'
        test_validity = generate_types_validity_test(
            udf_name,
            udf_file_path,
            VALIDITY_MAP
        )
        setattr(TestUDFConfig, validity_test_name, test_validity)

        # Add a test case for the validity of the values in the UDF's configuration
        values_validity_test_name = f'test_{udf_name}_values_validity'
        test_values_validity = generate_test_values_validity(
            udf_name,
            udf_file_path,
            VALIDITY_MAP
        )
        setattr(TestUDFConfig, values_validity_test_name, test_values_validity)

# # Create the test cases for all UDFs in the TestUDFConfig class
create_all_test_cases()

if __name__ == '__main__':
    unittest.main()
