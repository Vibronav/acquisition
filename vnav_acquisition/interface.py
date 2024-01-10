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
    js = open(os.path.join(os.path.dirname(__file__), "main.js")).read()
    css = open(os.path.join(os.path.dirname(__file__), "style.css")).read()
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>{css}</style>
    </head>
    <body>
    
    <div class="content-wrapper">
        <div class="container">
            <div class="head">
                <div id="statusLabel" style="font-size: 15px; font-weight: bold; display: block"></div>
                <div class="select" style="display: block">
                    <label for="audioSource">Camera audio input source: </label><select id="audioSource"></select>
                </div>
            
                <div class="select">
                    <label for="videoSource">Video source: </label><select id="videoSource"></select>
                </div>
            </div>
            <div class="name">
                <p>Username</p>
                <input type="text" id="username" value=""><br>
            </div>
            <div class="type">
                <p>Material</p>
                {_choices2radiobuttons(materials, "material")}
            </div>
            <div class="kind">
                <p>Speed</p>
                {_choices2radiobuttons(speeds, "speed")}
            </div>
            <div class="video">
            
                <div id="controls">
                    <button id="rec" onclick="onBtnRecordClicked()">Record</button>
                    <button id="stop" onclick="onBtnStopClicked()"  style="visibility: hidden">Stop</button>
                </div>
                <video id="video" style="width: 960px; height: 480px" controls autoplay playsinline muted></video>
                
                
                <a id="downloadLink" download="mediarecorder.webm" name="mediarecorder.webm" href></a>
                <p id="data"></p>
            
            </div>
        </div>
    </div>
    
    <script type="text/javascript">{js}</script>
    </body>
    </html> 
    '''

    return html
