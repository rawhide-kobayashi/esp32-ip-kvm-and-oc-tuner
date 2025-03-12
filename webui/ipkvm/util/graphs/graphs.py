import networkx as nx
from networkx import Graph
from typing import Any
from ipkvm.util import esp32_serial
from ipkvm.util.mkb import ASCII2JS
import time

# Type checker lunacy!
type MultiDiGraph = Graph[Any]

key_delay = 0.1

def traverse_path(graph: MultiDiGraph, node_a: str, node_b: str):
    path = nx.shortest_path(graph, node_a, node_b)
    path_edges = list(zip(path[:-1], path[1:]))
    edge_path= [(u, v, graph[u][v]) for u, v in path_edges]

    for step in edge_path:
        if "initial_keypath" in step[2][0] and step[2][0]["visited"] == "false":
            keys = step[2][0]["initial_keypath"].split(',')
            # Type checker is simply wrong! This is the correct usage!
            graph.edges[step[0], step[1], 0]["visited"] = "true" # type: ignore

        else:
            keys = step[2][0]["keypath"].split(',')

        for key in keys:
            time.sleep(key_delay)
            esp32_serial.ez_press_key(key)

def apply_setting(graph: MultiDiGraph, setting_node: str, new_value: str):
    if graph.nodes[setting_node]["option_type"] == "list":
        possible_values = graph.nodes[setting_node]["options"].split(',')
        key = graph.nodes[setting_node]["traversal_key"]

        time.sleep(key_delay)
        esp32_serial.ez_press_key("Enter")

        for value in possible_values:
            time.sleep(key_delay)
            if value == new_value:
                esp32_serial.ez_press_key("Enter")
                break

            else:
                esp32_serial.ez_press_key(key)

    elif graph.nodes[setting_node]["option_type"] == "field":
        for key in new_value:
            time.sleep(key_delay)
            esp32_serial.ez_press_key(ASCII2JS[key])
        time.sleep(key_delay)
        esp32_serial.ez_press_key("Enter")

    print(f"Changed {setting_node} from {graph.nodes[setting_node]["value"]} to {new_value}!")
    graph.nodes[setting_node]["value"] = new_value



def test_route(settings: dict[Any, Any]):
    graph: MultiDiGraph = nx.nx_agraph.read_dot("bios-maps/asrock/b650e-riptide-wifi.gv")

    current_node = "Main"

    for category in settings:
        for setting_node in settings[category]:
            if graph.nodes[setting_node]["value"] != settings[category][setting_node]:
                traverse_path(graph, current_node, setting_node)
                current_node = setting_node
                apply_setting(graph, setting_node, settings[category][setting_node])
