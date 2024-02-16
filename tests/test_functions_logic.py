"""
Test the uniqueness of the UDFs
"""
import json
import os
import unittest
import jinja2
import yaml
from google.cloud import bigquery

UDFS_FOLDER = os.path.join(
    os.path.dirname(os.path.relpath(__file__)).replace('\\', '/'),
    '..',
    'user_defined_functions',
)
TEMPLATE_FOLDER = os.path.join(
    os.path.dirname(os.path.relpath(__file__)).replace('\\', '/'),
    '..',
    'templates',
)



class TestFunctionsLogic(unittest.TestCase):
    """
    Test the logic of the UDFs by running the functions against
    real examples stored in csv files.

    The class does not contain any test cases, but it will be populated with test cases.
    """
    def format_bigquery_result(result):
        column_headers = [field.name for field in result.schema]
        formatted_string = '\t'.join(column_headers) + '\n'

        for row in result:
            formatted_string += '\t'.join(str(row[column]) for column in column_headers) + '\n'

        return formatted_string

    def get_udf_config(self, udf_name):
        """
        Get the configuration of a UDF from its YAML file
        :param udf_name: The name of the UDF
        :return: args_info: names and types of the UDF's arguments
        :return: output_info: name and type of the UDF's output
        """
        udf_file_path = os.path.join(UDFS_FOLDER, f'{udf_name}.yaml')
        with open(udf_file_path, 'r', encoding='utf-8') as file:
            udf_config = yaml.safe_load(file)
            args_info = [(arg["name"], arg["type"]) for arg in udf_config['arguments']]
            output_info = udf_config['output']['name'], udf_config['output']['type']
        return args_info, output_info
    
    def get_temp_function_query(self, udf_name):
        """
        Get the query to create a temporary function
        :param udf_name: The name of the UDF
        :return: query: The query to create the UDF
        """
        udf_file_path = os.path.join(UDFS_FOLDER, f'{udf_name}.yaml')
        with open(udf_file_path, 'r', encoding='utf-8') as file:
            conf = yaml.safe_load(file)

        conf['name'] = udf_name
        template_file = os.path.join(TEMPLATE_FOLDER, f'temp_{conf["type"]}.sql')
        with open(template_file, 'r', encoding='utf-8') as file:
            template = jinja2.Template(file.read())
        query = template.render(**conf)
        return query

def generate_test_function(udf_name):
    """
    Generate a test case for a specific function
    :param udf_name: The name of the function
    :param args_info: a list of tuples containing the arguments of the function and their types
    :param output_info: a tuple containing the output of the function and its type
    :return: test_function: a test case that checks the logic of the function
    """
    def test_function(self):
        args_info, output_info = self.get_udf_config(udf_name)
        statements = []
        # read the test example from the json file
        test_file_path = os.path.join(UDFS_FOLDER, f'{udf_name}.json')
        self.assertTrue(os.path.exists(test_file_path), f"Test file for {udf_name} does not exist")

        with open(test_file_path, 'r', encoding='utf-8') as file:
            test_data = json.load(file)

        for test_sample in test_data:
            # get the arguments and the expected output of the current sample
            args = test_sample['args']
            # if the arguments are stored in a list, convert them to a literal string
            # with single quotes around each value
            if isinstance(args, list):
                args = [f"'{value}'" for value in args]
            # if the arguments are stored in a dictionary, convert them to a list
            # of literal strings with single quotes around each value
            if isinstance(args, dict):
                args = [f"'{args[name]}'" for name, _ in args_info]
            # get the expected output
            expected_output = f"'{test_sample['expected_output']}'"

            # create a list of tuples containing the arguments (and the output), their types and their names
            args_value_type_name = [
                (value, *args_info[i])
                for i, value in enumerate(args)
            ] + [(expected_output, *output_info)]
            statements.append(
                f"SELECT {', '.join([f'cast({value} as {type}) as {name}' for value, name, type in args_value_type_name])}"
            )
        # create the query
        temp_function_query = self.get_temp_function_query(udf_name)
        cte = "with test_data AS (" + '\n union all '.join(statements) + ")\n"
        query = (
            f"{temp_function_query}"
            f"{cte} SELECT *, "
            f"{udf_name}({','.join([name for name,_ in args_info])})"
            "\nfrom test_data\n"
            f"where {udf_name}({','.join([name for name,_ in args_info])}) <> {output_info[0]}"
        )
        # execute the query
        bigquery_client = bigquery.Client()
        result = bigquery_client.query(query).result()
        self.assertFalse(
            result,
            msg=(
                f"Test for {udf_name} failed"
                f"{self.format_bigquery_result(result)}"
            )
        )
    return test_function


def create_all_test_cases():
    """
    Create all test cases for the UDFs
    """
    # Collect all function names from YAML files
    for filename in os.listdir(UDFS_FOLDER):
        if filename.endswith('.yaml'):
            udf_name = filename.split('.')[0]
            test_name = f'test_logic_{udf_name}'
            test_function = generate_test_function(udf_name)
            setattr(TestFunctionsLogic, test_name, test_function)


create_all_test_cases()

if __name__ == '__main__':
    # Run the tests using unittest
    unittest.main()
