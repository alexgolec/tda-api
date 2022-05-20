'''
This example demonstrates how to create a client using the 
``client_from_access_functions`` method. This is an advanced piece of 
functionality designed for users who want to customize the reading and writing 
of their tokens. Most notably, it is useful for users who want to safely store 
their tokens in a cloud environment where they do not have access to a 
persistent filesystems, such as on AWS Lambda.
'''


import tda

API_KEY = 'XXXXXX'


# For the purposes of this demonstration, we will be storing the token object in 
# memory. For your use case, replace the contents of these functions with reads 
# and writes to your backing store.


# Note we assume that the token was already created and exists in the backing 
# store.
IN_MEMORY_TOKEN = {
        'dummy': 'token',
        'please': 'ignore',
}

def read_token():
    return IN_MEMORY_TOKEN

# Note the refresh_token kwarg is mandatory. It is passed by authlib on token 
# refreshes, and contains the refresh token that was used to generate the new 
# token (i.e. the first parameter). The current best practice is to ignore it, 
# but it's required.
def write_token(token, refresh_token=None):
    global IN_MEMORY_TOKEN
    IN_MEMORY_TOKEN = token


client = tda.auth.client_from_access_functions(
        API_KEY,
        token_read_func=read_token,
        token_write_func=write_token)
