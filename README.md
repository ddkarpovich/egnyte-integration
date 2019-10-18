# Egnyte API integration
## Local usage

Edit `egnyte_app/config.py` with a database settings.

Follow the next steps using console:
1. `python3.7 -m venv .venv/egnyte`
2. `source .venv/egnyte/bin/activate`
3. `pip install -r requirements.txt`
4. `export FLASK_APP=egnyte_app.app`
5. `flask db upgrade`
6. `flask create-user admin admin@admin.com password`
7. `python run.py`
8. Run ngrok under 5000 port - `./ngrok http 5000`
9. Edit `egnyte_app/integration/config.py`, change `EGNYTE_OAUTH_CALLBACK` and `EGNYTE_AUTHORIZE_CALLBACK` settings to match your ngrok URL.

Then:
1. Open your ngrok URL and click on `Login` - enter `admin`/`password` credentials.
2. Click on `Integrate Egnyte`.
3. Use Egnyte login credentials from Slack.
4. Allow access for our app.
5. You should see a success integration message `Egnyte integration successfully added!`.
6. Click on `Events` link at the top.
7. You should see a list of latest events fetched from the Egnyte API - try to upload any file to https://dkarpovich.egnyte.com/ and you should see a new events comming.
