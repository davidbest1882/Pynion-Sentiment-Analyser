#! /usr/bin/env python
from flask import request, jsonify, Flask, flash, redirect, render_template, session, abort, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from app import app,twittclient

from voice_reg import *
from app.models import Pynionquery
from app import db_session
from app.models import Pynionquery

app.debug = True

class ReusableForm(Form):
    name = TextField('Subject:', default="")

@app.route("/", methods=['GET', 'POST'])
def index():
    form = ReusableForm(request.form)
    if request.method == 'POST':
        subject=request.form['name']
        # print(subject)
        subject = subject.strip()
        if (len(subject) == 0):
            subject = '@makersacademy'

        if 'Text' in request.form:
            if form.validate():
                if subject == "":
                    return redirect('/')
                getOp(subject)
                databaseOperations(subject)
                return redirect('pynion')
        elif 'Voice' in request.form:
            subject = mymain()
            getOp(subject)
            databaseOperations(subject)
            return redirect('pynion')
    else:
        flash('To analyse the sentiments of Twitter-verse on a topic, please enter it below')
        return render_template('index.html', form=form,history = Pynionquery.query.order_by(Pynionquery.count.desc()).all()[:5])

def databaseOperations(subject):
    targetsearch = Pynionquery.query.filter_by(searchword = subject).first()
    if (targetsearch):
        print("found and updating")
        db_session.query(Pynionquery).filter(Pynionquery.searchword == subject).update({Pynionquery.count: Pynionquery.count+1})
    else:
        print("db file initialised....")
        pynionquery = Pynionquery(subject)
        db_session.add(pynionquery)
    db_session.commit()

def getOp(subject):
    ptwee = []
    ntwee = []
    # creating object of TwitterClient Class
    api = twittclient.TwitterClient()
    # calling function to get tweets

    session['searchtext'] = subject
    tweets = api.get_tweets(query = subject.strip(), count = 500)
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    # print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
    if len(tweets) > 0:
        session['pos'] = round(100*len(ptweets)/len(tweets))
    else:
        session['pos'] = 0
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    # print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
    if len(tweets) > 0:
        session['neg'] = round(100*len(ntweets)/len(tweets))
    # percentage of neutral tweets
    # print("Neutral tweets percentage: {} % \
        #  ".format(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets)))
        session['nue'] = round(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets))
    else:
        session['neg'] = 0
        session['nue'] = 0
    # printing first 5 positive tweets
    # print("\n\nPositive tweets:")
    for tweet in ptweets[:20]:
        # print(tweet['text'])
        ptwee.append(tweet['text'])
    session['ptweet'] = tuple(ptwee)

    # printing first 5 negative tweets
    # print("\n\nNegative tweets:")
    for tweet in ntweets[:20]:
        # print(tweet['text'])
        ntwee.append(tweet['text'])
    session['ntweet'] = tuple(ntwee)

@app.route("/pynion")
def pynion_matter():
    return render_template('pynion.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/history")
def returnHistory():
    return render_template(
        #'history.html', history = Pynionquery.query.order_by(Pynionquery.count).limit(3).all())
        'history.html', history = Pynionquery.query.order_by(Pynionquery.count.desc()).all()[:5])

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    app.run('0.0.0.0',5000,debug=True)
