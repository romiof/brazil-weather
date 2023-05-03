with fact as (select
                     station_code,
                     date as date_time,
                     date(date) as calendar_date,
                     {{ macro_9999("total_precipitation") }} as total_precipitation,
                     {{ macro_9999("dry_bulb_air_temperature") }} as dry_bulb_air_temperature,
                     {{ macro_9999("max_air_temp_dry_bulb") }} as max_air_temp_dry_bulb,
                     {{ macro_9999("min_air_temp_dry_bulb") }} as min_air_temp_dry_bulb,
                from {{ ref("all_data") }} )
SELECT 
    fact.station_code,
    fact.date_time,
    fact.calendar_date,
    fact.total_precipitation,
    fact.dry_bulb_air_temperature,
    fact.max_air_temp_dry_bulb,
    fact.min_air_temp_dry_bulb,

-- Stations
    sta.station_name,
    sta.status,
    sta.brazil_state,
    sta.brazil_region,
    sta.latitude,
    sta.longitude,
    sta.altitude_in_meters,

-- Calendar 
    calendar_month,
    calendar_year,
    year_seasson

FROM fact
JOIN {{ref("weather_stations")}} sta ON fact.station_code = sta.station_code
JOIN {{ref("dim_calendar")}} cal ON fact.calendar_date = cal.calendar_date



 