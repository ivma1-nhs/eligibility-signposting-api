# Networking stack

The networking stack contains the networking resources that are securing the Eligibility Signposting API application resources.

The stack is documented on [this Confluence page](https://nhsd-confluence.digital.nhs.uk/spaces/Vacc/pages/1054575846/VPC+structure)

## Traffic Flow Explanation

### Public HTTPS Request Flow

* External client makes HTTPS request → Internet Gateway
* Request routes to Load Balancer or API Gateway in public subnet
* Request forwards to Lambda (or other application) in private subnet
* Lambda processes the request and returns response
* Response returns to client through the same path

### Outbound Internet Access

* Lambda functions in private subnets can make outbound internet calls via NAT Gateways
* This allows Lambda to call external APIs, download packages, etc.
* No direct inbound access to Lambda from the internet

### Internal-Only Traffic

* Lambda functions access AWS services via VPC Endpoints:
  * Gateway Endpoints: S3, DynamoDB
  * Interface Endpoints: KMS, CloudWatch, SSM, Secrets Manager, Lambda, STS, SQS
* All traffic between Lambda and AWS services stays within the AWS network
* No internet transit required for AWS service access

### Security Controls

#### Network ACLs

Public subnets: Allow HTTP(80), HTTPS(443), ephemeral ports
Private subnets: Allow VPC traffic and responses to outbound requests

#### Security Groups

Default security group: Deny all
VPC Endpoint security group: Allow HTTPS(443) from within VPC

#### Route Tables

Public subnets: Route to Internet Gateway for external access
Private subnets: Route to NAT Gateways for outbound-only access

## Deployment to AWS Development Environment

This stack should only ever be deployed once per account (e.g. the use of Terraform workspaces is explicitly not recommended beyond specifying `dev` as the environment).

Deployment to the Development environment is done through use of `make` commands

### Initialize Terraform and Plan

Run the following command to initialize Terraform and generate a plan. Replace `<env>` with the target environment:

```bash
make terraform env=dev stack=networking tf-command=init workspace=<env>
```

then

```bash
make terraform env=dev stack=networking tf-command=plan workspace=<env>
```

### 1.4 Apply Terraform Changes

Deploy the Terraform configuration using the following command:

```bash
make terraform env=dev stack=networking tf-command=apply workspace=<env>
```

## Release Deployment to AWS (Int, Ref and Prod)

Deployment to Int, Ref and Prod, as well as running the automated tests can be done via GitHub actions, when they are developed.

## ACM Certificates needed for each environment

For each environment, in order to verify domain ownership and allow secure communication with the APIM API Proxy, we create:

1. A domain validation certificate
2. mTLS certificates and secrets

Each of these needs manual intervention for creation of the assets.

### Domain Validation

In `infrastructure/stacks/networking/acm_certificates.tf` ACM Certificate Manager is used to request a domain validation certificate.
Running the Terraform will create this certificate, but the DNS Validation will only happen if we request the DNS Team update the
CNAME record for the subdomain in question.

#### Action needed

1. In AWS Console, for the environment account, navigate to Certificate Manager --> List certificates.
2. In `Domains` download the CSV of the CNAME details.
3. Email `england.dnsteam@nhs.net` with subject `eligibility-signposting-api.nhs.uk - Requesting a sub domain - <env>` where 'env' is the
   environment to be provisioned (e.g. `dev` would be our development environment), attaching the exported csv and with the message:

   ```text
      Hi DNS Team,

      Please could we add the subdomain 'dev' for our top level domain  'eligibility-signposting-api.nhs.uk'?

      e.g.

      dev.eligibility-signposting-api.nhs.uk

      We've generated an ACM certificate for DNS validation, which has generated a CNAME name and value which I think would need adding to your records to allow us to validate. I've attached this to the email in a CSV, please let us know if this isn't the approach you expect.

      Thanks,

      Edd
   ```

4. Check the certificate for DNS validation once you've received a confirmation that the subdomain was created.

### mTLS certificates

See the [APIM documentation](https://nhsd-confluence.digital.nhs.uk/spaces/APM/pages/734397569/How+to+implement+mutual+TLS+mTLS+security+for+your+API+backend) for more details.

In order to generate the certificates used by our API Gateway, we need to do the following

#### Generate a CSR

1. Generate a Certificate Signing Request (CSR) and private key.
   1. Create a configuration file for the environment e.g. `dev.conf`

   ```text
   [req]
   default_bits = 4096
   distinguished_name = req_distinguished_name
   req_extensions = v3_req
   prompt = no

   [req_distinguished_name]
   C = GB
   ST = West Yorkshire
   L = Leeds
   O = NHS England
   OU = API Management
   CN = dev.eligibility-signposting-api.nhs.uk

   [v3_req]
   keyUsage = keyEncipherment, dataEncipherment
   extendedKeyUsage = serverAuth
   ```

   1. Run the following:

   ```bash
   mkdir -p csrs
   mkdir -p keys

   openssl req -new -newkey rsa:4096 -nodes -sha256 -keyout keys/<env>.eligibility-signposting-api.nhs.uk.key -out csrs/<env>.eligibility-signposting-api.nhs.uk.csr -config <env>.conf -extensions v3_req
   ```

1. Send the generated CSR to the appropriate team for signing:
    For all non-production environments, contact `itoc.supportdesk@nhs.net` and reference the INT / PTL environment
    For production environments, contact `dir@nhs.net`

```text
Hi,

Please could I get the attached CSR signed. Details as follows:

Name:
Company/Organisation: Eligibility Data Team, NHS England
Contact Number:
Common Name (CN):  dev.eligibility-signposting-api.nhs.uk
Reason for the Certificate: New APIM client
Environment: INT / PTL

Thanks,

Edd
```

#### Add root and intermediary CAs to our truststore

1. Download the INT CA certificates from [here](https://digital.nhs.uk/services/spine/updating-nhs-public-key-infrastructure-certificates/g2-certificate-technical-implementation#certificate-downloads)

  * NHS INT Root Authority G2 (Trusted Root)
  * NHS Authentication G2 (Intermediate/Subordinate)

2. `cat intermediate-cert.pem root-cert.pem > truststore.pem` **in this order** to create a truststore.pem. This is used in `infrastructure/stacks/api-layer/truststore_s3_bucket.tf`
3. Upload the truststore.pem to the s3 location and bucket in point 2.

#### Validate CSR

1. Run

```bash
openssl verify -CAfile truststore.crt new-cert.crt
```

It should return an 'OK' response.

#### Upload the CSR to SSM (both certificate and private key)

`infrastructure/stacks/networking/ssm.tf` contains the Terraform definition for the SSM parameters into which the CA Certificate, CSR and private key should be stored for the given environment.
