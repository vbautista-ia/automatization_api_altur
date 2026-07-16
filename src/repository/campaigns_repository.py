import logging

import requests

from answered_by import AnsweredBy
from configuration import config as cfg 
# import get_api_key, get_url_base
from configuration.platforms import Platforms
from status import StatusCall, StatusCampaign


class CampaignRepository:
    LIST_CAMPAIGNS = 'campaigns'
    RETRIVE_CAMPAING = 'campaigns/{id}'
    URL_LIST_CAMPAIGNS_CONTACTS = 'https://api.altur.io/api/v1.0/campaigns/{id}/contacts'
    CAMPAING_CALLS = '{id}/calls'

    def __init__(self, platform: Platforms):
        self.TOKEN = cfg.get_api_key(platform)
        self.URL_BASE = cfg.get_url_base()
        self.HEADERS = { 'Authorization': f"api-key {self.TOKEN}" }

    def list_campigns(self, startDate = None, endDate = None, pageSize = 100, cursor = None, agentId = None, status:StatusCampaign = None, archived = False):
        params = {
            'startDate': startDate,
            'endDate': endDate,
            'pageSize': pageSize,
            'cursor': cursor,
            'agentId': agentId,
            'status': status.value if status else None, 
            'integration': 'phone_call',
            'archived': archived,
        }

        query_params = self.to_query_params(params)

        response = requests.get(f"{self.URL_BASE}{self.LIST_CAMPAIGNS}", params=query_params, headers=self.HEADERS)
        logging.info(f"Get campaigns: {response.url}")

        if response.status_code == 200:
            return response.json()
        
        logging.warning(f"Error {response.status_code}, message: {response.text}. {response.url}")
        return None

    def retrive_campign(self, id_campaign: str):
        url = f"{self.URL_BASE}{self.RETRIVE_CAMPAING.format(id=id_campaign)}"

        response = requests.get(url, headers=self.HEADERS)
        logging.info(f"Get campaigns: {response.url}")

        if response.status_code == 200:
            return response.json()
        
        logging.warning(f"Error {response.status_code}, message: {response.text}. {response.url}")
        return None
    
    def list_campaign_contacts(self, id_campaign: str, pageIndex, status: str = None, pageSize = 100):
        params = {
            'status': status if status else None,
            'pageSize': pageSize,
            'pageIndex': pageIndex,
        }
        url = self.URL_LIST_CAMPAIGNS_CONTACTS.format(id=id_campaign)

        response = requests.get(url, params=params, headers=self.HEADERS)
        logging.info(f"List campaign contacts: {response.url}")

        if response.status_code == 200:
            return response.json()
        
        logging.warning(f"Error {response.status_code}, message: {response.text}. {response.url}")
        return None

    def get_campaign_calls(self, id_campaign, pageIndex, startDate = None, endDate = None, pageSize = 100, answeredBy: AnsweredBy = None, status: StatusCall = None):
        params = {
            'answeredBy': answeredBy.value if answeredBy else None,
            'startDate': startDate,
            'endDate': endDate,
            'pageSize': pageSize,
            'pageIndex': pageIndex,
            'status': status.value if status else None,
        }

        query_params = self.to_query_params(params)
        url = f"{self.URL_BASE}{self.URL_CAMPAING_CALLS.format(id=id_campaign)}"
        
        response = requests.get(url, params=query_params, headers=self.HEADERS)
        logging.info(f"Get campaign calls: {response.url}")

        if response.status_code == 200:
            return response.json()
        
        logging.warning(f"Error {response.status_code}, message: {response.text}. {response.url}")
        return None
        
    def to_query_params(self, params: dict):
        return {key: value for key, value in params.items() if value not in (None, '')}