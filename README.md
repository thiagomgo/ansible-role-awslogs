# **Ansible Role: AWSLogs**

[![Build Status](https://travis-ci.org/thiagomgo/ansible-role-awslogs.svg?branch=master)](https://travis-ci.org/thiagomgo/ansible-role-awslogs) [![Ansible Galaxy](https://img.shields.io/badge/ansible--galaxy-awslogs-blue.svg)](https://galaxy.ansible.com/thiagomgo/awslogs/)

This role install and configure the AWS CloudWatch Logs.

## Requirements

This role only requires Ansible version 1.9+ and EC2_FACTS module.

## Role Variables

This role only uses two variables, `awslogs_region` and `awslogs_logs`, which is a dictionary comprised of the following items:

```yaml

awslogs_logs:
  - file: /var/log/syslog            # The path to the log file you want to ship (required)
    format: "%b %d %H:%M:%S"         # The date and time format of the log file
    time_zone: "LOCAL"               # Timezone, can either be LOCAL or UTC
    initial_position: "end_of_file"  # Where log shipping should start from
    group_name: syslog               # The Cloudwatch Logs group name (required)
    stream_name: "{instance_id}"     # You can use a literal string and/or predefined variables ({instance_id}, {hostname}, {ip_address})
```

In addition, there are two variables that are not used by default:

```yaml
awslogs_access_key_id: XXX           # AWS key ID, used instead of IAM roles
awslogs_secret_access_key: XXX       # AWS secret key, used instead of IAM roles
```

This configuration is further expanded on in the [Amazon Cloudwatch Logs Documentation](http://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AgentReference.html#d0e2872).

## Dependencies

None

## Example Playbook

```yaml
---

- hosts: all

  vars:
    awslogs_region: us-east-1
    awslogs_logs:
      - file: /var/log/syslog
        format: "%b %d %H:%M:%S"
        time_zone: "LOCAL"
        initial_position: "end_of_file"
        group_name: syslog

      - file: /var/log/boot.log
        time_zone: "UTC"
        initial_position: "start_of_file"
        group_name: boot

  roles:
    - ansible-role-awslogs

```

## License

MIT / BSD

## Author Information

U.S. National Library of Medicine (NLM)
Based on work by:

Thiago Gomes
- thiago.mgomes [at] gmail.com
