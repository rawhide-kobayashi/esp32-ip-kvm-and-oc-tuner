var display = new SegmentDisplay("display");

function sevensegment_load()
{
    display.pattern         = "##";
    display.displayAngle    = 10;
    display.digitHeight     = 20;
    display.digitWidth      = 14;
    display.digitDistance   = 2.5;
    display.segmentWidth    = 2;
    display.segmentDistance = 0.3;
    display.segmentCount    = 7;
    display.cornerType      = 0;
    display.colorOn         = "#ff0000";
    display.colorOff        = "#4b1e05";
    display.setValue("00");
    display.draw();
}

function update_seven_segment(data)
{
    console.log(data);
    display.setValue(data);
}

socket.on("update_seven_segment", update_seven_segment);

window.addEventListener("load", sevensegment_load);