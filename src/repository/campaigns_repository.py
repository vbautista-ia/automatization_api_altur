import asyncio
import logging
from ssl import SSLError

import httpx
import requests

from answered_by import AnsweredBy
from configuration import config as cfg 
from configuration.platforms import Platforms
from status import StatusCall, StatusCampaign
 

class CampaignRepository:
    LIST_CAMPAIGNS = 'campaigns'
    RETRIVE_CAMPAING = 'campaigns/{id}'
    CAMPAIGNS_CONTACTS = 'campaigns/{id}/contacts'
    CAMPAING_CALLS = 'campaigns/{id}/calls'

    def __init__(self, platform: Platforms):
        self.TOKEN = cfg.get_api_key(platform)
        self.URL_BASE = cfg.get_url_base()
        self.HEADERS = { 'Authorization': f"api-key {self.TOKEN}" }

    async def list_campigns(self, client: httpx.AsyncClient, started_after = None, started_before = None, pageSize = 100, cursor = None, agentId = None, status:StatusCampaign = None):
        params = {
            'pageSize': pageSize,
            'startedAfter': started_after,
            'startedBefore': started_before,
            'cursor': cursor,
            'agentId': agentId,
            'status': status.value if status else None, 
        }
        query_params = self.to_query_params(params)
        url = f"{self.URL_BASE}{self.LIST_CAMPAIGNS}"
        try:
            response = await client.get(url=url, params=query_params, headers=self.HEADERS)
            if response.status_code == 200:
                return response.json()
            logging.warning(f"Error {response.status_code}, message: {response.text}. {response.url}")
        except (SSLError, httpx.ReadTimeout, httpx.ConnectError) as e:
            logging.info(f"ocurrio un error {e}")
            await asyncio.sleep(1)
            try:
                response = await client.get(url=url, params=params, headers=self.HEADERS)
                logging.info(f"Retrive get campaigns: {response.url}")
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                logging.warning(f"Error Retrive {response.status_code}, message: {response.text}. {response.url}")
        return {}

    def retrive_campign(self, id_campaign: str):
        url = f"{self.URL_BASE}{self.RETRIVE_CAMPAING.format(id=id_campaign)}"

        response = requests.get(url, headers=self.HEADERS)
        logging.info(f"Get campaigns: {response.url}")

        if response.status_code == 200:
            return response.json()
        
        logging.warning(f"Error {response.status_code}, message: {response.text}. {response.url}")
        return None
    
    async def list_campaign_contacts(self, client: httpx.AsyncClient, id_campaign: str, pageIndex, status: str = None, pageSize = 100):
        params = {
            'status': status if status else None,
            'pageSize': pageSize,
            'pageIndex': pageIndex,
        }
        url = f"{self.URL_BASE}{self.CAMPAIGNS_CONTACTS.format(id=id_campaign)}"
        try:
            response = await client.get(url, params=params, headers=self.HEADERS)

            if response.status_code == 200:
                return response.json()
            logging.warning(f"Error {response.status_code}, message: {response.text}. {response.url}")
        except (SSLError, httpx.ReadTimeout, httpx.ConnectError) as e:
            await asyncio.sleep(1)
            logging.info(f"ocurrio un error {e}")
            try:
                response = await client.get(url, params=params, headers=self.HEADERS)
                logging.info(f"Retrive list campaign contacts: {response.url}")

                if response.status_code == 200:
                    return response.json()
            except (SSLError, httpx.ReadTimeout, httpx.ConnectError) as e:
                logging.warning(f"Error {response.status_code}, message: {response.text}. {response.url}")
        return {}

    async def get_campaign_calls(self, client: httpx.AsyncClient, id_campaign, pageIndex: int, startDate = None, endDate = None, pageSize = 100, answeredBy: AnsweredBy = None, status: StatusCall = None):
        params = {
            'answeredBy': answeredBy.value if answeredBy else None,
            'startDate': startDate,
            'endDate': endDate,
            'pageSize': pageSize,
            'pageIndex': pageIndex,
            'status': status.value if status else None,
        }

        query_params = self.to_query_params(params)
        url = f"{self.URL_BASE}{self.CAMPAING_CALLS.format(id=id_campaign)}"
        
        response = await client.get(url, params=query_params, headers=self.HEADERS)

        if response.status_code == 200:
            return response.json()
        
        logging.warning(f"Error {response.status_code}, message: {response.text}. {response.url}")
        return {}
        
    def to_query_params(self, params: dict):
        return {key: value for key, value in params.items() if value not in (None, '')}