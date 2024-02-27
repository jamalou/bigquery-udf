from copy import deepcopy
from functools import cached_property
import json
import logging
import re

import yaml
from jinja2 import Template, Environment, FileSystemLoader
from google.api_core.exceptions import BadRequest

from udf_bigquery.src.udf_utils import (
    format_bq_result,
    render_test_entry,
    UDFS_FOLDER,
    TEMPLATE_FOLDER,
)

jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_FOLDER),
    cache_size=0,
    auto_reload=True,
    autoescape=False,
)

class UserDefinedFunction():
    """
    Class to handle BigQuery user defined functions
    """
    def __init__(self, udf_name, **additional_params):
        self.udf_name = udf_name
        self.udf_file_path = UDFS_FOLDER / f'{udf_name}.yaml'
        if not self.udf_file_path.is_file():
            raise FileNotFoundError(f"The UDF {udf_name} does not exist")
        self.additional_params = additional_params
        # list of fields that can be templated
        # if a field is templated, it will be rendered with the additional_params
        # code is not included because it is a special case
        self.templated_fields = ['project', 'dataset']
        self._conf = None

    @cached_property
    def config(self):
        """
        Get the configuration of a UDF from its yaml file
        :param udf_name: The name of the UDF
        :return: The configuration of the UDF
        """
        with open(self.udf_file_path, 'r', encoding='utf-8') as file:
            conf = yaml.safe_load(file)

        conf['name'] = self.udf_name
        # render templated fields with additional_params
        for field in self.templated_fields:
            conf[field] = jinja_env.from_string(conf[field]).render(**self.additional_params)
        return conf

    @cached_property
    def dependencies(self):
        """
        Get the dependencies of a UDF
        :return: A list of the dependencies of the UDF
        """
        code = self.config.get('code', '')
        # pylint: disable=C0301
        return re.findall(r"{{\s*ref\s*\(\s*[\"\']([^\"]+)[\"\']\s*(?:\s*,\s[^\)]+)?\)\s*}}", code)

    @cached_property
    def qualified_name(self):
        """
        Get the reference of a UDF in BigQuery
        :return: The reference of the UDF in BigQuery
        """
        return f'`{self.config["project"]}`.`{self.config["dataset"]}`.`{self.config["name"]}`'

    @cached_property
    def temp_qualified_name(self):
        """
        Get the reference of a UDF in BigQuery for a temporary function
        :return: The reference of the UDF in BigQuery for a temporary function
        """
        return f'`{self.udf_name}`'
    
    @cached_property
    def tests(self):
        
        for test in self.config.get('tests', []):
            test_path = UDFS_FOLDER / f'{test.get("file")}'
            test_name = test_path.stem
            test_query = self.render_test_query(test_path)
            test_throws_exception = test.get("throws_exception")
            yield {
                "name": test_name,
                "path": test_path,
                "query": test_query,
                "throws_exception": test_throws_exception,
            }

    def get_other_function_ref(self, ohter_udf_name, **additional_params):
        """
        Get the reference of a UDF in BigQuery
        :param ohter_udf_name: The name of the UDF
        :param additional_params: Additional parameters to render the project name
            example: env="dev"
        :return: The reference of the UDF in BigQuery
        """
        return UserDefinedFunction(ohter_udf_name, **additional_params).qualified_name

    def get_other_temp_function_ref(self, ohter_udf_name, **additional_params):
        """
        Get the reference of a UDF in BigQuery as a temporary function
        :param ohter_udf_name: The name of the UDF
        :param additional_params: Additional parameters to render the project name
        :return: The reference of the UDF in BigQuery
        """
        return UserDefinedFunction(ohter_udf_name, **additional_params).temp_qualified_name    

    def render_function_template(self):
        """
        Render the temporary function template with the configuration of a UDF
        :param udf_name: The name of the UDF
        :return: The rendered template
        """
        jinja_env.globals['ref'] = self.get_other_function_ref

        conf = deepcopy(self.config)
        conf["code"] = jinja_env.from_string(conf["code"]).render(**self.additional_params)

        query_template = jinja_env.get_template(f'{conf["function_type"]}.sql')
        query = query_template.render(**conf)

        return query

    def render_single_temp_function_template(self):
        """
        Render the temporary function template with the configuration of a UDF
        Used for testing
        :return: The rendered template
        """
        jinja_env.globals['ref'] = self.get_other_temp_function_ref

        conf = deepcopy(self.config)
        conf["code"] = jinja_env.from_string(conf["code"]).render(**self.additional_params)

        query_template = jinja_env.get_template(f'temp_{conf["function_type"]}.sql')
        query = query_template.render(**conf)

        return query
    
    def render_temp_function_template(
        self,
        query="",
        visited_udfs=frozenset(),
        **additional_params
    ):
        """
        Render the temporary function template with the configuration of a UDF
        If there are dependencies, they will be rendered as well
        :param udf_name: The name of the UDF
        :return: The rendered template
        """
        if self.udf_name in visited_udfs:
            return query, visited_udfs

        childs_query = ""
        # if there are dependencies, render them first
        for dependency in self.dependencies:
            if dependency in visited_udfs:
                continue

            denpendency_udf = UserDefinedFunction(dependency, **self.additional_params)
            depencency_query, visited_udfs = denpendency_udf.render_temp_function_template(
                query=query,
                visited_udfs=visited_udfs,
                **additional_params
            )
            childs_query += depencency_query
        
        if self.udf_name in visited_udfs:
            raise ValueError(f"UDF {self.udf_name} has circular dependencies")

        query += (
            f"{childs_query}"
            f"{self.render_single_temp_function_template()}"
            "\n"
        )
        visited_udfs = visited_udfs.union({self.udf_name})
        return query, visited_udfs
    
    def deploy_to_bq(
        self,
        bigquery_client,
        deployed_udfs=frozenset(),
        dry_run=False,
    ):
        """
        Deploy a user defined function to a dataset.
        The information of the function is stored in a yaml file in the "user_defined_functions" folder.
        The function will be deployed to the dataset specified by the user.
        And if the function has dependencies, they will be deployed first.
        :param bigquery_client: The bigquery client object
        :param deployed_udfs: A set of the already deployed udfs.
                            This is used to avoid deploying the same udf multiple times
        :param dry_run: If True, the function will not be deployed, it will only be printed
        :return: A set of the deployed udfs
        """
        # check if the udf is already deployed, if yes just return the deployed_udfs
        if self.udf_name in deployed_udfs:
            return deployed_udfs

        # if the udf has dependencies, deploy them first
        for dependency in self.dependencies:
            if dependency in deployed_udfs:
                continue
            denpendency_udf = UserDefinedFunction(dependency, **self.additional_params)
            deployed_udfs = denpendency_udf.deploy_to_bq(
                bigquery_client,
                deployed_udfs=deployed_udfs,
                dry_run=dry_run,
            )

        if self.udf_name in deployed_udfs:
            # raise an error for circular dependencies
            raise ValueError(f"UDF {self.udf_name} has circular dependencies")

        # now deploy the udf
        query = self.render_function_template()

        if dry_run:
            logging.info('Dry run: The function will not be deployed')
            logging.info('The query that will be executed is:')
            logging.info(query)
            deployed_udfs = deployed_udfs.union({self.udf_name})
            return deployed_udfs

        logging.info('Creating function %s', self.qualified_name)

        # execute the query to create the udf
        bigquery_client.query(query).result()
        logging.info('Successfully created %s', self.qualified_name)

        # add the udf to the deployed udfs set
        deployed_udfs = deployed_udfs.union({self.udf_name})

        return deployed_udfs

    def render_test_query(self, test_file_path):
        """
        Render all the test entries for a UDF
        :param udf_name: The name of the UDF
        :return: A list of rendered test entries
        """
        with open(test_file_path, 'r', encoding='utf-8') as file:
            test_entries = json.load(file)
        args_names = [ arg["name"] for arg in self.config.get("arguments")]
        args_types = [ arg["type"] for arg in self.config.get("arguments")]
        output_name = self.config.get("output").get("name")
        output_type = self.config.get("output").get("type")
        test_entries = [
            render_test_entry(
                args_names,
                args_types,
                test_entry["args"],
                output_name,
                output_type,
                test_entry["output"],
            ) for test_entry in test_entries
        ]
        # temporary test cte that holds all the test entries
        temp_test_cte = (
            f"with test_cte_{self.udf_name} as (\n"
            + "\n\tunion all ".join(test_entries)
            + "\n)\n"
        )
        test_query = (
            f"-- Test for {self.udf_name}\n"
            f"{self.render_temp_function_template()[0]}"
            f"{temp_test_cte}"
            f"select *, {self.udf_name}({', '.join(args_names)}) as result from test_cte_{self.udf_name}"
            f"\nwhere {output_name} <> {self.udf_name}({', '.join(args_names)});\n"
        )
        return test_query

    def generate_test_case(self, test, bigquery_client=None):
        """
        Generate a test case for a UDF
        :param test: The test dictionary that contains the test name, path, query and throws_exception
        :return: A test case for the UDF
        """
        print(test["query"])
        def test_case(self):
            """
            Test the UDF with the test entries
            """
            name = test["name"]
            path = test["path"]
            query = test["query"]
            throws_exception = test["throws_exception"]

            if throws_exception:
                try:
                    result = bigquery_client.query(query).result()
                except BadRequest as e:
                    # check if the error code is 400 (Bad Request)
                    self.assertEqual(e.code, 400, f"Test {name} should throw a 400 error")
                return
            result = bigquery_client.query(query).result()
            self.assertEqual(result.total_rows, 0, format_bq_result(result))

        return test_case

    def __repr__(self):
        return f"UserDefinedFunction({self.udf_name})"

    def __str__(self):
        return f"UserDefinedFunction({self.udf_name})"


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    udf = UserDefinedFunction('foo', env='dev')
    udf.render_test_query(UDFS_FOLDER / 'foo_simple_test.json')
