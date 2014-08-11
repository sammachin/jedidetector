import cherrypy
import os
from cherrypy.process import servers
import requests
import json
import  urllib


apikey = "XXXXXXXX"
dataset = "QS210EW" 


def fake_wait_for_occupied_port(host, port): 
	return

servers.wait_for_occupied_port = fake_wait_for_occupied_port


class start(object):
	def index(self):
		f = open('static/index.html')
		page = f.read()
		f.close()
		cherrypy.response.headers['Content-Type']= 'text/html' 
		return page
	def css(self):
		f = open('static/style.css')
		page = f.read()
		f.close()
		cherrypy.response.headers['Content-Type']= 'text/css' 
		return page
	def lookup(self, var=None, **params):
		# get the geography code from lat long
		lat = urllib.unquote(cherrypy.request.params['lat'])
		lng = urllib.unquote(cherrypy.request.params['lng'])
		ll = str(lat)+","+str(lng)
		url = "http://uk-postcodes.com/latlng/"+ll+".json"
		r = requests.get(url)
		data = json.loads(r.text)
		geog_code = data['administrative']['ward']['code']
		# get the data from ONS
		baseurl = "http://data.ons.gov.uk/ons/api/data/dataset/"
		payload = {'apikey': apikey, 'context': 'Census', 'geog' : '2011WARDH', 'dm/2011WARDH' : geog_code, 'totals' : 'false', 'jsontype' : 'json-stat' }
		r = requests.get(baseurl+"/"+dataset+".json", params=payload)
		obj = json.loads(r.text)
		data = {}
		values  =  obj[dataset]['value']
		index = obj[dataset]['dimension'][obj[dataset]['dimension']['id'][1]]['category']['index']
		labels = obj[dataset]['dimension'][obj[dataset]['dimension']['id'][1]]['category']['label']
		for l in labels:
			num = index[l]
			count = values[str(num)]
			data[labels[l]] = count
		jedi = data['No religion: Jedi Knight']
		total = data['All categories: Religion']
		rat = float(jedi)/float(total)
		ewrat = "0.0031498729793284505"
		resp = {}
		resp['local_ratio'] = rat
		resp['national_ratio'] = ewrat
		resp['pixels'] = int(rat * 47620)
		cherrypy.response.headers['Content-Type']= 'text/json' 
		return json.dumps(resp)
	css.exposed = True
	index.exposed = True
	lookup.exposed = True

cherrypy.config.update({'server.socket_host': '0.0.0.0',})
cherrypy.config.update({'server.socket_port': int(os.environ.get('PORT', '5000')),})
cherrypy.quickstart(start())