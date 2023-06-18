from AuthorizedUser import AuthorizedUser
from utils import ResponseError, create_unauthorized_response
import logger

def create_tenant(
  auth: AuthorizedUser,
  tenant_details,
  table_tenant_details,
  table_system_settings,
): 
  logger.info(auth.userRole)
  if not auth.isSysAdmin():
    raise ResponseError(
       'Currently only sys-admins can create tenants',
       response= create_unauthorized_response()
    )

  api_gateway_url = ''       

  try:          
      # for pooled tenants the apigateway url is saving in settings during stack creation
      # update from there during tenant creation
      if(tenant_details['dedicatedTenancy'].lower() == 'true'):
        raise ResponseError(
          'Dedicated tenancy',
          response= create_unauthorized_response()
        )

      settings_response = table_system_settings.get_item(
          Key={
              'settingName': 'apiGatewayUrl-Pooled'
          } 
      )
      api_gateway_url = settings_response['Item']['settingValue']

      response = table_tenant_details.put_item(
          Item={
                  'tenantId': tenant_details['tenantId'],
                  'tenantName' : tenant_details['tenantName'],
                  'tenantAddress': tenant_details['tenantAddress'],
                  'tenantEmail': tenant_details['tenantEmail'],
                  'tenantPhone': tenant_details['tenantPhone'],
                  'tenantTier': tenant_details['tenantTier'],
                  'apiKey': tenant_details['apiKey'],
                  'userPoolId': tenant_details['userPoolId'],                 
                  'appClientId': tenant_details['appClientId'],
                  'dedicatedTenancy': tenant_details['dedicatedTenancy'],
                  'isActive': True,
                  'apiGatewayUrl': api_gateway_url
              }
          )                    

  except Exception as e:
      raise Exception('Error creating a new tenant', e)
  