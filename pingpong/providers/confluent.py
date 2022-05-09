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

import json
import logging
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic


def delivery_report(error, message):
    """
    Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush().
    """
    if error is not None:
        logging.error('> Message delivery failed: {}'.format(error))
    else:
        logging.info('> Message delivered to {} [{}]'.format(message.topic(), message.partition()))


class ConfluentProducer(object):
    """
    Kafka Producer using https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html
    with JSON serialization.
    """
    def __init__(self, bootstrap_servers: list, schema: dict) -> None:
        """
        Create the Producer instance.
        """
        config = {
            'bootstrap.servers': bootstrap_servers
        }
        self.bootstrap_servers = bootstrap_servers
        self.schema = schema
        self.producer = Producer(config)

    def send(self, topic: str, key: str, value: dict) -> None:
        """
        Send the specified Value to a Kafka Topic.
        """
        data = json.dumps(value).encode('utf-8')
        self.producer.poll(0)
        self.producer.produce(topic=topic, key=key, value=data, on_delivery=delivery_report)
        self.producer.flush()


class ConfluentConsumer(object):
    """
    Kafka Consumer using https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html
    with JSON deserialization
    """
    def __init__(self, bootstrap_servers: list, group_id: str, topics: list, schema: dict) -> None:
        """
        Create the Consumer instance.
        """
        config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        self.bootstrap_servers = bootstrap_servers
        self.schema = schema
        self.consumer = Consumer(config)
        self.consumer.subscribe(topics)

    def create_topics(self, topics: list, num_partitions: int = 2, replication_factor: int = 1):
        """
        Create the specified list of Topics.
        """
        topic_list = []

        config = {
            'bootstrap.servers': self.bootstrap_servers
        }
        admin_client = AdminClient(config)

        for topic in topics:
            try:
                t = NewTopic(name=topic, num_partitions=num_partitions, replication_factor=replication_factor)
                admin_client.create_topics(new_topics=[t])
                topic_list.append(t)
            except:  # Ignore error when the Topic already exists.
                pass

        return topic_list

    def read(self):
        """
        Read messages from the configured Kafka Topics.
        """
        message = self.consumer.poll(1.0)
        results = []

        if message is not None:
            if message.error():
                logging.error('Consumer error: {}'.format(message.error()))
            else:
                results.append({
                    'topic': message.topic(),
                    'key': message.key(),
                    'value': json.loads(message.value().decode('utf-8'))
                })
            self.consumer.commit()

        return results
