from datetime import datetime, timezone
import hmac
import hashlib
from urllib.parse import quote, urlencode
import asyncio
import websockets
import hmac
import hashlib
import pyaudio
from urllib.parse import quote_plus, urlencode
from botocore.credentials import Credentials
import datetime
# AWS credentials and region
import boto3
session = boto3.Session(
    aws_access_key_id='AKIAZQ3DUFIK26LNH35Z',
    aws_secret_access_key='Q/D+obwgwG2ProirfC5QAMBr7OZ5pmR8etMM8JuD',
    region_name='us-west-2'  # or your preferred region
)

print(session.token)