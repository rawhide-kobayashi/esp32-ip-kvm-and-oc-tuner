import tomlkit
from ipkvm.app import ui
from . import profile_manager

@ui.on("get_current_profile")
def handle_current_profile():
    return tomlkit.dumps(profile_manager.profile)

@ui.on("save_profile")
def handle_save_profile(data: str):
    profile_manager.save_profile(tomlkit.parse(data)) # type: ignore

@ui.on("save_profile_as")
def handle_save_profile_as(data: str, name: str):
    profile_manager.save_profile(tomlkit.parse(data), name) # type: ignore