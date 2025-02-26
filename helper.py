from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    num_messages = df.shape[0]
    words = [word for message in df['message'].dropna() for word in message.split()]
    num_media_messages = df[df['message'].str.strip() == '<Media omitted>'].shape[0]
    links = [url for message in df['message'].dropna() for url in extract.find_urls(message)]
    
    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    percent_df = df['user'].value_counts(normalize=True).mul(100).reset_index()
    percent_df.columns = ['name', 'percent']
    return x, percent_df

def create_wordcloud(selected_user, df):
    try:
        with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
            stop_words = set(f.read().split())

        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        temp = df[(df['user'] != 'group_notification') & (df['message'].str.strip() != '<Media omitted>')]

        temp['message'] = temp['message'].astype(str).apply(lambda msg: " ".join([word for word in msg.lower().split() if word not in stop_words]))
        
        temp = temp[temp['message'].str.strip() != ""]

        if temp.empty:
            return None  # Avoid generating an empty word cloud

        wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
        return wc.generate(temp['message'].str.cat(sep=" "))

    except Exception as e:
        print(f"Error in create_wordcloud: {e}")
        return None

def most_common_words(selected_user, df):
    try:
        with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
            stop_words = set(f.read().split())

        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        temp = df[(df['user'] != 'group_notification') & (df['message'].str.strip() != '<Media omitted>')]
        temp = temp.dropna(subset=['message'])

        words = [word for message in temp['message'].astype(str) for word in message.lower().split() if word not in stop_words]
        
        return pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])

    except Exception as e:
        print(f"Error in most_common_words: {e}")
        return pd.DataFrame(columns=['word', 'count'])

def emoji_helper(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        emojis = [char for message in df['message'].dropna() for char in message if char in emoji.EMOJI_DATA]

        return pd.DataFrame(Counter(emojis).most_common(), columns=['emoji', 'count']) if emojis else pd.DataFrame(columns=['emoji', 'count'])

    except Exception as e:
        print(f"Error in emoji_helper: {e}")
        return pd.DataFrame(columns=['emoji', 'count'])

def monthly_timeline(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        if df.empty:
            return pd.DataFrame(columns=['time', 'message'])

        timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
        timeline['time'] = timeline['month'] + '-' + timeline['year'].astype(str)

        return timeline

    except Exception as e:
        print(f"Error in monthly_timeline: {e}")
        return pd.DataFrame(columns=['time', 'message'])

def daily_timeline(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        if df.empty:
            return pd.DataFrame(columns=['only_date', 'message'])

        df['only_date'] = pd.to_datetime(df['only_date'], errors='coerce')
        return df.groupby('only_date').count()['message'].reset_index()

    except Exception as e:
        print(f"Error in daily_timeline: {e}")
        return pd.DataFrame(columns=['only_date', 'message'])

def week_activity_map(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        return df['day_name'].value_counts() if not df.empty else pd.Series(dtype='int')

    except Exception as e:
        print(f"Error in week_activity_map: {e}")
        return pd.Series(dtype='int')

def month_activity_map(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        return df['month'].value_counts() if not df.empty else pd.Series(dtype='int')

    except Exception as e:
        print(f"Error in month_activity_map: {e}")
        return pd.Series(dtype='int')

def activity_heatmap(selected_user, df):
    try:
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]

        if df.empty:
            return pd.DataFrame()

        return df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    except Exception as e:
        print(f"Error in activity_heatmap: {e}")
        return pd.DataFrame()
