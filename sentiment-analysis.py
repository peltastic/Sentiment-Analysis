import tweepy
import praw
import re
from textblob import TextBlob
import pandas as pd
import nltk

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# ======================
# Twitter API Setup
# ======================
# Replace with your Twitter API credentials
TWITTER_API_KEY = 'YOUR_TWITTER_API_KEY'
TWITTER_API_SECRET_KEY = 'YOUR_TWITTER_API_SECRET_KEY'
TWITTER_BEARER_TOKEN = 'YOUR_TWITTER_BEARER_TOKEN'

# Initialize Twitter client
twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

def get_twitter_comments(query, max_results=100):
    """
    Fetch recent tweets matching the query.

    Args:
        query (str): The search query.
        max_results (int): Number of tweets to fetch.

    Returns:
        list: List of tweet texts.
    """
    try:
        tweets = twitter_client.search_recent_tweets(query=query, max_results=max_results, tweet_fields=['text'])
        comments = []
        if tweets.data:
            for tweet in tweets.data:
                comments.append(tweet.text)
        return comments
    except Exception as e:
        print(f"Error fetching Twitter data: {e}")
        return []

# ======================
# Reddit API Setup
# ======================
# Replace with your Reddit API credentials
REDDIT_CLIENT_ID = 'YOUR_REDDIT_CLIENT_ID'
REDDIT_CLIENT_SECRET = 'YOUR_REDDIT_CLIENT_SECRET'
REDDIT_USER_AGENT = 'YourAppName by /u/YourRedditUsername'

# Initialize Reddit client
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_USER_AGENT)

def get_reddit_comments(query, limit=100):
    """
    Fetch comments from Reddit matching the query.

    Args:
        query (str): The search query.
        limit (int): Number of comments to fetch.

    Returns:
        list: List of comment texts.
    """
    comments = []
    try:
        for submission in reddit.subreddit('all').search(query, limit=limit):
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                comments.append(comment.body)
        return comments
    except Exception as e:
        print(f"Error fetching Reddit data: {e}")
        return []

# ======================
# Text Cleaning and Sentiment Analysis
# ======================
def clean_text(text):
    """
    Clean the input text by removing URLs, special characters, and converting to lowercase.

    Args:
        text (str): The original text.

    Returns:
        str: The cleaned text.
    """
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove emojis and special characters
    text = re.sub(r'[^A-Za-z0-9\s]+', '', text)
    # Convert to lowercase
    text = text.lower()
    return text

def analyze_sentiment(text):
    """
    Analyze the sentiment of the given text.

    Args:
        text (str): The cleaned text.

    Returns:
        str: Sentiment category ('Positive', 'Negative', 'Neutral').
    """
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return 'Positive'
    elif polarity < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

# ======================
# Data Collection Function
# ======================
def collect_comments(apps, platforms, max_results=100):
    """
    Collect comments from specified platforms for given apps.

    Args:
        apps (list): List of e-commerce app names.
        platforms (list): List of platforms ('Twitter', 'Reddit').
        max_results (int): Number of comments to fetch per app per platform.

    Returns:
        pandas.DataFrame: DataFrame containing collected data.
    """
    data = {
        'App': [],
        'Platform': [],
        'Comment': [],
        'Cleaned_Comment': [],
        'Sentiment': []
    }
    
    for app in apps:
        for platform in platforms:
            print(f"Collecting data for {app} on {platform}...")
            if platform == 'Twitter':
                query = f'"{app}" -is:retweet lang:en'
                comments = get_twitter_comments(query, max_results)
            elif platform == 'Reddit':
                query = app
                comments = get_reddit_comments(query, max_results)
            else:
                comments = []
            
            print(f"Collected {len(comments)} comments from {platform} for {app}.")
            
            for comment in comments:
                cleaned = clean_text(comment)
                sentiment = analyze_sentiment(cleaned)
                
                data['App'].append(app)
                data['Platform'].append(platform)
                data['Comment'].append(comment)
                data['Cleaned_Comment'].append(cleaned)
                data['Sentiment'].append(sentiment)
    
    df = pd.DataFrame(data)
    return df

# ======================
# Main Function
# ======================
def main():
    """
    Main function to execute data collection, sentiment analysis, and export results.
    """
    apps = ['Amazon', 'Target', 'eBay', 'Jumia', 'AliExpress']
    platforms = ['Twitter', 'Reddit']  # Extend to ['Twitter', 'Reddit', 'Facebook', 'Instagram', 'LinkedIn'] as needed
    max_results = 100  # Number of comments per app per platform
    
    print("Starting data collection and sentiment analysis...")
    df = collect_comments(apps, platforms, max_results)
    
    # Save raw data
    raw_filename = 'sentiment_analysis_raw.xlsx'
    df.to_excel(raw_filename, index=False)
    print(f"Raw data saved to {raw_filename}")
    
    # Create summary
    summary = df.groupby(['App', 'Platform', 'Sentiment']).size().unstack(fill_value=0)
    summary_filename = 'sentiment_summary.xlsx'
    summary.to_excel(summary_filename)
    print(f"Sentiment summary saved to {summary_filename}")
    
    print("Process completed successfully.")

if __name__ == "__main__":
    main()
