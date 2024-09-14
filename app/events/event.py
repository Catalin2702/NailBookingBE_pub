from app.events.booking import BookingEvent

class Event:
	booking = BookingEvent
	@classmethod
	def start_process(cls):
		cls.booking.register_events()
