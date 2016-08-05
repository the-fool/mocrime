import sys, os

from database_setup import Base, Criminal, Citation, Violation, User
from sqlalchemy import create_engine, func, funcfilter, or_, and_
from sqlalchemy.orm import sessionmaker
from re import split
import cgi
from urlparse import urlparse
from flask import Flask
from flask import request, render_template, redirect, url_for
from telephony import *

INTERP = os.path.expanduser("/home/thorub2/MOcrime.thomasruble.com/env/bin/python")
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

application = Flask(__name__)

engine = create_engine('mysql://steveballmer:developers@crimelab.mocrime.thomasruble.com:3306/mocrime')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@application.context_processor
def utility_processor():
    return dict(str=str)

@application.route('/')
@application.route('/index/')
def index():
    return render_template('index.html')

@application.route('/newcriminal/', methods=['GET', 'POST'])
def newCriminal():
    if request.method == 'POST':
        name = request.form['name']
	infraction = request.form['infraction']
        if name:
            newCriminal = Criminal(name=name, infraction=infraction)
            session.add(newCriminal)
            session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('newCriminal.html')

@application.route('/data/', methods=['GET', 'POST'])
def displayData():
    if request.method == 'GET':
        citations = session.query(Citation).all()
        return render_template('displaydata.html', citations=citations)

@application.route('/text/', methods=['POST'])
def send_sms():
    if request.method == 'POST':
        msg = request.form['message']
        client.messages.create(to="+17023284071", from_="+13342474764", body=msg)
        return redirect(url_for('index'))

@application.route('/twilio/', methods=['POST', 'GET'])
def receiveTwilio():
     if request.method == 'POST':
        msg = request.values.get('Body')
        from_number = request.values.get('From', None)
        resp = twilio.twiml.Response()
        resp.message(parseText(msg))
        return str(resp)

@application.route('/ticket_info/')
def ticketInfo():
    return render_template('ticket_info.html')

@application.route('/warrants_info/')
def warrantsInfo():
    return render_template('warrants_info.html')

@application.route('/more_info/')
def moreInfo():
    return render_template('more_info.html')

@application.route('/submit/', methods=['POST', 'GET'])
def submitInfo():
    if request.method == 'POST':
        first_name = request.values.get('FirstName')
        last_name = request.values.get('LastName')
        license_number = request.values.get('License')
        phone = request.values.get('Phone')

        if license_number:
            q = session.query(Citation).filter(Citation.drivers_license_number.like(license_number))
            license_entries = q.all()
        q = session.query(Citation).filter_by((Citation.last_name.like("%%%s%%" % (last_name)) & Citation.first_name.like("%%%s%%" % (first_name))))
        name_entries = q.all()

@application.route('/admin/')
def admin():
    return render_template('admin.html')

@application.route('/<name>/display_info/')
def displayInfo(name):
    n = split('_', name)
    v = []
    q = session.query(Citation).filter(and_(Citation.first_name.like(n[0]), Citation.last_name.like(n[1])))
    e = q.all()
    for i in range(len(e)):
        q = session.query(Violation).filter(Violation.citation_number.like(e[i].citation_number))
        entries = q.all()
        for j in entries:
            v.append(j)


    return render_template('output.html', violations=v)



def parseText(msg):
    if isLicense(msg):
        return parseLicense(msg)
    msg.lower()
    return parseName(msg)

def isLicense(s):
    return any(char.isdigit() for char in s)

def parseLicense(lic):
    lic.lower()
    q = session.query(Citation).filter((Citation.drivers_license_number.like(lic)))
    entries = q.all()
    if not entries:
        return "You are clean"
    else:
        return "You've got a record"

def parseName(name):
    m = name.split()
    if len(m) < 2:
        return badMessage()
    else:
        q = session.query(Citation).filter((Citation.last_name.like("%%%s%%" % (m[len(m)-1]))) & Citation.first_name.like("%%%s%%" % (m[0])))
        entries = q.all()
        if not entries:
            return "You're clean"
        elif len(entries) > 1:
            lic = entries[0].drivers_license_number
            if lic:
                for i in range(len(entries[1:])):
                    if lic and lic != entries[i].drivers_license_number:
                        return duplicateName(entries[0].id)
            else:
                dob = entries[0].date_of_birth
                for i in range(len(entries[1:])):
                    if dob != entries[i].date_of_birth:
                        return duplicateName(entries[0].id)
        return getRecord(entries[0])



def duplicateName(id):
    return "Duplicate name"

def badMessage():
    return "usage: <first_name last_name> || <license_number>"

def getRecord(cit):
    q = session.query(Violation).filter_by(citation_number=cit.citation_number)
    entries = q.all()
    if not entries:
        return "You have a citation, but no violation"
    msg = "You are a violator.  You're violations are: "
    for i in entries:
        msg += i.violation_description + ". "
    return msg
#m = sys.argv[1]
#print m
#parseText(m)
