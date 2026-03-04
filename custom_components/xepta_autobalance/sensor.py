from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfVolume

from .const import (
    _LOGGER,
    DOMAIN
)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = [
        XeptaAutoBalanceSensor(coordinator, config_entry), 
        XeptaAutoBalancePHSensor(coordinator, config_entry),
        XeptaAutoBalanceSystemStateSensor(coordinator, config_entry)
    ]

    endpoints = {
        "/dispenser/kh": "kH Dispenser Remaining", 
        "/dispenser/ca": "Calcium Dispenser Remaining", 
        "/dispenser/reagent": "Reagent Remaining", 
        "/dispenser/trace": "Trace Elements Remaining"
    }
    
    for endpoint, name in endpoints.items():
        sensors.append(XeptaAutoBalanceReagentSensor(coordinator, config_entry, endpoint, name))
        
    async_add_entities(sensors)

class XeptaBaseEntity(CoordinatorEntity, SensorEntity):
    """Base class for Xepta AutoBalance entities."""
    
    _attr_has_entity_name = True
    
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._ip = config_entry.data["ip_address"]

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        system_data = self.coordinator.data.get("/system", {})
        fw_version = system_data.get("firmwareVersion", "Unknown")
        hw_version = system_data.get("pcbVersion", "Unknown")
        
        device_name = self.config_entry.data.get("device_name", f"Xepta AutoBalance {self._ip}")
        
        return {
            "identifiers": {(DOMAIN, self._ip)},
            "name": device_name,
            "manufacturer": "Xepta",
            "model": "AutoBalance",
            "sw_version": fw_version,
            "hw_version": hw_version,
        }

class XeptaAutoBalanceSensor(XeptaBaseEntity):
    """Representation of the kH Value Sensor."""
    
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_name = "kH"
    _attr_native_unit_of_measurement = "dKH"

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_kh_value"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data.get("/analysis/0", {})
        if data and data.get("isFinished", False):
            return round(data.get("khResult", 0), 2)
        return None

class XeptaAutoBalancePHSensor(XeptaBaseEntity):
    """Representation of the pH Value Sensor."""
    
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.PH
    _attr_name = "pH"

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_ph_value"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data.get("/analysis/0", {})
        if data and data.get("isFinished", False):
            return round(data.get("firstPh", 0), 2)
        return None

class XeptaAutoBalanceReagentSensor(XeptaBaseEntity):
    """Representation of a Xepta AutoBalance Reagent Level Sensor."""
    
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.VOLUME_STORAGE
    _attr_native_unit_of_measurement = UnitOfVolume.MILLILITERS

    def __init__(self, coordinator, config_entry, endpoint, sensor_name):
        super().__init__(coordinator, config_entry)
        self.endpoint = endpoint
        self._attr_name = sensor_name
        self._attr_unique_id = f"{config_entry.entry_id}_{endpoint.split('/')[-1]}_level"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data.get(self.endpoint, {})
        return round(data.get("depositLeft", 0)) if data else None

class XeptaAutoBalanceSystemStateSensor(XeptaBaseEntity):
    """Representation of the Xepta AutoBalance System State Sensor."""

    _attr_name = "Status"
    
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_system_state"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        system_data = self.coordinator.data.get('/system', {})
        state_human = system_data.get("stateHuman", None)
        if state_human:
            return state_human
        
        # Fallback to numeric state logic if stateHuman is missing
        state = system_data.get('state', None)
        return "Dosification" if state == 5 else "Unhealthy" if state is not None else "Unknown"
