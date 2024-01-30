import asyncio
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import async_get as async_get_device_registry

from .const import (
    _LOGGER,
    DOMAIN
)

async def async_setup(hass: HomeAssistant, config: dict):
    # Set up the Xepta AutoBalance component.
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Set up Xepta AutoBalance from a config entry.
    coordinator = XeptaAutoBalanceCoordinator(hass, entry)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        _LOGGER.debug(f'Last Update Failed')
        raise ConfigEntryNotReady

    # Register device in the Home Assistant device registry
    device_registry = async_get_device_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.data["ip_address"])},
        name=entry.data["device_name"],
        manufacturer="Xepta",
        model="AutoBalance",  # Update this with the actual model if available
#        sw_version="1.0"  # Update this with the actual software version if available
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator
    # Create the sensor platform setup tasks
    _LOGGER.debug('Setting up platforms for Xepta AutoBalance integration')
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def update_listener(hass, entry):
    # Update listener.
    _LOGGER.debug(f'Update config options')
    await hass.config_entries.async_reload(entry.entry_id)

class XeptaAutoBalanceCoordinator(DataUpdateCoordinator):
    # Class to manage fetching Xepta AutoBalance data for each device.
    def __init__(self, hass, entry):
        # Initialize the coordinator.
        self.api = XeptaAutoBalanceAPI(entry.data["ip_address"], hass)
        self.entry = entry
        self.update_interval = timedelta(seconds=entry.data["polling_frequency"])

        _LOGGER.debug(f"Update interval {self.update_interval.total_seconds()} seconds")
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=self.update_interval)

    async def _async_update_data(self):
        # Fetch data from Xepta AutoBalance.
        _LOGGER.debug(f'Fetching data from Xepta - async_update_data')
        try:
            data = await self.api.get_data()
            _LOGGER.debug(f'Coordinator data is {data}')
            return data
        except Exception as e:
            _LOGGER.error(f"Error fetching data: {e}")
            raise UpdateFailed(f"Error fetching data: {e}")

class XeptaAutoBalanceAPI:
    # Class to communicate with Xepta AutoBalance device.
    def __init__(self, ip_address, hass):
        """Initialize the API."""
        self._ip_address = ip_address
        self.session = async_get_clientsession(hass)

    async def get_data(self):
        # Get data from the device.
        _LOGGER.debug(f'Getting data from Xepta - get_data')
        endpoints = ["/system","/analysis/0", "/dispenser/kh", "/dispenser/ca", "/dispenser/reagent", "/dispenser/trace"]
        data = {}
        for endpoint in endpoints:
            response = await self.session.get(f"http://{self._ip_address}{endpoint}")
            response.raise_for_status()
            json_data = await response.json()
            data[endpoint] = json_data
            await asyncio.sleep(1)  # Delay to prevent overwhelming the device
        return data
