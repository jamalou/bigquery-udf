"""
Helper functions for UDFs
"""
from pathlib import Path

SRC_FOLDER = Path(__file__).parent
UTILS_FOLDER = SRC_FOLDER / 'utils'
UDFS_FOLDER = SRC_FOLDER / 'user_defined_functions'
TEMPLATE_FOLDER = SRC_FOLDER / 'templates'


def get_all_udf_names():
    """
    Get the list of all UDFs
    :return: A list of the names of all UDFs
    """
    return [udf.stem for udf in UDFS_FOLDER.glob('*.yaml')]


def render_test_entry(
    args_names,
    args_types,
    args_values,
    output_name,
    output_type,
    output_value,
):
    """
    Render a test entry
    :param args_name: The name of the arguments
    :param args_type: The type of the arguments
    :param args_value: The value of the arguments
    :param output_name: The name of the output
    :param output_type: The type of the output
    :param output_value: The value of the output
    :return: The rendered test entry
    """
    all_values = args_values + [output_value]
    all_types = args_types + [output_type]
    all_names = args_names + [output_name]
    entry = zip(all_names, all_types, all_values)
    
    entry_query = "select " + ", ".join(
        [
            f'cast("{value}" as {type_}) as {name}'
            if type_.lower() != 'any type' else f'{value} as {name}'
            for name, type_, value in entry
        ]
    )

    return entry_query


def format_bq_result(result):
    """
    Format the result of a BigQuery query
    :param result: The result of a BigQuery query
    :return: The formatted result
    """
    header = [field.name for field in result.schema]
    rows = [[str(row[col]) for col in header] for row in result]
    data = [header] + rows
    rows_max_width = [max(len(cell) for cell in col) for col in zip(*data)]
    formatted_data = [
        " | ".join(
            f"{cell.ljust(width)}" for cell, width in zip(row, rows_max_width)
        )
        for row in data
    ]
    formatted_data.insert(1, " | ".join("-" * width for width in rows_max_width))
    return "\n" + "\n".join(formatted_data)
