from .logger import logger
import time
from django.utils.deprecation import MiddlewareMixin
import socket
from api.settings import DEBUG


class LoggerMiddlware(MiddlewareMixin):

    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        content_type = response.get("content-type")
        if content_type == 'application/json':
            if getattr(response, 'streaming', False):
                response_body = '<<<Streaming>>>'
            else:
                response_body = response.content
        else:
            response_body = '<<<Not JSON>>>'
            
        logger.debug(response_body)
        log_data = {
            'user': request.user.pk,

            'remote_address': request.META['REMOTE_ADDR'],
            'server_hostname': socket.gethostname(),

            'request_method': request.method,
            'request_path': request.get_full_path(),

            'response_status': response.status_code,
            'response_body': response_body,

            'run_time': time.time() - request.start_time,
        }
        if DEBUG:
            logger.debug("logging request and response", extra=log_data)

        return response
