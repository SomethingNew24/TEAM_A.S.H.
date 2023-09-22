import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Read the CSV file into a DataFrame
df = pd.read_csv("lead_gen.csv")

# Initialize a new column for sentiment analysis
df['Sentiment_Analysis'] = None

# Perform sentiment analysis using TextBlob polarity
for i, row in df.iterrows():
    text = row['Comment']
    stars = row['Stars']

    # Perform sentiment analysis using TextBlob
    obj = TextBlob(text)
    sentiment_polarity = obj.sentiment.polarity

    # Determine Sentiment_Analysis based on both Comment and Stars
    if stars in [1, 2]:
        df.at[i, 'Sentiment_Analysis'] = "Negative"
    elif stars == 3:
        df.at[i, 'Sentiment_Analysis'] = "Neutral"
    elif stars in [4, 5]:
        if sentiment_polarity > 0:
            df.at[i, 'Sentiment_Analysis'] = "Positive"
        elif sentiment_polarity < 0:
            df.at[i, 'Sentiment_Analysis'] = "Negative"
        else:
            df.at[i, 'Sentiment_Analysis'] = "Neutral"

# Sort the DataFrame based on Sentiment_Analysis (Negative, Neutral, Positive)
df_sorted = df.sort_values(by='Sentiment_Analysis', ascending=False)

# Explore Sentiment Distribution
sentiment_counts = df_sorted['Sentiment_Analysis'].value_counts()
plt.figure(figsize=(8, 6))
plt.bar(sentiment_counts.index, sentiment_counts.values)
plt.xlabel('Sentiment')
plt.ylabel('Count')
plt.title('Sentiment Distribution')
plt.show()

# Compare Ratings and Sentiments
average_ratings = df_sorted.groupby('Sentiment_Analysis')['Stars'].mean()
plt.figure(figsize=(8, 6))
plt.bar(average_ratings.index, average_ratings.values)
plt.xlabel('Sentiment')
plt.ylabel('Average Rating')
plt.title('Average Rating by Sentiment')
plt.show()

# Identify Most Positive and Negative Reviews
most_positive_review = df_sorted[df_sorted['Sentiment_Analysis'] == 'Positive'].nlargest(1, 'Stars')
most_negative_review = df_sorted[df_sorted['Sentiment_Analysis'] == 'Negative'].nsmallest(1, 'Stars')
print("Most Positive Review:")
print(most_positive_review[['Comment', 'Stars', 'User Profile Link']])
print("\nMost Negative Review:")
print(most_negative_review[['Comment', 'Stars', 'User Profile Link']])

# Create Word Clouds for Positive and Negative Sentiment Reviews
positive_reviews = " ".join(df_sorted[df_sorted['Sentiment_Analysis'] == 'Positive']['Comment'])
negative_reviews = " ".join(df_sorted[df_sorted['Sentiment_Analysis'] == 'Negative']['Comment'])

positive_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(positive_reviews)
negative_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(negative_reviews)

# Display Word Clouds
plt.figure(figsize=(10, 6))
plt.imshow(positive_wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud for Positive Sentiment Reviews')
plt.show()

plt.figure(figsize=(10, 6))
plt.imshow(negative_wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud for Negative Sentiment Reviews')
plt.show()

# Perform actions using the user profile links for lead generation
for idx, row in most_positive_review.iterrows():
    user_profile_link = row['User Profile Link']
    # Perform actions based on user profile link, e.g., sending messages or qualification

for idx, row in most_negative_review.iterrows():
    user_profile_link = row['User Profile Link']
    # Perform actions based on user profile link, e.g., sending messages or qualification



