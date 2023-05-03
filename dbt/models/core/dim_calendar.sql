with all_dates as (select distinct 
                            date(date) as calendar_date,
                            extract(month from date) as calendar_month,
                            extract(year from date) as calendar_year
                        from {{ ref("all_data") }} )
--
select 
    calendar_date,
    calendar_month,
    calendar_year,
    case when calendar_date BETWEEN DATE(calendar_year, 03, 21) AND DATE(calendar_year, 06, 20) then 'Fall'
         when calendar_date BETWEEN DATE(calendar_year, 06, 21) AND DATE(calendar_year, 09, 22) then 'Winter'
         when calendar_date BETWEEN DATE(calendar_year, 09, 23) AND DATE(calendar_year, 12, 20) then 'Spring'
         else 'Summer'
    end AS year_seasson
from all_dates