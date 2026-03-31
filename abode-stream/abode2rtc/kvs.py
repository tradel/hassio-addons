import json
from urllib.parse import parse_qs, urlparse
from dataclasses import dataclass

from logger import log


@dataclass
class KVSEndpointData:
    endpoint_url: str
    channel_arn: str
    channel_id: str
    client_id: str
    ice_servers: str


def parse_kvs_response(data: dict, cam_name: str) -> KVSEndpointData:
    endpoint = data['channelEndpoint']
    endpoint_url = urlparse(endpoint)
    endpoint_qs = parse_qs(endpoint_url.query)

    channel_arn = endpoint_qs['X-Amz-ChannelARN'][0]
    log.debug(f"Channel ARN for {cam_name} is {channel_arn}")
    channel_arn = channel_arn.split(':')
    assert channel_arn[0] == 'arn'
    assert channel_arn[1] == 'aws'
    assert channel_arn[2] == 'kinesisvideo'

    channel_parts = channel_arn[-1].split('/')
    assert channel_parts[0] == 'channel'

    channel_id = channel_parts[1]
    client_id = channel_parts[2]
    ice_servers = json.dumps(data['iceServers'])

    return KVSEndpointData(endpoint, channel_arn, channel_id, client_id, ice_servers)
