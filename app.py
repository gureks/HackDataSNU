from flask import Flask, render_template, session, g, request, redirect, url_for
import pymongo
import json
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient

app = Flask('__name__')
connection = MongoClient()
db = connection['SNU']
app.config['SECRET_KEY']='youcantguessthis'

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	print('login')
	session.pop('user', None)
	user = db['users'].find_one({'username': request.form['username']})
	print(user)
	if user != None and user['password'] == request.form['password']:
		session['user'] = user
		return redirect(url_for('panel'))
	return redirect(url_for('index'))

@app.before_request
def before_request():
	g.user = None
	if 'user' in session:
		g.user = session['user']

@app.route('/logout')
def logout():
	session.pop('user', None)
	return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
	if g.user:
		return render_template('profile.html', user=g.user)
	return redirect(url_for('index'))

@app.route('/panel', methods=['GET', 'POST'])
def panel():
	if g.user:
		scores = db['scores'].find_one({'_id': g.user['_id']})
		prediction = sum(scores['scores'])
		percent = prediction/len(scores['scores'])*100.00

		if (prediction>=0.45*len(scores['scores'])):
			prediction = 1
		else:
			prediction = 0
			percent = 100 - percent

		scores['scores'].append(prediction)
		# plt.figure(figsize=(6, 7))
		# ax = plt.subplot(111)
		# ax.spines['top'].set_visible(False)
		# ax.spines['bottom'].set_visible(False)
		# ax.spines['right'].set_visible(False)
		# ax.spines['left'].set_visible(False)
		# plt.ylim(0, 1.1)
		# plt.xlim(0, 12)
		# plt.xticks(range(11), [str(i+1) + ' day ago' for i in range(11)], rotation=30, fontsize=7)
		# plt.yticks(fontsize=7)
		# plt.tick_params(axis='both', which='both', bottom='off', top='off', labelbottom='on', left='off', right='off', labelleft='on')
		# plt.plot(range(11), scores['scores'])
		# plt.title(g.user['name'] + ' Health status for past 10 days and future prediction.')
		# plt.savefig('static/' + g.user['username'] + '.png')
		# g.user['filename'] = g.user['username'] + '.png'
		return render_template('admin.html', user=g.user, scores=scores, prediction=prediction, percent=percent)
	return redirect(url_for('index'))

@app.route('/graph', methods=['GET', 'POST'])
def graph():
	if g.user:
		scores = db['scores'].find_one({'_id': g.user['_id']})
		prediction = sum(scores['scores'])
		percent = prediction/len(scores['scores'])*100.00

		if (prediction>=0.45*len(scores['scores'])):
			prediction = 1
		else:
			prediction = 0
			percent = 100 - percent

		scores['scores'].append(prediction)
		plt.figure(figsize=(6, 7))
		ax = plt.subplot(111)
		ax.spines['top'].set_visible(False)
		ax.spines['bottom'].set_visible(False)
		ax.spines['right'].set_visible(False)
		ax.spines['left'].set_visible(False)
		plt.ylim(0, 1.1)
		plt.xlim(0, 12)
		plt.xticks(range(11), [str(i+1) + ' day ago' for i in range(11)], rotation=30, fontsize=7)
		plt.yticks(fontsize=7)
		plt.tick_params(axis='both', which='both', bottom='off', top='off', labelbottom='on', left='off', right='off', labelleft='on')
		plt.plot(range(11), scores['scores'])
		plt.title(g.user['name'] + ' Health status for past 10 days and future prediction.')
		plt.savefig('static/' + g.user['username'] + '.png')
		g.user['filename'] = g.user['username'] + '.png'
		return render_template('graph.html', user=g.user, scores=scores, prediction=prediction, percent=percent)
	return redirect(url_for('index'))

@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
	if g.user:
		scores = db['scores'].find_one({'_id': g.user['_id']})
		prediction = sum(scores['scores'])
		percent = prediction/len(scores['scores'])*100.00

		if (prediction>=0.45*len(scores['scores'])):
			prediction = 1
			songs = db.songs.find_one({'mood':'sad'})
		else:
			prediction = 0
			percent = 100 - percent
			songs = db.songs.find_one({'mood':'happy'})

		# songs = songs['songs']

		scores['scores'].append(prediction)
		return render_template('suggestions.html', user=g.user, prediction=prediction, songs=songs)
	return redirect(url_for('index'))

@app.route('/downloaddata')
def downloaddata():
	response = {
			'user': g.user,
			'scores': db['scores'].find_one({'_id': g.user['_id']})
		}
	return json.dumps(response)

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = 8000, debug = True)
