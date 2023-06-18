import logger
import boto3

client = boto3.client('cognito-idp')

SYSTEM_ADMINS_GROUP = 'SystemAdmins'

def create_user_pool(tenant_id, application_site_url):
    email_message = ''.join(["Login into tenant UI application at ", 
                    application_site_url,
                    " with username {username} and temporary password {####}"])
    email_subject = "Your temporary password for tenant UI application"  
    response = client.create_user_pool(
        PoolName= tenant_id + '-ServerlessSaaSUserPool',
        AutoVerifiedAttributes=['email'],
        AccountRecoverySetting={
            'RecoveryMechanisms': [
                {
                    'Priority': 1,
                    'Name': 'verified_email'
                },
            ]
        },
        Schema=[
            {
                'Name': 'email',
                'AttributeDataType': 'String',
                'Required': True,                    
            },
            {
                'Name': 'tenantId',
                'AttributeDataType': 'String',
                'Required': False,                    
            },            
            {
                'Name': 'userRole',
                'AttributeDataType': 'String',
                'Required': False,                    
            }
        ],
        AdminCreateUserConfig={
            'InviteMessageTemplate': {
                'EmailMessage': email_message,
                'EmailSubject': email_subject
            }
        }
    )    
    return response

def create_user_pool_client(user_pool_id, user_pool_callback_url):
    response = client.create_user_pool_client(
        UserPoolId= user_pool_id,
        ClientName= 'ServerlessSaaSClient',
        GenerateSecret= False,
        AllowedOAuthFlowsUserPoolClient= True,
        AllowedOAuthFlows=[
            'code', 'implicit'
        ],
        SupportedIdentityProviders=[
            'COGNITO',
        ],
        CallbackURLs=[
            user_pool_callback_url,
        ],
        LogoutURLs= [
            user_pool_callback_url,
        ],
        AllowedOAuthScopes=[
            'email',
            'openid',
            'profile'
        ],
        WriteAttributes=[
            'email',
            'custom:tenantId'
        ]
    )
    return response

def create_user_pool_domain(user_pool_id, tenant_id):
    response = client.create_user_pool_domain(
        Domain= tenant_id + '-serverlesssaas',
        UserPoolId=user_pool_id
    )
    return response

def create_user_group(user_pool_id, group_name, group_description):
    response = client.create_group(
        GroupName=group_name,
        UserPoolId=user_pool_id,
        Description= group_description,
        Precedence=0
    )
    return response

def create_tenant_admin(user_pool_id, tenant_admin_user_name, user_details):
    response = client.admin_create_user(
        Username=tenant_admin_user_name,
        UserPoolId=user_pool_id,
        ForceAliasCreation=True,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': user_details['tenantEmail']
            },
            {
                'Name': 'email_verified',
                'Value': 'true'
            },
            {
                'Name': 'custom:userRole',
                'Value': 'TenantAdmin' 
            },            
            {
                'Name': 'custom:tenantId',
                'Value': user_details['tenantId']
            }
        ]
    )
    return response

def add_user_to_group(user_pool_id, user_name, group_name):
    logger.info({
        'user_pool_id': user_pool_id,
        'user_name': user_name,
        'group_name': group_name,
    })
    response = client.admin_add_user_to_group(
        UserPoolId=user_pool_id,
        Username=user_name,
        GroupName=group_name
    )
    return response

def create_user_tenant_mapping(user_name, tenant_id, table_tenant_user_map):
    response = table_tenant_user_map.put_item(
            Item={
                    'tenantId': tenant_id,
                    'userName': user_name
                }
            )                    

    return response
