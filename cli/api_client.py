from typing import List, Union, Dict
import starlette.status as status
from fastapi import HTTPException
import requests
from requests.models import Response
from urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # type: ignore


class ApiRunner():
    base_url = ''


    def __init__(self, base_url) -> None:
        self.base_url = base_url
    

    def call(self, endpoint: str, method: str, ex_code: int, ex_reason: str, payload: Union[Dict, List, None] = None) -> Union[Response, None]:
        url = f'{self.base_url}{endpoint}'
        headers =  {'Content-Type': 'application/json; charset=utf-8'}
        proxies = {
            'http': 'http://127.0.0.1:8085',
            'https': 'http://127.0.0.1:8085',
        }

        with requests.Session() as client_session:      
            if method == 'POST':
                response = client_session.post(url, headers=headers, json=payload, proxies=proxies)
            elif method == 'PUT':
                response = response = client_session.put(url, headers=headers, json=payload, proxies=proxies)
            else:
                response = client_session.get(url, headers=headers, proxies=proxies)
            
            if not response or not response.ok:
                raise HTTPException(
                    status_code=ex_code, detail=ex_reason
                )
            return response                
