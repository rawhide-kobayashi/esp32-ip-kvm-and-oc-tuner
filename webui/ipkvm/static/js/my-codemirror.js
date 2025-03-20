let code_mirror;
let code_div;

function codemirror_load()
{
    code_div = document.getElementById('codemirror');

    code_mirror = CodeMirror(code_div, {
       lineNumbers: true 
    })

    socket.emit("get_current_profile", (data) => {
        code_mirror.setValue(data)
    });

    code_div.addEventListener("mouseleave", disable_input);
    code_div.addEventListener("mouseenter", enable_input);
}

function disable_input()
{
    code_mirror.setOption("readOnly", "nocursor");
}

function enable_input()
{
    code_mirror.setOption("readOnly", false);
}

window.addEventListener("load", codemirror_load);