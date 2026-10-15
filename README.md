# MeshHome apps

The app catalog for the [MeshHome](https://github.com/roach0816/MeshHome) bot. Apps add commands
that people on the mesh can send to your node, such as `/weather`. You install them from
**Settings → Bot → Apps** in MeshHome.

| App | Command | What it does |
| --- | --- | --- |
| [Ecowitt weather station](apps/ecowitt/app.json) | `/weather` | Temperature, humidity, wind, rain and air quality from your Ecowitt gateway, read on your network |

## How apps work

An app is a **recipe**, a JSON file. It describes the settings it needs, where it reads data from,
and how to word the reply. It contains no code. MeshHome runs every app with the same small engine,
and the engine only allows a few things:

- **Requests:** an app can only make HTTP GET requests that return JSON, either to a device on your
  own network (an address you enter) or to internet hosts it names. You see those hosts before you
  install the app.
- **No secrets in replies:** a reply can only use values from the response, never your settings, so
  an app can't send your addresses or keys over the air.
- **Updates need your approval:** when a new version is published, MeshHome shows what changes (new
  commands, settings or hosts), and it only runs after you choose **Update**.

MeshHome reads `catalog.json` from this repository. It only installs a recipe whose SHA-256 matches
the one listed there.

## Adding, updating or removing an app

1. Edit `apps/<id>/app.json`, or add or delete an app's folder. The folder name is the app's `id`.
   When you change an app, raise its `version`.
2. Run `python3 tools/build_catalog.py` to regenerate `catalog.json` with the new checksums.
3. Commit and push. CI checks every app with MeshHome's recipe engine.

MeshHome servers see the change within a few hours, or straight away with **Refresh** in the
catalog. No MeshHome release is needed.

The recipe format is described in [FORMAT.md](FORMAT.md).

## Licence

MIT
