# Setup guide

### HACS Installation

1. Install [HACS](https://github.com/custom-components/hacs) if you haven't already.
2. Search for the “fritzbox voicemail” integration in HACS
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
