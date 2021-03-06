# coding=UTF-8
import re
from datetime import datetime

from yammer_service.yammer import YammerConnector

HIGHLIGHTS = '#highlights'
HIGHLIGHTS_PATTERN = '(?:([^#]*) )?' + HIGHLIGHTS + '(?:[ :]*([^#]*))?'


class Highlights(object):
    def __init__(self):
        self.__highlights = {}
        self.__yc = YammerConnector()

    def add(self, username, highlight):
        m = re.match(HIGHLIGHTS_PATTERN, highlight)
        if m:
            self.__highlights[username] = (m.group(1) or m.group(2)).strip()
            return True
        else:
            return False

    def get(self, username):
        if username in self.__highlights:
            return self.__highlights[username]
        else:
            return None

    def is_not_empty(self):
        return not not self.__highlights

    def clear(self):
        self.__highlights.clear()

    def message_string(self):
        return '\n\n'.join('%s: %s' % (key, val) for (key, val) in self.__highlights.items())

    def send_to_yammer(self):
        return self.__yc.post_meine_woche(
            u'Die Südsterne in %s:\n%s' % (current_calendar_week(), self.message_string()),
            ('südsterne', current_calendar_week()))


def current_calendar_week():
    return 'KW_%s' % datetime.today().strftime('%U')
