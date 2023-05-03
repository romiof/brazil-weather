{#
    This macro translate the `cd_situacao`column to English.
#}

{% macro station_status(cd_situacao) -%}

    case {{ cd_situacao }}
        when 'Pane' then 'Malfunction'
        when 'Operante' then 'Operating'
        else 'N/A'
    end

{%- endmacro %}