from sqlalchemy import and_
from sqlalchemy.orm import Query
from typing import Union

from app.services.context import Context
from utils.constants import ConstDevice, ConstRoles, EnumBookingStates
from utils.exceptions import exception
from utils.env import SettingsEnv
from utils.tools import response, Parameter
from utils.messages import generic_error, Messages, Errors
from views.view import View

MAX_FEEDBACK_LENGTH = 100
class FeedbackView(View):
	"""
		View per la gestione dei Feedback
	"""

	def __init__(self, **kwargs):
		kwargs['mapping'] = {
			'viewData': self.get_view_data,
			'getFeedbackData': self.get_feedback_data,
			'getNextFeedbacks': self.get_next_feedbacks,
			'createNewFeedback': self.create_new_feedback,
		}
		super().__init__(**kwargs)

	@classmethod
	@exception(generic_error)
	def get_feedbacks(cls,  _id: int = None, limit: int = None, offset: int=None) -> dict[str, Union[bool, str, list[View.Feedback]]]:
		if _id:
			feedback: cls.Feedback = cls.Feedback.get(cls.Feedback.id == _id)
			return response(True, '', [feedback])

		with cls.get_session(commit=False) as session:
			query: Query = session.query(cls.Feedback).filter(cls.Feedback.state == True).order_by(cls.Feedback.upd_datetime.desc())
			if limit:
				query: Query = query.limit(limit)
			if offset:
				query: Query = query.offset(offset)

			list_feedback: list[cls.Feedback] = query.all()

		return response(True, '', list_feedback)

	@classmethod
	@exception(generic_error)
	async def get_view_data(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		try:
			_device: int = Parameter('device', kwargs, int, False, default_=ConstDevice.DESKTOP).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		if _device <= len(SettingsEnv.MAX_FEEDBACK_DATA):
			max_feedback = int(SettingsEnv.MAX_FEEDBACK_DATA[_device])
		else:
			max_feedback = 10

		feedbacks = cls.get_feedbacks(limit=max_feedback)
		if not feedbacks['status']:
			return feedbacks

		return response(True, '', {'feedback': [feedback.to_dict(MAX_FEEDBACK_LENGTH) for feedback in feedbacks['content']]})

	@classmethod
	@exception(generic_error)
	async def get_feedback_data(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		try:
			_id: int = Parameter('id', kwargs, int, True).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		feedback = cls.get_feedbacks(_id=_id)
		if not feedback['status']:
			return feedback

		return response(True, '', {'feedback': feedback['content'][0].to_dict()})

	@classmethod
	@exception(generic_error)
	async def get_next_feedbacks(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		try:
			_device: int = Parameter('device', kwargs, int, False, default_=ConstDevice.DESKTOP).value
			_len: int = Parameter('len', kwargs, int, False, default_=0).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		if _device <= len(SettingsEnv.MAX_FEEDBACK_DATA):
			max_feedback = int(SettingsEnv.MAX_FEEDBACK_DATA[_device])
		else:
			max_feedback = 10

		feedbacks = cls.get_feedbacks(limit=max_feedback, offset=_len)

		if not feedbacks['status']:
			return feedbacks

		return response(True, '', {'feedback': [feedback.to_dict(MAX_FEEDBACK_LENGTH) for feedback in feedbacks['content']]})

	@classmethod
	@exception(generic_error)
	async def create_new_feedback(cls, **kwargs):
		try:
			_identifier = Parameter('identifier', kwargs, str, True).value
			_title = Parameter('title', kwargs, str, False).value
			_description = Parameter('description', kwargs, str, False).value
			_rating = Parameter('rating', kwargs, int, True).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		if not _identifier in Context:
			return generic_error
		user: cls.User = Context[_identifier]
		with cls.get_session() as session:
			id_booking: cls.Booking.id = session.query(cls.Booking.id).filter(
				and_(
					cls.Booking.id_user == user.id,
					cls.Booking.status == EnumBookingStates.COMPLETED
				)
			).first()
			if not id_booking and not user.role == ConstRoles.ADMIN:
				return response(False, Errors.NEED_BOOKING_TO_FEEDBACK)

			if not _rating:
				return response(False, Errors.INVALID_RATING)
			else:
				_rating = int(_rating)
				if _rating < 1 or _rating > 5:
					return response(False, Errors.INVALID_RATING)

			feedback = cls.Feedback(
				title=_title,
				description=_description,
				rating=_rating,
			)
			session.add(feedback)

		return response(True, Messages.ADDED_FEEDBACK)
