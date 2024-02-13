CREATE OR REPLACE FUNCTION `{{ project_id }}.{{ dataset_id }}.{{ function_name }}`(x INT64) AS
  {{ query }}
;