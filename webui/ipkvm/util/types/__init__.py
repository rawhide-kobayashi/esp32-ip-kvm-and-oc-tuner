from networkx import Graph
from typing import Any, TypedDict

# Type checker lunacy!
type MultiDiGraph = Graph[Any]

class VideoDict(TypedDict):
    friendly_name: str
    resolution: str
    fps: str

class ServerDict(TypedDict):
    esp32_serial: str
    video_device: VideoDict

class OverclockingDict(TypedDict):
    common: dict[str, str]
    cpu: dict[str, str]
    memory: dict[str, str]

class ClientDict(TypedDict):
    hostname: str
    hwinfo_port: str
    ssh_username: str
    ryzen_smu_cli_path: str
    ycruncher_path: str
    bios_map_path: str
    overclocking: OverclockingDict

class ProfileDict(TypedDict):
    server: ServerDict
    client: ClientDict
