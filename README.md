# multi-tenant-saas
Altostra implementation of Serverless SaaS -
Reference Solution https://github.com/aws-samples/aws-saas-factory-ref-solution-serverless-saas

## Changes

- Instead of assuming the role `AuthorizerAccessRole` in the authorizer (a role that gives
full access to all DynamoDB tables of the account in the region 😖), we will just
authenticate the request, and give lambdas fine-grained access
- No alarms. 
- No deployments.
- No APIs policies, and blocking access on a IAM basis
- No throttling support (no support for API-KEYs or usage plans)
- Authorizer must be lambda authorizer (rather than token)
- No way to pass parameters to custom resources

## Installation


