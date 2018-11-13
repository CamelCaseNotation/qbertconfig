# Copyright 2018 Platform9 Systems, Inc.

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import sys
import logging
import tempfile

# local imports
from qbertconfig.QbertConfig import QbertConfig
from qbertconfig.cli.dispatcher import Dispatcher
import tests.samples.kubeconfigs as samples

from mock import patch


LOG = logging.getLogger(__name__)

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class QcTestCase(unittest.TestCase):
    @patch('qbertconfig.QbertConfig.QbertConfig._initialize_qbert_client')
    def setUp(self, mock_qbert_client):
        # Don't need a working qbert client for unit tests
        mock_qbert_client.return_value = None

        # create temporary file to use for kubeconfig
        with tempfile.NamedTemporaryFile(prefix='qbertconfig', delete=False) as kcfg_f:
            self.kubeconfig_path = kcfg_f.name

        # load one profile into here
        # use vars as if we were a user at the command line
        self.qc = QbertConfig(**{'kcfg_path': self.kubeconfig_path, 'kcfg': samples.BASE_TEST_KUBECONFIG})

        self.dispatcher = Dispatcher(self.qc)

    def tearDown(self):
        if os.path.exists(self.kubeconfig_path):
            os.remove(self.kubeconfig_path)
