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
import logging
import openstack
import sys
from keystoneauth1.exceptions import MissingRequiredOptions

# Local imports
from QbertClient import QbertClient
from Kubeconfig import Kubeconfig

LOG = logging.getLogger(__name__)


class QbertConfig(object):
    """ Combination of QbertClient and Kubeconfig """

    def __init__(self, **kwargs):
        self._initialize_qbert_client(**kwargs)
        self.master_kubeconfig = Kubeconfig(**kwargs)

    def _initialize_qbert_client(self, **kwargs):
        self.qbert_client = None
        if kwargs.get('cloud'):
            self.cloud = kwargs['cloud']
        else:
            cloud_config = openstack.config.OpenStackConfig()
            # Try to get a cloud from OpenStack config
            try:
                self.cloud = cloud_config.get_one_cloud()
            except MissingRequiredOptions as ex:
                # If this fails, it means no other credentials were provided another way
                LOG.error("Unable to validate openstack credentials. Check this error out: \n" + ex.message)
                LOG.error("Check to ensure your OpenStack credentials are in clouds.yaml"
                          " or available as environment variables")
                sys.exit(1)
        self.qbert_client = QbertClient(os_cloud=self.cloud)

    def save(self):
        """ Saves the current kubeconfig to file """
        self.master_kubeconfig.save()

    def fetch(self, cluster_name=None, cluster_uuid=None):
        """
        Using the qbert API, download a kubeconfig file for the specified cluster

        Args:
            cluster_name: name of the qbert cluster
            cluster_uuid: ID of the qbert cluster

        Returns:
            KubeConfig object
        """
        LOG.debug("Cluster: '%s' (%s)", cluster_name, cluster_uuid)
        cluster = self.qbert_client.find_cluster(cluster_uuid, cluster_name)
        new_kubeconfig = Kubeconfig(kcfg=self.qbert_client.get_kubeconfig(cluster))
        self.master_kubeconfig.merge_kubeconfigs(new_kubeconfig)
        return self.master_kubeconfig
