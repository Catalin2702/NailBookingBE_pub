from calendar import monthrange, weekday
from datetime import date
from functools import cache
from dateutil.relativedelta import relativedelta
from typing import Union

from utils.constants import ConstDevice
from utils.env import ParamsEnv
from utils.exceptions import exception
from utils.tools import response, Parameter
from utils.messages import generic_error
from views.view import View


class BookingView(View):
	"""
		View per la gestione delle prenotazioni
	"""

	def __init__(self, **kwargs):
		kwargs['mapping'] = {
			'viewData': self.get_view_data,
			'deviceData': self.get_view_data,
			'getSelectedData': self.get_selected_data,
		}
		super().__init__(**kwargs)

	@staticmethod
	@exception(generic_error)
	async def get_view_data(**kwargs) -> dict:
		try:
			_month: int = Parameter('month', kwargs['period'], int, True).value
			_year: int = Parameter('year', kwargs['period'], int, True).value
			_device: int = Parameter('device', kwargs, int, True).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		return response(True, '', make_calendar(_month, _year, _device))

	@classmethod
	@exception(generic_error)
	async def get_selected_data(cls, **kwargs) -> dict:
		"""
			Get selected data
			:return: list[dict]
		"""
		try:
			_now: date = Parameter('now', kwargs, date, True, format_='%Y-%m-%d').value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		_months = list(ParamsEnv.BOOKING.MONTHS_SELECTABLE.values())
		return response(True, '', make_selected(int(_months[0]), int(_months[1]), _now))


@cache
def create_day(date_: date) -> dict:
	return {'d': date_.day, 'm': date_.month, 'y': date_.year, 'dw': date_.weekday()}


@cache
def make_calendar(month: int, year: int, device: int) -> list[dict[str, int]]:
	"""
		Crea un calendario per il mese e l'anno correnti
		:param month: Il mese corrente
		:param year: L'anno corrente
		:param device: Il dispositivo
		:return: Un elenco di dizionari che rappresentano i giorni del mese corrente
	"""
	_GIORNI_SETTIMANA = 6  # parte da 0
	_PRIMO_GIORNO_MESE = date(year, month, 1)

	giorni_attuali: int = monthrange(year, month)[1]
	if device == ConstDevice.MOBILE:
		giorni_precedenti: int = 0
		giorni_successivi: int = 0
	else:
		giorni_precedenti: int = weekday(year, month, 1)
		giorni_successivi: int = _GIORNI_SETTIMANA - weekday(year, month, giorni_attuali)

	return list(map(create_day, [_PRIMO_GIORNO_MESE + relativedelta(days=day) for day in range(-giorni_precedenti, giorni_attuali + giorni_successivi)]))


@cache
def make_selected(before: int, after: int, now: date) -> list[dict[str, Union[int, bool]]]:
	"""
		Crea un elenco di mesi-anno selezionabili
	"""
	def options(data: tuple) -> dict:
		return {'month': data[0].month, 'year': data[0].year, 'today': data[1]}
	return list(map(options, [(now + relativedelta(months=i), i == 0) for i in range(before, after)]))
