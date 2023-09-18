# netbox-peering-manager

[NetBox Peering Manager](https://github.com/jsenecal/netbox-peering-manager) is a BGP session management plugin for [NetBox](https://github.com/netbox-community/netbox). Meant as a way to document Internet Exchanges points and peering sessions, it also provides a source of truth and configuration management for external BGP sessions of all kind (transit, customers, peering, etc).

This project gets its name from the [original *Peering Manager* project](https://github.com/peering-manager/peering-manager), and most functionality is inspired by that project. I needed a tighter intergration and the existing models within NetBox allowed to do much more rather than copy/pasting/api glueing information between the two tools (even though they both have a lot in comon).

Currently the codebase is mostly a fork of the original [NetBox BGP Plugin](https://github.com/k01ek/netbox-bgp) by [Nikolay Yuzefovich](https://github.com/k01ek) but over time the two will diverge significantly as I work on the plugin.

## Features
This plugin provide following Models:
* BGP Communities
* BGP Sessions
* Routing Policy
* Prefix Lists 

## Compatibility

| Netbox Version | Plugin Version |
|----------------|----------------|
| NetBox 3.5     | >= 0.0.1       |
| NetBox 3.6     | >= 0.0.1       |

## Installation

The plugin can be installed with pip:

```
pip install git+https://github.com/jsenecal/netbox-peering-manager.git
```
Enable the plugin in /opt/netbox/netbox/netbox/configuration.py:
```
PLUGINS = ['netbox_peering_manager']
```
Restart NetBox and add `netbox-peering-manager` to your local_requirements.txt

See [NetBox Documentation](https://docs.netbox.dev/en/stable/plugins/#installing-plugins) for details

## Configuration

The following options are available:
* `device_ext_page`: String (default right) Device related BGP sessions table position. The following values are available:  
left, right, full_width. Set empty value for disable.
* `top_level_menu`: Bool (default True) Enable top level section navigation menu for the plugin. 

## Screenshots

BGP Session
![BGP Session](docs/img/session.png)

BGP Sessions
![BGP Session Table](docs/img/sessions.png)

Community
![Community](docs/img/commun.png)

Peer Group
![Peer Group](docs/img/peer_group.png)

Routing Policy
![Routing Policy](docs/img/routepolicy.png)

Prefix List
![Prefix List](docs/img/preflist.png)
