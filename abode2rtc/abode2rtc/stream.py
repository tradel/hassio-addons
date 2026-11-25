#! /usr/bin/env python3

import sys

from abode import AbodeApiClient
from kvs import parse_kvs_response


abode_conf = sys.argv[1]
cam_id = sys.argv[2]

# Reuse the session spawn.py saved (and keeps refreshed). Only log in again if
# Abode rejects it: every login sends the account owner a sign-in email.
with AbodeApiClient.load(abode_conf) as abode:
    data = abode.get_kvs_stream(cam_id)
    if data is None:  # camera offline; a fresh login wouldn't help
        sys.exit(1)
    try:
        kvs = parse_kvs_response(data, cam_id)
    except (KeyError, TypeError):  # session rejected: log in once and save it
        abode.login()
        abode.save(abode_conf)
        kvs = parse_kvs_response(abode.get_kvs_stream(cam_id), cam_id)

print(f"webrtc:{kvs.endpoint_url}"
      "#format=kinesis"
      f"#client_id={kvs.client_id}"
      f"#ice_servers={kvs.ice_servers}")

sys.exit(0)
