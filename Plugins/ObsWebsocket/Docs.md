### Description

This plugin allows you to control OBS through it's WebSocket interface.

---
### Options

* `AuthDataFilepath` : `String` : `"$Private$/Auth/ObsAuthData.txt"` - marks file path to OBS WebSocket Authentication data.

* `ConnectionTimeout` : `Float` : `3` - duration of a connection attempt.

* `AutoReconnect` : `Bool` : `True` - should the plugin try to automatically reconnect to OBS WebSocket in case of connection failure.

* `AutoReconnectTimeout` : `Float` : `5` - time between auto reconnect attempts

---
### Event Processor Functions

- `SetScene` (`NewScene` : `String`) — Switches the current program scene to `NewScene`. Reads from `event.data`, overridable by `arguments`. Aborts if no scene name is given or if not connected.

- `SetSourceVisibility` (`SceneName` : `String`, `SourceName` : `String`, `Visible` : `Bool`, optional) — Sets or toggles visibility of `SourceName` in `SceneName`. Reads from `event.data`, overridable by `arguments`. If `Visible` is omitted, the current state is inverted. Aborts if either name is missing or if not connected.

- `SetInputMute` (`InputName` : `String`, `Muted` : `Bool`, optional) — Mutes, unmutes, or toggles the input `InputName`. Reads from `event.data`, overridable by `arguments`. If `Muted` is omitted, the state is toggled. Aborts if `InputName` is missing or if not connected.

- `SetInputVolume` (`InputName` : `String`, `Volume` : `Float`) — Sets `InputName` volume to the linear multiplier `Volume` (1.0 = 100%). Reads from `event.data`, overridable by `arguments`. Defaults to 1.0 if unspecified. Aborts if `InputName` is missing or if not connected.

- `ControlMedia` (`InputName` : `String`, `Action` : `String`) — Controls playback of media input `InputName`. `Action` is case-insensitive: `PLAY`, `PAUSE`, `STOP`, or `RESTART`. Reads from `event.data`, overridable by `arguments`. Aborts on missing/invalid arguments or if not connected.

---
### Custom Configuration

Connection to OBS WebSocket requires filling out `ObsAuthData.txt` file at `GLady/Private/Auth`. Required information can be found in OBS Studio: 

**Tools -> WebSocket Server Settings -> Show Connection Info**