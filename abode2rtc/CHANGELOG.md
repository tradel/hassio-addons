# 1.2.0

- Major refactoring, grouped most functions into separate modules
- Wait to get KVS endpoints until stream is actually requested
- Request port assignments from HASS supervisor and pass into `go2rtc`

# 1.1.1

- Added debug option and more debug logging around HA connection
- Fixed crash if Home Assisant API is not available
- If API is available, go2rtc slug for each camera will be copied from HA entity name
- Obscure passwords and tokens in debug output

# 1.1.0

- Added an apparmor profile

# 1.0.0

- Initial release
