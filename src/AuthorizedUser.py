import logger

class AuthorizedUser:
    def __init__(self, authData) -> None:
        logger.info(authData)

        self.userName = authData.get('userName')
        self.tenantId = authData.get('tenantId')
        self.userPoolId = authData.get('userPoolId')
        self.apiKey = authData.get('apiKey')
        self.userRole = authData.get('userRole')

    def isSysAdmin(self) -> bool:
        return self.userRole == 'SystemAdmin'