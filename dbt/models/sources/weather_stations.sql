with all_stations as (select * from {{ source("weather", "seed_stations") }})

select
    dc_nome as station_name,
    cd_estacao as station_code,
    {{station_status('cd_situacao')}}  status,
    sg_estado as brazil_state,
    {{ brazil_regions("sg_estado") }} as brazil_region,
    vl_latitude as latitude,
    vl_longitude as longitude,
    vl_altitude as altitude_in_meters,
    parse_date('%d/%m/%Y', dt_inicio_operacao) as start_date
from all_stations