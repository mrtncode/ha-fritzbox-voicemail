# FRITZ!Box Voicemail

### Custom component to manage and listen to your FRITZ!Box answering machine in Home Assistant

![Version](https://img.shields.io/github/v/release/mrtncode/ha-fritzbox-voicemail)
[![Downloads](https://img.shields.io/github/downloads/mrtncode/ha-fritzbox-voicemail/total)](https://tooomm.github.io/github-release-stats/?username=mrtncode&repository=ha-fritzbox-voicemail)
![HACS Install Badge](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20installations&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.fritzbox_voicemail.total)
[![Latest Release](https://img.shields.io/github/release-date/mrtncode/ha-fritzbox-voicemail?style=flat&label=Latest%20Release)](https://github.com/mrtncode/ha-fritzbox-voicemail/releases)
[![Open Issues](https://img.shields.io/github/issues/mrtncode/ha-fritzbox-voicemail?style=flat&label=Open%20Issues)](https://github.com/mrtncode/ha-fritzbox-voicemail/issues)

---

## Features

| Feature | Description
|---------|-------------
| Answering Machine Switch | Turn your FRITZ!Box voicemail / answering machine on or off directly via a Home Assistant switch.
| Message Counter & Attributes | A dedicated sensor displaying the number of messages, with detailed attributes like caller ID, timestamp, and duration.
| Delete Action | Service call to programmatically delete voice messages from the system after listening or processing.
| Media Source Integration | Play back your voicemail messages directly within Home Assistant using the standard Media Browser.

---

## Setup
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mrtncode&repository=ha-fritzbox-voicemail&category=integration)

You can install FRITZ!Box Voicemail via HACS or manually. For detailed instructions, see the dedicated setup guide:

[**Setup & Installation Guide**](docs/SETUP.md)
