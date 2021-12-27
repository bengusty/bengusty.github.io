import json

import requests
from flask import Flask, request, Response, make_response

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/exchange_token')
def exchange_token():
    code = request.args.get("code")
    scope = request.args.get("scope")
    expected_scope = "read,activity:read"

    if not scope == expected_scope:
        resp = make_response("The 'View data about your activities' checkbox must be checked in order to use the app", 400)
        return resp

    data = {"client_id": 6003, "client_secret": "0a3e2238fba9cae0d5a28dc1e58c0b2ef207c902", "code": code,
            "grant_type": "authorization_code"}
    response = requests.post("https://www.strava.com/oauth/token", data=data)
    response_data = json.loads(response.text)
    # refresh_token = response_data.get("refresh_token")
    access_token = response_data.get("access_token")

    activities_resp = requests.get("https://www.strava.com/api/v3/athlete/activities?per_page=100&scope={}".format(scope),
                                   headers={"Authorization": "Bearer {}".format(access_token)})

    if activities_resp.status_code != 200:
        resp = make_response("Bad request", 400)
        return resp

    activities = json.loads(activities_resp.text)
    activities_info = [{"id": activity.get("id"),
                        "distance": round(activity.get("distance") / 1609.344, 2),
                        "elevation": int(activity.get("total_elevation_gain") * 3.28084),
                        "name": activity.get("name"),
                        "date": activity.get("start_date_local")} for activity in activities]

    return make_response(str(activities_info))


if __name__ == '__main__':
    app.run()
