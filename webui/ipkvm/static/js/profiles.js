let profileDropdown;
let serialDropdown;
let videoDropdown;
let resolutionDropdown;
let fpsDropdown;
let deviceData = {};

function profiles_load()
{
    profileDropdown = document.getElementById("profile-select");
    serialDropdown = document.getElementById("serial-select");
    videoDropdown = document.getElementById("video-select");
    resolutionDropdown = document.getElementById("resolution-select");
    fpsDropdown = document.getElementById("fps-select");
    populate_video_devices();
    populate_serial_devices();
}

function update_toml(field, new_value) {
    let re = new RegExp(String.raw`(${field}\s*=\s*)".*?"`, "g");
    return code_mirror.getValue().replace(re, `$1"${new_value}"`);
}

function removeAllButFirstChild(element) {
    while (element.children.length > 1) {
        element.removeChild(element.lastChild);
    }
}

function populate_video_devices()
{
    removeAllButFirstChild(videoDropdown)
    socket.emit("get_video_devices", (data) => {
        deviceData = data;
        Object.keys(data).forEach((key, index) => {
            let option = document.createElement("option");
            option.id = key;
            option.textContent = key;
            videoDropdown.appendChild(option);
        });
    });
}

function populate_resolution(deviceName)
{
    removeAllButFirstChild(resolutionDropdown)
    Object.keys(deviceData[deviceName]["formats"]).forEach((key, index) => {
        let option = document.createElement("option");
        option.id = key;
        option.textContent = key;
        resolutionDropdown.appendChild(option);
    });

    populate_fps(resolutionDropdown.value, videoDropdown.value);
    
    if (resolutionDropdown.value != "Resolution...") {
        code_mirror.setValue(update_toml('resolution', resolutionDropdown.value));
    }
}

function populate_fps(resolution, deviceName)
{
    removeAllButFirstChild(fpsDropdown)
    deviceData[deviceName]["formats"][resolution].forEach((key, index) => {
        let option = document.createElement("option");
        option.id = key;
        option.textContent = key;
        fpsDropdown.appendChild(option);
    });

    if (fpsDropdown.value != "FPS...") {
        code_mirror.setValue(update_toml('fps', fpsDropdown.value));
    }
}

function populate_serial_devices()
{
    removeAllButFirstChild(serialDropdown)
    socket.emit("get_serial_devices", (data) => {
        data.forEach((key, index) => {
            let option = document.createElement("option");
            option.id = key;
            option.textContent = key;
            serialDropdown.appendChild(option);
        });
    });

    if (serialDropdown.value != "Serial device...") {
        code_mirror.setValue(update_toml('esp32_serial', serialDropdown.value));
    }
}

function save_new_profile() {
    socket.emit("save_profile_as", code_mirror.getValue(), prompt("Input new profile name!"));
}

window.addEventListener("load", profiles_load);