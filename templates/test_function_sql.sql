create temp function {{ name }}({% for argument in arguments %}`{{ argument.name }}` {{ argument.type }}{% if not loop.last %}, {% endif %}{% endfor %})
{% if output.type != 'any type' %}returns {{ output.type }}{% endif %}
as (
{{ code }}
);
with test_cte as (
    {% for test in tests %}
    select
        {% for argument in test.arguments %}{{ argument.value }} as {{ argument.name }}{% if not loop.last %}, {% endif %}{% endfor %}
        {% if output.type != 'any type' %}{{ test.output.value }} as expected{% endif %}
    {% if not loop.last %}union all{% endif %}
    {% endfor %}
    select
        {}
    from
        
)