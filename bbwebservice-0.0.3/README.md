# How to make your first web-app
```py 
from bbwebservice.webserver import *

@register(route='/',type=MIME_TYPE.HTML)
def main_page():
    return load_file('/content/index.html')

@register(route='/main.css',type=MIME_TYPE.CSS)
def main_css():
    return load_file('/content/main.css')

start()
```