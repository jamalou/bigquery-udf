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

class test_udfs_config(unittest.TestCase):
    """
    test the uniqueness of the UDFs and the completeness of their configuration
    """
    def test_uniqueness(self):
        """
        Test that the UDFs have unique names
        """
        names_count = defaultdict(int)
        names_files_mapping = defaultdict(list)
        duplicate_names = dict()
        for filename in os.listdir(UDFS_FOLDER):
            if filename.endswith(".yaml"):
                file_path = os.path.join(UDFS_FOLDER, filename)

                with open(file_path, "r", encoding='utf-8') as file:
                    udf_conf = yaml.safe_load(file)
                    if "name" in udf_conf:
                        names_count[udf_conf("name")] += 1
                        names_files_mapping[udf_conf("name")].append(filename)
                        # check if the name is unique
                        # if not, add it to the duplicate_names dictionary
                        if names_count[udf_conf("name")] > 1:
                            duplicate_names[udf_conf("name")] = names_files_mapping[udf_conf("name")]

        self.assertEqual(
            len(duplicate_names),
            0,
            msg=(
                "Duplicate UDF names found: \n "
                f"{'\n'.join(
                    [f'Duplicated udf {name}, appears in files {files}' for name, files in duplicate_names.items()]
                )}"
            ),
        )

    def test_udfs_config_completeness(self):
        """
        Test that the UDFs have complete configuration
        """
        required_config_keys = ["name", "type", "description", "code"]
        incomplete_udfs = defaultdict(list)

        for filename in os.listdir(UDFS_FOLDER):
            if filename.endswith(".yaml"):
                file_path = os.path.join(UDFS_FOLDER, filename)

                with open(file_path, "r", encoding='utf-8') as file:
                    udf_conf = yaml.safe_load(file)
                    for key in required_config_keys:
                        if key not in udf_conf:
                            incomplete_udfs[filename].append(key)

        self.assertEqual(
            len(incomplete_udfs),
            0,
            msg=(
                "Incomplete UDF configurations found: \n"
                f"{'\n'.join([f'UDF {udf} is missing keys: {keys}' for udf, keys in incomplete_udfs.items()])}"
            ),
        )
    
    def test_udfs_config_validity(self):
        """
        Test that the UDFs have valid configuration
        """
        valid_types = ["function_sql", "function_js", "procedure"]
        invalid_udfs = defaultdict(list)

        for filename in os.listdir(UDFS_FOLDER):
            if filename.endswith(".yaml"):
                file_path = os.path.join(UDFS_FOLDER, filename)

                with open(file_path, "r", encoding='utf-8') as file:
                    udf_conf = yaml.safe_load(file)
                    if "type" in udf_conf and udf_conf["type"] not in valid_types:
                        invalid_udfs[filename].append(udf_conf["type"])

        self.assertEqual(
            len(invalid_udfs),
            0,
            msg=(
                "Invalid UDF configurations found: \n"
                f"{'\n'.join([f'UDF {udf} has invalid type: {type}' for udf, type in invalid_udfs.items()])}.\n"
                f"Valid types are: {', '.join(valid_types)}"
            ),
        )

if __name__ == '__main__':
    unittest.main()