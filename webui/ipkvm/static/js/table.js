let container;
let hot;

function table_load() {
    container = document.getElementById("stats-table");
}

function create_table(data) {
    let row_headers = []
    let col_headers = []

    container.innerText = ""

    Object.keys(data).forEach((key, index) => {
        col_headers.push(key)
        Object.keys(data[key]).forEach((value, subIndex) => {
            row_headers.push(value)
        });
    });

    hot = new Handsontable(container, {
        rowHeaders: row_headers,
        rowHeaderWidth: 60,
        colHeaders: col_headers,
        height: 'auto',
        autoWrapRow: true,
        autoWrapCol: true,
        licenseKey: 'non-commercial-and-evaluation' // for non-commercial use only
    });
}

function update_core_info_table(data) {
    if (hot) {
        hot.batch(() => {
            Object.keys(data).forEach((key, index) => {
                Object.keys(data[key]).forEach((value, subIndex) => {
                    hot.setDataAtCell(subIndex, index, data[key][value])
                });
            });
        });
    }

    else {
        create_table(data)
    }
}

socket.on("update_core_info_table", update_core_info_table);

window.addEventListener("load", table_load);
