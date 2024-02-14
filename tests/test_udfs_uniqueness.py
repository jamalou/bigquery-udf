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
    test the completeness the UDFs configuration.
    test the validity of the UDFs configuration.
    """
    def test_udfs_config_completeness(self):
        """
        Test that the UDFs have complete configuration
        """
        required_config_keys = ["type", "description", "code"]
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
                '\n'.join([f'UDF {udf} is missing keys: {keys}' for udf, keys in incomplete_udfs.items()])
            ),
        )
    
    def test_udfs_config_validity(self):
        """
        Test that the UDFs have valid configuration
        """
        valid_types = ["function_sql", "function_js", "procedure"]
        invalid_udfs = dict()

        for filename in os.listdir(UDFS_FOLDER):
            if filename.endswith(".yaml"):
                file_path = os.path.join(UDFS_FOLDER, filename)

                with open(file_path, "r", encoding='utf-8') as file:
                    udf_conf = yaml.safe_load(file)
                    if "type" in udf_conf and udf_conf["type"] not in valid_types:
                        invalid_udfs[filename] = udf_conf["type"]

        self.assertFalse(
            invalid_udfs,
            msg=(
                "Invalid UDF configurations found: \n"
                f"\n".join([f'UDF {udf} has invalid type: {type}' for udf, type in invalid_udfs.items()])
                # "\nValid types are: "
                # ", ".join(valid_types)
            ),
        )

if __name__ == '__main__':
    unittest.main()