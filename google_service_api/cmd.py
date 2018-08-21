# coding=utf-8

from my_logging import checked_load_logging_config, get_logger
from google_service_api.sheet import per_user_status_details, get_welfare_status_for

checked_load_logging_config("~/.python/logging_debug.conf")

log = get_logger(__name__)
print('\n'.join([get_welfare_status_for(name) for name in per_user_status_details().keys()]))

