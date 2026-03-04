import asyncio
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

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
    
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    # Create the sensor platform setup tasks
    _LOGGER.debug('Setting up platforms for Xepta AutoBalance integration')
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def update_listener(hass, entry):
    # Update listener.
    _LOGGER.debug(f'Update config options')
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class XeptaAutoBalanceCoordinator(DataUpdateCoordinator):
    # Class to manage fetching Xepta AutoBalance data for each device.
    def __init__(self, hass, entry):
        # Initialize the coordinator.
        from datetime import timedelta
        self.api = XeptaAutoBalanceAPI(entry.data["ip_address"], hass)
        self.entry = entry
        
        # Read from entry.options with fallback to entry.data
        polling_freq = entry.options.get("polling_frequency", entry.data.get("polling_frequency", 60))
        self.update_interval = timedelta(seconds=polling_freq)

        _LOGGER.debug(f"Update interval {self.update_interval.total_seconds()} seconds")
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=self.update_interval)

    async def _async_update_data(self):
        # Fetch data from Xepta AutoBalance.
        _LOGGER.debug(f'Fetching data from Xepta - async_update_data')
        try:
            # Note: asyncio.timeout is preferred in newer Python, but async_timeout is safer for older HA
            async with async_timeout.timeout(30):
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
            await asyncio.sleep(0.5)  # Slight delay to prevent overwhelming the device
        return data
