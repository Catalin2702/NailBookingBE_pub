from contextlib import ExitStack

from utils.constants import EnumMailTypes, EnumMailComponents


mail_types = {
	EnumMailTypes.BOOK_BOOKING: 'mail/content/booking.html',
	EnumMailTypes.UPDATE: 'mail/content/update.html',
	EnumMailTypes.CANCEL: 'mail/content/cancel.html',
	EnumMailTypes.REQUEST_BOOKING: 'mail/content/request_booking.html',
	EnumMailTypes.CONFIRM_BOOKING: 'mail/content/confirm_booking.html',
	EnumMailTypes.RULES: 'mail/content/rules.html',
	EnumMailTypes.GENERATE_NEW_BOOKING: 'mail/content/generate_new_booking.html',
	EnumMailTypes.CONFIRM_EMAIL: 'mail/content/confirm_email.html',
	EnumMailTypes.JOIN_ACCOUNT: 'mail/content/join_account.html',
	EnumMailTypes.REQUEST_NEW_BOOKING: 'mail/content/request_new_booking.html',
	EnumMailTypes.FORGOT_PASSWORD: 'mail/content/forgot_password.html',
}

mail_components = {
	EnumMailComponents.TEMPLATE: 'mail/content/template.html',
	EnumMailComponents.BOOKING_DETAILS: 'mail/content/booking_details.html',
	EnumMailComponents.USER_DETAILS: 'mail/content/user_details.html',
	EnumMailComponents.BUTTON: 'mail/content/button.html',
	EnumMailComponents.FOOTER: 'mail/content/footer.html',
	EnumMailComponents.INFORMATION_DETAILS: 'mail/content/information_details.html',
	EnumMailComponents.REGULATION_DETAILS: 'mail/content/regulation_details.html',
	EnumMailComponents.NEW_BOOKING_DETAILS: 'mail/content/new_booking_details.html',
}

with ExitStack() as stack:
	mails = {
		key: stack.enter_context(open(value, 'r')).read() for key, value in
		{
			**mail_types,
			**mail_components,
		}.items()
	}
