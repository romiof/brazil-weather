{#
    This macro decode Regions of Brazil
#}

{% macro brazil_regions(brazil_state) -%}

    case when {{ brazil_state }} IN ('AC','AM','RN','RO','AP','TO','PA') then 'North'
         when {{ brazil_state }} IN ('AL','BA','CE','MA','PE','PI','PB','SE','RN') then 'Northeast'
         when {{ brazil_state }} IN ('GO','MT','MS','DF') then 'Central-West'
         when {{ brazil_state }} IN ('ES','MG','SP','RJ') then 'Southeast'
         when {{ brazil_state }} IN ('PR','SC','RS') then 'South'
         else 'N/A'
    end

{%- endmacro %}