import argparse
import logging
import sys
import json

from logger.custom_logger import Logger
from payloads.payloads import PayloadTypes
from main import cfg

log = Logger(log_level=cfg.log_level, name=__name__).get_logger()


class BezelException(BaseException):
    def __init__(self, error_messages: list = None, error_message: str = None) -> None:
        self.error_messages = error_messages
        self.error_message = error_message

    def __str__(self):
        if self.error_messages:
            return '\n'.join(self.error_messages)

        if self.error_message:
            return self.error_message


def validate_heart_beat_interval(heart_beat_interval: int) -> None:
    try:
        if heart_beat_interval < 1:
            raise BezelException(error_message=f'Heart beat interval cannot be less than 1 | '
                                               f'Heart beat interval: {heart_beat_interval}')

    except BezelException as e:
        log.setLevel(logging.ERROR)
        log.error(e)

        sys.exit(1)


def validate_mode(bezel_mode: str) -> None:
    try:
        if bezel_mode not in ['blink', 'cook']:
            raise BezelException(error_message=f'Invalid mode: {bezel_mode} | Valid values: [\'blink\', \'cook\']')

    except BezelException as e:
        log.setLevel(logging.ERROR)
        log.error(e)

        sys.exit(1)


def validate_cook_flow_events_string(flow_string):
    cook_flow_event_errors = list()

    try:
        events = flow_string.lower().replace(' ', '').split('|')

        for event in events:
            if event not in list(PayloadTypes.PTYPE.value.keys())[4:-1]:
                cook_flow_event_errors.append(event)

        if cook_flow_event_errors:
            cook_flow_event_errors.insert(0, 'Invalid events')
            raise BezelException(error_messages=cook_flow_event_errors)

    except BezelException as e:
        log.setLevel(logging.ERROR)
        log.error(e)

        sys.exit(1)


def validate_loop_and_retry(num_loops: int, loop_interval_time: int, retry_interval_time: int) -> None:
    loop_retry_errors = list()
    try:
        for k, v in {
            '--loop': num_loops,
            '--loop_interval': loop_interval_time,
            '--retry-interval': retry_interval_time
        }.items():
            if v < 0:
                loop_retry_errors.append(f'{k} cannot  be less than 0 | {k}={v}')

        if loop_retry_errors:
            raise BezelException(error_messages=loop_retry_errors)

    except BezelException as e:
        log.setLevel(logging.ERROR)
        log.error(e)

        sys.exit(1)


def validate_payload_quantities(config: argparse.Namespace) -> None:
    payload_quantity_errors = list()
    payload_quantities = dict()

    if config.mode == 'blink':
        payload_quantities = {
            '--blink-ack': config.blink_ack,
            '--blink-success': config.blink_success,
            '--blink-fail': config.blink_fail
        }

    if config.mode == 'cook':
        payload_quantities = {
            '--cook-start': config.cook_start,
            '--cook-quantity': config.cook_quantity,
            '--cook-complete': config.cook_complete,
            '--cook-cancel': config.cook_cancel,
            '--cook-complete-ack': config.cook_complete_ack
        }

    try:
        for k, v in payload_quantities.items():
            if v < 0:
                payload_quantity_errors.append(f'{k} cannot be less than 0 | {k}: {v}')
            if v > 3:
                payload_quantity_errors.append(f'{k} cannot be greater than 3 | {k}: {v}')

        if sum(payload_quantities.values()) == 0:
            payload_quantity_errors.append('No payloads to process')

        if payload_quantity_errors:
            raise BezelException(error_messages=payload_quantity_errors)

    except BezelException as e:
        log.setLevel(logging.ERROR)

        log.error(e)
        log.error(json.dumps(payload_quantities, indent=4))

        sys.exit(1)
