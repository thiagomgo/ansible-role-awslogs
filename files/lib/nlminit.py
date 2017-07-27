#!/usr/bin/env python
#
# Description:
#    This script is responsible to reconfigure AWSlogs agent on a running EC2 instance as it is booting.
#    We wish to do this for several reasons:
#     - The same packer build can be used then in multiple regions
#     - The log stream name can be overridden based on the instances tags when the instance can read these tags
#
# Notes:
#    - We expect this script to be run by Python 2, but use from __future__ to future proof
#    - We use the boto 2.x library as this is required by awslogs itself, and is therefore installed
#    - We are able to use requests, as it is present on the EC2 instance.
#    - We are able to use Jinja2, as it is present on the EC2 instance.
#
# References:
#    - EC2 Instance Metadata - http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html
#    - boto 2.x - http://boto.cloudhackers.com/en/latest/ref/ec2.html#boto.ec2.connection.EC2Connection.get_all_reservations
#    - http://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/QuickStartEC2Instance.html
#
from __future__ import print_function, unicode_literals
import sys
import re

import requests
from jinja2 import Template
from boto import ec2
import netaddr


# Update when we move to the next one
METADATA = 'http://169.254.169.254/2016-09-02/meta-data/{}'

# Map from VPC CIDR block to account name
VPC_CIDR_TO_ACCOUNT = {
    '10.154.224.0/24': 'NLM-INT',
    '10.154.226.0/23': 'NLM-PROD',
    '10.154.228.0/23': 'NLM-PROD',
    '10.154.230.0/23': 'NLM-PROD',
    '10.154.232.0/23': 'NLM-QA',
    '10.154.234.0/23': 'NLM-QA',
    '10.154.236.0/23': 'NLM-QA',
    '10.154.238.0/23': 'NLM-INT',
    '10.154.240.0/23': 'NLM-INT',
    '10.154.242.0/23': 'NLM-INT',
    '10.154.224.0/23': 'NLM-INT',
    '10.154.246.0/23': 'NLM-INT'
}


# Template for generating /var/awslogs/etc/aws.conf
AWS_CONF_TEMPLATE = Template(
    """[plugins]
    cwlogs = cwlogs

    [default]
    region = {{ region }}
    """
)


# Template for generating /var/awslogs/etc/awslogs.conf, which contains rules for OS specific logs.
AWSLOGS_CONF_TEMPLATE = Template(
    """Nothing here yet"""
)


class BaseMetadata(object):
    """
    Proxy for instance metadata that uses lazy initialization and adds additional properties
    """

    def __init__(self):
        self.__region = None
        self.__instance_id = None
        self.__iaminfo = None
        self.__private_address = None

    @property
    def region(self):
        """
        My region from Instance Metadata
        """
        if self.__region is None:
            r = requests.get(METADATA.format('placement/availability-zone'))
            assert r.ok
            self.__region = r.content.decode('utf-8')[:-1]
        return self.__region

    @property
    def instance_id(self):
        """
        My instance id from Instance Metadata
        """
        if self.__instance_id is None:
            r = requests.get(METADATA.format('instance-id'))
            assert r.ok
            self.__instance_id = r.content.decode('utf-8')
        return self.__instance_id

    @property
    def private_address(self):
        """
        My local, private IPv4 address
        """
        if self.__private_address is None:
            r = requests.get(METADATA.format('local-ipv4'))
            assert r.ok
            self.__private_address = r.content.decode('utf-8')
        return self.__private_address

    @property
    def iam_info(self):
        """
        My iam info from instance metadata
        """
        if self.__iaminfo is None:
            r = requests.get(METADATA.format('iam/info'))
            assert r.ok
            self.__iaminfo = r.json()
        return self.__iaminfo


class EnhancedMetadata(BaseMetadata):
    """
    Adds meta-data derived from boto 2.x requests for the instance, and NLM derived meta-data that is not standard
    """

    def __init__(self):
        super(EnhancedMetadata, self).__init__()
        self.__tags = False

    @property
    def tags(self):
        """
        Read this instances tags
        """
        if self.__tags is False:
            conn = ec2.connect_to_region(self.region)
            rsvs = conn.get_all_reservations(instance_ids=[self.instance_id])
            assert len(rsvs) == 1
            assert len(rsvs[0].instances) == 1
            self.__tags = rsvs[0].instances[0].tags
        return self.__tags

    @staticmethod
    def _nlmaccount(ipstr, dflt=None):
        """
        Determines an NLM account name using an IP address

        :param ipstr: a string representing an IP address
        :param dfltacconut: a value to be returned as the default
        :return: a string representing the semantic name of the NLM-OCCS account
        """
        ip = netaddr.IPAddress(ipstr)
        for cidrmask, accountname in VPC_CIDR_TO_ACCOUNT.items():
            cidrnet = netaddr.IPNetwork(cidrmask)
            if ip in cidrnet:
                return accountname
        return dflt

    @property
    def nlmaccount(self):
        """
        Determines the NLM account name using the local IP address

        :return: a string representing the semantic name of the NLM-OCCS account
        """
        return EnhancedMetadata._nlmaccount(self.private_address, dflt='NLM-INT')


def write_aws_conf(path='/var/awslogs/etc/aws.conf', region='us-east-1'):
    """
    Write region to aws.conf, making sure to use logs template
    """
    with open(path, 'w') as f:
        f.write(AWS_CONF_TEMPLATE.render(region=region))


def get_logstream_name(meta):
    """
    Determine a logstream name used for most logs
    """
    name = 'unknown'
    try:
        if u'Name' in meta.tags:
            _name = meta.tags[u'Name']
            _name = _name.encode('ascii', 'ignore')
            _name = re.sub(r'[^a-zA-Z0-9]+', r'-', _name).strip('-')
            _name = re.sub(r'--+', r'-', _name)
            name = _name
    except Exception as e:
        sys.stderr.write('Exception: %s\n' % e)
        pass
    return '{}-{}-{}'.format(name, meta.private_address, meta.instance_id)


def main(args):
    meta = EnhancedMetadata()
    write_aws_conf(region=meta.region)
    print('log_stream_name = %s' % get_logstream_name(meta))
    print('Account = %s' % meta.nlmaccount)


if __name__ == '__main__':
    main(sys.argv)
