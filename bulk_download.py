import logging
import time

from alpha_ess_client import AlphaEssClient
from alpha_ess_config import alpha_ess_app_id, alpha_ess_app_secret, alpha_ess_system_serial_num



client = AlphaEssClient(appID=alpha_ess_app_id, appSecret=alpha_ess_app_secret)


