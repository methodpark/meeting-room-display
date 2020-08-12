Inspired by the CoffeCaller project's Ansible deployment.

Invoking the installation on the device and code deployment:

    ansible-playbook -i hosts deploy.yml

Invoking only the installation on the device:

    ansible-playbook -i hosts deploy.yml --tags "installation"

Invoking only the code deployment:

    ansible-playbook -i hosts deploy.yml --tags "deployment"

Deploying only to a single device (mind the comma!):

    ansible-playbook -i mrd-dev, deploy.yml
