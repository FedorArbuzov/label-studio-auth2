#from keycloak import KeycloakOpenID

def check_user_in_keycloak(email, password):
    return True
    keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/auth/",
                                 client_id="example_client",
                                 realm_name="example_realm",
                                 client_secret_key="secret")
    
    token = keycloak_openid.token(email, password)

    if token:
        return True
