from flask import Flask, request, redirect
import twilio.twiml

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def send_sms():
	resp = twilio.twiml.Response()
	resp.message("Hello Monkey")
	return str(resp)

if __name__ == "__main__": 	#I don't know what to put here
	app.run(debug=True)	#I figure it has something to do
				#with flask. -Andrew

