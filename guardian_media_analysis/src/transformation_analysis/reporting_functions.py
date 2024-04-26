import duckdb
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class DataProcessor:
    """
    A class for processing and analyzing data related to Justin Trudeau articles.
    """
    def __init__(self, df):
        self.df = df

    def get_trudeau_articles_count(self):
        """
        Retrieve the count of articles related to Justin Trudeau over time.
        Returns:
            tuple: A tuple containing the result DataFrame and the average number of articles per day.
        """
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

    def get_top_section(self):
        """
        Identify the top sections with the most articles.
        Returns:
            pandas.DataFrame: A DataFrame containing the section names and their article counts.
        """
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

    def get_total_article_count(self):
        """
        Calculate the total number of articles since 2018.
        Returns:
            int: The total count of articles.
        """

        con = duckdb.connect()
        query = """
            SELECT COUNT(*) AS total_articles
            FROM (
                SELECT CAST(webPublicationDate AS DATE) AS date, COUNT(*) AS article_count
                FROM df
                WHERE type = 'article'
                  AND webPublicationDate >= '2018-01-01'
                GROUP BY CAST(webPublicationDate AS DATE)
            ) AS daily_counts
            WHERE article_count > 0
        """

        result = con.execute(query).fetchdf()
        con.close()
        if not result.empty and 'total_articles' in result.columns:
            total_count = result['total_articles'].iloc[0]
        else:
            total_count = 0
        return total_count

    def get_unusual_events(self, article_count, threshold=2):
        """
         Detect unusual events based on the number of articles published on each date.
        Args:
            article_count (pandas.DataFrame): The DataFrame containing the article counts per date.
            threshold (int, optional): The threshold for determining unusual events. Defaults to 2.
        Returns:
            pandas.DataFrame: A DataFrame containing the unusual event dates and their article counts.
        """

        mean_articles = np.mean(article_count['No_of_articles'])
        std_articles = np.std(article_count['No_of_articles'])

        unusual_events = article_count[(article_count['No_of_articles'] > mean_articles + threshold * std_articles) |
                                       (article_count['No_of_articles'] < mean_articles - threshold * std_articles)]

        unusual_events = unusual_events.sort_values('No_of_articles', ascending=False)

        return unusual_events

    def get_articles_unusual_events(self, unusual_dates):
        """
        Retrieve the headlines of articles published on unusual event dates.
        Args:
            unusual_dates (list): A list of unusual event dates.
        """
        self.df['webPublicationDate'] = pd.to_datetime(self.df['webPublicationDate'])
        
        unusual_articles = self.df[(self.df['webPublicationDate'].dt.date.astype(str).isin(unusual_dates)) & (self.df['type'] == 'article')]
        
        for date in unusual_dates:
            print(f"Unusual Event Date: {date}")
            print("Article Headlines:")
            articles_on_date = unusual_articles[unusual_articles['webPublicationDate'].dt.date.astype(str) == date]
            
            if articles_on_date.empty:
                print("No articles found for this date.")
            else:
                for _, article in articles_on_date.iterrows():
                    print(f"- {article['webTitle']}")
            
            print()

    def get_unusual_event_details(self, unusual_dates):
        """
        Provide detailed information about articles published on unusual event dates.
        Args:
            unusual_dates (list): A list of unusual event dates.
        """
        for date in unusual_dates:
            start_date = pd.to_datetime(date).date()  # Convert to datetime.date for comparison

            event_articles = self.df[
                (self.df['webPublicationDate'].dt.date == start_date) &  # Ensure comparison is with datetime.date
                (self.df['type'] == 'article')
            ]

            print(f"Event Date: {date}")
            print(f"Total Articles: {len(event_articles)}")
            print("Article Details:")

            for _, article in event_articles.iterrows():
                print(f"Date: {article['webPublicationDate'].date()}")
                print(f"Headline: {article['webTitle']}")
                print(f"Section: {article['sectionName']}")
                print(f"URL: {article['webUrl']}")
                print("---")
            
            print()



class DataVisualizer:
    """
    A class for visualizing data related to Justin Trudeau articles.
    """
    def __init__(self, df):
        self.df = df

    def plot_articles_by_section(self, top_section_df):
        """
        Create a bar chart showing the number of articles by section.
        Args:
            top_section_df (pandas.DataFrame): The DataFrame containing the top sections and their article counts.
        """
        fig = px.bar(top_section_df, x='sectionName', y='section_count', 
                     title='Number of Articles by Section',
                     labels={'sectionName': 'Section Name', 'section_count': 'Number of Articles'})
        fig.show()

    def plot_article_by_time(self, article_count, group_by='month'):
        """
        Generate a bar chart displaying the number of articles about Justin Trudeau over time.

        Args:
            article_count (pandas.DataFrame): The DataFrame containing the article counts per date.
            group_by (str, optional): The time unit to group the articles by. Defaults to 'month'.
                Allowed values are 'month', 'year', 'week', or 'day'.
        """
        con = duckdb.connect()

        query = f"""
            SELECT DATE_TRUNC('{group_by}', Date) AS group_date, SUM(No_of_articles) AS total_articles
            FROM article_count
            GROUP BY group_date
            ORDER BY group_date
        """
        grouped_data = con.execute(query).df()

        # Set the x-axis title and tick format based on the group_by parameter
        if group_by == 'month':
            x_title = 'Month'
            tick_format = '%b %Y'
            group_by_title = 'Month'
        elif group_by == 'year':
            x_title = 'Year'
            tick_format = '%Y'
            group_by_title = 'Year'
        elif group_by == 'week':
            x_title = 'Week'
            tick_format = '%Y-W%W'
            group_by_title = 'Week'
        elif group_by == 'day':
            x_title = 'Day'
            tick_format = '%Y-%m-%d'
            group_by_title = 'Day'
        else:
            raise ValueError("Invalid group_by value. Allowed values are 'month', 'year', 'week', or 'day'.")

        fig = go.Figure(data=[go.Bar(x=grouped_data['group_date'], y=grouped_data['total_articles'],
                                    name='Number of Articles', marker_color='#1f77b4', marker_opacity=0.8)])

        fig.update_layout(
            title=f'<b>Number of Articles about Justin Trudeau (Grouped by {group_by_title})</b>',
            xaxis_title=x_title,
            yaxis_title='Number of Articles',
            xaxis=dict(
                tickformat=tick_format
            ),
            showlegend=True,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        fig.show()

    def plot_unusual_events(self, article_count):
        """
        Visualize the distribution of the number of articles using a box plot, highlighting unusual events.

        Args:
            article_count (pandas.DataFrame): The DataFrame containing the article counts per date.
        """
      
        fig = go.Figure()

        # Create a text string with the date and number of articles for each data point
        hover_text = [f"Date: {date}<br>Number of Articles: {count}" for date, count in
                      zip(article_count['Date'], article_count['No_of_articles'])]

        fig.add_trace(go.Box(
            y=article_count['No_of_articles'],
            name='Number of Articles',
            boxpoints='suspectedoutliers',  # Display suspected outliers
            text=hover_text,  # Set the hover text
            hoverinfo='text',  # Display only the hover text
            marker=dict(
                color='rgb(8,81,156)',
                outliercolor='rgba(219, 64, 82, 0.6)',
                line=dict(outliercolor='rgba(219, 64, 82, 0.6)', outlierwidth=2)
            )
        ))

        fig.update_layout(
            title='Box Plot of Number of Articles',
            yaxis_title='Number of Articles',
            showlegend=False
        )

        fig.show()