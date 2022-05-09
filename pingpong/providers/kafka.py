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
from kafka import KafkaProducer as k_KafkaProducer, KafkaConsumer as k_KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic


class KafkaProducer(object):
    """
    Kafka Producer using https://kafka-python.readthedocs.io/ with JSON serialization.
    """
    def __init__(self, bootstrap_servers: list, schema: dict) -> None:
        """
        Create the Producer instance.
        """
        self.bootstrap_servers = bootstrap_servers
        self.schema = schema
        self.producer = k_KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

    def send(self, topic: str, key: str, value: dict) -> None:
        """
        Send the specified Value to a Kafka Topic.
        """
        self.producer.send(topic, value)
        self.producer.flush()


class KafkaConsumer(object):
    """
    Kafka Consumer using https://kafka-python.readthedocs.io/ with JSON deserialization.
    """
    def __init__(self, bootstrap_servers: list, group_id: str, topics: list, schema: dict) -> None:
        """
        Create the Consumer instance.
        """
        self.bootstrap_servers = bootstrap_servers
        self.schema = schema
        self.consumer = k_KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def create_topics(self, topics: list, num_partitions: int = 2, replication_factor: int = 1):
        """
        Create the specified list of Topics.
        """
        admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        topic_list = []

        new_topics = set(topics) - set(self.consumer.topics())
        for topic in new_topics:
            try:
                t = NewTopic(name=topic, num_partitions=num_partitions, replication_factor=replication_factor)
                admin_client.create_topics(new_topics=[t], validate_only=False)
                topic_list.append(t)
            except:  # Ignore error when the Topic already exists.
                pass

        return topic_list

    def read(self):
        """
        Read messages from the configured Kafka Topics.
        """
        for message in self.consumer:
            yield message
