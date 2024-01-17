import ipaddress
import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    _LOGGER,
    DOMAIN
)

class XeptaAutoBalanceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        self.device_config = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            valid_ip = self._validate_ip(user_input["ip_address"])
            if not valid_ip:
                errors["base"] = "invalid_ip"
            elif await self._is_already_configured(user_input["ip_address"]):
                errors["base"] = "already_configured"
            else:
                self.device_config = user_input
                return await self.async_step_device_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str,
                vol.Required("polling_frequency", default=60): cv.positive_int,
            }),
            errors=errors
        )

    async def async_step_device_options(self, user_input=None):
        """Handle the options for the device."""
        if user_input is not None:
            self.device_config.update(user_input)
            return self.async_create_entry(title=f"Device {self.device_config['ip_address']}", data=self.device_config)

        return self.async_show_form(
            step_id="device_options",
            data_schema=vol.Schema({
                vol.Optional("device_name", default="Xepta AutoBalance Device"): str,
            })
        )

    def _validate_ip(self, ip_address):
        """Validate the IP address."""
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    async def _is_already_configured(self, ip_address):
        """Check if an IP address is already configured."""
        existing_entries = self._async_current_entries()
        return any(entry.data["ip_address"] == ip_address for entry in existing_entries)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return XeptaAutoBalanceOptionsFlowHandler(config_entry)

class XeptaAutoBalanceOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("polling_frequency", default=self.config_entry.options.get("polling_frequency", 60)): cv.positive_int,
            })
        )
