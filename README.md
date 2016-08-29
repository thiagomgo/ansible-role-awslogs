# **Ansible Role: AWSLogs**

[![Build Status](https://travis-ci.org/thiagomgo/ansible-role-awslogs.svg?branch=master)](https://travis-ci.org/thiagomgo/ansible-role-awslogs) [![Ansible Galaxy](https://img.shields.io/badge/ansible--galaxy-awslogs-blue.svg)](https://galaxy.ansible.com/thiagomgo/awslogs/)

This role install and configure the AWS CloudWatch Logs.

## Requirements

This role only requires Ansible version 1.9+ and EC2_FACTS module.

## Role Variables

Here is a list of all the default variables for this role, which are also available in `defaults/main.yml`.

```yaml
---

# logs:
#    - file: /var/log/syslog            (required)
#      format: "%b %d %H:%M:%S"
#      time_zone: "LOCAL"
#      initial_position: "end_of_file"
#      group_name: syslog               (required)
#
```

## Dependencies

None

## Example Playbook

```yaml
---

- hosts: all

  vars:

    logs:
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

Thiago Gomes
- thiago.mgomes [at] gmail.com


