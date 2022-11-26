import urllib.parse
import re
import uuid
from . import core

class HTTPMessageType:
    GET     = 0
    POST    = 1
    PUT     = 2
    HEAD    = 3
    DELETE  = 4
    TRACE   = 5
    OPTIONS = 6
    CONNECT = 7
    choose = {'GET':0,'POST':1,'PUT':2,'HEAD':3,'DELETE':4,'TRACE':5,'OPTIONS':6,'CONNECT':7}
    @staticmethod
    def getName(type:int) -> str:
        return['GET', 'POST', 'PUT', 'HEAD', 'DELETE', 'TRACE', 'OPTIONS','CONNECT'][type]

class HTTPStatus:
    OK = 200
    ERROR = 404
    NO_CONTENT = 204
    @staticmethod
    def getString(type:int) -> str:
        return {200:'200 OK',404:'404 Not Found',204:'204 No Content'}[type]

class HTTPProtocol:
        HTTP_1_0 = "HTTP/1.0"
        HTTP_1_1 = "HTTP/1.1"

def parse_post(args,msg,session_id)-> dict:

    '''Parses payload of a POST request and sends it back as a dictionary'''
    
    result = {}
    result['session_id'] = session_id
    parts = re.split('\n\n|\r\n\r\n',msg)  
    if len(parts) > 1:
        payload = parts[1]
        if 'content-type' in args:
            content_type = args['content-type']
            result['content-type'] = content_type
            if  content_type == 'application/x-www-form-urlencoded':
                key_value = payload.split('&')
                for pair in key_value:
                    p = pair.split('=')
                    if len(p) == 2:
                        result[urllib.parse.unquote(p[0])] = urllib.parse.unquote(p[1])
            else:
                result['payload'] = payload         
    return result

def get_query_string(path) ->dict:
    parts = re.split('\?(?!.+\/)',path)
    outer_args = {}
    inner_args = {}
    if len(parts) > 1:
        query_string = parts[-1]
        key_value = query_string.split('&')
        for pair in key_value:
            p = pair.split('=')
            if len(p) == 2:
                inner_args[urllib.parse.unquote(p[0])] = urllib.parse.unquote(p[1])
    outer_args['query_string'] = inner_args
    return outer_args
                    
def get_cookies(token:dict) -> dict:
    res = {}
    try:
        if 'cookie' in token:
            content = token['cookie']
            vars = content.split(';')
            for val in vars:
                pair = val.split('=')
                if len(pair) > 1:
                    res[pair[0].strip()] = pair[1].strip()
    except Exception as e:
        print(e)
    return res

def get_notfound_msg(err:str) -> str:
    CONTENT = 'Page not found.'
    HEADER = err
    length =len(CONTENT.encode('utf-8'))
    HEADER += 'connection: close\n'
    HEADER += f"content-length: {length}\n"
    HEADER += 'content-language: en\n'
    HEADER += f"content-type: text/plain\n"
    HEADER += '\n'+CONTENT  
    return HEADER          

            
def parse_message(message:str) -> bytes:
    ERROR_0 = f'{HTTPProtocol.HTTP_1_1} {HTTPStatus.getString(HTTPStatus.ERROR)}\n\r'
    ERROR = f'{HTTPProtocol.HTTP_1_1} {HTTPStatus.getString(HTTPStatus.NO_CONTENT)}\n\r'
    session_id = str(uuid.uuid1().int)
    if len(message) == 0:
        return ERROR_0.encode('utf-8')
    lines = re.split('\n|\r\n',message)
    if len(lines) == 0:
        return ERROR_0.encode('utf-8')
    tokens_0 = re.split('\s',lines[0])
    if len(tokens_0) != 3:
        return ERROR_0.encode('utf-8')
    HEADER = ''
    CONTENT = ''
    TYPE = HTTPMessageType.choose[tokens_0[0]]
    PATH = tokens_0[1]
    PROTOCOL = tokens_0[2]
    tokens_1 = {}
    SESSION_COOKIE = ''
    for line in lines:
        token = re.split(':',line)
        if len(token) == 2:
            tokens_1[token[0].strip().lower()] = token[1].strip()
    COOKIES = get_cookies(tokens_1)
    QUERY_STRING_ARGS = get_query_string(PATH)
    if len(PATH.split('?')) > 1:
        PATH = ''.join(PATH.split('?')[:-1])
    if 'session_id' not in COOKIES:
        SESSION_COOKIE = f'set-cookie: session_id={session_id}\n'
    else:
        session_id = COOKIES['session_id']
    if session_id not in core.SESSIONS:
        core.SESSIONS[session_id] = []
    if TYPE == HTTPMessageType.GET:
        if PATH not in core.PAGES:
            return get_notfound_msg(ERROR_0).encode('utf-8')
        mimetype = core.PAGES[PATH][1]
        payload = ''
        if core.PAGES[PATH][0].__code__.co_argcount == 1:
            payload = core.PAGES[PATH][0]({**COOKIES, **QUERY_STRING_ARGS})
        else:
            payload = core.PAGES[PATH][0]()
        if mimetype == 'text/css':
             CONTENT = '\n'+re.sub('(?<=;|{|})\s+','', payload)
        else:
            CONTENT = payload
        HEADER += f'{HTTPProtocol.HTTP_1_1} {HTTPStatus.getString(HTTPStatus.OK)}\n'
        HEADER += f'accept-ranges: bytes\n'
        length = 0
        if mimetype in ['video/mp4']:
            length = len(CONTENT)
        else:
            length = len(CONTENT.encode('utf-8'))
        HEADER += f"content-length: {length}\n"
        HEADER += 'content-language: en\n'
        HEADER += f"content-type: {mimetype}\n"
        HEADER += SESSION_COOKIE
        
    if TYPE == HTTPMessageType.POST:
        if PATH not in core.POST_HANDLER:
            return get_notfound_msg(ERROR_0).encode('utf-8')
        mimetype = core.POST_HANDLER[PATH][1]
        args = parse_post(tokens_1,message,session_id)
        if mimetype == 'text/css':
             CONTENT = '\n'+re.sub('(?<=;|{|})\s+','', core.POST_HANDLER[PATH][0]({**args,**QUERY_STRING_ARGS}))
        else:
            CONTENT = core.POST_HANDLER[PATH][0]({**args,**QUERY_STRING_ARGS})
        HEADER += f'{HTTPProtocol.HTTP_1_1} {HTTPStatus.getString(HTTPStatus.OK)}\n'
        HEADER += f'accept-ranges: bytes\n'
        length = 0
        if mimetype in ['video/mp4']:
            length = len(CONTENT)
        else:
            length = len(CONTENT.encode('utf-8'))
        HEADER += f"content-length: {length}\n"
        HEADER += 'content-language: en\n'
        HEADER += f"content-type: {mimetype}\n"
        HEADER += SESSION_COOKIE
    if mimetype in ['video/mp4']:
        return (HEADER+"\n").encode('utf-8') + CONTENT 
    return (HEADER+"\n"+CONTENT).encode('utf-8')