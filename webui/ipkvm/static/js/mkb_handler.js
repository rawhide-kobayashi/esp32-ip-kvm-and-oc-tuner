var last_mouse_update = Date.now()

var socket = io();

function mkbhandler_load()
{
    const streamview = document.getElementById('streamview');

    streamview.addEventListener("mouseenter", enable_listener);
    streamview.addEventListener("mouseleave", disable_listener);
}

function keydown_handler(event)
{
    socket.emit('key_down', event.code);
    event.preventDefault();
    event.stopPropagation();
}

function keyup_handler(event)
{
    socket.emit('key_up', event.code);
    event.preventDefault();
    event.stopPropagation();
}

function mousemove_handler(event)
{
    // limit the mouse update rate to 60fps (approximately) because serial bandwidth limits be low
    if (Date.now() - last_mouse_update >= 16)
    {
        last_mouse_update = Date.now();
        const bounds = streamview.getBoundingClientRect();
        const x = event.clientX - bounds.left;
        const y = event.clientY - bounds.top;
        const x_scale_factor = 32768 / streamview.clientWidth;
        const y_scale_factor = 32768 / streamview.clientHeight;
        const scaled_x = x * x_scale_factor;
        const scaled_y = y * y_scale_factor
        socket.emit("mouse_move", [scaled_x, scaled_y]);
    }
}

function mousedown_handler(event)
{
    socket.emit('mouse_down', event.button);
    event.preventDefault();
    event.stopPropagation();
}

function mouseup_handler(event)
{
    socket.emit('mouse_up', event.button);
    event.preventDefault();
    event.stopPropagation();
}

function prevent_right_click(event)
{
    event.preventDefault();
}

function enable_listener()
{
    document.addEventListener("keydown", keydown_handler);
    document.addEventListener("keyup", keyup_handler);
    document.addEventListener("mousemove", mousemove_handler);
    document.addEventListener("mousedown", mousedown_handler);
    document.addEventListener("mouseup", mouseup_handler);
    document.addEventListener('contextmenu', prevent_right_click);
}

function disable_listener()
{
    document.removeEventListener("keydown", keydown_handler);
    document.removeEventListener("keyup", keyup_handler);
    document.removeEventListener("mousemove", mousemove_handler);
    document.removeEventListener("mousedown", mousedown_handler);
    document.removeEventListener("mouseup", mouseup_handler);
    document.removeEventListener('contextmenu', prevent_right_click);
}

window.addEventListener("load", mkbhandler_load);
