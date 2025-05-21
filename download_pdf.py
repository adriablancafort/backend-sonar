import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from main import read_results

# 1) Configura Jinja2
env = Environment(
    loader=FileSystemLoader('template'),  # carpeta on estigui activities_template.html
    autoescape=True
)
template = env.get_template('template_versio7.html')

# Exemples de dades de prova per al nou template
def get_day_dots(day):
    mapping = {
        "thursday": ["●","○","○"],
        "friday":   ["●","●","○"],
        "saturday": ["●","●","●"]
    }
    return mapping.get(day.lower(), ["○","○","○"])

def get_time_icon(t):
    return "moon" if t.lower() == "night" else "sun"

raw_activities = read_results(631)


# Construcció del context amb els camps calculats
activities = []
for act in raw_activities:
    day, tod = act["schedules"]["title"].split(" ")
    activities.append({
        **act,
        "time_info": f"{act['start_time']} - {act['end_time']}",
        "day_dots":  get_day_dots(day),
        "time_icon": get_time_icon(tod)
    })

context = {
    "background_uri": "template/fons_results.png",
    "background_header_uri": "template/fons_header.png",
    "images_days_uris": {
        "Thursday Day": "template/Thursday_day_image_template.png",
        "Friday Day": "template/Friday_day_image_template.png",
        "Friday Night": "template/Friday_night_image_template.png",
        "Saturday Day": "template/Saturday_day_image_template.png",
        "Saturday Night": "template/Saturday_night_image_template.png",
    },
    "activities": activities
}



# 3) Renderitza l’HTML
html_out = template.render(**context)


HTML(string=html_out, base_url=os.getcwd()) \
    .write_pdf("results_test.pdf")

print("PDF generat: results_test.pdf")