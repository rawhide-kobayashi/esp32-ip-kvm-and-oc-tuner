import threading
import re
import requests
from ipkvm.app import logger, ui
from ipkvm.util.profiles import profile_manager
import time
import pandas as pd

class HWInfoMonitor(threading.Thread):
    def __init__(self):
        super().__init__()
        self.request_url = f"http://{profile_manager.profile["client"]["hostname"]}:{profile_manager.profile["client"]["hwinfo_port"]}/json.json"
        self.core_dataframe: pd.DataFrame
        self._is_hwinfo_alive = False
        self._new_data = threading.Event()
        self.start()

    def run(self):
        profile_manager.restart_hwinfo.wait()
        while True:
            profile_manager.restart_hwinfo.clear()
            self.do_work()
            

    def do_work(self):
        while not profile_manager.restart_hwinfo.is_set():
            self.create_dataframe()
            time.sleep(0.25)

    def create_dataframe(self):
        try:
            request = requests.get(self.request_url, timeout=1)

            if request.status_code == 200 and len(request.json()) > 0:
                self._is_hwinfo_alive = True
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
                            vid_list.append(round(reading["value"], 3))

                        elif match.group("core_mhz"):
                            mhz_list.append(round(reading["value"], 2))

                        elif match.group("core_power"):
                            power_list.append(round(reading["value"], 2))

                self.core_dataframe = pd.DataFrame({
                    "CCD": ccd_list,
                    "Clk": mhz_list,
                    "VID": vid_list,
                    "Power": power_list,
                    "Temp": temp_list
                }, index=cpu_list)

                ui.emit("update_core_info_table", self.core_dataframe.to_dict("index"))

                self._new_data.set()

            else:
                self._is_hwinfo_alive = False

        except Exception as e:
            #logger.info(e)
            pass
    
    def collect_data(self, time_to_collect: int):
        start_time = time.time()
        dataframe_list: list[pd.DataFrame] = []

        while time.time() - start_time <= time_to_collect:
            self._new_data.wait()
            self._new_data.clear()
            dataframe_list.append(self.core_dataframe)

        return dataframe_list

    @property
    def is_hwinfo_alive(self):
        return self._is_hwinfo_alive
