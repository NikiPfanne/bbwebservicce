import os
import re
from . import core
from .__init__ import MAIN_PATH

class MIME_TYPE:
    HTML = 'text/html'
    JAVA_SCRIPT = 'text/javascript'
    CSS = 'text/css'
    ICO = "image/x-icon"
    PNG = "image/png"
    SVG = "image/svg+xml"
    TEXT = "text/plain"
    MP4 = "video/mp4"

def register(*args, **kwargs):

    '''The register decorator adds the decorated function to the servers PAGES
    dictionary. The decorater requires a path and a type argument to be specified. The decorated function
    gets called whenever a GET request is targeted to the speciefied path. The function is expected to return a String
    that's been served under the specified route the type argument must provide the matching MIME-type.'''

    if 'route' not in kwargs:
        raise Exception('The "route" argument is missing.')
    if 'type' not in kwargs:
        raise Exception('The "type" argument is missing.')
    route = kwargs['route']
    def inner(func):
        if kwargs['route'] not in core.PAGES:
                core.PAGES[route] = [func,kwargs['type']]
        return func            
    return inner

def post_handler(*args, **kwargs):

    '''The post_handler decorator adds the decorated function to the servers POST_HANDLER
    dictionary. The decorater requires a path and a type argument to be specified the decorated function
    gets called whenever a post is targeted to the speciefied path. The function is expected to return a string of the
    under the type attribute declared MIME-type. The function decorated gets passed a dictionary containing
    the variables passed with the POST'''

    if 'route' not in kwargs:
        raise Exception('The "route" argument is missing.')
    if 'type' not in kwargs:
        raise Exception('The "type" argument is missing.')
    route = kwargs['route']
    def inner(func):
        if func.__code__.co_argcount != 1:
            raise Exception('The function decorated with the post_handler decorater has to\n accept one Argument "args":dict')
        if kwargs['route'] not in core.POST_HANDLER:
                core.POST_HANDLER[route] = [func,kwargs['type']]
        return func            
    return inner

def load_file(path:str) -> str:

    '''The load_file function attempts to read the content of a file with given path and returns it as a utf-8 encoded string'''

    with open(MAIN_PATH+path,'r',encoding='utf-8') as content:
            lines = content.readlines()
            return ''.join(lines)

def load_bin_file(path:str) -> bytes:

    '''The load_file function attempts to read the content of a file with given path and returns it as bytes'''
    path = MAIN_PATH+path
    size = os.path.getsize(path)
    with open(path,'rb') as content:
            return content.read(size)

def render_page(path:str, args:dict) -> str:

    '''The render_page function reads a files content and executes python-code wrapped in double curly braces "{{".
    If a variable name starts with an underscore "_" the python code wrapped in curley braces will be substituded by it's content.
    The values passed with the args dictionary can be accessed with the globals() function in the targeted file'''

    content = ''
    try:
        with open(MAIN_PATH+path,'r',encoding='utf-8') as page:
            content = '\n'.join(page.readlines())
            
        to_eval= re.finditer("{{(.|\n)*?}}",content)
        for var in to_eval:
            OUTPUT = {}
            var = content[var.span()[0]:var.span()[1]]
            exec(compile(var.strip('{{}}'),'temp','exec'),args,OUTPUT)
            insert = '\n'.join([str(OUTPUT[x]) for x in OUTPUT.keys() if x[0] == '_'])
            content = content.replace(var,insert)
    except Exception as e:
        print('[RENDERER] Error with rendering Page.')
        print(e)
    return content

def substitude_vars(content:str, vars:dict) -> str:
    
    '''This function accepts a string and substitudes all "%% + key + %%" with the according value from the dictionary'''
    
    try:
        _content = content
        for key in vars:
            _content = re.sub(f'%%{key}%%',vars[key],_content)
    except:
        print('[SUBSTITUDE_VARS] Error substituding vars.')
    return _content

def start() -> None:

    '''The start function causes the server to start by invoking core.start()'''

    core.start()
 
def get_pages() -> dict:
    return core.PAGES

def get_sessions() -> dict:
    return core.SESSIONS
    
def get_post_handler() -> dict:
    return core.POST_HANDLER

def set_logging(option:str,state:bool) -> None:
    if option in core.SERVER_LOGGING:
        core.SERVER_LOGGING[option] = state
        print("[LOGGER] logging-option ",f'"{option}" set to {state}.')
    else:
        print("[LOGGER] Error there is no logging-option called",f'"{option}".')