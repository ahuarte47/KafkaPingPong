# -*- coding: utf-8 -*-
"""
===============================================================================

   Project  : PingPong Service
   Purpose  : Toolkit for testing stream processing with Apache Kafka.

   Copyright (c) 2022, MyCompany - xyz@mycompany.com. All rights reserved.

   Redistribution and use of this code in source and binary forms, with
   or without modification, are permitted provided that the following
   conditions are met:
   * Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above copyright notice,
     this list of conditions and the following disclaimer in the documentation
     and/or other materials provided with the distribution.

   THIS SAMPLE CODE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
   TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
   OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SAMPLE CODE, EVEN IF
   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

===============================================================================
"""

import sys
import os
import logging
import argparse
import traceback
import json
import uuid
from time import sleep
from datetime import datetime

from jsonschema import Draft7Validator as SchemaValidator
from item import Item


# =============================================================================
# Consumers/Producers:
#
#  For this demo there are implemented Producers and Consumers using two
#  different python libraries:
#   + https://kafka-python.readthedocs.io/
#   + https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html
#
#  I do not have tested this yet, but this library looks amazing:
#   + https://faust.readthedocs.io/en/latest/
#     https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_6_stream_processing/streams/stream.py
#
#  The loading of a specific implementation is done reading the input parameter
#  "service_impl" and importing their python modules by-hand.
#  But if we have to implement readers or writers of many data providers,
#  The loading of these py files could be done using "importlib.import_module"
#  depending on the name of the provider, instead of using hard-coding.

def create_consumer(service_impl: str, bootstrap_servers: list, topics: list, schema: dict):
    """
    Returns a new Kafka Consumer of the specified implementation.
    """
    try:
        service_impl = service_impl.lower()
        group_id = 'pingpong_' + uuid.uuid4().hex

        if service_impl == 'kafka':
            from providers.kafka import KafkaConsumer
            c = KafkaConsumer(bootstrap_servers=bootstrap_servers, group_id=group_id, topics=topics, schema=schema)
            c.create_topics(topics=topics, num_partitions=2, replication_factor=1)
            return c
        if service_impl == 'confluent':
            from providers.confluent import ConfluentConsumer
            c = ConfluentConsumer(bootstrap_servers=bootstrap_servers, group_id=group_id, topics=topics, schema=schema)
            c.create_topics(topics=topics, num_partitions=2, replication_factor=1)
            return c
        if service_impl == 'dummy':
            from providers.dummy import DummyConsumer
            c = DummyConsumer(bootstrap_servers=bootstrap_servers, group_id=group_id, topics=topics, schema=schema)
            c.create_topics(topics=topics, num_partitions=2, replication_factor=1)
            return c

    except Exception as e:
        # TODO: Catch specific Exception when Connection is refused because of Brokers are not ready yet.
        logging.error(e)
        return None

    raise Exception(f'The Kafka provider "{service_impl}" is not supported!')


def create_producer(service_impl: str, bootstrap_servers: list, schema: dict):
    """
    Returns a new Kafka Producer of the specified implementation.
    """
    try:
        service_impl = service_impl.lower()

        if service_impl == 'kafka':
            from providers.kafka import KafkaProducer
            p = KafkaProducer(bootstrap_servers=bootstrap_servers, schema=schema)
            return p
        if service_impl == 'confluent':
            from providers.confluent import ConfluentProducer
            p = ConfluentProducer(bootstrap_servers=bootstrap_servers, schema=schema)
            return p
        if service_impl == 'dummy':
            from providers.dummy import DummyProducer
            p = DummyProducer(bootstrap_servers=bootstrap_servers, schema=schema)
            return p

    except Exception as e:
        # TODO: Catch specific Exception when Connection is refused because of Brokers are not ready yet.
        logging.error(e)
        return None

    raise Exception(f'The Kafka provider "{service_impl}" is not supported!')


# =============================================================================
# Service:
#
#  Yes, I am doing bad things, I am sharing the "service.py" file
#  for different needs.
#
#  For doing simple this demo, I implement all logic in one unique
#  "service.py" file that runs in all cases on the same unique Docker
#  image.
#
#  In a real project, each component (e.g. services that send messages,
#  run geoworkflows, write outputs, ...) will have different dependencies,
#  python libraries and probably will run on different Docker images.
#
#  The entrypoint "service.py" accepts settings from two ways, command line
#  parameters and environment variables (The Helm chart configures the
#  application using environment variables).

def run_service(command_args: list) -> None:
    """
    Implements the PingPong logic producing, validating of finally
    digesting Kafka Topics.
    """
    service_role = os.environ.get('SERVICE_ROLE', 'producer')
    service_impl = os.environ.get('SERVICE_IMPL', 'kafka')
    bootstrap_server = os.environ.get('BOOTSTRAP_SERVER', 'localhost:9092')
    schema_def = Item.schema()

    # Define the command parameters of the application.
    parser = argparse.ArgumentParser()
    parser.add_argument('--service_role', dest='service_role', required=False, action='store',
                        help='Service role',
                        default=service_role, choices=['producer', 'validator', 'reader'])
    parser.add_argument('--service_impl', dest='service_impl', required=False, action='store',
                        help='Package that implements Kafka messaging',
                        default=service_impl, choices=['kafka', 'confluent', 'dummy'])
    parser.add_argument('--bootstrap_server', dest='bootstrap_server', required=False, action='store',
                        help='Kafka bootstrap server',
                        default=bootstrap_server)
    parser.add_argument('--log_level', dest='log_level', required=False, action='store',
                        help='Level of logging', default='INFO')
    #
    args, pipeline_args = parser.parse_known_args(command_args)

    logging.basicConfig(level=args.log_level, format="[%(levelname)s]: %(message)s")
    logging.info('========================================================================')
    logging.info('PingPong Service:')
    logging.info('Dummy application for testing stream processing with Apache Kafka.')
    logging.info('Author: xyz@mycompany.com')
    logging.info('========================================================================')
    logging.info('')

    # For debugging...
    logging.info('Environment variables:')
    for k, v in sorted(os.environ.items()): logging.info(' + {}: {}'.format(k,v))

    service_role = args.service_role.lower()
    service_impl = args.service_impl
    bootstrap_server = args.bootstrap_server
    logging.info(f'PingPong Service is running as "{service_role}", using "{service_impl}"...')

    # Run service...
    try:
        if service_role == 'producer':
            producer = None
            item_count = 0

            # Create Kafka Producer, waiting valid object.
            while producer is None:
                producer = create_producer(service_impl=service_impl,
                                           bootstrap_servers=[bootstrap_server],
                                           schema=schema_def)
                if producer is None:
                    sleep(10)

            # This dummy Producer sends a pair of Items, the first one matches the Schema, the second one no.
            items = [
                {'transaction-id': '', 'payload': {'message': 'ping'}},
                {'transaction-id': '', 'payload': {'message': 'FAIL'}}
            ]
            # Writing messages to Kafka Topic...
            while True:
                for item in items:
                    now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    msg = 'Sending Item #{} ({})...'.format(item_count, now_time)

                    key_id = 'ID' + str(item_count)
                    item['transaction-id'] = key_id
                    producer.send(topic='dev.pingpong.requested', key=key_id, value=item)

                    msg += '\n> ok!'
                    logging.info(msg)
                    item_count += 1
                    sleep(5)

        elif service_role == 'validator':
            validator_obj = SchemaValidator(schema_def)
            consumer = None
            producer = None

            # Create Kafka Producer & Consumer, waiting valid object.
            while consumer is None or producer is None:
                consumer = create_consumer(service_impl=service_impl,
                                           bootstrap_servers=[bootstrap_server],
                                           topics=['dev.pingpong.requested'],
                                           schema=schema_def)
                producer = create_producer(service_impl=service_impl,
                                           bootstrap_servers=[bootstrap_server],
                                           schema=schema_def)

                if consumer is None or producer is None:
                    sleep(10)

            # Reading & Writing messages from/to Kafka Topics...
            while True:
                for message in consumer.read():
                    item = message.value

                    now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    msg = 'Validating Item from Topic "{}" ({})...'.format(message.topic, now_time)
                    msg += '\n> Item: ' + json.dumps(item)

                    if validator_obj.is_valid(instance=item):
                        item.get('payload')['message'] = 'pong'

                        msg +=\
                            '\n> The Item matches the Schema, sending message to the topic "dev.pingpong.succeeded"...'

                        producer.send(topic='dev.pingpong.succeeded', key=item['transaction-id'], value=item)
                    else:
                        error_message = '\n'.join([e.message for e in validator_obj.iter_errors(instance=item)])
                        item.get('payload')['message'] = 'Validation Error: ' + error_message

                        msg +=\
                            '\n> The Item does not the Schema, sending message to the topic "dev.pingpong.failed"...'

                        producer.send(topic='dev.pingpong.failed', key=item['transaction-id'], value=item)

                    msg += '\n> ok!'
                    logging.info(msg)

                sleep(1)

        # Service working as final reader by default.
        else:
            consumer = None

            # Create Kafka Producer & Consumer, waiting valid object.
            while consumer is None:
                consumer = create_consumer(service_impl=service_impl,
                                           bootstrap_servers=[bootstrap_server],
                                           topics=['dev.pingpong.succeeded', 'dev.pingpong.failed'],
                                           schema=schema_def)
                if consumer is None:
                    sleep(10)

            # Reading messages from Kafka Topics...
            while True:
                for message in consumer.read():
                    item = message.value

                    now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    msg = 'Digesting Item from Topic "{}" ({})...'.format(message.topic, now_time)
                    msg += '\n> Item: ' + json.dumps(item)
                    msg += '\n> ok!'
                    logging.info(msg)

                sleep(1)

    except Exception as e:
        logging.error(e)
        traceback.print_exc(file=sys.stdout)


if __name__ == '__main__':
    run_service(command_args=sys.argv[1:])
