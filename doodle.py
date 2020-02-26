"""
Python wrapper for the Doodle API
GET, no POST
"""
from datetime import datetime, timedelta, timezone
import json
import urllib.parse
import requests

import pytz
from pprint import pprint

class Doodle:
    """Connect with Doodle"""

    def __init__(self, url=None, poll_id=None):
        assert url or poll_id
        if not poll_id:
            parsed = urllib.parse.urlparse(url)
            poll_id = parsed.path.replace('/', '').replace('poll', '')
        self.base_url = f"https://doodle.com/api/v2.0/polls/{poll_id}?adminKey=&participantKey="
        self.url = url if url else f"https://doodle.com/poll/{poll_id}"
        self.json_file = None
        self.update()
        tz = self.json_file['initiator'].get('timeZone')
        self.timezone = pytz.timezone(tz) if tz else timezone(timedelta(hours=-12))  # todo



    def update(self, url: str=None):
        """Send a request to Doodle"""
        if not url:
            url = self.base_url
        req = requests.request('get', url)
        if req.status_code == 200:
            self.json_file = json.loads(req.text)
            pprint(self.json_file)
        elif req.status_code == 404:
            return
        else:
            print(url)
            print(req.status_code)
            print(req.text)
            raise ConnectionError

    def get_participants(self) -> list:
        return [p['name'] for p in self.json_file["participants"]]

    def get_title(self) -> str:
        return self.json_file['title']

    def get_location(self) -> str or None:
        location = self.json_file.get('location')
        if location:
            return location['name']

    def get_description(self) -> str or None:
        return self.json_file.get('description')

    def get_comments(self) -> list:
        return self.json_file.get('comments')

    def get_initiator(self) -> str:
        return self.json_file["initiator"][0]['name']

    def get_latest_change(self) -> datetime:
        return datetime.fromtimestamp(self.json_file["latestChange"]/1000, tz=self.timezone)

    def get_final(self) -> list:
        options = self.json_file.get('options')
        result = []
        if options:
            for o in options:
                if o.get('final'):
                    dt_start = None
                    dt_end = None
                    try:
                        dt_start = datetime.fromtimestamp(o.get('start')/1000, tz=self.timezone)
                    except ValueError:
                        pass
                    try:
                        dt_end = datetime.fromtimestamp(o.get('end')/1000, tz=self.timezone)
                    except (ValueError, TypeError):
                        pass
                    if dt_start or dt_end:
                        result.append((dt_start, dt_end))
            return result

    def is_open(self) -> bool:
        if self.json_file['state'] == 'OPEN':
            return True
        else:
            return False
