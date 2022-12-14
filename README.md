# netbox-peering-manager

[NetBox Peering Manager](https://github.com/jsenecal/netbox-peering-manager) is a BGP session management plugin for [NetBox](https://github.com/netbox-community/netbox). Meant as a way to document Internet Exchanges points and peering sessions, it also provides a source of truth and configuration management for external BGP sessions of all kind (transit, customers, peering, etc).

This project gets its name from the [original *Peering Manager* project](https://github.com/peering-manager/peering-manager), and most functionality is inspired by that project. I needed a tighter intergration and the existing models within NetBox allowed to do much more rather than copy/pasting/api glueing information between the two tools (even though they both have a lot in comon).
