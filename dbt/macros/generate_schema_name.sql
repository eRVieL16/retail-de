{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set clean_schemas = ['sales', 'inventory'] -%}

    {%- if custom_schema_name is none -%}

        {{ target.schema }}

    {%- elif (custom_schema_name | trim) in clean_schemas -%}

        {{ custom_schema_name | trim }}

    {%- else -%}

        {{ target.schema }}_{{ custom_schema_name | trim }}

    {%- endif -%}

{%- endmacro %}