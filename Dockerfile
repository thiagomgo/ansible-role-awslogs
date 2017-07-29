# Start vanilla
FROM centos:7

# Add the tools needed
RUN yum -y install epel-release
RUN yum -y install ansible python2-pip python-virtualenv

# Add some convenience
RUN yum -y install which less

# Add the ansible role
ADD . /etc/ansible/roles/occs-awslogs/
ADD tests/hosts /etc/ansible/hosts

