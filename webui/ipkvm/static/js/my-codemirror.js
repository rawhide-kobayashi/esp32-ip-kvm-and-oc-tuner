function codemirror_load()
{
    const code_div = document.getElementById('codemirror');

    var code_mirror = CodeMirror(code_div, {
       lineNumbers: true 
    })

    socket.emit("get_current_profile", (data) => {
        code_mirror.setValue(data)
    });
}

window.addEventListener("load", codemirror_load);