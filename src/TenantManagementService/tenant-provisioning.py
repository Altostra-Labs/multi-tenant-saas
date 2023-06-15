# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import boto3
import utils
from botocore.exceptions import ClientError
import logger
import os
from aws_lambda_powertools import Tracer
import tenant_management.tenant_provisioning as tenant_provisioning
tracer = Tracer()

tenant_stack_mapping_table_name = os.environ['TABLE_TENANTSTACKMAPPINGTABLE']

dynamodb = boto3.resource('dynamodb')
codepipeline = boto3.client('codepipeline')
cloudformation = boto3.client('cloudformation')
table_tenant_stack_mapping = dynamodb.Table(tenant_stack_mapping_table_name)

stack_name = 'stack-{0}'
@tracer.capture_lambda_handler
def provision_tenant(event, context):
    
    tenant_details = json.loads(event['body'])
    
    try:
       tenant_provisioning.provision_tenant(tenant_details, table_tenant_stack_mapping)

    except utils.ResponseError as e:
        return e.response
    except Exception as e:
        raise
    else:
        return utils.create_success_response("Tenant Provisioning Started")

@tracer.capture_lambda_handler
#this method uses IAM Authorization and protected using a resource policy. This method is also invoked async
def deprovision_tenant(event, context):
    logger.info("Request received to deprovision a tenant")
    
    tenantid_to_deprovision = event['tenantId']
    
    try:          
        response_ddb = table_tenant_stack_mapping.delete_item(
            Key={
                    'tenantId': tenantid_to_deprovision                    
                }
            )    
        
        logger.info(response_ddb)

        response_cloudformation = cloudformation.delete_stack(
            StackName=stack_name.format(tenantid_to_deprovision)
        )

        logger.info(response_cloudformation)

    except Exception as e:
        raise
    else:
        return utils.create_success_response("Tenant Deprovisioning Started")

 
