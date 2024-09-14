from django.http import JsonResponse

from app.services.action import ActionService


def confirm_email(_, action_code: str) -> JsonResponse:
	return JsonResponse(ActionService.confirm_email(action_code), safe=False)

def confirm_join_account(_, action_code: str) -> JsonResponse:
	return JsonResponse(ActionService.confirm_join_account(action_code), safe=False)
