from datetime import date, datetime, timedelta

import httpx

from config.platforms import Platforms
from repository.campaigns_repository import CampaignRepository
from repository.data_importer_repository import DataImporterRepository
from utils.utils import iso_to_datetime


class DataImporterService:
    def __init__(self, data_repository: DataImporterRepository):
        self.__data_epository = data_repository
        self.__campaign_repository = CampaignRepository(Platforms.BBVA_COBRANZA)
    
    async def download_data(self):
        after = date.today() - timedelta(days=1)
        start = datetime(after.year, after.month, after.day, 5, 0, 0).isoformat(' ')
        end = datetime(after.year, after.month, after.day, 23, 59, 59).isoformat(' ')
        cursor = None
        has_next_campaigns = True
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while has_next_campaigns:
                campaigns_response = await self.__campaign_repository.list_campigns(client, started_after=start, started_before=end, cursor=cursor)
                campaigns = campaigns_response.get('campaigns')
                if campaigns:
                    data_campaigns = [{
                        'id': campaign.get('id'),
                        'name': campaign.get('name', ''),
                        'description': campaign.get('description', ''),
                        'status': campaign.get('status'),
                        'created_at': iso_to_datetime(campaign.get('created_at')),
                        'started_at': iso_to_datetime(campaign.get('started_at')),
                        'ended_at': iso_to_datetime(campaign.get('ended_at')),
                        'agent': campaign.get('agent', {}).get('name', ''),
                        'timezone': campaign.get('timezone', ''),
                        'retries': campaign.get('retries'),
                        'archived': campaign.get('archived'),
                        'first_message': campaign.get('first_message', '')
                    } for campaign in campaigns]
                    
                    self.__data_epository.insert(data_campaigns, 'campaings')
                    
                    for camapaign in campaigns:
                        campaign_id = camapaign.get('id')
                        has_next_contacts = True
                        page_index_contacts = 0
                        
                        while has_next_contacts:
                            contacts_response = await self.__campaign_repository.list_campaign_contacts(client, campaign_id, page_index_contacts)
                            
                            contacts = contacts_response.get('contacts')
                            if contacts:
                                data_contacts = [{
                                    'id': contact.get('id'),
                                    'f_id': contact.get('f_id'),
                                    'name': contact.get('name'),
                                    'contact': contact.get('contact'),
                                    'status': contact.get('status'),
                                    'context': contact.get('context'),
                                    'retries': contact.get('retries'),
                                    'has_follow_up': contact.get('has_follow_up'),
                                    'call_count': contact.get('call_count'),
                                    'billed_duration': contact.get('billed_duration'),
                                    'last_call_at': iso_to_datetime(contact.get('last_call_at')),
                                    'extracted_data': contact.get('extracted_data'),
                                    'tags': contact.get('tags'),
                                    'campaign_id': campaign_id
                                } for contact in contacts]
                                
                                self.__data_epository.insert(data_contacts, 'contacts')
                            has_next_contacts = contacts_response.get('pagination', {}).get('has_next')
                            page_index_contacts = contacts_response.get('pagination', {}).get('next_page')
                            
                        
                        has_next_calls = True
                        page_index_calls = 0
                        while has_next_calls:
                            calls_response = await self.__campaign_repository.get_campaign_calls(client, campaign_id, page_index_calls)
                            
                            calls = calls_response.get('calls')
                            if calls:
                                data_calls = [{
                                    'id': call.get('id'),
                                    'type': call.get('type'),
                                    'status': call.get('status'),
                                    'answered_by': call.get('answered_by'),
                                    'create_at': iso_to_datetime(call.get('create_at')),
                                    'started_at': iso_to_datetime(call.get('started_at')),
                                    'ended_at': iso_to_datetime(call.get('ended_at')),
                                    'ended_by': call.get('ended_by') or None,
                                    'ended_reason': call.get('ended_reason'),
                                    'duration': call.get('duration'),
                                    'billed_duration': call.get('billed_duration'),
                                    'campaign_id': campaign_id,
                                    'contact_id': call.get('contact', {}).get('id')
                                } for call in calls]
                                
                                self.__data_epository.insert(data_calls, 'calls')
                            
                            has_next_calls = calls_response.get('pagination', {}).get('has_next')
                            page_index_calls = calls_response.get('pagination', {}).get('next_page')
                has_next_campaigns = campaigns_response.get('pagination', {}).get('has_next')
                cursor = campaigns_response.get('pagination', {}).get('next_cursor')