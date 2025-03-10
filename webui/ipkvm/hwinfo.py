import json
import threading
import re
import requests
#from ipkvm import profile
import time
from rich import print
import pandas as pd
from ipkvm import ui

class HWInfoMonitor(threading.Thread):
    def __init__(self):
        super().__init__()
        #self.request_url = f"http://{profile["client"]["hostname"]}:{profile["client"]["port"]}/json.json"
        self.request_url = "http://10.20.30.48:60000/json.json"
        self.dataframe = self.create_dataframe()
        self.start()

    def run(self):
        while True:
            self.create_dataframe()
            time.sleep(0.25)

    def create_dataframe(self):
        while not self.is_hwinfo_alive():
            time.sleep(1)

        request = requests.get(self.request_url)

        data = request.json()

        cpu_list: list[str] = []
        vid_list: list[str] = []
        mhz_list: list[str] = []
        ccd_list: list[str] = []
        temp_list: list[str] = []
        power_list: list[str] = []

        for reading in data["hwinfo"]["readings"]:
            label = reading["labelOriginal"]

            match = re.match(r"(?P<core_ccd>Core[0-9]* \(CCD[0-9]\))|(?P<core_vid>Core [0-9]* VID)|(?P<core_mhz>Core [0-9]* T0 Effective Clock)|(?P<core_power>Core [0-9]* Power)", label)
    
            if match:
                if match.group("core_ccd"):
                    core_ccd = match.group("core_ccd").split(' ')
                    core_ccd[0] = core_ccd[0][:4] + ' ' + core_ccd[0][4:]
                    cpu_list.append(core_ccd[0])
                    ccd_list.append(core_ccd[1].strip('()'))
                    temp_list.append(round(reading["value"], 2))

                elif match.group("core_vid"):
                    vid_list.append(reading["value"])

                elif match.group("core_mhz"):
                    mhz_list.append(round(reading["value"], 2))

                elif match.group("core_power"):
                    power_list.append(round(reading["value"], 2))

        core_dataframe = pd.DataFrame({
            "CCD": ccd_list,
            "Clk": mhz_list,
            "VID": vid_list,
            "Power": power_list,
            "Temp": temp_list
        }, index=cpu_list)

        ui.emit("update_core_info_table", core_dataframe.to_dict("index"))

    def is_hwinfo_alive(self):
        request = requests.get(self.request_url)

        if request.status_code == 200 and len(request.json()) > 0:
            return True
        
        return False
