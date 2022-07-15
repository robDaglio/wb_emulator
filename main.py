import asyncio
import json
import time

from logger.custom_logger import Logger
from payloads.payloads import PayloadTypes
from config import cfg

from time import perf_counter
from asyncio_mqtt import Client

log = Logger(log_level=cfg.log_level, name=__name__).get_logger()


def shutdown(future):
    for _task in asyncio.all_tasks():
        _task.cancel()


async def blink_flow():
    blinker = Blink(
        cfg.bezel_mac,
        cfg.mqtt_broker,
        cfg.mqtt_port,
        cfg.mqtt_control_subscribe_topic,
        cfg.mqtt_control_publish_topic,
        cfg.mqtt_monitor_publish_topic,
        retry_interval=cfg.retry_interval,
        loop_interval=cfg.loop_interval,
        loop=cfg.loop,
        blink_ack=cfg.blink_ack,
        blink_success=cfg.blink_success,
        blink_fail=cfg.blink_fail
    )

    client_subscriber = Client(
                cfg.mqtt_broker,
                port=cfg.mqtt_port,
                client_id=f'Wi-Fi Bezel Emulator {cfg.bezel_mac}',
                clean_session=False
            )

    async def event_loop(blink_obj):
        while True:
            if not blink_obj.message_queue:
                await asyncio.sleep(1)
            else:
                for _ in range(cfg.loop):
                    log.info(f'Initializing loop {_ + 1}.')

                    # this function will create a number of response payloads as per cfg.blink_ack,
                    # cfg.blink_success and cfg.blink_fail
                    # returns tuple of lists
                    response_payloads = blink_obj.iterate_payload_quantity()

                    # iterates over the list of lists created by iterate_payload_quantity()
                    for index, payload_type in enumerate(response_payloads):
                        for p in payload_type:
                            if p:
                                blink_obj.log_payload_send(json.loads(p), str(index + 1), _)
                                await blink_obj.mqtt_publisher(p)

                                # If there exist any blink-ack payloads in response_payloads ->
                                # if this is the last blink-ack payload
                                # sleep for the value specified in message_queue[0]['time'] to emulate 'blinking'
                                if cfg.blink_ack > 0:
                                    if p == response_payloads[0][-1]:  # response_payloads[0] is a
                                        log.info(f'Blink Time: {blink_obj.message_queue[0]["time"]}s')
                                        await asyncio.sleep(blink_obj.message_queue[0]["time"])

                                # If payload qty is greater than 1 -> If this is not the last payload of its type,
                                # log and await the retry-interval
                                if len(response_payloads[index]) > 1:
                                    if p != response_payloads[index][-1]:
                                        log.info(f'Retry Interval: {cfg.retry_interval}s')
                                        await asyncio.sleep(cfg.retry_interval)

                    # If there is more than one iteration to be processed AND the current iteration is not the last
                    # log and await the loop_interval between each iteration
                    if cfg.loop > 1 and _ != cfg.loop - 1:
                        log.info(f'Loop Interval: {cfg.loop_interval}s')
                        await asyncio.sleep(cfg.loop_interval)

                # delete the incoming payload from the queue
                # and display a ready message for the next
                del blink_obj.message_queue[0]
                log.info('Ready.')

    subscriber_task = asyncio.create_task(blinker.mqtt_subscriber(client_subscriber))
    event_loop_task = asyncio.create_task(event_loop(blinker))
    heart_beat_task = asyncio.create_task(blinker.send_heart_beat(cfg.heart_beat_interval, loop=True))

    await asyncio.gather(subscriber_task, event_loop_task, heart_beat_task)


async def cook_flow(init_time):
    cooker = Cook(
        cfg.bezel_mac,
        cfg.mqtt_broker,
        cfg.mqtt_port,
        cfg.mqtt_workflow_subscribe_topic,
        cfg.mqtt_workflow_publish_topic,
        cfg.mqtt_monitor_publish_topic,
        destination_mac_address=cfg.dest_mac,
        cook_start=cfg.cook_start,
        cook_quantity=cfg.cook_quantity,
        cook_complete=cfg.cook_complete,
        cook_cancel=cfg.cook_cancel,
        cook_complete_ack=cfg.cook_complete_ack,
        recipe_instance_id=cfg.recipe_instance_id,
        recipe_name=cfg.recipe_name,
        remaining_time=cfg.remaining_time,
        product_quantity=cfg.product_quantity,
        flow=cfg.flow
    )

    client_subscriber = Client(
        cfg.mqtt_broker,
        port=cfg.mqtt_port,
        client_id=f'Wi-Fi Bezel Emulator {cfg.bezel_mac}',
        clean_session=False
    )

    async def event_loop(cook_obj, exec_start_time):
        log.info(f'Total payloads to send: {cooker.total_to_send * cfg.loop}')

        try:
            for i in range(cfg.loop):
                for index, event in enumerate(cooker.flow):
                    if cook_obj.payload_retries[event] and event in cooker.flow:
                        log.info(f'Initializing: {event.upper()} events.')

                        for _ in range(cook_obj.payload_retries[event]):
                            # Set the generated guid as the correlationId if this is the
                            # first payload being sent, otherwise, keep it the same
                            dialogue_origin = True if index == 0 and _ == 0 else False

                            payload = cook_obj.events[event](start_dialogue=dialogue_origin)

                            log.info(f'Publishing to: {cfg.mqtt_workflow_publish_topic}.')
                            cooker.log_payload_send(payload, str(_ + 1), i)

                            await cook_obj.mqtt_publisher(json.dumps(payload))

                            # If this is the last cook_quantity sent, and cook start was already sent,
                            # await the remaining_time attribute
                            if event == 'cook_quantity' and (_ + 1) == cook_obj.payload_retries[event]:
                                if PayloadTypes.PTYPE.value['cook_start'] in cook_obj.results.sent_payload_types:
                                    log.info(f'Cook time: {cook_obj.remaining_time}s')
                                    await asyncio.sleep(cook_obj.remaining_time)

                            # If there is more than one payload to be sent, and it is not the last payload of its
                            # type, await the retry interval
                            if 0 < cook_obj.payload_retries[event] != (_ + 1):
                                log.info(f'Retry Interval: {cfg.retry_interval}s')
                                await asyncio.sleep(cfg.retry_interval)

                            # Await 1 second to ensure ack can be received.
                            await asyncio.sleep(1)

                # If there is more than one loop to be processed, and this is not the last iteration,
                # await the loop interval
                if 1 < cfg.loop != (i + 1):
                    log.info(f'Loop Interval: {cfg.loop_interval}s')
                    await asyncio.sleep(cfg.loop_interval)

            cooker.results.display_results(execution_time=(time.perf_counter() - exec_start_time))
            log.info('Flow completed successfully.')
            return True

        except asyncio.exceptions.CancelledError:
            pass

        except Exception as e:
            log.exception(f'Publish failed!\n{e}')

    subscriber_task = asyncio.create_task(cooker.mqtt_subscriber(client_subscriber))
    cook_flow_task = asyncio.create_task(event_loop(cooker, init_time))
    heart_beat_task = asyncio.create_task(cooker.send_heart_beat(cfg.heart_beat_interval, loop=True))

    cook_flow_task.add_done_callback(shutdown)
    await asyncio.gather(subscriber_task, cook_flow_task, heart_beat_task)


if __name__ == '__main__':
    from payloads.validation import (
        validate_payload_quantities,
        validate_loop_and_retry,
        validate_cook_flow_events_string,
        validate_mode,
        validate_heart_beat_interval
    )

    # Startup
    from utils.utils import (
        read_properties_file,
        # log_config,
        VERSION_PROPERTIES,
        API_PROPERTIES
    )

    # Show config?
    if cfg.show_config:
        log.info(f'Configuration: {json.dumps(vars(cfg), indent=4)}')

    log.info(f'Starting Wi-fi Bezel Emulator | '
             f'Version: {read_properties_file(VERSION_PROPERTIES)} '
             f'| API Version: {read_properties_file(API_PROPERTIES)}')

    log.info(f'Bezel MAC Address: {cfg.bezel_mac}')

    # Validation
    validate_mode(cfg.mode)
    validate_payload_quantities(cfg)
    validate_loop_and_retry(cfg.loop, cfg.loop_interval, cfg.retry_interval)
    validate_heart_beat_interval(cfg.heart_beat_interval)

    # log.setLevel(logging.INFO)

    # Start emulation
    if cfg.mode == 'blink':
        from modes.modes import Blink

        try:
            asyncio.run(blink_flow())

        except KeyboardInterrupt:
            log.info('Process cancelled by user.')

        except asyncio.exceptions.CancelledError:
            pass

    if cfg.mode == 'cook':
        validate_cook_flow_events_string(cfg.flow)
        start = perf_counter()

        from modes.modes import Cook

        try:
            asyncio.run(cook_flow(start))

        except KeyboardInterrupt:
            log.info('Process cancelled by user.')

        except asyncio.exceptions.CancelledError:
            pass
