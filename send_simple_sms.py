from twilio.rest import TwilioRestClient

account_sid = "AC7baad23321d71c42448deb02c3cb31ae"
auth_token = "4c35e0337dc3963f457d477c8a59996f"
client = TwilioRestClient(account_sid, auth_token)

message = client.messages.create(to="+17023284071", from_="+13342474764", body="Hey idiot")
