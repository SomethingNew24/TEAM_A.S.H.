from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

app = Flask(__name__)

# Get the current directory of the app.py file
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to ChromeDriver (assuming it's in the same directory)
chrome_driver_path = os.path.join(current_directory, 'chromedriver.exe')

# Define the route for the input page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        urls = request.form["urls"]

        # Split the entered URLs into a list
        url_list = urls.split('\n')

        # Call your login function to authenticate the user
        driver = login_to_mouthshut(username, password)

        if driver:
            # Create an empty list to store analysis results
            results = []

            # Iterate through each URL and extract data
            for url in url_list:
                data_list = extract_data(driver, url.strip())
                for data in data_list:
                    # Perform sentiment analysis using TextBlob
                    text = data['Comment']
                    stars = data['Stars']

                    # Perform sentiment analysis using TextBlob
                    obj = TextBlob(text)
                    sentiment_polarity = obj.sentiment.polarity

                    # Determine Sentiment_Analysis based on both Comment and Stars
                    if stars in [1, 2]:
                        data['Sentiment_Analysis'] = "Negative"
                    elif stars == 3:
                        data['Sentiment_Analysis'] = "Neutral"
                    elif stars in [4, 5]:
                        if sentiment_polarity > 0:
                            data['Sentiment_Analysis'] = "Positive"
                        elif sentiment_polarity < 0:
                            data['Sentiment_Analysis'] = "Negative"
                        else:
                            data['Sentiment_Analysis'] = "Neutral"

                    results.append(data)

            # Close the browser window
            driver.quit()

            # Sort the results DataFrame based on Sentiment_Analysis
            df_sorted = pd.DataFrame(results).sort_values(by='Sentiment_Analysis', ascending=False)

            # Explore Sentiment Distribution
            sentiment_counts = df_sorted['Sentiment_Analysis'].value_counts()
            plt.figure(figsize=(8, 6))
            plt.bar(sentiment_counts.index, sentiment_counts.values)
            plt.xlabel('Sentiment')
            plt.ylabel('Count')
            plt.title('Sentiment Distribution')
            plt.savefig(os.path.join(current_directory, 'static/sentiment_distribution.png'))  # Save the plot as an image
            plt.close()

            # Compare Ratings and Sentiments
            average_ratings = df_sorted.groupby('Sentiment_Analysis')['Stars'].mean()
            plt.figure(figsize=(8, 6))
            plt.bar(average_ratings.index, average_ratings.values)
            plt.xlabel('Sentiment')
            plt.ylabel('Average Rating')
            plt.title('Average Rating by Sentiment')
            plt.savefig(os.path.join(current_directory, 'static/average_rating_by_sentiment.png'))  # Save the plot as an image
            plt.close()

            # Identify Most Positive and Negative Reviews
            most_positive_review = df_sorted[df_sorted['Sentiment_Analysis'] == 'Positive'].nlargest(1, 'Stars')
            most_negative_review = df_sorted[df_sorted['Sentiment_Analysis'] == 'Negative'].nsmallest(1, 'Stars')

            # Create Word Clouds for Positive and Negative Sentiment Reviews
            positive_reviews = " ".join(df_sorted[df_sorted['Sentiment_Analysis'] == 'Positive']['Comment'])
            negative_reviews = " ".join(df_sorted[df_sorted['Sentiment_Analysis'] == 'Negative']['Comment'])

            # Check if there are positive and negative reviews
            if positive_reviews:
                positive_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(positive_reviews)
                positive_wordcloud.to_file(os.path.join(current_directory, 'static/positive_wordcloud.png'))

            if negative_reviews:
                negative_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(negative_reviews)
                negative_wordcloud.to_file(os.path.join(current_directory, 'static/negative_wordcloud.png'))
            else:
                # Handle the case where there are no negative reviews
                print("No negative reviews to generate a word cloud.")

            return render_template(
                "result.html",
                results=results,
                sentiment_distribution="static/sentiment_distribution.png",
                average_rating_by_sentiment="static/average_rating_by_sentiment.png",
                positive_wordcloud="static/positive_wordcloud.png",
                negative_wordcloud="static/negative_wordcloud.png"
            )

    # Render the input page
    return render_template("index.html")

def login_to_mouthshut(username, password):
    # Start the Chrome WebDriver with the specified path
    driver = webdriver.Chrome(executable_path=chrome_driver_path)

    try:
        # Open the login page
        driver.get("https://www.mouthshut.com")
        driver.find_element(By.ID, "sign-in").click()

        # Wait for the email input field to be visible
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "loginId"))
        )

        # Enter username and password and submit the form
        email_input.send_keys(username)
        driver.find_element(By.ID, "pwd").send_keys(password)
        driver.find_element(By.ID, "btnAjax_Login").click()

        # Wait for the login to complete (you may need to adjust the wait time based on your internet speed)
        time.sleep(5)

        return driver
    except Exception as e:
        print("Error during login:", e)
        driver.quit()
        return None

def extract_data(driver, url):
    try:
        # Open the URL
        driver.get(url)

        # Find all review articles
        review_articles = driver.find_elements(By.XPATH, "//div[@id='dvreview-listing']/div[@class='row review-article']")

        # Store the data in a list of dictionaries
        data_list = []
        for review_article in review_articles:
            # Find the comment
            comment_element = review_article.find_element(By.XPATH, ".//div[@class='more reviewdata']/p")
            comment = comment_element.text.strip()

            # Find the user profile link
            user_profile_link_element = review_article.find_element(By.XPATH, ".//div[@class='user-ms-name']/a")
            user_profile_link = user_profile_link_element.get_attribute("href")

            # Find the stars count for this review
            stars_element = review_article.find_elements(By.XPATH, ".//div[@class='rating']//i[@class='icon-rating rated-star']")
            stars_count = len(stars_element)

            data_list.append({"Comment": comment, "User Profile Link": user_profile_link, "Stars": stars_count})

        return data_list

    except Exception as e:
        print("Error during data extraction:", e)
        return []

if __name__ == "__main__":
    app.run(debug=True)
