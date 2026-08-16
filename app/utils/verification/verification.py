from uuid import uuid4

def generate_verification_token() -> str:
    return str(uuid4())
