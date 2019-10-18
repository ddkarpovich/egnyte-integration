from flask import render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required

from egnyte_app.app import app, db
from egnyte_app.integration import config
from egnyte_app.integration.models import EgnyteIntegration
from egnyte_app.integration.exceptions import TokenExchangeFailed
from egnyte_app.integration.service import (
    EgnyteEventsAPI, get_authorize_url,
    exchange_code, get_user_info
)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/authorize')
@login_required
def egnyte_app_authorize():
    authorize_url = get_authorize_url()
    return redirect(authorize_url)


@app.route('/return')
@login_required
def egnyte_app_return():
    data = request.args
    error = data.get('error')
    if error:
        if error == 'access_denied':
            flash('You should accept our app to proceed with integration')
        else:
            flash(f'An error occured while processing integration - {error}')
        return redirect(url_for('home'))

    try:
        # Exchange OAuth code for a access token
        access_token, expires_in = exchange_code(data.get('code'))
    except TokenExchangeFailed:
        flash('Something went wrong during Egnyte authorization')
        return redirect(url_for('home'))

    user = get_user_info(access_token)
    if user.get('user_type') != 'admin':
        flash(f'Can not process Egnyte integration - admin user type is required.')
        return redirect(url_for('home'))

    integration = current_user.egnyte_integration
    if integration is None:
        integration = EgnyteIntegration(
            user=current_user,
            access_token=access_token,
            expires_in=expires_in
        )
    else:
        integration.access_token = access_token
        integration.expires_in = expires_in

    db.session.add(integration)
    db.session.commit()

    flash('Egnyte integration successfully added!')
    return redirect(url_for('home'))


@app.route('/events')
@login_required
def process_events():
    integration = current_user.egnyte_integration

    events = EgnyteEventsAPI(domain=config.EGNYTE_DOMAIN, access_token=integration.access_token)

    if integration.latest_event_id is None:
        start_id = events.oldest_event_id
    else:
        start_id = integration.latest_event_id

    events = events.fetch(start_id)

    for event in events.get('events', {}):
        flash(f"[{event['type']}] {event['object_detail']}")

    return redirect(url_for('home'))
