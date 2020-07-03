from flask import Flask, render_template, url_for, request
from newsapi import NewsApiClient
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
db = SQLAlchemy(app)

class News(db.Model):
    title = db.Column(db.String(2000), primary_key=True)
    content = db.Column(db.String(5000))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String(5000))
    img_url = db.Column(db.String(5000))

    def __repr__(self):
        return '<Article %r>' % self.title

def clear_cache():
    articles = News.query.all()
    length = len(articles)
    if length > 50:
        xs = length - 50
        to_delete = News.query.order_by(News.date_created.asc()).limit(xs).all()
        for task in to_delete:
            db.session.delete(task)
            db.session.commit()
    length = len(News.query.all())
    return News.query.all()

def call(all_articles):
    img = []
    news = []
    desc = []
    con = []
    url = []
    pub = []
    rm = []
    for i in range(len(all_articles)):
        art = all_articles[i]
        
        news.append(art['title'])
        db_news = art['title']
        
        desc.append(art['description'])

        img.append(art['urlToImage'])
        db_img_url = art['urlToImage']

        url.append(art['url'])
        db_url = art['url']

        if art['content']:     
            ind = art['content'].find('[+')
            if ind:
                rm.append(art['content'][ind:])
                art['content'] = art['content'][:ind]
                con.append(art['content'])
                db_content = art['content']
            else:
                rm.append(' ')
                con.append(art['content'])
                db_content = art['content']
        else:
            db_content = ' '
            con.append(' ')
            rm.append(' ')
        
        if art['publishedAt']:
            db_date_created = datetime.strptime(art['publishedAt'][:19], '%Y-%m-%dT%H:%M:%S')
            pub.append(db_date_created)
        else:
            db_date_created = datetime.datetime.utcnow
            pub.append(' ')

        new_article = News(title=db_news, content=db_content, date_created=db_date_created, url=db_url, img_url=db_img_url)
        db.session.merge(new_article)
        db.session.commit()
    

    mylist = zip(news, desc, img, con, rm, url, pub)
    return mylist

def get_api():
    file = open('api.txt', 'r')
    return file.read()

@app.route('/', methods=['POST', 'GET'])
def index():
    articles = News.query.order_by(News.date_created.desc()).all()
    return render_template('index.html', context=articles)

@app.route('/bbc', methods=['POST', 'GET'])
def bbc():
    newsapi = NewsApiClient(api_key=get_api())
    headlines = newsapi.get_top_headlines(sources='bbc-news')
    articles = headlines['articles']
    mylist = call(articles)
 
    return render_template('news.html', context=mylist)

@app.route('/all', methods=['POST', 'GET'])
def all():
    url = ('http://newsapi.org/v2/top-headlines?'
        'language=en&'
        'apiKey=' + get_api())
    response = requests.get(url).json()
    all_articles = response["articles"]
    mylist = call(all_articles)
 
    return render_template('news.html', context=mylist)

@app.route('/query', methods=['POST', 'GET'])
def query():
    if request.method == 'POST':
        keyword = request.form['keyword']
        url = ('https://newsapi.org/v2/top-headlines?q=' + keyword + '&language=en&apiKey=' + get_api())
        response = requests.get(url).json()
        all_articles = response["articles"]
        mylist = call(all_articles)
    
        return render_template('news.html', context=mylist)

if __name__ == '__main__':
    app.run(debug=True)
