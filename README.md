
# Home battery + Sonos

I have rooftop solar and a battery which are connected to the AlphaESS cloud monitoring. 

This repo contains a simple python client for the Alpha ESS API (https://open.alphaess.com/api), and some scripts that use the client:
 * Sonos status light
 * Bulk download


## Sonos status light

I have a Sonos speaker in my kitchen with a status light that can be turned on or off over the local network.

This code monitors my home energy use and sets the status light as follows:
 * Off: No power is being drawn from the grid (all supplied by the solar + battery).
 * On: Power is being drawn from the grid, because the battery is empty.
 * Flashing: The battery is not empty, but more power is being used than can be supplied by the solar + battery.

`sonos_status_light.py` is designed to run on a RaspberryPi, and comes with an example service configuration file `sonos-status-light.service.example` to get it setup to always run. It requires a the `soco` package to communicate with the Sonos speaker (`pip install soco`).


## Bulk download

...