# MeshHome apps

The app catalog for the [MeshHome](https://github.com/roach0816/MeshHome) bot. Apps add commands
that people on the mesh can send to your node, such as `/weather`. You install them from
**Settings → Bot → Apps** in MeshHome.

| App | Category | Command | What it does |
| --- | --- | --- | --- |
| [AdGuard Home](apps/adguardhome/app.json) | Network | `/dns` | DNS queries, blocked queries and protection status from AdGuard Home on your network |
| [Ambient Weather station](apps/ambientweather/app.json) | Weather | `/weather` | Temperature, humidity, wind, rain, pressure and air quality from your Ambient Weather station, read from AmbientWeather.net with your API keys |
| [Ecowitt weather station](apps/ecowitt/app.json) | Weather | `/weather` | Temperature, humidity, wind, rain and air quality from your Ecowitt gateway, read on your network |
| [Enphase Envoy solar](apps/enphase/app.json) | Energy & solar | `/solar` | Solar production now and today, home use and grid power from your Envoy (firmware 7+), read on your network |
| [Home Assistant](apps/homeassistant/app.json) | Home automation | `/ha <group>` | The state of each entity in a group you define, such as both garage doors, read on your network over http:// or https:// |
| [openHAB](apps/openhab/app.json) | Home automation | `/oh <group>` | The state of each item in a group you define, read on your network |
| [PiAware / dump1090-fa](apps/piaware/app.json) | Radio & tracking | `/planes`, `/feeder` | Aircraft your ADS-B receiver is tracking, message rate and signal, and PiAware's feeder status, read on your network |
| [Pi-hole](apps/pihole/app.json) | Network | `/dns` | Queries today, blocked queries and blocking status from Pi-hole 6 on your network |
| [Speedtest Tracker](apps/speedtest-tracker/app.json) | Network | `/speed` | The latest download, upload and ping from Speedtest Tracker on your network |
| [Sports scores](apps/sports/app.json) | Sports | `/sports` | Your team's latest result and next game, with its record, from ESPN |
| [Tempest weather station (imperial)](apps/tempest-imperial/app.json) | Weather | `/weather` | Conditions, temperature, humidity, wind, rain, pressure and UV from your WeatherFlow Tempest station in °F, mph, inches and inHg, read from the Tempest API with your access token |
| [Tempest weather station (metric)](apps/tempest/app.json) | Weather | `/weather` | The same in °C, km/h, mm and hPa |

## How apps work

An app is a **recipe**, a JSON file. It describes the settings it needs, where it reads data from,
and how to word the reply. It contains no code. MeshHome runs every app with the same small engine,
and the engine only allows a few things:

- **Requests:** an app can only make HTTP GET requests that return JSON, either to a device on your
  own network (an address you enter) or to internet hosts it names. You see those hosts before you
  install the app. An app for a device that needs a session (such as Pi-hole) may also sign in to
  that same device, and the install sheet says so.
- **Groups:** an app like Home Assistant only reads the entities you put in named groups. What
  someone types after the command (`/ha garage`) only picks one of your groups.
- **No secrets in replies:** a reply can only use values from the response, never your settings, so
  an app can't send your addresses or keys over the air.
- **Updates need your approval:** when a new version is published, MeshHome shows what changes (new
  commands, settings or hosts), and it only runs after you choose **Update**.

MeshHome reads `catalog.json` from this repository. It only installs a recipe whose SHA-256 matches
the one listed there.

## Adding, updating or removing an app

1. Edit `apps/<id>/app.json`, or add or delete an app's folder. The folder name is the app's `id`.
   Give it a `category`; MeshHome's catalog filters by the categories its apps use, so a new
   category appears as soon as an app has it. When you change an app, raise its `version`.
2. Run `python3 tools/build_catalog.py` to regenerate `catalog.json` with the new checksums.
3. Commit and push. CI checks every app with MeshHome's recipe engine.

MeshHome servers see the change within a few hours, or straight away with **Refresh** in the
catalog. No MeshHome release is needed.

The recipe format is described in [FORMAT.md](FORMAT.md).

## Licence

MIT
