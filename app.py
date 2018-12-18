#! /usr/bin/env python
from flask import request, jsonify, Flask, flash, redirect, render_template, session, abort, url_for
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from app import app,twittclient

from voice_reg import *
from app import db_session,db
from app.models import Pynionquery
from app import db_session
from app.models import Pynionquery

class ReusableForm(Form):
    name = TextField('Subject:', validators=[validators.required()])

@app.route("/", methods=['GET', 'POST'])
def index():
    form = ReusableForm(request.form)

    print (form.errors)
    if request.method == 'POST':
        subject=request.form['name']
        print (subject)

    if form.validate():
# Save the comment here.
        # flash('Your Subject is ' + subject)
        #print("adding to database")
        getOp(subject)
        targetsearch = Pynionquery.query.filter_by(searchword = subject).first()
        print("Search exists {}".format(targetsearch))
        if (targetsearch):
            print("found and updating")
            db.session.query(Pynionquery).filter(Pynionquery.searchword == subject).update({Pynionquery.count: Pynionquery.count+1})
            print("fired update query")
            db.session.commit()
            print("fired commit")

        else:
            print("not found and creating")
            pynionquery = Pynionquery(subject)
            db.session.add(pynionquery)
            db.session.commit()
        return redirect('pynion')
    else:
        flash('To see what the twitterverse current opinion is, on a topic, enter it below')
        return render_template('index.html', form=form)

def getOp(subject):
    ptwee = []
    ntwee = []
    # creating object of TwitterClient Class
    api = twittclient.TwitterClient()
    # print(api)
    # calling function to get tweets
    tweets = api.get_tweets(query = subject, count = 100)
    # print(tweets)
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
    session['pos'] = round(100*len(ptweets)/len(tweets))
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
    session['neg'] = round(100*len(ntweets)/len(tweets))
    # percentage of neutral tweets
    print("Neutral tweets percentage: {} % \
         ".format(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets)))
    session['nue'] = round(100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets))

    # printing first 5 positive tweets
    print("\n\nPositive tweets:")
    for tweet in ptweets[:10]:
        print(tweet['text'])
        ptwee.append(tweet['text'])
    session['ptweet'] = tuple(ptwee)

    # printing first 5 negative tweets
    print("\n\nNegative tweets:")
    for tweet in ntweets[:10]:
        print(tweet['text'])
        ntwee.append(tweet['text'])
    session['ntweet'] = tuple(ntwee)

@app.route("/pynion")
def pynion_matter():
    return render_template('pynion.html')

@app.route("/result")
def test():
    return render_template(
        'result.html')

@app.route("/test")
def test2():
    return render_template(
        'test.html')

@app.route("/history")
def returnHistory():
    return render_template(
        'history.html', history = Pynionquery.query.order_by(Pynionquery.count).all())

# @app.after_request
# def add_header(response):
#     """
#     Add headers to both force latest IE rendering engine or Chrome Frame,
#     and also to cache the rendered page for 10 minutes.
#     """
#     response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
#     response.headers['Cache-Control'] = 'public, max-age=0'
#     return response

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    app.run('0.0.0.0',5000,debug=True)
