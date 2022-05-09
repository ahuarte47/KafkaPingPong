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

import unittest

from pingpong.item import Item
from jsonschema import Draft7Validator as SchemaValidator


class TestSchema(unittest.TestCase):
    """
    Testing the schema of PingPong message items.
    """
    def setUp(self) -> None:
        self._schema_def = Item.schema()
        self._validator_obj = SchemaValidator(schema=self._schema_def)

    def test_valid(self) -> None:
        item = {"transaction-id": "ID01", "payload": {"message": "ping"}}
        self.assertTrue(self._validator_obj.is_valid(instance=item))

    def test_invalid(self) -> None:
        items = [
            {"transaction-id_": "ID01", "payload": {"message": "ping"}},
            {"transaction-id": "ID01", "payload_": {"message": "ping"}},
            {"transaction-id": "ID01", "payload": {"message_": "ping"}},
            {"transaction-id": "ID01", "payload": {"message": "ping_"}},
            {"transaction-id": "ID01", "payload": {"message": "pinG"}},
            {"transaction-id": 100000, "payload": {"message": "ping"}},
            {"transaction-id": "ID01", "payload": 'my_string'},
        ]
        for item in items:
            if not self._validator_obj.is_valid(instance=item):
                error_message = '\n'.join([e.message for e in self._validator_obj.iter_errors(instance=item)])
                print('Validation error: {}'.format(error_message))

            self.assertFalse(self._validator_obj.is_valid(instance=item))
