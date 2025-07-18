
import requests
from django.conf import settings
import hmac
import hashlib
import base64
import json
import time

def get_cashfree_payout_base_url():
    env = getattr(settings, 'CASHFREE_ENV', 'TEST').upper()
    if env == 'PROD':
        return 'https://payout-api.cashfree.com'
    return 'https://payout-gamma.cashfree.com'

def generate_signature(data, secret_key):
    message = json.dumps(data, separators=(',', ':'))
    signature = hmac.new(
        bytes(secret_key, 'utf-8'),
        msg=bytes(message, 'utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode()

def get_cashfree_auth_token():
    base_url = get_cashfree_payout_base_url()
    url = f"{base_url}/payout/v1/authorize"
    client_id = getattr(settings, 'CASHFREE_PAYOUT_CLIENT_ID', '')
    client_secret = getattr(settings, 'CASHFREE_PAYOUT_CLIENT_SECRET', '')
    timestamp = str(int(time.time()))
    sig1, sig2 = generate_cashfree_signature(client_id, client_secret, timestamp)
    # Try with X-Signature and both signature orders
    for signature in [sig1, sig2]:
        headers = {
            "X-Client-Id": client_id,
            "X-Client-Secret": client_secret,
            "X-Signature": signature,
            "X-Timestamp": timestamp
        }
        response = requests.post(url, headers=headers)
        data = response.json()
        if data.get('status') == 'SUCCESS':
            return data.get('data', {}).get('token')
        else:
            print('Cashfree Auth Error:', data)
    return None

def create_cashfree_beneficiary(owner, bank_info):
    # --- DUMMY RESPONSE FOR DEMO ---
    return {'status': 'SUCCESS', 'message': 'Mock beneficiary created (demo mode)'}

def send_payout_to_owner(owner, amount, order_id):
    # --- DUMMY RESPONSE FOR DEMO ---
    return {'status': 'SUCCESS', 'message': 'Mock payout sent (demo mode)'}