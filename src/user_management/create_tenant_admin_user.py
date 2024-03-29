import logger
import user_management
from utils import ResponseError

def create_tenant_admin_user(
  tenant_details,
  tenant_user_pool_id,
  tenant_app_client_id,
  table_tenant_user_map,
  application_site_url
):
  tenant_id = tenant_details['tenantId']
  logger.info(tenant_details)

  if (tenant_details['dedicatedTenancy'] == 'true'):
      raise ResponseError('Dedicated tenants are not supported yet')

      user_pool_response = user_management.create_user_pool(tenant_id, application_site_url)
      user_pool_id = user_pool_response['UserPool']['Id']
      logger.info (user_pool_id)
      
      app_client_response = user_management.create_user_pool_client(
          user_pool_id, 
          os.environ['TENANT_USER_POOL_CALLBACK_URL']
      )
      logger.info(app_client_response)
      app_client_id = app_client_response['UserPoolClient']['ClientId']
      user_pool_domain_response = user_management.create_user_pool_domain(user_pool_id, tenant_id)
      
      logger.info ("New Tenant Created")
  else:
      user_pool_id = tenant_user_pool_id
      app_client_id = tenant_app_client_id

  #Add tenant admin now based upon user pool
  tenant_user_group_response = user_management.create_user_group(
      user_pool_id,
      tenant_id,
      "User group for tenant {0}".format(tenant_id)
  )

  tenant_admin_user_name = 'tenant-admin-{0}'.format(tenant_details['tenantId'])

  create_tenant_admin_response = user_management.create_tenant_admin(user_pool_id, tenant_admin_user_name, tenant_details)
  
  add_tenant_admin_to_group_response = user_management.add_user_to_group(
      user_pool_id, 
      tenant_admin_user_name, 
      tenant_user_group_response['Group']['GroupName']
  )
  
  tenant_user_mapping_response = user_management.create_user_tenant_mapping(
      tenant_admin_user_name,
      tenant_id,
      table_tenant_user_map
  )
  
  response = {
    "userPoolId": user_pool_id,
    "appClientId": app_client_id,
    "tenantAdminUserName": tenant_admin_user_name
  }
  
  return response