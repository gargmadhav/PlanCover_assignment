from backend.app.services.policy_service import policy_service, PolicyService

def get_policy_service() -> PolicyService:
    return policy_service
