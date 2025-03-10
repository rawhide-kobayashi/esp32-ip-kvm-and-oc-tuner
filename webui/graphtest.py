import networkx as nx
import serial
#from ipkvm.util.mkb import HIDKeyCode
import json
import time

# Load the Graphviz file
graph = nx.nx_agraph.read_dot("bios-maps/asrock/b650e-riptide-wifi.gv")

print(type(graph))

print(graph)

print(graph.edges())

# Example: Access node attributes
for node, data in graph.nodes(data=True):
    print(f"Node: {node}, Attributes: {data}")

print(graph.edges(data=True))

# Example: Access edge attributes (keypress actions)
for edge_a, edge_b, data in graph.edges(data=True):
    print(f"Edge: {edge_a} to {edge_b}, Attributes: {data}")

path = nx.shortest_path(graph, "Exit", "TDP to 105W")

for pair in nx.utils.pairwise(path):
    print(pair)
    print(graph.edges(pair, data=True))

edge_path = list(zip(path[:-1], path[1:]))

print("Node path:", path)
print("Edge path:", edge_path)

edge_path_with_data = [(u, v, graph[u][v]) for u, v in edge_path]
print("Edge path with data:", edge_path_with_data)

print("GENERATOR TEST")

for path in sorted(nx.all_simple_edge_paths(graph, "Exit", "Tool")):
    for edge in path:
        #print(edge)
        keys = graph.get_edge_data(edge[0], edge[1])[0]["keypath"].split(',')
        #print(keys)

        # with serial.Serial('/dev/serial/by-id/usb-1a86_USB_Single_Serial_585D015807-if00', 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE) as ser:
        for key in keys:
            print(key)
            #test_json_a = {
            #    "mouseX": 99999,
            #    "mouseY": 99999,
            #    "mouse_down": ["rbutton", "lbutton"],
            #    "mouse_up": ["otherbutton"],
            #    "key_down": [HIDKeyCode[key]],
            #    "key_up": []
            #}
#      #
            #print(key)
            ##ser.write(json.dumps(test_json_a).encode())
#
            #test_json_a = {
            #    "mouseX": 99999,
            #    "mouseY": 99999,
            #    "mouse_down": ["rbutton", "lbutton"],
            #    "mouse_up": ["otherbutton"],
            #    "key_down": [],
            #    "key_up": [HIDKeyCode[key]]
            #}
#      #
            #print(key)
            ##ser.write(json.dumps(test_json_a).encode())
            ##time.sleep(0.1)