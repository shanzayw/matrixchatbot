from datetime import date
import json
import requests

from cleaninsights import CleanInsights
from cleaninsights.store.memory import MemoryStore
from cleaninsights.conf import Configuration

# initalization 
config = Configuration.from_dict({
        "debug": False,
        "persist_every_n_times": 1,
        "server": "metrics.cleaninsights.org",
        "server_side_anon_usage": True,
        "max_retry_delay": 0,
        "site_id": 26,
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
store = MemoryStore()
#store = Store("memory")
ci = CleanInsights(config, store)


# measuring visit 
ci.measure_visit("app.element.io/#/room/!KLZJkDkGXKDcfJiNbW:matrix.org", "chatstats")
# https://app.element.io/#/room/!KLZJkDkGXKDcfJiNbW:matrix.org

# add an additional call to measure_view --> like everytime it gets a chat
# message 
# fidn wherever its getting the loop of incomign messages from matrix 
# and that is where you need to (in main.py) --> you can see send message
# maybe add a view --> async def message_cb(room, event):
# log measure_view for --> user_name = room.user_name(event.sender)
# logging how many messages does thic chatbot reiceve everyday 
# log using measure_view call with that linke --> user_name = room.user_name(event.sender)





report = json.dumps({
            "idsite": ci.conf.site_id,
            "visits": ci.store.visits
        }, cls=CleanInsightsEncoder)
print(report)
r = requests.post('https://metrics.cleaninsights.org/cleaninsights.php', data=report)
print(r.content)
r.raise_for_status()