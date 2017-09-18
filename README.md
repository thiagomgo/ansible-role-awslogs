# **Ansible Role: AWSLogs**

This role install and configure the AWS CloudWatch Logs.

## Requirements

This role only requires Ansible version 1.9+

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

## Testing

### Python code

This code includes a Python library and script built in a modular fashion for
testing.  The python alone can be tested as follows (use a virtualenv):

    pip install -r requirements.txt
    pytest

### Ansible role

(NOTE: The stuff below is aspirational - systemctl isn't really running well
       inside the container, and although I know people have fixed that, and 
       in fact run ansible via ssh into docker, I haven't got there yet.)

This role can be tested using Vagrant. A base box named `centos7_test_packer`
is expected to be present.

* Bring up guest and run ansible in it

    cd tests; vagrant up

* Clean-up

    cd tests; vagrant destroy -f

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
