from IPython.display import HTML, display
import os


def _choices2radiobuttons(choice_list, choice_name):
    choice_html_str = []
    for choice in choice_list:
        choice_html_str.append(
            f'<input type="radio" name="{choice_name}" value="{choice}">{choice}<br>'
        )
    return '\n'.join(choice_html_str)


def get_html(materials, speeds):
    html = f'''
    
    <div class="select">
        <label for="audioSource">Camera audio input source: </label><select id="audioSource"></select>
    </div>

    <div class="select">
        <label for="videoSource">Video source: </label><select id="videoSource"></select>
    </div>
    
    <video id="video" controls autoplay playsinline muted></video>
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
    {_choices2radiobuttons(materials, "material")}
    </div>
    
    <div style="float: left; width: 30%;">
    <p>Speed</p>
    {_choices2radiobuttons(speeds, "speed")}
    </div>
    
    <a id="downloadLink" download="mediarecorder.webm" name="mediarecorder.webm" href></a>
    <p id="data"></p>
    '''

    js = open(os.path.join(os.path.dirname(__file__), "main.js")).read()

    return f'{html}<script type="text/javascript">{js}</script>'
