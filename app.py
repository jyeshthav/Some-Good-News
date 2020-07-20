from flask import Flask, render_template, url_for, request, redirect
from newsapi import NewsApiClient
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import operations

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
db = SQLAlchemy(app)

class Master(db.Model):
    title = db.Column(db.String(2000), primary_key=True)
    content = db.Column(db.String(5000))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String(5000))
    img_url = db.Column(db.String(5000))
    desc = db.Column(db.String(5000))
    read = db.Column(db.String(5000))

    def __repr__(self):
        return '<Article %r>' % self.title

class sgn(db.Model):
    title = db.Column(db.String(2000), primary_key=True)
    content = db.Column(db.String(5000))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String(5000))
    img_url = db.Column(db.String(5000))
    desc = db.Column(db.String(5000))
    read = db.Column(db.String(5000))

    def __repr__(self):
        return '<Happy Article %r>' % self.title

def get_api():
    file = open('api.txt', 'r')
    return file.read()

def call(all_articles):

    # Function retrieves news articles from the web through API call, 
    # formats a bit, inserts into Master table and passes to context.

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
        db_desc = art['description']

        img.append(art['urlToImage'])
        db_img_url = art['urlToImage']

        url.append(art['url'])
        db_url = art['url']

        if art['content']:     
            ind = art['content'].find('[+')
            if ind > 0:
                rm.append(art['content'][ind:])
                db_rm = art['content'][ind:]
                art['content'] = art['content'][:ind]
                con.append(art['content'])
                db_content = art['content']
            else:
                db_content = ' '
                db_rm = ' '
                con.append(' ')
                rm.append(' ')
        else:
            db_content = ' '
            db_rm = ' '
            con.append(' ')
            rm.append(' ')
        
        if art['publishedAt']:
            db_date_created = datetime.strptime(art['publishedAt'][:19], '%Y-%m-%dT%H:%M:%S')
            pub.append(db_date_created)
        else:
            db_date_created = datetime.datetime.utcnow
            pub.append(' ')

        new_article = Master(title=db_news, content=db_content, date_created=db_date_created, url=db_url, img_url=db_img_url, desc=db_desc, read=db_rm)
        db.session.merge(new_article)
        db.session.commit()
    
    ziplist = zip(news, desc, img, con, rm, url, pub)
    return ziplist

@app.route('/', methods=['POST', 'GET'])
def index():
    
    # Function in the operations module that fetches from master, filters* and puts into sgn. 
    # Then query sgn from flask app and display in template
    # Uncomment after model is added
    
    # operations.endpoints()
    # sgn_articles = sgn.query.order_by(sgn.date_created.desc()).all()
    return render_template('index.html')

@app.route('/cache', methods=['POST', 'GET'])
def cache():
    articles = Master.query.order_by(Master.date_created.desc()).all()
    return render_template('cache.html', context=articles)

@app.route('/clear', methods=['POST', 'GET'])
def clear():
    if request.method == 'GET':
        tab = request.args['table_name']
        if tab == '/cache':
            table = Master
            ret = 'cache'
        if tab =='/':
            table = sgn
            ret = 'index'
    
    articles = table.query.all()
    today = datetime.now()
    for art in articles:
        if art.date_created < today-timedelta(hours=24):
            db.session.delete(art)
    db.session.commit()
    return redirect(url_for(ret))

@app.route('/source/<choice>', methods=['POST', 'GET'])
def source(choice):
    dictionary = {
        'BBC': 'bbc-news',
        'ABC': 'abc-news',
    }
    src = dictionary[choice]
    newsapi = NewsApiClient(api_key=get_api())
    headlines = newsapi.get_top_headlines(sources=src)
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
    ziplist = call(all_articles)
 
    return render_template('news.html', context=ziplist)

@app.route('/query', methods=['POST', 'GET'])
def query():
    if request.method == 'POST':
        keyword = request.form['keyword']
        url = ('https://newsapi.org/v2/top-headlines?q=' + keyword + '&language=en&apiKey=' + get_api())
        response = requests.get(url).json()
        all_articles = response["articles"]
        ziplist = call(all_articles)
    
        return render_template('news.html', context=ziplist)

if __name__ == '__main__':
    app.run(debug=True)