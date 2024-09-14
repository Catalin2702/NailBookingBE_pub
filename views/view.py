from app.models.booking import BookingModel
import app.models.view as view
from app.models.param import ParamModel
from app.models.user import UserModel
from utils.template import Mapper


class View(Mapper):
	Booking = BookingModel
	Feedback = view.ViewFeedbackModel
	Gallery = view.ViewGalleryModel
	Home = view.ViewHomeModel
	Param = ParamModel
	User = UserModel

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def get_view_data(self):
		raise NotImplementedError('You must implement this method')
