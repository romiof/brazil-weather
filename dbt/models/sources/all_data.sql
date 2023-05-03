with all_data as (select *
                    from {{ source("weather", "raw_zone") }} 
                    -- limit 10000000
                )
--
select *
from all_data
