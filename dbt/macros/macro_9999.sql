{#
    This macro replace values -9999 which was written by a failed station
#}

{% macro macro_9999(value) -%}

    case when {{ value }} < -9000 then NULL
        else {{ value }}
    end

{%- endmacro %}