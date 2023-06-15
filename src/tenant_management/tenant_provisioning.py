import logger
import boto3
from utils import ResponseError

codepipeline = boto3.client('codepipeline')
stack_name = 'stack-{0}'

def provision_tenant(tenant_details, table_tenant_stack_mapping):
  raise ResponseError('Tenant provisioning not yet supported')

  response_ddb = table_tenant_stack_mapping.put_item(
    Item={
        'tenantId': tenant_details['tenantId'],
        'stackName': stack_name.format(tenant_details['tenantId']),
        'applyLatestRelease': True,
        'codeCommitId': ''
      }
    )    

  logger.info(response_ddb)

  response_codepipeline = codepipeline.start_pipeline_execution(
    name='serverless-saas-pipeline'
  )

  logger.info(response_codepipeline)