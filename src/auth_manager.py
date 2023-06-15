# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import utils

# These are the roles being supported in this reference architecture
class UserRoles:
    SYSTEM_ADMIN    = "SystemAdmin"
    CUSTOMER_SUPPORT  = "CustomerSupport"
    TENANT_ADMIN    = "TenantAdmin"    
    TENANT_USER     = "TenantUser"
    
def isTenantAdmin(user_role):
    if (user_role == UserRoles.TENANT_ADMIN):
        return True
    else:
        return False

def isSystemAdmin(user_role):
    if (user_role == UserRoles.SYSTEM_ADMIN):
        return True
    else:
        return False


def isSaaSProvider(user_role):
    if (user_role == UserRoles.SYSTEM_ADMIN or user_role == UserRoles.CUSTOMER_SUPPORT):
        return True
    else:
        return False
def isTenantUser(user_role):
    if (user_role == UserRoles.TENANT_USER):
        return True
    else:
        return False

def getPolicyForUser(user_role, service_identifier, tenant_id, region, aws_account_id):
    """ This method is being used by Authorizer to get appropriate policy by user role

    Args:
        user_role (string): UserRoles enum
        tenant_id (string): 
        region (string): 
        aws_account_id (string):  

    Returns:
        string: policy that tenant needs to assume
    """
    iam_policy = ""

    return iam_policy
