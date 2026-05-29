"""Lightweight PayPal REST client.

Only depends on the Python standard library (urllib + json). When
PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET are not configured, the helpers
raise PayPalNotConfigured so callers can degrade gracefully.
"""
from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request

from flask import current_app


SANDBOX_BASE = 'https://api-m.sandbox.paypal.com'
LIVE_BASE = 'https://api-m.paypal.com'


class PayPalNotConfigured(RuntimeError):
    """Raised when PayPal credentials are missing."""


class PayPalError(RuntimeError):
    """Raised on PayPal API failure."""


def _base_url() -> str:
    mode = (current_app.config.get('PAYPAL_MODE') or 'sandbox').lower()
    return LIVE_BASE if mode == 'live' else SANDBOX_BASE


def is_configured() -> bool:
    return bool(
        current_app.config.get('PAYPAL_CLIENT_ID')
        and current_app.config.get('PAYPAL_CLIENT_SECRET')
    )


def _request(method, path, token=None, json_body=None, form_body=None):
    url = _base_url() + path
    headers = {'Accept': 'application/json'}
    data = None
    if json_body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(json_body).encode('utf-8')
    elif form_body is not None:
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        data = urllib.parse.urlencode(form_body).encode('utf-8')

    if token:
        headers['Authorization'] = f'Bearer {token}'
    else:
        cid = current_app.config['PAYPAL_CLIENT_ID']
        sec = current_app.config['PAYPAL_CLIENT_SECRET']
        creds = base64.b64encode(f'{cid}:{sec}'.encode()).decode()
        headers['Authorization'] = f'Basic {creds}'

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = resp.read().decode('utf-8') or '{}'
            return json.loads(payload)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        raise PayPalError(f'PayPal HTTP {e.code}: {body}') from e
    except urllib.error.URLError as e:
        raise PayPalError(f'PayPal network error: {e}') from e


def get_access_token():
    if not is_configured():
        raise PayPalNotConfigured('PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET not set')
    data = _request('POST', '/v1/oauth2/token', form_body={'grant_type': 'client_credentials'})
    return data['access_token']


def create_order(amount, currency, return_url, cancel_url, reference=''):
    token = get_access_token()
    body = {
        'intent': 'CAPTURE',
        'purchase_units': [{
            'reference_id': reference or 'default',
            'amount': {'currency_code': currency, 'value': f'{float(amount):.2f}'},
        }],
        'application_context': {
            'return_url': return_url,
            'cancel_url': cancel_url,
            'shipping_preference': 'NO_SHIPPING',
            'user_action': 'PAY_NOW',
        },
    }
    return _request('POST', '/v2/checkout/orders', token=token, json_body=body)


def capture_order(paypal_order_id):
    token = get_access_token()
    return _request('POST', f'/v2/checkout/orders/{paypal_order_id}/capture',
                    token=token, json_body={})


def approval_link(create_response):
    for link in create_response.get('links', []):
        if link.get('rel') in ('approve', 'payer-action'):
            return link.get('href')
    return None
