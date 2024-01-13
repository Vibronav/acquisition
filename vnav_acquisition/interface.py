import os


def _choices2radiobuttons(choice_list, choice_name):
    choice_html_str = []
    for choice in choice_list:
        choice_html_str.append(
            f'<input type="radio" name="{choice_name}" value="{choice}">{choice}<br>'
        )
    return '\n'.join(choice_html_str)


def get_html(materials, speeds):
    content = {
        "JS": open(os.path.join(os.path.dirname(__file__), "main.js")).read(),
        "CSS": open(os.path.join(os.path.dirname(__file__), "style.css")).read(),
        "MATERIAL": _choices2radiobuttons(materials, "material"),
        "SPEED": _choices2radiobuttons(speeds, "speed")
    }

    html = open(os.path.join(os.path.dirname(__file__), "index.html")).read()
    for key, value in content.items():
        html = html.replace("$" + key, value)

    return html
