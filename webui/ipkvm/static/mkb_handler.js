const streamview = document.getElementById('streamview');

var socket = io();

function keydown_handler(event)
{
    console.log(`Key pressed: ${event.code}`);
    socket.emit('key_down', event.code);
}

function keyup_handler(event)
{
    console.log(`Key released: ${event.code}`);
    socket.emit('key_up', event.code);
}

function enable_listener()
{
    document.addEventListener("keydown", keydown_handler);
    document.addEventListener("keyup", keyup_handler);
}

function disable_listener()
{
    document.removeEventListener("keydown", keydown_handler);
    document.removeEventListener("keyup", keyup_handler);
}

streamview.addEventListener("mouseenter", enable_listener);
streamview.addEventListener("mouseleave", disable_listener);