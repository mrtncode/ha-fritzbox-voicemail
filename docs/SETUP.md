# Setup guide

### HACS Installation

1. Install [HACS](https://github.com/custom-components/hacs) if you haven't already.
2. Add the custom repository to HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mrtncode&repository=ha-fritzbox-voicemail&category=integration)

3. Click on install
4. Restart Home Assistant
5. Add the integration via the [Home Assistant UI](https://my.home-assistant.io/redirect/integrations/)
6. Follow the UI config flow


### Manual Installation

1. Copy all files from `custom_components/fritzbox_voicemail/` to your Home Assistant config directory at `custom_components/fritzbox_voicemail/`.
2. Restart Home Assistant.
3. Add the integration via the [Home Assistant UI](https://my.home-assistant.io/redirect/integrations/)
4. Follow the UI config flow



## UI configuration
There are three fields:

| UI Field | Description                                                        |
| ------------- | ----------------------------------------------------------------------------------------- |
| FRITZ!Box URL | The IP/ hostname of your FRITZ!Box |                                 
| Username      | Your local fritz!box user. It is recommended to create a separate user for home assistant |
| Password      | The user's password                                                                       |