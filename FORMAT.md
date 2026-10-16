# Recipe format

A recipe is `apps/<id>/app.json`. MeshHome checks it before installing it, with the engine in
[`backend/app/services/bot_recipes.py`](https://github.com/roach0816/MeshHome/blob/main/backend/app/services/bot_recipes.py).
The [Ecowitt app](apps/ecowitt/app.json) is a complete example.

This page describes format 1. [Format 3](#format-3) adds groups, dropdowns, several sources per
command, Basic auth, self-signed local HTTPS, a login and more path selectors; a recipe that uses
any of them declares `"schema": 3` and `"min_meshhome": "1.0.1"`.

```json
{
  "schema": 1,
  "id": "ecowitt",
  "name": "Ecowitt weather station",
  "version": "1.0.0",
  "category": "Weather",
  "summary": "One line for the catalog.",
  "description": "A paragraph shown before installing.",
  "author": "…",
  "homepage": "https://…",
  "min_meshhome": "1.0.0",
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
| `category` | Groups apps in MeshHome's catalog, such as `Weather` or `Home automation`. Up to 30 characters (letters, digits, spaces, `&`, `/`, `+`, `-`). Required in this catalog; apps without one show under "Other". |
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
- `groups` and `select`: see [Format 3](#format-3).

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

## Format 3

Everything above still applies. A setting value is at most 253 characters (groups: 4000) and can't
contain control characters or line breaks.

### Groups: `/ha garage`

A `groups` setting holds named groups of IDs, one per line:

```text
garage: cover.garage_left, cover.garage_right
office: sensor.office_temp
```

Names are 1–20 letters or digits; at most 10 groups of 6 IDs. A command with `"group"` is sent as
`/ha <group>`. It reads its one `source` once per ID, with the ID in `{item}`, and words
`reply.each` for each response, in group order. The [Home Assistant app](apps/homeassistant/app.json)
is a complete example.

```json
"sources": {
  "state": { "url": "http://{host}/api/states/{item}", "network": "local",
             "headers": { "Authorization": "Bearer {token}" } }
},
"commands": [{
  "name": "ha", "help": "Home Assistant: /ha <group>", "source": "state", "group": "groups",
  "values": { "name": { "from": ["attributes.friendly_name"], "format": "text" },
              "state": { "from": ["state"], "format": "text" } },
  "reply": { "each": "{name}: {state}", "join": " · ",
             "no_group": "Try /ha <group>: {groups}", "unknown_group": "No group {arg}. Try: {groups}" }
}]
```

- What a mesh user types after the command only picks a group by name. It never reaches a request.
- `no_group` and `unknown_group` answer a missing or unknown group. They're the only templates that
  may use `{groups}` (the owner's group names) and `{arg}` (the word sent). Group names are sent
  over the air, so say so in the setting's `help`.
- IDs that fail or can't fill `each` are left out; when all fail the reply is `unavailable`.

### Dropdowns

```json
{ "key": "league", "label": "Sport", "type": "select",
  "options": [ { "value": "football/nfl", "label": "NFL" }, { "value": "hockey/nhl", "label": "NHL" } ] },
{ "key": "team", "label": "Team", "type": "select", "depends_on": "league",
  "options_by": { "football/nfl": [ { "value": "12", "label": "Kansas City Chiefs" } ],
                  "hockey/nhl": [ { "value": "1", "label": "Boston Bruins" } ] } }
```

A dependent select needs one list for each option of its parent. Up to 60 options per list and
1000 per app. Values match `^[A-Za-z0-9][A-Za-z0-9._/-]{0,59}$` and go into URLs as written. The
[Sports app](apps/sports/app.json) is a complete example.

### Sources

- **Headers** take settings as written (format 1 URL-encodes them, which breaks tokens with
  `|`, `=` or `+`).
- **`"auth": { "basic": { "username": "{username}", "password": "{password}" } }`**: HTTP Basic auth.
- **`"verify_tls": false`**: accept a local device's self-signed certificate. Local sources only.
- **`"max_kb"`**: the largest response read, 512 by default, up to 2048.
- **`"login"`** with **`{login.token}`**: send the session token of the recipe's login.

### Login

For devices that only accept a session, such as Pi-hole 6. See the [Pi-hole app](apps/pihole/app.json).

```json
"logins": {
  "pihole": { "url": "http://{host}/api/auth", "body": { "password": "{password}" },
              "token_from": "session.sid", "ttl_from": "session.validity", "ttl_max": 1800 }
}
```

It's a JSON POST to the same host setting as the sources that use it. The token is reused until it
is about to expire, and MeshHome signs in again once if a source answers 401 or 403. It never
reaches a reply.

### Several sources per command

`"sources": ["team", "schedule"]` (up to 3) instead of `"source"`. A value reads the first one
unless it names another with `"source": "schedule"`. A source that fails only leaves its values out.

### Values and paths

- **`"format": "count"`**: how many items the list has, or how many match its last filter.
- **`"format": "duration"`**: seconds as `45s`, `1m23s`, `1h23m`, `2d7h`.
- **`"map"`** (text values): `{"ON": "on", "not_home": "away"}`, ignoring case. Mapping to `""`
  leaves the value out.
- **`[-1]`**: the last item.
- **Dotted filter fields**: `events[competitions.0.status.type.completed=true]`.
- **`[last:field=value]`**: the last match. **`[has:field]`**: the first item where the field is
  present and not empty, such as `aircraft[has:lat]`.
