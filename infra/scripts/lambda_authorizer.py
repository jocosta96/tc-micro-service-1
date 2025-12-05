import os
    
def lambda_handler(event, context):
    token = event.get('authorizationToken')
    method_arn = event.get('methodArn')
    arn_base = ':'.join(method_arn.split(':')[:-1])
    resource = arn_base + ':*'

    if not token or token != os.environ.get("TOKEN"):
        return {
            "principalId": "user",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": "Deny",
                        "Resource": resource
                    }
                ]
            }
        }

    return {
        "principalId": "user",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": resource
                }
            ]
        }
    }