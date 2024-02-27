"""
Helper functions to generate tests for UDF configurations
"""
import os
import json
import yaml

if os.path.dirname(os.path.relpath(__file__)) == "":
    TESTS_FOLDER = "."
else:
    TESTS_FOLDER = os.path.dirname(os.path.relpath(__file__))

with open(os.path.join(TESTS_FOLDER, "validity_map.json"), 'r', encoding='utf-8') as map_file:
    VALIDITY_MAP = json.load(map_file)

UDFS_FOLDER = os.path.join(
    TESTS_FOLDER,
    '..',
    'user_defined_functions',
)

def validate_config(conf, validity_map, parent_key=""):
    """
    Validate the configuration of a UDF
    :param conf: The configuration of the UDF
    :param validity_map: A map that contains the validity rules of the configuration
    :return: missing_keys: A list of missing keys in the configuration
    :return: invalid_types: A list of keys that have the wrong type in the configuration
    :return: invalid_values: A list of keys that have the wrong value in the configuration
    """
    missing_keys = []
    invalid_types = []
    invalid_values = []

    if validity_map["type"] == "str" and validity_map.get("valid_values"):
        if conf not in validity_map["valid_values"]:
            invalid_values.append(
                (f"{parent_key}", validity_map["valid_values"], conf)
            )

    if validity_map["type"] == "dict":
        # loop through the attributes
        for attr, attr_conf in validity_map["attributes"].items():
            # Check if the required keys are present
            if attr_conf["required"] is True and attr not in conf:
                missing_keys.append(f"{parent_key}.{attr}")
                continue
            # Check if the attribute has the right type
            if attr in conf and attr_conf["type"] != conf[attr].__class__.__name__:
                invalid_types.append(
                    (f"{parent_key}.{attr}", attr_conf["type"], conf[attr].__class__.__name__)
                )
            # recursively validate the attribute
            if attr in conf:
                att_missing_keys, att_invalid_types, att_invalid_values = validate_config(
                    conf[attr],
                    attr_conf,
                    f"{parent_key}.{attr}"
                )
                missing_keys.extend(att_missing_keys)
                invalid_types.extend(att_invalid_types)
                invalid_values.extend(att_invalid_values)

    elif validity_map["type"] == "list":
        for i, item in enumerate(conf):
            att_missing_keys, att_invalid_types, att_invalid_values = validate_config(
                item,
                validity_map["list_item"],
                f"{parent_key}[{i}]"
            )
            missing_keys.extend(att_missing_keys)
            invalid_types.extend(att_invalid_types)
            invalid_values.extend(att_invalid_values)

    return missing_keys, invalid_types, invalid_values


def formatter(udf_name, missing_keys, invalid_types, invalid_values):
    """
    Format the missing keys, invalid types and invalid values
    :param missing_keys: A list of missing keys
    :param invalid_types: A list of invalid types
    :param invalid_values: A list of invalid values
    :return: formatted_missing_keys: A formatted string of missing keys
    :return: formatted_invalid_types: A formatted string of invalid types
    :return: formatted_invalid_values: A formatted string of invalid values
    """
    formatted_missing_keys = (
        f"UDF `{udf_name}` config is uncomplete, missing keys:\n"
        "\n".join([f"* {key}" for key in missing_keys])
    )
    formatted_invalid_types = (
        f"UDF `{udf_name}` config has wrong types:\n"
        "\n".join([
            f"Invalid type: {key}, expected {expected_type}, but got {actual_type}" 
            for key, expected_type, actual_type in invalid_types
        ])
    )
    formatted_invalid_values = (
        f"UDF `{udf_name}` config has invalid values:\n"
        "\n".join([
            f"Invalid value: {key}, expected one of {valid_values}, but got {actual_value}"
            for key, valid_values, actual_value in invalid_values
        ])
    )

    return formatted_missing_keys, formatted_invalid_types, formatted_invalid_values


def generate_config_completeness_test(udf_name, udf_file_path, validity_map):
    """
    Generate a test case for the completeness of the UDF configuration.
    :param udf_name: The name of the UDF
    :param udf_file_path: The path to the UDF configuration file (yaml)
    :param validity_map: A map that contains the validity rules of the configuration
    :return: test_config_completeness: A test case for the completeness of the UDF configuration
    """
    def test_config_completeness(self):
        """
        Test the completeness of the UDF configuration (no missing keys).
        """
        with open(udf_file_path, "r", encoding='utf-8') as file:
            conf = yaml.safe_load(file)

        missing_keys, _, _ = validate_config(
            conf,
            validity_map
        )
        formatted_missing_keys, _, _ = formatter(udf_name, missing_keys, [], [])
        self.assertEqual(
            missing_keys,
            [],
            msg=formatted_missing_keys
        )
    return test_config_completeness


def generate_types_validity_test(udf_name, udf_file_path, validity_map):
    """
    Generate a test case for the validity of the UDF configuration types.
    :param udf_name: The name of the UDF
    :param udf_file_path: The path to the UDF configuration file (yaml)
    :param validity_map: A map that contains the validity rules of the configuration
    :return: test_types_validity: A test case for the validity of the UDF configuration types
    """
    def test_types_validity(self):
        """
        Test the validity of the UDF configuration.
        """
        with open(udf_file_path, "r", encoding='utf-8') as file:
            conf = yaml.safe_load(file)

        _, invalid_types, _ = validate_config(
            conf,
            validity_map
        )
        _, formatted_invalid_types, _ = formatter(udf_name, [], invalid_types, [])
        self.assertEqual(
            invalid_types,
            [],
            msg=formatted_invalid_types
        )
    return test_types_validity


def generate_test_values_validity(udf_name, udf_file_path, validity_map):
    """
    Generate a test case for the validity of the values in the UDF configuration.
    :param udf_name: The name of the UDF
    :param udf_file_path: The path to the UDF configuration file (yaml)
    :param validity_map: A map that contains the validity rules of the configuration
    :return: test_values_validity: A test case for the validity of the values in the configuration
    """
    def test_values_validity(self):
        """
        Test the validity of the values in the UDF configuration.
        """
        with open(udf_file_path, "r", encoding='utf-8') as file:
            conf = yaml.safe_load(file)

        _, _, invalid_values = validate_config(
            conf,
            validity_map
        )
        _, _, formatted_invalid_values = formatter(udf_name, [], [], invalid_values)
        self.assertEqual(
            invalid_values,
            [],
            msg=formatted_invalid_values
        )
    return test_values_validity
