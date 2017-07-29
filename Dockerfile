# Builds a docker image that is suitable for testing 
# or developing our docker role.
FROM centos:7.3.1611

# Add the tools needed
RUN yum install -y epel-release openssh-server
RUN yum install -y ansible python2-pip python-virtualenv

# Add some convenience
RUN yum -y install which less

# Add the ansible role
ADD . /etc/ansible/roles/occs-awslogs/
ADD tests/inventory /etc/ansible/hosts

# NOTE: This is not going well - this role modifies systemctl services, as do
# many others.  So, you need a real init.  docker-init is often used, but
# clearly, if you want to test provisioning *without* fighting against Docker,
# then use vagrant.

