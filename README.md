# gear-visor
Simple Web UI for gearman servers monitoring.

# Requirements
* python3
* flask
* [gear](https://github.com/bbrodriges/gear)

# Manual deploy
* download sources
* edit `SERVERS` directive in `settings.py`
* run `python3 visor.py`
* open `localhost:5000/visor/` in your browser

# Automatic monitoring
You can send GET request to `/visor/ajax/servers/<server_alias>` to get JSON representation. It can be useful if you want to monitor your gearman servers with any external monitoring system.

