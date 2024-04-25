import pandas as pd
import numpy as np
import duckdb

def count_trudeau_articles(df):
    con = duckdb.connect()
    query = """ 
        with date_series as(
            SELECT day::date as complete_date
            FROM generate_series('2018-01-01'::date, current_date, INTERVAL '1 day') as series(day)
        ),
        article_count as(
            select date_series.complete_date Date, coalesce(count(df.webPublicationDate), 0) as No_of_articles
            from date_series left join df 
            on date_series.complete_date = df.webPublicationDate::date and df.type = 'article'
            group by date_series.complete_date
        ),
        average_article as (
            select Date, No_of_articles, avg(No_of_articles) over() as avg_articles_per_day
            from article_count
        )
        select * from average_article order by Date
    """

    result = con.execute(query).fetchdf()
    con.close()
    if not result.empty and 'avg_articles_per_day' in result.columns:
        avg_count = result['avg_articles_per_day'].iloc[0]
    else:
        avg_count = -999
    return result, avg_count

def get_top_section(df):
    con = duckdb.connect()
    query = """
        SELECT sectionName, count(*) as section_count
        FROM df
        WHERE type = 'article'
        GROUP BY sectionName
        ORDER BY section_count DESC
    """
    result = con.execute(query).fetchdf()
    con.close()
    
    return result