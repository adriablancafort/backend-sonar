import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import time
import logging
import sys
from main import read_results

def download_pdf(input, only_render:bool = False, write_pdf:bool = True, destination_path:str='results.pdf', template_directory_path:str='template', template_images_directory_path:str='template/images/', template_name:str='results_template.html', background_image_name:str = "fons_results.png", background_image_header_name:str = "fons_header.png", thursday_day_image_name:str = "Thursday_day_image_template.png", friday_day_image_name:str = "Friday_day_image_template.png", friday_night_image_name:str = "Friday_night_image_template.png", saturday_day_image_name:str = "Saturday_day_image_template.png", saturday_night_image_name:str = "Saturday_night_image_template.png", show_time:bool=False, show_debug:bool=False):
    """
    Renders the input results to a PDF using an HTML template and WeasyPrint.

    Args:
        input (list): List of dictionaries containing activity data.
        only_render (bool): If True, only render the HTML without saving to PDF. Returns the rendered HTML.
        write_pdf (bool): If True, save the rendered HTML to a PDF file. Write to destination_path.
        destination_path (str): Path to save the generated PDF.
        template_directory_path (str): Path to the directory containing the Jinja2 template.
        template_images_directory_path (str): Path to the directory containing images for the template.
        template_name (str): Name of the template file.
        background_image_name (str): Name of the background image file.
        background_image_header_name (str): Name of the header background image file.
        thursday_day_image_name (str): Name of the Thursday day image file.
        friday_day_image_name (str): Name of the Friday day image file.
        friday_night_image_name (str): Name of the Friday night image file.
        saturday_day_image_name (str): Name of the Saturday day image file.
        saturday_night_image_name (str): Name of the Saturday night image file.
        show_time (bool): If True, log time taken for each step.

    Returns:
        None: If only_render is False and write_pdf is True.
        WeasyPrint.Document: Rendered HTML if only_render is True. You can later save it to a PDF with .write_pdf().
    
    Raises:
        FileNotFoundError: If the specified template or image files do not exist.
    """
    # Functions for context
    def _get_day_dots(day):
        mapping = {
            "thursday": ["●","○","○"],
            "friday":   ["●","●","○"],
            "saturday": ["●","●","●"]
        }
        return mapping.get(day.lower(), ["○","○","○"])

    def _get_time_icon(t):
        return "moon" if t.lower() == "night" else "sun"
    

    # Check if the template and images directories exist
    if not os.path.exists(template_directory_path):
        raise FileNotFoundError(f"Template directory {template_directory_path} does not exist.")
    if not os.path.exists(template_images_directory_path):
        raise FileNotFoundError(f"Template images directory {template_images_directory_path} does not exist.")
    if not os.path.exists(os.path.join(template_directory_path, template_name)):
        raise FileNotFoundError(f"Template file {template_name} does not exist in {template_directory_path}.")
    if not os.path.exists(os.path.join(template_images_directory_path, background_image_name)):
        raise FileNotFoundError(f"Background image {background_image_name} does not exist in {template_images_directory_path}.")
    if not os.path.exists(os.path.join(template_images_directory_path, background_image_header_name)):
        raise FileNotFoundError(f"Background header image {background_image_header_name} does not exist in {template_images_directory_path}.")
    if not os.path.exists(os.path.join(template_images_directory_path, thursday_day_image_name)):
        raise FileNotFoundError(f"Thursday day image {thursday_day_image_name} does not exist in {template_images_directory_path}.")
    if not os.path.exists(os.path.join(template_images_directory_path, friday_day_image_name)):
        raise FileNotFoundError(f"Friday day image {friday_day_image_name} does not exist in {template_images_directory_path}.")
    if not os.path.exists(os.path.join(template_images_directory_path, friday_night_image_name)):
        raise FileNotFoundError(f"Friday night image {friday_night_image_name} does not exist in {template_images_directory_path}.")
    if not os.path.exists(os.path.join(template_images_directory_path, saturday_day_image_name)):
        raise FileNotFoundError(f"Saturday day image {saturday_day_image_name} does not exist in {template_images_directory_path}.")
    if not os.path.exists(os.path.join(template_images_directory_path, saturday_night_image_name)):
        raise FileNotFoundError(f"Saturday day night image {saturday_night_image_name} does not exist in {template_images_directory_path}.")
    
    # Set up logging
    if show_time:
        logging.basicConfig(level=logging.INFO,format="%(levelname)s - %(name)s - %(message)s")
        if show_debug:
            progress_logger = logging.getLogger('weasyprint.progress')
            progress_logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            progress_logger.addHandler(handler)
        
        start = time.time()
        logging.info("Loading template...")

    # Load the template
    env = Environment(loader=FileSystemLoader(template_directory_path),  autoescape=True)
    template = env.get_template(template_name)

    # Add context
    if show_time:
        end1 = time.time()
        logging.info("Template loaded in seconds: %2f", end1 - start)
        logging.info("Adding context to template...")

    activities = []
    for act in input:
        day, tod = act["schedules"]["title"].split(" ")
        activities.append({
            **act,
            "time_info": f"{act['start_time']} - {act['end_time']}",
            "day_dots":  _get_day_dots(day),
            "time_icon": _get_time_icon(tod)
        })
    
    context = {
        "background_uri": os.path.join(template_images_directory_path, background_image_name),
        "background_header_uri": os.path.join(template_images_directory_path, background_image_header_name),
        "images_days_uris": {
            "Thursday Day": os.path.join(template_images_directory_path, thursday_day_image_name),
            "Friday Day": os.path.join(template_images_directory_path, friday_day_image_name),
            "Friday Night": os.path.join(template_images_directory_path, friday_night_image_name),
            "Saturday Day": os.path.join(template_images_directory_path, saturday_day_image_name),
            "Saturday Night": os.path.join(template_images_directory_path, saturday_night_image_name),
        },
        "activities": activities
    }

    # Render the template with the context
    html_content = template.render(**context)

    if show_time:
        end2 = time.time()
        logging.info("Context added in seconds: %2f", end2 - end1)

    # Render the HTML to a PDF and return it
    if only_render:
        if show_time: logging.info("Rendering template...")

        html = HTML(string=html_content, base_url=os.getcwd())
        doc = html.render()
        
        if show_time: 
            logging.info("Template rendered in seconds: %2f", time.time() - end2)
            logging.info("Total process in seconds: %2f", time.time() - end2)
        
        return doc

    # Render the HTML to a PDF and save it to the specified path
    elif write_pdf:
        if show_time: logging.info("Generating PDF...")
        HTML(string=html_content, base_url=os.getcwd()).write_pdf(destination_path)
        if show_time: 
            logging.info("PDF generated in seconds: %.2f — saving to: %s",time.time() - end2,destination_path)
            logging.info("Total process in seconds: %2f", time.time() - start)

    # Better practices
    return None

def main():
    """This is for testing purposes only"""
    if len(sys.argv) < 2:
        input = read_results(631) #example id

    else:
        quizz_id = sys.argv[1]
        input = read_results(quizz_id)
    
    download_pdf(input, show_time=True)

if __name__ == "__main__":
    main()

