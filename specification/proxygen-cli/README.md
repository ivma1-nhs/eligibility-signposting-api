# Proxygen CLI usage

The [proxygen-cli](https://github.com/NHSDigital/proxygen-cli/tree/main) is a tool which can be used to interact with the APIM proxy layer,
to deploy our OAS specification to different environments, deploy a sandbox backend and store secrets and certificates.

## Pre-requisites

### Install proxygen-cli

The proxygen-cli package currently requires python v3.9 or greater, but not v3.13.

```bash
pyenv install 3.11.1
pyenv virtualenv 3.11.1 proxygenenv
pyenv local 3.11.1 # if you want to switch to this env in this directory
pyenv activate proxygenenv

python --version # check the virtual env is 3.11.1
pip install proxygen-cli
```

### AWS login

The AWS Portal for logging into the eligibility-signposting-api provides information about access keys for your respective accounts. Any secrets related to proxygen are stored
in the development environment account. You need to set up your AWS cli with your developer credentials to use the related `make` commands.

## Getting credentials

There are `make` commands available in the main Makefile:

* `retrieve-proxygen-key` - this retrieves the private key for our APIM machine account and places it in `~/.proxygen/`. This location is where proxygen-cli stores it's configuration.
* `setup-proxygen-credentials` - this copies the configuration in `/specification/.proxygen` to `~/.proxygen/`, to pre-configure the cli with details of our api.
* `get-spec` - this retrieves the specification we have published in the API catalogue (production environment)

## Further Usage

See [the CLI documentation](https://nhsd-confluence.digital.nhs.uk/pages/viewpage.action?spaceKey=APM&title=Proxygen+CLI+user+guide)
