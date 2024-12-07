from enum import Enum
import logging
import time

from alpha_ess_client import AlphaEssClient
from alpha_ess_config import alpha_ess_app_id, alpha_ess_app_secret, alpha_ess_system_serial_num

import soco  # type: ignore


### inputs #########################################################################################
sonon_speaker_name = "Kitchen"
polling_period = 60  # in seconds
min_soc = 15  # percentage battery state of charge considered "low"
min_p_grid = 100  # in watts, when p_grid is above this it is considered to be withdrawing
####################################################################################################


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%y-%m-%d %I:%M:%S",
)
client = AlphaEssClient(appID=alpha_ess_app_id, appSecret=alpha_ess_app_secret)
logging.info("Created Alpha ESS client")
sonos = soco.discovery.by_name(sonon_speaker_name)
logging.info(f"Found Sonos speaker called '{sonon_speaker_name}'")


class State(Enum):
    EMPTY_BATTERY = "Empty battery"
    HIGH_LOAD = "High load"
    NOT_WITHDRAWING = "Not withdrawing"


while True:
    # poll Open AlphaESS API
    try:
        power_data = client.getLastPowerData(sysSn=alpha_ess_system_serial_num)
        p_grid = power_data["pgrid"]  # +ve means withdrawing, -ve means injecting
        bess_soc = power_data["soc"]  # state of charge as percentage, 0 to 100
    except Exception as e:
        logging.error(f"Error when polling Alpha ESS API: {e}")
        time.sleep(polling_period)
        continue

    # decide which state to be in
    if p_grid > min_p_grid and bess_soc < min_soc:
        state = State.EMPTY_BATTERY  # withdrawing from grid due to low battery charge
    elif p_grid > min_p_grid:
        state = State.HIGH_LOAD  # withdrawing from grid due to high MW load
    else:
        state = State.NOT_WITHDRAWING  # not withdrawing from grid
    logging.info(
        f"Power from grid: {p_grid} W. State of charge: {bess_soc}%. State: '{state.value}'"
    )

    # set sonos status light accordingly
    if state == State.NOT_WITHDRAWING:
        sonos.status_light = False
        time.sleep(polling_period)
    elif state == State.HIGH_LOAD:
        for i in range(polling_period):
            sonos.status_light = i % 2 == 0
            time.sleep(1)
    elif state == State.EMPTY_BATTERY:
        sonos.status_light = True
        time.sleep(polling_period)
    else:
        raise ValueError(f"State '{state}' not known")
