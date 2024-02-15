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
REQUIRED_CONFIG_KEYS = ["type", "description", "code", "tests"]
VALID_TYPES = ["function_sql", "function_js", "procedure"]


class TestUDFConfig(unittest.TestCase):
    """
    test the completeness the UDFs configuration.
    test the validity of the UDFs configuration.
    the class does not contain any test cases, but it will be populated with test cases
    depending on the UDFs YAML files that are found in the "user_defined_functions" folder.
    """


def generate_config_completeness_test(udf_name, udf_file_path, required_config_keys):
    """
    Generate config completeness test case for a specific function
    :param udf_name: The name of the function
    :param udf_file_path: The path to the function's YAML file
    :param required_config_keys: A list of required keys in the function's YAML file
    :return: test_config_completeness: a test case that checks if the function's YAML file
    contains all the required keys
    """
    def test_config_completeness(self):
        missing_keys = []
        with open(udf_file_path, "r", encoding='utf-8') as file:
            udf_conf = yaml.safe_load(file)
            for key in required_config_keys:
                if key not in udf_conf:
                    missing_keys.append(key)

        self.assertFalse(
            missing_keys,
            msg=f"UDF `{udf_name}` config is uncomplete, missing keys: {', '.join(missing_keys)}",
        )

    return test_config_completeness


def generate_type_validity_test(udf_name, udf_file_path, valid_types):
    """
    Generate a test case for a specific function
    :param udf_name: The name of the function
    :param udf_file_path: The path to the function's YAML file
    :param valid_types: A list of valid types
    :return: test_type_validity: a test case that checks if the function's type
    is in the list of valid types
    """
    def test_type_validity(self):
        with open(udf_file_path, "r", encoding='utf-8') as file:
            udf_conf = yaml.safe_load(file)
            self.assertIn(
                udf_conf.get("type"),
                valid_types,
                msg=(
                    f"UDF `{udf_name}` type is invalid."
                    f"Valid types are: {', '.join(valid_types)} but provided type: ",
                    f"{udf_conf.get('type') if udf_conf.get('type') else 'No type was provided'}"
                ),
            )
    return test_type_validity


def create_all_test_cases():
    """
    Generate test cases for all UDFs
    """
    for filename in os.listdir(UDFS_FOLDER):
        if filename.endswith('.yaml'):
            udf_name = filename.split('.')[0]
            udf_file_path = os.path.join(UDFS_FOLDER, filename)

            # Add a test case for the validity of the UDF's type
            validity_test_name = f'test_{udf_name}_type_validity'
            test_type_validity = generate_type_validity_test(
                udf_name,
                udf_file_path,
                VALID_TYPES
            )
            setattr(TestUDFConfig, validity_test_name, test_type_validity)

            # Add a test case for the completeness of the UDF's configuration
            completeness_test_name = f'test_{udf_name}_completeness'
            test_completeness = generate_config_completeness_test(
                udf_name,
                udf_file_path,
                REQUIRED_CONFIG_KEYS
            )
            setattr(TestUDFConfig, completeness_test_name, test_completeness)

# Create the test cases for all UDFs in the TestUDFConfig class
create_all_test_cases()

if __name__ == '__main__':
    unittest.main()
