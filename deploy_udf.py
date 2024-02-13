from google.cloud import bigquery
from jinja2 import Template

def read_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def run_bigquery_query_with_template(project_id, dataset_id, function_name, template_path, query_path):
    """
    Fucntion to deploy a udf into bigquery
    """
    # Create a BigQuery client
    client = bigquery.Client(project=project_id)

    # Read the template and query from files
    template_content = read_from_file(template_path)
    query_content = read_from_file(query_path)

    # Create Jinja2 template object
    template = Template(template_content)

    # Render the template with provided variables
    rendered_query = template.render(
        project_id=project_id,
        dataset_id=dataset_id,
        function_name=function_name,
        query=query_content
    )

    print(rendered_query)
    # # Run the query
    query_job = client.query(rendered_query)

    # Wait for the query to complete
    query_job.result()


# Replace 'your-project-id' with your actual Google Cloud project ID
project_id = 'manifest-canto-413823'

# Replace 'your_dataset', 'your_function', 'your_template.sql', and 'your_query.sql' with your actual values
dataset_id = 'your_dataset'
function_name = 'my_func'
template_path = 'templates/sql_func.sql'
query_path = 'user_defined_functions/my_func.sql'

# Execute the query with template
run_bigquery_query_with_template(project_id, dataset_id, function_name, template_path, query_path)
