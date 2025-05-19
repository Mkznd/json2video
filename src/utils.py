import tempfile

import requests


def download_file(url):
    r = requests.get(url)
    r.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(r.content)
    tmp.close()
    return tmp.name
