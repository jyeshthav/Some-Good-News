import sqlite3
import pandas as pd

def sentimental_model():
    pass

def endpoints():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()

    def read_from_master():
        c.execute('SELECT * FROM master LIMIT 20')
        all_articles = c.fetchall()
        return all_articles

    all_articles = read_from_master()

    features = ['Title', 'Content', 'Date Created', 'News URL', 'Image URL', 'Description', 'Extra chars']
    df = pd.DataFrame(all_articles, columns=features)
    df.loc[df['Content'] == ' ', 'Content'] = df['Description']

    def insert_into_sgn(df):
        for i, article in df.iterrows():
            query = "INSERT OR REPLACE INTO sgn VALUES (?, ?, ?, ?, ?, ?, ?)"
            c.execute(query, tuple(article))
        conn.commit()

    insert_into_sgn(df)
    c.close()
    conn.close()


