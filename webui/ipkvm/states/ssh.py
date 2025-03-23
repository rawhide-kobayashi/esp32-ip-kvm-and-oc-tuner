import paramiko
from paramiko import Channel

class ssh_conn():
    def __init__(self, hostname: str, ssh_username: str, ycruncher_path: str, ryzen_smu_cli_path: str):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Yuck!
        self.ycruncher_cmd = f"& \"{ycruncher_path.replace("\\", "\\\\")}\"\r"
        # MEGA YUCK!
        self.smu_cmd = f"Start-Process -FilePath \"{ryzen_smu_cli_path.replace("\\", "\\\\")}\" -Verb RunAs -ArgumentList "

        client.connect(hostname=hostname, username=ssh_username, key_filename=f"/home/{ssh_username}/.ssh/id_rsa.pub")

        self.channel_ycruncher = client.invoke_shell()
        self.channel_smu = client.invoke_shell()

    def ez_send_line(self, channel: Channel, cmd: str | int, wait: bool = False, wait_string: str = ""):
        channel.send(f"{cmd}\r".encode())
    
        if wait:
            self.read_channel_line_until(channel, wait_string)
    
    def read_channel_line_until(self, channel: Channel, desired_line: str):
        line = ""
        for byte in iter(lambda: channel.recv(1), b""):
            line += byte.decode()
            if desired_line.lower() in line.lower():
                return
            elif byte == b'\n' or byte == b'\r':
                line = ""
    
    def start_ycruncher(self, core_list: list[int], test_list: list[int], test_length: int = 120):
        self.ez_send_line(self.channel_ycruncher, self.ycruncher_cmd, True, "option:")
        self.ez_send_line(self.channel_ycruncher, 2, True, "option:")
        self.ez_send_line(self.channel_ycruncher, 1, True, "option:")
        self.ez_send_line(self.channel_ycruncher, "d", True, "option:")
    
        for core in core_list:
            self.ez_send_line(self.channel_ycruncher, core, True, "option:")
    
        self.ez_send_line(self.channel_ycruncher, "", True, "option:")
        self.ez_send_line(self.channel_ycruncher, 8, True, "option:")
        for test in test_list:
            self.ez_send_line(self.channel_ycruncher, test, True, "option:")
    
        self.ez_send_line(self.channel_ycruncher, 4, True, "(seconds) =")
        self.ez_send_line(self.channel_ycruncher, test_length, True, "option:")
    
        self.ez_send_line(self.channel_ycruncher, 0, False)

    def run_smu_cmd(self, args: str):
        self.ez_send_line(self.channel_smu, f"{self.smu_cmd}\"{args}\"")
    


    #start_ycruncher(channel, 
    #                "& \"C:\\Users\\rawhide\\Downloads\\y-cruncher v0.8.6.9545\\y-cruncher v0.8.6.9545\\y-cruncher.exe\"\r",
    #                [0,1,6,9,19,25,31], [11,12], 5)
#
    #while True:
    #    line = b''
    #    for byte in iter(lambda: channel.recv(1), b""):
    #        line += byte
    #        if byte == b'\n' or byte == b'\r':
    #            line = f"{line.decode('utf-8', errors='replace').rstrip()}"
    #            print(line)
    #            line = b''
