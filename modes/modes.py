import asyncio
import asyncio.exceptions
import logging
import json
import copy
import uuid
import random
import arrow

from payloads.payloads import (
    APIVersionInfo,
    PayloadAttributes,
    PayloadTypes,
    BlinkStatus,
    Payloads,
    LEDS
)

from main import shutdown
from config import cfg
from logger.custom_logger import Logger

from asyncio_mqtt import Client, MqttError
from utils.utils import read_properties_file, API_PROPERTIES, VERSION_PROPERTIES

log = Logger(log_level=cfg.log_level, name=__name__).get_logger()


class Bezel:
    """
    Class Bezel will serve as the base class for Blink and Cook classes. MQTT publisher and subscriber methods are
    defined here, as well as validation methods used to verify payload attributes. Display_results, append, increment
    and calculate methods are used for reporting results at the end of cook cycle. Can also be implemented within
    blink flow if desired.
    """

    def __init__(
        self,
        bezel_mac_address: str,
        mqtt_broker_ip: str,
        mqtt_broker_port: int,
        mqtt_subscribe_topic: str,
        mqtt_publish_topic: str,
        mqtt_monitor_publish_topic: str
    ) -> None:
        """

        param bezel_mac_address [str] <xx:xx:xx:xx:xx:xx>: The specified mac address for the bezel.
            Will be used as source mac address attribute in any payloads sent from the bezel.
        param mqtt_broker_ip [str] <xxx.xxx.xxx.xxx>: The IP address of the target MQTT broker.
        param mqtt_broker_port [int] <xxxx>: The receiving port of the target MQTT broker.
        param mqtt_subscribe_topic [str] </iot/device/control>: The target MQTT subscribe topic
        param mqtt_publish_topic [str] </iot/client/control>: The target MQTT publish topic
        """

        # MQTT params
        self.bezel_mac_address = bezel_mac_address.upper()
        self.mqtt_broker_ip = mqtt_broker_ip
        self.mqtt_broker_port = mqtt_broker_port
        self.mqtt_subscribe_topic = mqtt_subscribe_topic
        self.mqtt_publish_topic = mqtt_publish_topic
        self.mqtt_monitor_publish_topic = mqtt_monitor_publish_topic

        self.client_id = f'Wi-Fi Bezel Emulator {self.bezel_mac_address}'
        self.message_queue = list()
        self.api_version = read_properties_file(API_PROPERTIES)

        self.results = Results()

    def validate_bezel_mac(self, target_payload: dict) -> bool:
        if target_payload['header']['destination'].upper() == self.bezel_mac_address:
            return False
        else:
            log.setLevel(logging.DEBUG)
            log.debug(f'Incoming payload for {target_payload["header"]["destination"]} '
                      f'!= Bezel Mac: {self.bezel_mac_address}')
            return True

    def build_heart_beat(self):
        heart_beat = copy.deepcopy(Payloads.TEMPLATE.value[self.api_version])
        heart_beat['header']['versionInfo']['api'] = self.api_version
        heart_beat['header']['versionInfo']['applianceSpec'] = read_properties_file(VERSION_PROPERTIES)

        heart_beat['header']['guid'] = str(uuid.UUID(int=random.Random().getrandbits(128)))
        heart_beat['header']['destination'] = '00:00:00:00:00:00'
        heart_beat['header']['source'] = self.bezel_mac_address
        heart_beat['header']['correlationId'] = heart_beat['header']['guid']
        heart_beat['header']['type'] = PayloadTypes.PTYPE.value['heart_beat']
        heart_beat['header']['dateTime'] = arrow.now().format('YYYY-MM-DDTHH:mm:ssZ')

        return heart_beat

    async def send_heart_beat(self, interval: int = 0, loop: bool = False) -> None:

        if loop:
            while True:
                new_heart_beat = self.build_heart_beat()
                self.log_payload_send(new_heart_beat, 'init', -1)

                await self.mqtt_publisher(json.dumps(new_heart_beat), publish_topic=self.mqtt_monitor_publish_topic)

                if interval > 0:
                    await asyncio.sleep(interval)
                else:
                    break

        else:
            new_heart_beat = self.build_heart_beat()

            self.log_payload_send(new_heart_beat, 'init', -1)
            await self.mqtt_publisher(json.dumps(new_heart_beat), publish_topic=self.mqtt_monitor_publish_topic)

    def parse_api_version(self) -> list:
        # Create a copy of HEADER values list to edit
        header_attributes = PayloadAttributes.HEADER.value[:]

        if self.api_version == APIVersionInfo.API_VERSION.value['latest']:
            header_attributes.remove('equipmentType')
            header_attributes.append('equipmentInfo')

        return header_attributes

    def validate_payload_attributes(self, target_payload: dict) -> bool:
        try:
            error, missing_attrs = False, list()

            payload_keys = target_payload.keys()
            header_keys = target_payload['header'].keys()
            version_info_keys = target_payload['header']['versionInfo'].keys()

            # Verify required HEADER attrs
            header_attributes = self.parse_api_version()

            for attr in header_attributes:
                if attr not in header_keys:
                    error = True
                    missing_attrs.append(attr)

            # Verify required BODY attrs
            for attr in PayloadAttributes.BODY.value:
                if attr not in payload_keys:
                    error = True
                    missing_attrs.append(attr)

            # Verify required VERSION INFO attrs
            for attr in PayloadAttributes.VERSION.value:
                if attr not in version_info_keys:
                    error = True
                    missing_attrs.append(attr)

            if error:
                raise Exception(f'Required attributes missing: {missing_attrs}')

        except KeyError as ke:
            log.error(f'Required key missing: {ke.args[0]}')
            return True

        except Exception as e:
            log.error(e)
            return True

        return False

    def validator(self, payload: dict) -> bool:
        """
        Validator runs a series of validation tests for incoming payloads. More tests may
        be added as needed.

        param payload <dict>: the payload to validate
        return <bool>: Will return True if one of the validation tests fail
        """

        tests = [
            self.validate_payload_attributes(payload),
            self.validate_bezel_mac(payload),
        ]

        return True if True in tests else False

    def get_payload(self, incoming_payload) -> dict:
        decoded = incoming_payload.payload.decode('utf-8')
        serialized = json.loads(decoded)

        self.results.append_received_payload(copy.deepcopy(serialized))
        self.results.increment_payload_received()

        return serialized

    async def mqtt_publisher(self, payload: str, publish_topic: str = None) -> None:

        target_publish_topic = publish_topic if publish_topic else self.mqtt_publish_topic

        try:
            self.results.increment_payload_sent()
            self.results.append_sent_payload(copy.deepcopy(json.loads(payload)))

            async with Client(self.mqtt_broker_ip) as client:
                await client.publish(target_publish_topic, payload=payload, qos=1)

        except MqttError:
            log.error(f'Publish failed - check MQTT connection.')
            shutdown(None)

        except asyncio.exceptions.CancelledError:
            pass

    async def mqtt_subscriber(self, client: Client) -> None:
        try:
            async with client.unfiltered_messages() as messages:
                async with client:
                    log.info(f'Listening on: {self.mqtt_subscribe_topic}')

                    await client.subscribe(self.mqtt_subscribe_topic, qos=1)
                    log.info('Ready.')

                    async for message in messages:
                        incoming_payload = self.get_payload(message)

                        if self.validator(incoming_payload):
                            continue

                        self.log_payload_receive(incoming_payload)
                        self.message_queue.append(incoming_payload)

        except MqttError:
            log.error(f'Subscribe failed - check MQTT connection.')
            shutdown(None)

        except asyncio.exceptions.CancelledError:
            pass

    @staticmethod
    def log_payload_receive(received: dict) -> None:
        log.info(f'Received {received["header"]["type"]}:')

        log.info(f'bezel ({received["header"]["destination"]})'
                 f' <-|{received["header"]["type"]}|<- mqtt ({received["header"]["source"]})')

        log.info(f'cid: {received["header"]["correlationId"]} | guid: {received["header"]["guid"]}')

        log.debug(f'Payload content:\n{json.dumps(received, indent=4)}')

    @staticmethod
    def log_payload_send(l_payload: dict, retry_count: str, loop_count: int) -> None:
        log.info(f'Sending {l_payload["header"]["type"]} ({retry_count}) | Loop: {loop_count + 1}:')

        log.info(f'bezel ({l_payload["header"]["source"]}) ->|'
                 f'{l_payload["header"]["type"]}|-> mqtt ({l_payload["header"]["destination"]})')

        log.info(f'cid: {l_payload["header"]["correlationId"]} | guid: {l_payload["header"]["guid"]}')

        log.debug(f'Payload content:\n{json.dumps(l_payload, indent=4)}')


class Blink(Bezel):
    """

    """
    def __init__(
            self,
            bezel_mac_address: str,
            mqtt_broker_ip: str,
            mqtt_broker_port: int,
            mqtt_subscribe_topic: str,
            mqtt_publish_topic: str,
            mqtt_monitor_publish_topic: str,
            **kwargs
    ) -> None:
        super().__init__(
            bezel_mac_address,
            mqtt_broker_ip,
            mqtt_broker_port,
            mqtt_subscribe_topic,
            mqtt_publish_topic,
            mqtt_monitor_publish_topic
        )

        self.retry_interval = kwargs['retry_interval']
        self.loop_interval = kwargs['loop_interval']
        self.loop = kwargs['loop']
        self.blink_ack = kwargs['blink_ack']
        self.blink_success = kwargs['blink_success']
        self.blink_fail = kwargs['blink_fail']

    @staticmethod
    def validate_blink_attributes(target_payload: dict) -> bool:
        try:
            error, missing_attrs = False, list()

            for attr in PayloadAttributes.BLINK.value:
                if attr not in target_payload.keys():
                    error = True
                    missing_attrs.append(attr)
            if error:
                raise Exception(f'Required blink attributes missing: {missing_attrs}')

            # Validate type attribute
            if 'type' in target_payload['header']:
                if not target_payload['header']['type']:
                    raise Exception('Payload type attribute missing | type: <empty>')
                else:
                    if target_payload['header']['type'] != PayloadTypes.PTYPE.value['blink_request']:
                        raise Exception(f'Invalid type: {target_payload["header"]["type"]}')

        except Exception as e:
            log.error(e)
            return True

        return False

    def validate_blink_params(self, target_payload: dict) -> bool:
        try:
            if 'all' in target_payload.keys():
                if target_payload['all']:
                    return False
                else:
                    for led in target_payload['spec'].split(';'):
                        if led not in LEDS.SPEC.value[self.api_version]:
                            raise ValueError(f'Invalid LED: {led}')

        except ValueError as e:
            log.error(e)
            return True

    def validator(self, payload: dict) -> bool:
        tests = [
            self.validate_payload_attributes(payload),
            self.validate_bezel_mac(payload),
            self.validate_blink_attributes(payload),
            self.validate_blink_params(payload)
        ]

        return True if True in tests else False

    async def mqtt_subscriber(self, client: Client) -> None:
        try:
            async with client.unfiltered_messages() as messages:
                async with client:
                    log.info('Connected to MQTT Broker.')
                    await client.subscribe(self.mqtt_subscribe_topic, qos=1)
                    log.info('Ready.')

                    async for message in messages:
                        incoming_payload = self.get_payload(message)

                        if self.validator(incoming_payload):
                            continue

                        self.log_payload_receive(incoming_payload)
                        self.message_queue.append(incoming_payload)

        except MqttError as e:
            log.error(f'Subscribe failed - check MQTT connection.\n{e}')
            shutdown(None)
        except asyncio.exceptions.CancelledError:
            pass

    def iterate_payload_quantity(self) -> list:
        blink_responses = list()

        if self.blink_ack > 0:
            blink_responses.append([self.build_response_payload(status='start', payload_type='blink_ack') for _ in
                                    range(self.blink_ack)])

        if self.blink_success > 0:
            blink_responses.append([self.build_response_payload(status='success', payload_type='blink_success') for _ in
                                    range(self.blink_success)])

        if self.blink_fail > 0:
            blink_responses.append([self.build_response_payload(status='fail', payload_type='blink_fail') for _ in
                                    range(self.blink_fail)])

        return blink_responses

    def build_response_payload(self, status: str = 'start', payload_type: str = 'blink_ack') -> str:
        try:
            blink_response = copy.deepcopy(self.message_queue[0])

            blink_response['header']['versionInfo']['api'] = self.api_version
            blink_response['header']['versionInfo']['applianceType'] = 'Emulator'
            blink_response['header']['versionInfo']['applianceSpec'] = read_properties_file(VERSION_PROPERTIES)
            blink_response['header']['guid'] = str(uuid.UUID(int=random.Random().getrandbits(128)))
            blink_response['header']['destination'] = self.message_queue[0]['header']['source']
            blink_response['header']['source'] = self.bezel_mac_address
            blink_response['header']['correlationId'] = self.message_queue[0]['header']['correlationId']
            blink_response['header']['type'] = PayloadTypes.PTYPE.value[payload_type]
            blink_response['header']['dateTime'] = arrow.now().format('YYYY-MM-DDTHH:mm:ssZ')
            blink_response['status'] = BlinkStatus.STATUS.value[status]

            del blink_response['time']
            del blink_response['all']
            del blink_response['spec']

            return json.dumps(blink_response)
        except (json.JSONDecodeError, KeyError) as e:
            log.exception(f'Error parsing incoming payload:\n{e}')


class Cook(Bezel):
    def __init__(
            self,
            bezel_mac_address: str,
            mqtt_broker_ip: str,
            mqtt_broker_port: int,
            mqtt_subscribe_topic: str,
            mqtt_publish_topic: str,
            mqtt_monitor_publish_topic: str,
            **kwargs
    ) -> None:
        super().__init__(
            bezel_mac_address,
            mqtt_broker_ip,
            mqtt_broker_port,
            mqtt_subscribe_topic,
            mqtt_publish_topic,
            mqtt_monitor_publish_topic
        )

        # Logic
        self.destination_mac = kwargs['destination_mac_address']

        # Cook Parameters
        self.recipe_instance_id = kwargs['recipe_instance_id']
        self.recipe_name = kwargs['recipe_name']
        self.remaining_time = kwargs['remaining_time']
        self.product_quantity = kwargs['product_quantity']

        self.flow = kwargs['flow'].lower().replace(' ', '').split('|')

        self.template = copy.deepcopy(Payloads.TEMPLATE.value[self.api_version])
        self.correlationId = ''     # Initialize empty correlationId

        self.payload_retries = {
            'cook_start': kwargs['cook_start'],
            'cook_quantity': kwargs['cook_quantity'],
            'cook_complete': kwargs['cook_complete'],
            'cook_cancel': kwargs['cook_cancel'],
            'cook_complete_ack': kwargs['cook_complete_ack']
        }

        self.events = {
            'cook_start': self.cook_start,
            'cook_quantity': self.cook_quantity,
            'cook_complete': self.cook_complete,
            'cook_cancel': self.cook_cancel,
            'cook_complete_ack': self.cook_complete_ack
        }

        self.total_to_send = sum([y for x, y in self.payload_retries.items() if x in self.flow])

    def set_generic_payload_attrs(self, payload: dict, payload_type: str, start_dialogue: bool) -> dict:
        payload['header']['versionInfo']['api'] = self.api_version
        payload['header']['versionInfo']['applianceType'] = 'Emulator'
        payload['header']['versionInfo']['applianceSpec'] = read_properties_file(VERSION_PROPERTIES)

        payload['header']['destination'] = self.destination_mac
        payload['header']['source'] = self.bezel_mac_address
        payload['header']['type'] = PayloadTypes.PTYPE.value[payload_type]
        payload['header']['dateTime'] = arrow.now().format('YYYY-MM-DDTHH:mm:ssZ')

        if start_dialogue:
            log.info('Generating new CID.')
            self.correlationId = str(uuid.UUID(int=random.Random().getrandbits(128)))
            payload['header']['guid'] = payload['header']['correlationId'] = self.correlationId
        else:
            payload['header']['correlationId'] = self.correlationId
            payload['header']['guid'] = str(uuid.UUID(int=random.Random().getrandbits(128)))

        return payload

    def cook_start(self, start_dialogue: bool = True) -> dict:
        payload = copy.deepcopy(self.template)
        payload = self.set_generic_payload_attrs(payload, 'cook_start', start_dialogue)

        payload['recipeInstanceId'] = self.recipe_instance_id
        payload['recipeName'] = self.recipe_name
        payload['remainingTime'] = self.remaining_time

        return payload

    def cook_quantity(self, quantity_sent: bool = True, start_dialogue: bool = True) -> dict:
        payload = copy.deepcopy(self.template)
        payload = self.set_generic_payload_attrs(payload, 'cook_quantity', start_dialogue)

        payload['recipeInstanceId'] = self.recipe_instance_id
        payload['recipeName'] = self.recipe_name
        payload['quantity'] = self.product_quantity if quantity_sent else 0

        return payload

    def cook_complete(self, start_dialogue: bool = True) -> dict:
        payload = copy.deepcopy(self.template)
        payload = self.set_generic_payload_attrs(payload, 'cook_complete', start_dialogue)

        payload['recipeInstanceId'] = self.recipe_instance_id
        payload['recipeName'] = self.recipe_name

        return payload

    def cook_cancel(self, start_dialogue: bool = True) -> dict:
        payload = copy.deepcopy(self.template)
        payload = self.set_generic_payload_attrs(payload, 'cook_cancel', start_dialogue)

        payload['recipeInstanceId'] = self.recipe_instance_id
        payload['recipeName'] = self.recipe_name
        payload['remainingTime'] = self.remaining_time

        return payload

    def cook_complete_ack(self, start_dialogue: bool = True) -> dict:
        payload = copy.deepcopy(self.template)
        payload = self.set_generic_payload_attrs(payload, 'cook_complete_ack', start_dialogue)

        payload['recipeInstanceId'] = self.recipe_instance_id
        payload['recipeName'] = self.recipe_name

        return payload


class Results:
    def __init__(self):
        # Results
        self.total_payloads_sent = 0
        self.total_payloads_received = 0
        self.sent_payloads = list()
        self.received_payloads = list()
        self.sent_payload_types = list()

    def display_results(self, execution_time: float = 0.0) -> None:
        log.info(f'Total payloads processed: {self.calculate_total_processed()}')
        log.info(f'Total payloads sent: {self.total_payloads_sent}')
        log.info(f'Total payloads received: {self.total_payloads_received}')

        if self.sent_payload_types:
            log.info(f'Events sent: {self.sent_payload_types}')

        if execution_time:
            log.info(f'Total execution time: {execution_time:.2f}s')

    def increment_payload_sent(self):
        self.total_payloads_sent += 1

    def increment_payload_received(self):
        self.total_payloads_received += 1

    def append_sent_payload(self, sent_payload: dict) -> None:
        self.sent_payloads.append(sent_payload)

        payload_type = sent_payload['header']['type']

        if payload_type not in self.sent_payload_types:
            self.sent_payload_types.append(payload_type)

    def append_received_payload(self, received_payload):
        self.received_payloads.append(received_payload)

    def calculate_total_processed(self):
        return self.total_payloads_sent + self.total_payloads_received






