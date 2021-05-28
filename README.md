
# crowdstrike-mirror

Create local package repository of [CrowdStrike][crowdstrike] packages

[crowdstrike]: https://www.crowdstrike.com/

## Limitations

- mirrors only Falcon Sensor packages
- supports only `.deb` packages (Debian and Ubuntu)
- does not sign packages or repository
- requires working `apt` installation (typically a Debian/Ubuntu server)
