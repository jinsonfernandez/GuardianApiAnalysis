import os
from src.api_extarction import GuardianAPI
from src.utility import setup_logger
from datetime import datetime
from src.transformation_analysis import count_trudeau_articles

def main():
    logger = setup_logger(__name__)

    try:
        guardianapi = GuardianAPI()
        search_query = "Justin Trudeau"
        from_date = "2018-01-01"
        to_date = datetime.now().strftime("%Y-%m-%d")

        articles = guardianapi.guardian_search(search_query, from_date, to_date)
        df = guardianapi.results_to_dataframe(articles, search_query)
       
        if df is not None:
             article_count, avg_count = count_trudeau_articles(df)
             print(f"the average article per day is {avg_count:.2f}")
        else:
            logger.warning("No DataFrame was created.")

    except Exception as e:
        logger.exception("An error occurred during execution.")
        raise

if __name__ == "__main__":
    main()
