# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
from AuthorizedUser import AuthorizedUser
import boto3
import os
from tenant_management import tenant_creation, tenant_provisioning
import utils
import uuid
import logger
import requests
import re
from user_management.create_tenant_admin_user import create_tenant_admin_user

region = os.environ['AWS_REGION']

platinum_tier_api_key = os.environ['PLATINUM_TIER_API_KEY']
premium_tier_api_key = os.environ['PREMIUM_TIER_API_KEY']
standard_tier_api_key = os.environ['STANDARD_TIER_API_KEY']
basic_tier_api_key = os.environ['BASIC_TIER_API_KEY']

lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')

def register_tenant(event, context):
    logger.info(event)
    try:
        api_key=''
        tenant_id = uuid.uuid1().hex
        tenant_details = json.loads(event['body'])
        tenant_details['dedicatedTenancy'] = 'false'

        if (tenant_details['tenantTier'].upper() == utils.TenantTier.PLATINUM.value.upper()):
            tenant_details['dedicatedTenancy'] = 'true'
            api_key = platinum_tier_api_key
        elif (tenant_details['tenantTier'].upper() == utils.TenantTier.PREMIUM.value.upper()):
            api_key = premium_tier_api_key
        elif (tenant_details['tenantTier'].upper() == utils.TenantTier.STANDARD.value.upper()):
            api_key = standard_tier_api_key
        elif (tenant_details['tenantTier'].upper() == utils.TenantTier.BASIC.value.upper()):
            api_key = basic_tier_api_key

        tenant_details['tenantId'] = tenant_id
        tenant_details['apiKey'] = api_key

        logger.info(tenant_details)

        create_user_response: dict[str, any] = __create_tenant_admin_user(tenant_details)
        logger.info(create_user_response)
        
        tenant_details['userPoolId'] = create_user_response['userPoolId']
        tenant_details['appClientId'] = create_user_response['appClientId']
        tenant_details['tenantAdminUserName'] = create_user_response['tenantAdminUserName']

        authData = AuthorizedUser(event['requestContext']['authorizer'])
        __create_tenant(tenant_details, authData)

        if (tenant_details['dedicatedTenancy'].upper() == 'TRUE'):
            provision_tenant_response = __provision_tenant(tenant_details)
            logger.info(provision_tenant_response)

    
    except utils.ResponseError as e:
        return e.response
    except Exception as e:
        err = Exception('Error registering a new tenant', e)
        logger.error(e)
        raise err
    else:
        return utils.create_success_response("You have been registered in our system")

def __create_tenant_admin_user(tenant_details):
    tenant_user_pool_id = os.environ['TENANT_USER_POOL_ID']
    tenant_app_client_id = os.environ['TENANT_APP_CLIENT_ID']
    table_tenant_user_map = dynamodb.Table(os.environ['TABLE_TENANTUSERMAPPINGTABLE'])

    try:
        result: dict[str, any] = create_tenant_admin_user(
            tenant_details,
            tenant_user_pool_id,
            tenant_app_client_id,
            table_tenant_user_map,
            application_site_url= os.environ['TENANT_USER_POOL_CALLBACK_URL']
        )
    except utils.ResponseError:
        raise
    except Exception as e:
        err = Exception('Error occurred while calling the create tenant admin user service', e)
        logger.error(err)
        raise err
    else:
        return result

def __create_tenant(tenant_details, auth: AuthorizedUser):
    try:
        table_tenant_details = dynamodb.Table(os.environ['TABLE_TENANTDETAILSTABLE'])
        table_system_settings = dynamodb.Table(os.environ['TABLE_SERVERLESSSAASSETTINGSTABLE'])

        tenant_creation.create_tenant(
            auth, 
            tenant_details, 
            table_tenant_details, 
            table_system_settings,
        )
    except utils.ResponseError:
        raise
    except Exception as e:
        err = Exception('Error occurred while creating the tenant record in table', e) 
        logger.error(err)
        raise err

def __provision_tenant(tenant_details):
    table_tenant_stack_mapping = dynamodb.Table(os.environ['TABLE_TENANTSTACKMAPPINGTABLE'])
    tenant_provisioning.provision_tenant(tenant_details, table_tenant_stack_mapping)

              
