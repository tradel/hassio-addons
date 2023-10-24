import os 
import sys 
import tempfile

import requests
import jsonpath

from logger import log 

GO2RTC_REPO = 'AlexxIT/go2rtc'
GO2RTC_BIN = 'go2rtc_linux_amd64'


def download_go2rtc() -> str:
    """
    Downloads the most recent copy of go2rtc for our platform, from the project's
    releases page on Github.
    """
    # Get the list of releases for the go2rtc project:
    response = requests.get(f'https://api.github.com/repos/{GO2RTC_REPO}/releases')
    response.raise_for_status()
    data = response.json()

    # Find the first release that is not a draft or prerelease:
    releases = jsonpath.findall("$[?(@.draft==false && @.prerelease==false)]", data)
    if len(releases) == 0:
        raise Exception(f"No releases found on Github for project {GO2RTC_REPO}")
    log.info(f"Current release of go2rtc is {releases[0]['tag_name']}")

    # Now that we have the most recent release, find the asset for our platform:
    assets = jsonpath.findall(f"$.assets[?(@.name=='{GO2RTC_BIN}')]", releases[0])
    if len(assets) == 0:
        raise Exception(f"No {GO2RTC_BIN} binary found for {GO2RTC_REPO}")
    asset_url = assets[0]['url']

    # Download the asset to a temporary location and make it executable:    
    log.info(f"Downloading version {releases[0]['tag_name']} of {GO2RTC_BIN} from {asset_url}")
    response = requests.get(asset_url, stream=True, headers={"Accept": assets[0]["content_type"]})
    with tempfile.NamedTemporaryFile('wb', delete=False) as f:
        for chunk in response.iter_content(chunk_size=16384):
            f.write(chunk)
        os.chmod(f.name, 0o0755)
        return f.name


def find_in_path(filename: str, matchFunc=os.path.isfile) -> str:
    """
    Finds a file in the system path, set via the PATH environment variable.
    """
    sys.path.insert(0, '/usr/local/bin')
    for dirname in sys.path:
        candidate = os.path.join(dirname, filename)
        if matchFunc(candidate):
            return candidate
    return None


def find_or_download() -> str:
    log.info("Searching for go2rtc binary in system path")
    log.debug(f"Searching for go2rtc in {sys.path}")
    go2rtc_path = find_in_path('go2rtc')
    if not go2rtc_path:
        log.warning("go2rtc not found in system path, downloading a fresh copy")
        go2rtc_path = download_go2rtc()
    log.info(f"Found go2rtc in {go2rtc_path}")
    return go2rtc_path

