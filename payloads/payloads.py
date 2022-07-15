from enum import Enum


class Payloads(Enum):
    TEMPLATE = {
        '3.1.0': {
            "header": {
                "versionInfo": {
                    "api": "3.1.0",
                    "applianceType": "Emulator",
                    "applianceSpec": ""
                },
                "equipmentType": "FRYER"
            }
        },
        '3.2.0': {
            "header": {
                "versionInfo": {
                    "api": "3.2.0",
                    "applianceType": "Emulator",
                    "applianceSpec": ""
                },
                "equipmentInfo": {
                    "type": "FRYER"
                }
            }
        }
    }

class APIVersionInfo(Enum):
    API_VERSION = {
        'legacy': '3.1.0',
        'latest': '3.2.0'
    }


class PayloadAttributes(Enum):
    BODY = [
        'header'
    ]

    HEADER = [
        'versionInfo',
        'guid',
        'source',
        'destination',
        'correlationId',
        'dateTime',
        'equipmentType',
        'type'
    ]

    EQUIPMENT = [
        'type'
    ]

    VERSION = [
        'api',
        'applianceType',
        'applianceSpec',
    ]

    BLINK = [
        'time',
        'all',
        'spec'
    ]


class LEDS(Enum):
    SPEC = {
        '3.1.0': [
            'WIFI_LED',
            'BT_LED',
            'PWR_LED',
            'DISPLAY',
        ],
        '3.2.0': [
            'WIFI_LEDS',
            'WIFI_LEDS_CONTROLLER_DISPLAY'
        ]
    }


class PayloadTypes(Enum):
    PTYPE = {
        'blink_request': 'BLINK_REQUEST',
        'blink_ack': 'BLINK_ACK',
        'blink_success': 'BLINK_SUCCESS',
        'blink_fail': 'BLINK_FAIL',
        'cook_start': 'COOK_START',
        'cook_quantity': 'COOK_QUANTITY',
        'cook_complete': 'COOK_COMPLETE',
        'cook_cancel': 'COOK_CANCEL',
        'cook_complete_ack': 'COOK_COMPLETE_ACK',
        'ack': 'ACK',
        'heart_beat': 'HEARTBEAT'
    }


class BlinkStatus(Enum):
    STATUS = {
        'start': 'Blink Starting',
        'success': 'Blink Complete',
        'fail': 'Blink Failed'
    }
