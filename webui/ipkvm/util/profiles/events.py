import tomlkit
from ipkvm.app import ui
from . import profile_manager
from ipkvm.util.mkb import esp32_serial
from ipkvm.states import model

@ui.on("get_current_profile")
def handle_current_profile():
    return tomlkit.dumps(profile_manager.profile)

@ui.on("save_profile")
def handle_save_profile(data: str):
    profile_manager.save_profile(tomlkit.parse(data)) # type: ignore

@ui.on("save_profile_as")
def handle_save_profile_as(data: str, name: str):
    profile_manager.save_profile(tomlkit.parse(data), name) # type: ignore

@ui.on("apply_current_bios_settings")
def handle_bios_settings():
    model.current_BIOS_location = esp32_serial.apply_all_settings(profile_manager.profile["client"]["overclocking"],
                                                                  profile_manager.bios_map, model.current_BIOS_location)