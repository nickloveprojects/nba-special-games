import logging
import time

import requests

log = logging.getLogger("nba")
UA = "nba-special-games/1.0 (personal project; contact: set-your-email@example.com)"


class SourceError(RuntimeError):
    """A data source failed after retries. The pipeline degrades instead of crashing."""


class NotFound(SourceError):
    """The source has no record for this item (HTTP 404). Not worth retrying."""


def get_json(url, params=None, headers=None, retries=4, timeout=40):
    h = {"User-Agent": UA, **(headers or {})}
    last = None
    for i in range(retries):
        try:
            r = requests.get(url, params=params, headers=h, timeout=timeout)
            if r.status_code == 429:
                time.sleep(10 * (i + 1))
                raise SourceError("rate limited (429)")
            if r.status_code == 404:
                raise NotFound(f"{url}: not found")
            r.raise_for_status()
            return r.json()
        except NotFound:
            raise
        except Exception as e:  # noqa: BLE001
            last = e
            log.warning("GET %s failed (%s/%s): %s", url, i + 1, retries, e)
            time.sleep(2 ** i)
    raise SourceError(f"{url}: {last}")
