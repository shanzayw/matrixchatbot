from datetime import date
import json
import requests

from cleaninsights import CleanInsights
from cleaninsights.store import Store
from cleaninsights.conf import Configuration

# initalization 
config = Configuration.from_dict({
        "debug": False,
        "persist_every_n_times": 1,
        "server": "metrics.cleaninsights.org",
        "server_side_anon_usage": True,
        "max_retry_delay": 0,
        "site_id": 11,
        "timeout": 10,
        "campaigns": {
            "chatstats": {
                "aggregation_period_length": 3,
                "end": date(30, 12, 22),
                "event_aggregation_rule": "sum",
                "only_record_once": False,
                "start": date(28, 12, 22)
            }
        }
    })

# initialization 
store = Store("memory")
ci = CleanInsights(config, store)


# measuring visit 
ci.measure_visit("/#/room/!KLZJkDkGXKDcfJiNbW:matrix.org", "chatstats")
# https://app.element.io/#/room/!KLZJkDkGXKDcfJiNbW:matrix.org


report = json.dumps({
            "idsite": ci.conf.site_id,
            "visits": ci.store.visits
        }, cls=CleanInsightsEncoder)
print(report)
r = requests.post('https://metrics.cleaninsights.org/cleaninsights.php', data=report)
print(r.content)
r.raise_for_status()