# Recipe format (schema 1)

A recipe is `apps/<id>/app.json`. MeshHome checks it before installing it, with the engine in
[`backend/app/services/bot_recipes.py`](https://github.com/roach0816/MeshHome/blob/main/backend/app/services/bot_recipes.py).
The [Ecowitt app](apps/ecowitt/app.json) is a complete example.

```json
{
  "schema": 1,
  "id": "ecowitt",
  "name": "Ecowitt weather station",
  "version": "1.0.0",
  "summary": "One line for the catalog.",
  "description": "A paragraph shown before installing.",
  "author": "…",
  "homepage": "https://…",
  "min_meshhome": "1.0.1",
  "hosts": [],
  "settings": [ … ],
  "sources": { … },
  "commands": [ … ]
}
```

| Field | Rules |
| --- | --- |
| `id` | 2–32 characters: lowercase letters, digits, `-`. Matches the folder name. |
| `version` | `major.minor.patch`. Raise it with every change. |
| `min_meshhome` | Optional: the oldest MeshHome that can run it. |
| `hosts` | Internet hosts the app may contact, such as `api.example.com`. Shown before installing. |

## Settings

What the owner fills in when installing.

```json
{ "key": "host", "label": "Gateway address", "type": "host", "required": true,
  "placeholder": "192.168.1.50", "help": "Shown behind an (i) next to the field." }
```

`type` is one of:

- `host`: an IP address or hostname, optionally `:port`.
- `text`: free text.
- `secret`: never shown again once saved, for example an API key.

## Sources

Where data comes from: an HTTP GET request that returns JSON.

```json
"sources": {
  "live": { "url": "http://{host}/get_livedata_info", "network": "local", "timeout": 6, "cache_seconds": 60 }
}
```

- **`{key}`** in the `url` or in `headers` inserts a setting. A `host` setting is inserted as
  written; others are URL-encoded.
- **`network: "local"`:** the URL's host must be a `host` setting, and it must resolve to a private
  address on the owner's network.
- **`network: "internet"`:** the URL's host must be listed in `hosts`.
- **Limits:** no redirects, at most 512 KB, `timeout` at most 10 seconds, `cache_seconds` from 0 to
  3600.

## Commands

```json
{
  "name": "weather",
  "help": "local weather",
  "source": "live",
  "values": { … },
  "reply": { … }
}
```

- `name` is 2–20 lowercase letters and digits, used as `/name`.
- `help` is shown in `/help`.
- `/help`, `/info` and `/ping` are built into MeshHome and can't be used.

### Values

Each value is picked out of the JSON response.

```json
"temp": {
  "from": ["common_list[id=0x02].val"],
  "unit_from": ["common_list[id=0x02].unit"],
  "unit_map": { "F": "°F", "C": "°C" }
},
"rain": {
  "from": [
    { "path": "piezoRain[id=0x7C].val", "label": "24h" },
    { "path": "piezoRain[id=0x10].val", "label": "today" }
  ]
},
"wind_dir": { "from": ["common_list[id=0x0A].val"], "format": "compass" }
```

**Paths** are dot-separated keys. `[n]` takes item *n* of a list. `[field=value]` takes the first
item whose `field` equals `value`, ignoring case.

**`from`** is a list of paths. The first one that gives a usable value wins, and its `label` (if
any) is available as `{name.label}`.

**`format`** is one of:

- `number` (the default): `"3.40mph"` becomes `3.4`, with unit `mph`. Numbers are shown with up to
  two decimals.
- `compass`: degrees become a 16-point compass direction, such as `NE`.
- `text`: the value as sent, up to 60 characters.

**`unit_from` and `unit_map`:** `unit_from` gives paths to read the unit from when the value doesn't
include it. `unit_map` renames units, ignoring case and `°`.

### Reply

```json
"reply": {
  "parts": [
    { "items": ["{temp}{temp.unit}", "{humidity}% RH"] },
    { "items": ["wind {wind} {wind.unit}[ {wind_dir}][, gust {gust}]"] },
    { "items": ["AQI {aqi}", "PM2.5 {pm25}", "PM10 {pm10}"], "drop": "end" }
  ],
  "join": " · ",
  "item_join": " ",
  "max_bytes": 150,
  "empty": "Shown when no value could be read.",
  "unavailable": "Shown when the source can't be reached."
}
```

- **Placeholders:** `{name}` is a value; `{name.unit}` and `{name.label}` are its unit and label.
  Templates can only use values, never settings.
- **Missing values:** an item is left out when a value outside `[ ]` is missing. Text inside `[ ]` is
  only kept when all of its values exist.
- **Fitting one message:** if the reply is longer than `max_bytes` (150 at most, for one direct
  message), items are removed from the end of parts marked `"drop": "end"`, starting with the last
  part. If it's still too long, it's cut off with `...`.
