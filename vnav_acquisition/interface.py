from IPython.display import HTML
import os

MATERIALS = ("Slime", "Silicone", "PU", "Plato (play dough)", "Plastic", "Ikea (plastic bag)",
             "African (silk)")
SPEEDS = ("slow", "medium", "fast")


def _choices2radiobuttons(choice_list, choice_name):
    choice_html_str = []
    for choice in choice_list:
        choice_code = hash(choice)
        choice_html_str.append(
            f'<input type="radio" name="{choice_name}" value="{choice}">{choice}<br>'
        )
    return '\n'.join(choice_html_str)


def build_interface(materials=MATERIALS, speeds=SPEEDS):
    html = f'''
    <video id="live" controls autoplay playsinline muted></video>
    <div id="controls">
        <button id="rec" onclick="onBtnRecordClicked()">Record</button>
        <button id="stop" onclick="onBtnStopClicked()"  style="visibility: hidden">Stop</button>
    </div>
    
    <div style="float: left; width: 30%;">
    <p>Username</p>
    <input type="text" id="username" value=""><br>
    </div>
    
    <div style="float: left; width: 30%;">
    <p>Material</p>
    {_choices2radiobuttons(MATERIALS, "material")}
    </div>
    
    <div style="float: left; width: 30%;">
    <p>Speed</p>
    {_choices2radiobuttons(SPEEDS, "speed")}
    </div>
    
    <a id="downloadLink" download="mediarecorder.webm" name="mediarecorder.webm" href></a>
    <p id="data"></p>
    '''

    js = open(os.path.join(os.path.dirname(__file__), "main.js")).read()

    display(HTML(f'{html}<script type="text/javascript">{js}</script>'))