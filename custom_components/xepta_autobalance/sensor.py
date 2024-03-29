from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorStateClass

from .const import (
    _LOGGER,
    DOMAIN
)

from . import XeptaAutoBalanceCoordinator

async def async_setup_entry(hass, config_entry, async_add_entities):
    # Set up the sensor platform.
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Now that we have data, create and add sensor entities
    sensors = [XeptaAutoBalanceSensor(coordinator, config_entry), XeptaAutoBalancePHSensor(coordinator, config_entry)]  # Added pH sensor to the list
    endpoints = ["/dispenser/kh", "/dispenser/ca", "/dispenser/reagent", "/dispenser/trace"]
    sensors.extend([XeptaAutoBalanceReagentSensor(coordinator, config_entry, endpoint) for endpoint in endpoints])
    sensors.append(XeptaAutoBalanceSystemStateSensor(coordinator, config_entry))
    async_add_entities(sensors)

class XeptaAutoBalanceSensor(CoordinatorEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    # Representation of a Xepta AutoBalance Sensor.
    def __init__(self, coordinator, config_entry):
        device_name = config_entry.data.get("device_name", f"Xepta AutoBalance {coordinator.api._ip_address}")
        # Initialize the sensor.
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_name = f"{device_name} kH Value"
        self._attr_unique_id = f"{config_entry.entry_id}_kh_value"

    @property
    def state(self):
        # Return the state of the sensor.
        data = self.coordinator.data.get("/analysis/0", {})
        if data and data.get("isFinished", False):  # Check if analysis is finished
            return round(data.get("khResult", 0), 2)
        return None  # Return None if analysis is in progress or data is unavailable
        
    @property
    def device_info(self):
        device_name = self.config_entry.data.get("device_name", f"Xepta AutoBalance {self.coordinator.api._ip_address}")
        return {
            "identifiers": {(DOMAIN, self.config_entry.data["ip_address"])},
            "name": device_name,
            "manufacturer": "Xepta",
            "model": "AutoBalance Model",
            "sw_version": "1.0"
        }

class XeptaAutoBalancePHSensor(CoordinatorEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, config_entry):
        device_name = config_entry.data.get("device_name", f"Xepta AutoBalance {coordinator.api._ip_address}")
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_name = f"{device_name} pH Value"
        self._attr_unique_id = f"{config_entry.entry_id}_ph_value"

    @property
    def state(self):
        # Return the state of the sensor.
        data = self.coordinator.data.get("/analysis/0", {})
        if data and data.get("isFinished", False):  # Check if analysis is finished
            return round(data.get("firstPh", 0), 2)
        return None  # Return None if analysis is in progress or data is unavailable
        
        
    @property
    def device_info(self):
        device_name = self.config_entry.data.get("device_name", f"Xepta AutoBalance {self.coordinator.api._ip_address}")
        return {
            "identifiers": {(DOMAIN, self.config_entry.data["ip_address"])},
            "name": device_name,
            "manufacturer": "Xepta",
            "model": "AutoBalance Model",
            "sw_version": "1.0"
        }

class XeptaAutoBalanceReagentSensor(CoordinatorEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    # Representation of a Xepta AutoBalance Reagent Level Sensor.
    def __init__(self, coordinator, config_entry, endpoint):
        # Initialize the sensor.
        device_name = config_entry.data.get("device_name", f"Xepta AutoBalance {coordinator.api._ip_address}")
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.endpoint = endpoint
        self._attr_name = f"{device_name} {endpoint.split('/')[-1]} Level"
        self._attr_unique_id = f"{config_entry.entry_id}_{endpoint.split('/')[-1]}_level"

    @property
    def state(self):
        # Return the state of the sensor.
        data = self.coordinator.data.get(self.endpoint, {})
        return round(data.get("depositLeft", 0)) if data else None

    @property
    def device_info(self):
        device_name = self.config_entry.data.get("device_name", f"Xepta AutoBalance {self.coordinator.api._ip_address}")
        return {
            "identifiers": {(DOMAIN, self.config_entry.data["ip_address"])},
            "name": device_name,
            "manufacturer": "Xepta",
            "model": "AutoBalance Model",
            "sw_version": "1.0"
        }

    # Implement other properties and methods as needed
class XeptaAutoBalanceSystemStateSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Xepta AutoBalance System State Sensor."""

    def __init__(self, coordinator, config_entry):
        device_name = config_entry.data.get("device_name", f"Xepta AutoBalance {coordinator.api._ip_address}")
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_name = f"{device_name} System State"
        self._attr_unique_id = f"{config_entry.entry_id}_system_state"

    @property
    def state(self):
        """Return the state of the sensor."""
        system_data = self.coordinator.data.get('/system', {})
        state = system_data.get('state', None)
        return "OK" if state == 5 else "Unhealthy"

    @property
    def device_info(self):
        device_name = self.config_entry.data.get("device_name", f"Xepta AutoBalance {self.coordinator.api._ip_address}")
        return {
            "identifiers": {(DOMAIN, self.config_entry.data["ip_address"])},
            "name": device_name,
            "manufacturer": "Xepta",
            "model": "AutoBalance Model",
            "sw_version": "1.0"
        }

    # Implement other properties and methods as needed
