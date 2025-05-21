import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from main import read_results
import time

env = Environment(
    loader=FileSystemLoader('template'),  
    autoescape=True
)
template = env.get_template('results_template.html')


def get_day_dots(day):
    mapping = {
        "thursday": ["●","○","○"],
        "friday":   ["●","●","○"],
        "saturday": ["●","●","●"]
    }
    return mapping.get(day.lower(), ["○","○","○"])

def get_time_icon(t):
    return "moon" if t.lower() == "night" else "sun"


start=time.time()
print("Starting generating schedule...")

raw_activities = read_results(631)

end1=time.time()
print("Schedule generated in seconds: ", end1-start)

print("Addind context to template...")
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

end2=time.time()
print("Context added in seconds: ", end2-end1)
print("Rendering template...")


html_out = template.render(**context)
end3=time.time()
print("Template rendered in seconds: ", end3-end2)
print("Generating PDF...")


HTML(string=html_out, base_url=os.getcwd()).write_pdf("results_test.pdf")
end4=time.time()
print("PDF generated in seconds: ", end4-end3)
print("Total time in seconds: ", end4-start)
print("PDF generated successfully.")