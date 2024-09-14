from importlib import import_module

HOME: str = 'Home'
BOOKING: str = 'Booking'
GALLERY: str = 'Gallery'
FEEDBACK: str = 'Feedback'
MODULE: str = 'views.'

view_mapping: dict = {
	HOME: import_module(MODULE + 'home').HomeView,
	BOOKING: import_module(MODULE + 'booking').BookingView,
	GALLERY: import_module(MODULE + 'gallery').GalleryView,
	FEEDBACK: import_module(MODULE + 'feedback').FeedbackView,
}
