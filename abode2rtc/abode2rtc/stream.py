#! /usr/bin/env python3

import sys

from abode import AbodeApiClient
from kvs import parse_kvs_response


abode_conf = sys.argv[1]
cam_id = sys.argv[2]

with AbodeApiClient.load(abode_conf) as abode:
    abode.login()
    kvs_data = abode.get_kvs_stream(cam_id)
    kvs = parse_kvs_response(kvs_data, cam_id)

print(f"webrtc:{kvs.endpoint_url}"
      "#format=kinesis"
      f"#client_id={kvs.client_id}"
      f"#ice_servers={kvs.ice_servers}")

sys.exit(0)
