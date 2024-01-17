# Xepta AutoBalance Custom Integration for Home Assistant

## Introduction
This custom integration for Home Assistant allows users to integrate their Xepta AutoBalance devices into their Home Assistant setup. With this integration, you can monitor your Xepta AutoBalance devices directly from Home Assistant.

## Features
- Monitor kH analysis results
- Monitor remaining reagent and dosing fluid levels
- Monitor Xepta AutoBalance device state

## Prerequisites
- Home Assistant installation.
- Xepta AutoBalance device setup and accessible within the same network as Home Assistant.

## Installation

### Using HACS (Home Assistant Community Store)
To install the Xepta AutoBalance integration via HACS, follow these steps:

1. **Ensure HACS is Installed**: Make sure you have HACS installed in your Home Assistant. If not, follow the [HACS installation guide](https://hacs.xyz/docs/installation/manual).

2. **Add Custom Repository**:
    - Open HACS in the Home Assistant UI.
    - Go to "Integrations".
    - Click on the three dots in the top right corner and select "Custom repositories".
    - Add the URL of this GitHub repository (`https://github.com/chrisc123/xepta_autobalance-homeassistant`).
    - Set the category to "Integration".
    - Click "Add".

3. **Install the Integration**:
    - In the HACS "Integrations" page, search for "Xepta AutoBalance".
    - Click "Install" on the Xepta AutoBalance card.

4. **Restart Home Assistant**: After installation, restart your Home Assistant.

## Configuration
After installation, you need to configure the integration in Home Assistant:

1. Go to "Configuration" in Home Assistant.
2. Click on "Integrations".
3. Click the "Add Integration" button.
4. Search for "Xepta AutoBalance" and select it.
5. Enter the required information (IP address, polling frequency, etc.) and follow the prompts to complete the setup.

## Usage
Setup automations as appropriate to notify on high/low kH and/or low fluid levels.

## Support
If you encounter any issues or have questions, please raise an issue on the [GitHub repository](https://github.com/chrisc123/xepta_autobalance-homeassistant/issues).

## Contributing
Contributions to the project are welcome! Feel free to fork the repository and submit pull requests.

---

This integration is not officially affiliated with Xepta, and it is maintained by community contributors.
