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
import os
from argparse import ArgumentParser

import requests
from jinja2 import Environment, FileSystemLoader
from boto import ec2


# Update when we move to the next one
METADATA = 'http://169.254.169.254/2016-09-02/meta-data/{}'

# Template for generating /var/awslogs/etc/aws.conf
TEMPLATES_PATH = '/var/awslogs/nlm/templates'

CONF_PATH = '/var/awslogs/etc'


class BaseMetadata(object):
    """
    Proxy for instance metadata that uses lazy initialization and adds additional properties
    """

    def __init__(self):
        self.__region = None
        self.__instance_id = None
        self.__iaminfo = None
        self.__private_address = None

    def mock(self):
        self.__region = 'us-east-1'
        self.__instance_id = 'i-am-groot'
        self.__iaminfo = {'realm': 'groot'}
        self.__private_address = '10.100.99.99'

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

ACCOUNT_KEY = u'AWS-Account'
NAME_KEY = u'Name'


class EnhancedMetadata(BaseMetadata):
    """
    Adds meta-data derived from boto 2.x requests for the instance, and NLM derived meta-data that is not standard
    """

    def __init__(self):
        super(EnhancedMetadata, self).__init__()
        self.__tags = False

    def mock(self):
        super(EnhancedMetadata, self).mock()
        self.mock_tags(u'groot', u'NLM-INT')

    def mock_tags(self, name, account):
        self.__tags = {NAME_KEY: name, ACCOUNT_KEY: account}

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

    @property
    def nametag(self):
        """
        Gets the 'Name' tag value, or returns a default
        """
        name = 'unknown'
        try:
            if NAME_KEY in self.tags:
                _name = self.tags[NAME_KEY]
                _name = re.sub(r'[^a-zA-Z0-9]+', r'-', _name).strip('-')
                _name = re.sub(r'--+', r'-', _name)
                name = _name
        except Exception as e:
            sys.stderr.write('Exception: %s\n' % e)
            pass
        return name

    @property
    def nlmaccount(self):
        """
        Gets the "AWS-Account" tag value, or returns a default
        """
        account = 'NLM-INT'
        try:
            if ACCOUNT_KEY in self.tags:
                _account = self.tags[ACCOUNT_KEY]
                _account = re.sub(r'[^a-zA-Z0-9]+', r'-', _account).strip('-')
                _account = re.sub(r'--+', r'-', _account)
                account = _account
        except Exception as e:
            sys.stderr.write('Exception: %s\n' % e)
            pass
        return account


class ConfigWriter(object):

    def __init__(self, templates_path=TEMPLATES_PATH, conf_path=CONF_PATH):
        self.templates_path = templates_path
        self.conf_path = conf_path
        self.__env = None

    @property
    def env(self):
        if self.__env is None:
            self.__env = Environment(loader=FileSystemLoader(self.templates_path))
        return self.__env

    def write_aws_conf(self, region):
        template = self.env.get_template('aws.conf.j2')
        path = os.path.join(self.conf_path, 'aws.conf')
        with open(path, 'w') as f:
            f.write(template.render(region=region))

    def write_awslogs_conf(self, nlmaccount, nametag):
        template = self.env.get_template('awslogs.conf.j2')
        path = os.path.join(self.conf_path, 'awslogs.conf')
        with open(path, 'w') as f:
            f.write(template.render(nlmaccount=nlmaccount, nametag=nametag))


def parse_args(args):
    parser = ArgumentParser(description='awslogs agent pre-initialization')
    parser.add_argument('--config', metavar='PATH', required=False, default=CONF_PATH,
                        help='Specify the path where to write the configuration')
    parser.add_argument('--templates', metavar='PATH', required=False, default=TEMPLATES_PATH,
                        help='Specify the path where this program looks for templates')
    parser.add_argument('--mock', action='store_true', default=None,
                        help='Enable mocking for AWS MetaData')
    return parser.parse_args(args)


def main(args):
    opts = parse_args(args)

    meta = EnhancedMetadata()
    if opts.mock:
        meta.mock()

    print('Account = %s' % meta.nlmaccount)
    print('Name tag = %s' % meta.nametag)

    config_writer = ConfigWriter(templates_path=opts.templates, conf_path=opts.config)
    config_writer.write_aws_conf(meta.region)
    config_writer.write_awslogs_conf(meta.nlmaccount, meta.nametag)


if __name__ == '__main__':
    main(sys.argv)
