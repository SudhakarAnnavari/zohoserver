from flask import Flask, json, request, jsonify
from oauthlib.oauth2 import WebApplicationClient
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

# Configuration
CLIENT_ID = '529326706888-8h1r3o9o1e88pitbkj3s4l30ib86fk08.apps.googleusercontent.com'
CLIENT_SECRET = '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'  # You need to get your client secret from Google Developer Console
REDIRECT_URI = 'http://localhost:3000'  # Should match the redirect URI in your Google Developer Console
TOKEN_URL = 'https://oauth2.googleapis.com/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/auth'
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# OAuth Client
client = WebApplicationClient(CLIENT_ID)

import psycopg2

DATABASE_NAME = 'stag_airlines_db'
DATABASE_USER = 'airlinedb_user'
DATABASE_PASSWORD = 'AVNS_SFBbzpFCBpvhgbI5M1T'
DATABASE_HOST = 'ec2-65-1-12-129.ap-south-1.compute.amazonaws.com'

# DATABASE_NAME = 'airlines_db'
# DATABASE_USER = 'airlinedb_user'
# DATABASE_PASSWORD = 'AVNS_SFBbzpFCBpvhgbI5M1T'
# DATABASE_HOST = 'ec2-65-1-12-129.ap-south-1.compute.amazonaws.com'

def connect_to_db():
    conn = psycopg2.connect(
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST
    )
    return conn

def get_tokens(code):
    token_url, headers, body = client.prepare_token_request(
        TOKEN_URL,
        redirect_url=REDIRECT_URI,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    client.parse_request_body_response(token_response.text)
    access_token = client.token['access_token']
    print("access_token",access_token)
    refresh_token = client.token['refresh_token']
    print("refresh_token",refresh_token)
    return access_token, refresh_token

@app.route('/callback', methods=['POST'])
def callback():
    code = request.json.get('code')
    access_token, refresh_token = get_tokens(code)

    # Get user data from the request
    name = request.json.get('name')
    email = request.json.get('email')

    # Convert JSON data to string format
    jsondata = json.dumps({"token": access_token, "refresh_token": refresh_token, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET})

    # Connect to the database
    conn = connect_to_db()
    cur = conn.cursor()

    # Insert user data and tokens into the database
    cur.execute("INSERT INTO zoho_users (name, email, json_token) VALUES (%s, %s, %s)",
                (name, email, jsondata))
    conn.commit()

    # Close the cursor and connection
    cur.close()
    conn.close()

    return jsonify({'success':True})

if __name__ == '__main__':
    app.run(debug=True)
