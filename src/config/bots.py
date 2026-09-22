from enum import Enum


class Bots(Enum):
    PRUEBAS = {
        'agente1': 's'
    }
    
    BBVA_COBRANZA = {
        '3d2de221-a5f8-4156-bc1f-a7d2fc45bef6': 'SPC_TDC_Moras_Altas',
        '00859262-febf-41d8-b231-8b938220a613': 'SPC_Mia_Hipotecario',
        '665d7311-d1b2-46ef-912a-81fa7a58c875': 'SPC_Mia_Consumo',
        '880f34f9-d9a6-4616-a6b0-2ba9a717ae4e': 'SPC_Mia_Reestructura',
        '2f68a7cb-e2c8-4df0-86a9-c224ca26c4b0': 'SPC_Mia_TDC',
        '44395ce7-8b92-44f0-9b00-d96ee0d52c5d': 'SPC_Mia_AUTO',
        '51870303-e5a2-4760-a08c-f67950a645ad': 'SPC_Mia_Seguimiento',
        'e72a525f-8e75-4b52-8bbe-af951064d25d': 'SPC_Muvox_Hipotecario',
        'e5aa48f7-8042-4595-9157-831702bb1679': 'SPC_Muvox_Consumo',
        '78080e23-8a7b-473a-8c3c-7e79b69767b7': 'SPC_Muvox_Reestructura',
        '4e411af5-43fd-4ad8-9847-1544701117e2': 'SPC_Muvox_TDC',
        'ead23278-6f54-4ed1-bdcc-a1c674b6df47': 'SPC_Muvox_AUTO',
        'a7c57a43-0470-4abb-9dde-9d775fb8aa94': 'SPC_Muvox_Seguimiento',
        
        '369a312d-319d-429c-beea-5fbd4f35ca1c': 'DESPACHO_TDC',
        '81f44f48-5f60-40ce-8a5c-47cd7ca83144': 'DESPACHO_Consumo',
        '0ef5bcc9-f188-46d0-b6fc-e673ca41332d': 'DESPACHO_Auto',
        '2811808e-51bb-4da2-a76d-aab52ca33d60': 'DESPACHO_QA',
        '1bee13c4-1f2e-4653-90b1-f5123a04d9b6': 'DESPACHO_Refil_TDC',
        'a15ed95d-5c54-4e7e-8043-2de8b8ac411d': 'DESPACHO_IN',
        '48906b30-ccd6-420a-b43b-4850903f229e': 'DESPACHO_Recuperacion'
    }
    
    BBVA_RETARGETING = {
        'c5b73914-6481-4d52-bf99-3249348a216f': 'WELCOME_Credito_Auto',
        '5b45da96-63ef-4628-9114-0ecaa4b3a476': 'WELCOME_Hogar',
        'ca52b2db-3013-4e6c-9165-bdc7e0d9e9cc': 'WELCOME_Vida',
        '55ff4ed8-4f72-4701-98ba-07bd56bd1de3': 'WELCOME_Auto',
        
        'ee089a02-73af-4484-a9d8-adf57dcd8c64': 'SERVICE_Saldo',
        'ddbdc9b2-3283-408b-b491-ef416139ce8a': 'SERVICE_Sin_Acceso',
        '0d481d55-9b3a-48b2-9b11-630808960f04': 'SERVICE_SPEI',
        '0e725f6f-f2f2-4f84-bcc2-edbce3da356e': 'SERVICE_Fundacion',
        '9e38bcbf-133b-4833-9c27-584ae34fe5c0': 'SERVICE_Promociones',

        '231c9fed-b5d7-4c2a-81d3-e4da1a512fe4': 'RTG_TDC',
        'afd0cde5-84d5-4fdc-9859-cea5c53a9e13': 'RTG_TDC_Recuperacion',
        '030ebd5e-c030-4404-afff-96f990bb61da': 'RTG_Portabilidad',
        '320f72cf-37b5-457c-a773-d587314f2246': 'RTG_EFI',
        'a53fcbd8-8a06-4f94-a9d0-b444f6c32577': 'RTG_Consumo_ATM',
        'd6f4e854-4082-43e3-aadf-8b3713163692': 'RTG_Consumo_Recuperacion',
        '88319388-76ac-4d1e-a9c7-48e60a538717': 'RTG_QA',
        '78b9011c-78ad-44ba-be03-4e3f2da4eba4': 'RTG_Consumo',
    }