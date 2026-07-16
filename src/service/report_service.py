from collections import defaultdict
from datetime import datetime
import logging
import os
import time
from fastapi import APIRouter
import openpyxl
import pandas as pd

from answered_by import AnsweredBy
from configuration.bots import Bots
from configuration.platforms import Platforms
from repository.campaigns_repository import CampaignRepository
from utils.utils import get_bots_by_paltform, get_bots_start_with, to_date_iso

class Account():
    inicio: str
    fin: str
    fecha_inicio_busqueda: str
    fecha_fin_busqueda: str
    cuentas: list[str]

class ReportService:
    def __init__(self, platform:Platforms):
        self.PLATFORM = platform
        self.campaign_repository = CampaignRepository(self.PLATFORM)

    def search_transaction_by_account(self, accounts: list[str], date_start:str, date_end:str, agent:str = None):
        campaigns: list[str] = []
        bots = Bots[self.PLATFORM.name].value
        agents = [key for key, bot in bots.items() if bot.startswith(agent)] if agent else None

        try:
            start = datetime.strptime(date_start, "%d-%m-%Y %H:%M:%S")
            end = datetime.strptime(date_end, "%d-%m-%Y %H:%M:%S")

            if start > end:
                raise ValueError(f"La fecha de inicio ({date_start}) debe ser menor a la fecha final ({date_end})")
            
            iso_start = start.isoformat() + 'Z'
            iso_end = end.isoformat() + 'Z'

            has_next = True
            cursor = None
            while has_next:
                result = self.campaign_repository.list_campigns(cursor=cursor, startDate=iso_start, endDate=iso_end)
                time.sleep(0.1)

                for campaign in result['campaigns']:
                    retrive_campaign = self.campaign_repository.retrive_campign(campaign['id'])
                    # print(retrive_campaign)
                    if agents and retrive_campaign['campaign']['agent']['id'] in agents:
                        campaigns.append(campaign['id'])
                        logging.info(f">>>>>> Agent name: {retrive_campaign['campaign']['agent']['name']}")
                    else:
                        campaigns.append(campaign['id'])

                # print(result['campaigns'])
                # if agents:
                #     campaigns.extend([campaign['id'] for campaign in result['campaigns'] if campaign['agent']['id'] in agents])
                # else:
                #     campaigns.extend([campaign['id'] for campaign in result['campaigns']])
                # >campaigns.extend([campaign['id'] for campaign in result['campaigns'] if campaign['name'].startswith('BBVA_DESP')])

                # campaigns.extend([campaign['id'] for campaign in result['campaigns']])

                if result['pagination']['has_next']:
                    cursor = result['pagination']['next_cursor']
                has_next = result['pagination']['has_next']
            
            logging.info(f"Searching in {len(campaigns)} campaigns, from {campaigns[:3]} to {campaigns[-3:]}"
                         if len(campaigns) > 3 else 
                         f"Searching in {len(campaigns)} campaigns {campaigns}")
            calls = []
            count = 0
            for id_campaign in campaigns:
                count +=1
                logging.info(f"<<<< Search {count} of {len(campaigns)} >>>>")

                has_next = True
                next_page = 0
                while has_next:
                    result = self.campaign_repository.get_campaign_calls(id_campaign, next_page)
                    time.sleep(0.1)

                    for call in result['calls']:
                        if call['contact']['f_id'] in accounts:
                            calls.append({
                                'account': call['contact']['f_id'],
                                'id': call['id'],
                                'created_at': call['created_at'],
                                'started_at': call['started_at'],
                                'ended_at': call['ended_at'],
                                'duration': call['duration'],
                                'billed_duration': call['billed_duration'],
                                'name': call['contact']['name'],
                                'phone_number': call['contact']['phone_number'],
                                'tags': call['tags'],
                                'recording_url': call['recording_url']
                            })
                            logging.info(f"<<< concidence: {call['contact']['f_id']} >>>")
                    
                    has_next = result['pagination']['has_next']
                    next_page = result['pagination']['next_page']
            
            if not calls:
                logging.info('Not found calls to accounts')
                return


            df = pd.DataFrame(calls)

            tags_df = df['tags'].str.join('|').str.get_dummies()
            tags_df = tags_df.astype(bool)
            df = df.join(tags_df)
            df = df.drop(columns=['tags'])

            file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
            path = os.path.join(self.PLATFORM.value)
            os.makedirs(path, exist_ok=True)   
            path = os.path.join(path, file_name)
        
            df.to_excel(path, sheet_name='calls', index=False, engine="openpyxl")
            
            logging.info('End search calls by accounts')
        except ValueError as e:
            logging.error(f"Error de valor/formato: {e}")
        except TypeError as e:
            logging.error(f"Error de tipo de dato: {e}")        

    def get_total_accounts(self, agent_start: str | None, start, end) -> dict[str, dict[str, int]]:
        total_accounts: defaultdict[str, int] = defaultdict(lambda: 0)
        # ids_campaigns: defaultdict[str, list[str]] = defaultdict(list)

        bots = Bots[self.PLATFORM.name].value
        agents = {key: bot for key, bot in bots.items() if bot.startswith(agent_start)} if agent_start else bots

        has_nexts_campaigns = True
        cursor = None
        while has_nexts_campaigns:
            response = self.campaign_repository.list_campigns(cursor=cursor, startDate=start, endDate=end)

            for campaign in response['campaigns']:
                retrive_campaign = self.campaign_repository.retrive_campign(campaign['id'])
                
                id_agent = retrive_campaign['campaign']['agent']['id']
                if agents and id_agent in agents:
                    page_index = 0
                    has_next_contact = True
                    while has_next_contact:
                        contacts = self.campaign_repository.list_campaign_contacts(campaign['id'], page_index)

                        total_accounts[agents.get(id_agent, 'Desconocido')] += contacts['total_count']
                        page_index = contacts['pagination']['next_page']
                        has_next_contact = contacts['pagination']['has_next']
            
            cursor = response['pagination']['next_cursor']
            has_nexts_campaigns = response['pagination']['has_next']

        date_start = datetime.date(datetime.fromisoformat(start)).strftime("%d/%m/%Y")
        return { 'fecha':date_start, 'total_cuentas': total_accounts}

    def search_by_account(self, accounts: list[Account], date_start:str, date_end:str, agent:str = None):
        bots = Bots[self.PLATFORM.name].value
        agents = [key for key, bot in bots.items() if bot.startswith(agent)] if agent else None
        campaigns: list[str] = []
        
        # for account in accounts:
        #     account.
            



        try:
            start = datetime.strptime(date_start, "%d-%m-%Y %H:%M:%S")
            end = datetime.strptime(date_end, "%d-%m-%Y %H:%M:%S")

            if start > end:
                raise ValueError(f"La fecha de inicio ({date_start}) debe ser menor a la fecha final ({date_end})")
            
            iso_start = start.isoformat() + 'Z'
            iso_end = end.isoformat() + 'Z'

            has_next = True
            cursor = None
            while has_next:
                result = self.campaign_repository.list_campigns(cursor=cursor, startDate=iso_start, endDate=iso_end)
                time.sleep(0.1)

                for campaign in result['campaigns']:
                    retrive_campaign = self.campaign_repository.retrive_campign(campaign['id'])
                    # print(retrive_campaign)
                    if agents and retrive_campaign['campaign']['agent']['id'] in agents:
                        campaigns.append(campaign['id'])
                        logging.info(f">>>>>> Agent name: {retrive_campaign['campaign']['agent']['name']}")
                    else:
                        campaigns.append(campaign['id'])

                # print(result['campaigns'])
                # if agents:
                #     campaigns.extend([campaign['id'] for campaign in result['campaigns'] if campaign['agent']['id'] in agents])
                # else:
                #     campaigns.extend([campaign['id'] for campaign in result['campaigns']])
                # >campaigns.extend([campaign['id'] for campaign in result['campaigns'] if campaign['name'].startswith('BBVA_DESP')])

                # campaigns.extend([campaign['id'] for campaign in result['campaigns']])

                if result['pagination']['has_next']:
                    cursor = result['pagination']['next_cursor']
                has_next = result['pagination']['has_next']
            
            logging.info(f"Searching in {len(campaigns)} campaigns, from {campaigns[:3]} to {campaigns[-3:]}"
                         if len(campaigns) > 3 else 
                         f"Searching in {len(campaigns)} campaigns {campaigns}")
            calls = []
            count = 0
            for id_campaign in campaigns:
                count +=1
                logging.info(f"<<<< Search {count} of {len(campaigns)} >>>>")

                has_next = True
                next_page = 0
                while has_next:
                    result = self.campaign_repository.get_campaign_calls(id_campaign, next_page)
                    time.sleep(0.1)

                    for call in result['calls']:
                        if call['contact']['f_id'] in accounts:
                            calls.append({
                                'account': call['contact']['f_id'],
                                'id': call['id'],
                                'created_at': call['created_at'],
                                'started_at': call['started_at'],
                                'ended_at': call['ended_at'],
                                'duration': call['duration'],
                                'billed_duration': call['billed_duration'],
                                'name': call['contact']['name'],
                                'phone_number': call['contact']['phone_number'],
                                'tags': call['tags'],
                                'recording_url': call['recording_url']
                            })
                            logging.info(f"<<< concidence: {call['contact']['f_id']} >>>")
                    
                    has_next = result['pagination']['has_next']
                    next_page = result['pagination']['next_page']
            
            if not calls:
                logging.info('Not found calls to accounts')
                return


            df = pd.DataFrame(calls)

            tags_df = df['tags'].str.join('|').str.get_dummies()
            tags_df = tags_df.astype(bool)
            df = df.join(tags_df)
            df = df.drop(columns=['tags'])

            file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
            path = os.path.join(self.PLATFORM.value)
            os.makedirs(path, exist_ok=True)   
            path = os.path.join(path, file_name)
        
            df.to_excel(path, sheet_name='calls', index=False, engine="openpyxl")
            
            logging.info('End search calls by accounts')
        except ValueError as e:
            logging.error(f"Error de valor/formato: {e}")
        except TypeError as e:
            logging.error(f"Error de tipo de dato: {e}")        

    def search_account(self, accounts, date_start:str, date_end:str, agent_start_wiht:str = None, answered_by:AnsweredBy = AnsweredBy.HUMAN):
        campaigns: list[str] = []
        bots = get_bots_by_paltform(self.PLATFORM)
        agents = get_bots_start_with(bots, agent_start_wiht)

        lista = [
            {
                "cuenta": "007410027492391224",
                "inicio": "2026-07-06T09:59:05Z",
                "fin": "2026-07-06T09:59:29Z",
                "tmo": "24"
            }
        ]

        try:
            start = to_date_iso(date_start)
            end = to_date_iso(date_end)

            if start > end:
                raise ValueError(f"La fecha de inicio ({date_start}) debe ser menor a la fecha final ({date_end})")

            # has_next = True
            cursor = None
            while has_next:
                result = self.campaign_repository.list_campigns(startDate=start, endDate=end, cursor=cursor)

                for campaign in result['campaigns']:
                    retrive_campaign = self.campaign_repository.retrive_campign(campaign['id'])
                    # print(retrive_campaign)
                    id_agent = retrive_campaign['campaign']['agent']['id']
                    if id_agent in agents:
                        if accounts['start'] > campaign['created_at'] and accounts['end'] <= campaign['cycle_last_iteration_at']:
                            campaigns.append(campaign['id'])
                            logging.info(f">>>>>> Agent name: {agents[id_agent]} - Campaign: {campaign['id']} - {campaign['SPC_AUTO_10072026_4']}")

                            page_index = 0
                            next_page = True
                            while next_page:
                                calls_response = self.campaign_repository.get_campaign_calls(campaign['id'], page_index, accounts['start'], accounts['end'], answeredBy=answered_by)
                                if calls_response
                                for call in result['calls']:
                                    if call['contact']['f_id'] in accounts:
                                        calls.append({
                                            'account': call['contact']['f_id'],
                                            'id': call['id'],
                                            'created_at': call['created_at'],
                                            'started_at': call['started_at'],
                                            'ended_at': call['ended_at'],
                                            'duration': call['duration'],
                                            'billed_duration': call['billed_duration'],
                                            'name': call['contact']['name'],
                                            'phone_number': call['contact']['phone_number'],
                                            'tags': call['tags'],
                                            'recording_url': call['recording_url']
                                        })
                                        logging.info(f"<<< concidence: {call['contact']['f_id']} >>>")    


                if result['pagination']['has_next']:
                    cursor = result['pagination']['next_cursor']
                has_next = result['pagination']['has_next']
            
            logging.info(f"Searching in {len(campaigns)} campaigns, from {campaigns[:3]} to {campaigns[-3:]}"
                         if len(campaigns) > 3 else 
                         f"Searching in {len(campaigns)} campaigns {campaigns}")
            calls = []
            count = 0
            for id_campaign in campaigns:
                count +=1
                logging.info(f"<<<< Search {count} of {len(campaigns)} >>>>")

                has_next = True
                next_page = 0
                while has_next:
                    result = self.campaign_repository.get_campaign_calls(id_campaign, next_page)
                    time.sleep(0.1)

                    for call in result['calls']:
                        if call['contact']['f_id'] in accounts:
                            calls.append({
                                'account': call['contact']['f_id'],
                                'id': call['id'],
                                'created_at': call['created_at'],
                                'started_at': call['started_at'],
                                'ended_at': call['ended_at'],
                                'duration': call['duration'],
                                'billed_duration': call['billed_duration'],
                                'name': call['contact']['name'],
                                'phone_number': call['contact']['phone_number'],
                                'tags': call['tags'],
                                'recording_url': call['recording_url']
                            })
                            logging.info(f"<<< concidence: {call['contact']['f_id']} >>>")
                    
                    has_next = result['pagination']['has_next']
                    next_page = result['pagination']['next_page']
            
            if not calls:
                logging.info('Not found calls to accounts')
                return


            df = pd.DataFrame(calls)

            tags_df = df['tags'].str.join('|').str.get_dummies()
            tags_df = tags_df.astype(bool)
            df = df.join(tags_df)
            df = df.drop(columns=['tags'])

            file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
            path = os.path.join(self.PLATFORM.value)
            os.makedirs(path, exist_ok=True)   
            path = os.path.join(path, file_name)
        
            df.to_excel(path, sheet_name='calls', index=False, engine="openpyxl")
            
            logging.info('End search calls by accounts')
        except ValueError as e:
            logging.error(f"Error de valor/formato: {e}")
        except TypeError as e:
            logging.error(f"Error de tipo de dato: {e}")