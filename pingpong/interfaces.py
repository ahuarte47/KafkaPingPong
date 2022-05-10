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


class AbstractProducer(object):
    """
    Abstract Kafka Producer doing nothing.
    """
    def __init__(self, bootstrap_servers: list, schema: dict) -> None:
        """
        Create the Producer instance.
        """
        self.bootstrap_servers = bootstrap_servers
        self.schema = schema

    def send(self, topic: str, key: str, value: dict) -> None:
        """
        Send the specified Value to a Kafka Topic.
        """
        pass


class AbstractConsumer(object):
    """
    Abstract Kafka Consumer doing nothing.
    """
    def __init__(self, bootstrap_servers: list, group_id: str, topics: list, schema: dict) -> None:
        """
        Create the Consumer instance.
        """
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topics = topics
        self.schema = schema

    def create_topics(self, topics: list, num_partitions: int = 2, replication_factor: int = 1):
        """
        Create the specified list of Topics.
        """
        return []

    def read(self):
        """
        Read messages from the configured Kafka Topics.
        """
        return []
