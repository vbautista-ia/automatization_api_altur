from enum import Enum


class Bots(Enum):
    PRUEBAS = {
        'agente1': 's'
    }
    
    BBVA_COBRANZA = {
        '00859262-febf-41d8-b231-8b938220a613': 'SPC_HIPOTECARIO',
        '2f68a7cb-e2c8-4df0-86a9-c224ca26c4b0': 'SPC_TDC',
        '665d7311-d1b2-46ef-912a-81fa7a58c875': 'SPC_CONSUMO',
        '880f34f9-d9a6-4616-a6b0-2ba9a717ae4e': 'SPC_REESTRUCTURA_TDC',
        'a7c57a43-0470-4abb-9dde-9d775fb8aa94': 'SPC_SEGUIMIENTO',
        '44395ce7-8b92-44f0-9b00-d96ee0d52c5d': 'SPC_AUTO',
        
        '81f44f48-5f60-40ce-8a5c-47cd7ca83144': 'COBRANZA_CONSUMO',
        '369a312d-319d-429c-beea-5fbd4f35ca1c': 'COBRANZA_TDC',
        '1bee13c4-1f2e-4653-90b1-f5123a04d9b6': 'COBRANZA_REFIL_TDC',
        '0ef5bcc9-f188-46d0-b6fc-e673ca41332d': 'COBRANZA_AUTO',
        '2811808e-51bb-4da2-a76d-aab52ca33d60': 'COBRANZA_QA',
        'a15ed95d-5c54-4e7e-8043-2de8b8ac411d': 'COBRANZA_IN',
        '48906b30-ccd6-420a-b43b-4850903f229e': 'COBRANZA_RECUPERACION'
    }
    
    BBVA_RETARGETING = {
        '231c9fed-b5d7-4c2a-81d3-e4da1a512fe4': 'TDC',
        '78b9011c-78ad-44ba-be03-4e3f2da4eba4': 'CONSUMO',
        'a53fcbd8-8a06-4f94-a9d0-b444f6c32577': 'CONSUMO ATM',
    }