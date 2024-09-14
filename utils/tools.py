from colorama import Fore
import datetime as d
from typing import Union, Any

from utils.messages import Errors


def print_error(error: str):
	print(f'\n{"\n".join([f'{Fore.RED}{err}{Fore.RESET}' for err in error.splitlines()])}\n')


def get_diff_dict(dict1: dict, dict2: dict):
	diff = {}
	for key in set(dict1.keys()).union(dict2.keys()):
		if dict1.get(key) != dict2.get(key):
			diff.update({
				key: [dict1.get(key), dict2.get(key)]
			})
		else:
			diff.update({
				key: [dict1.get(key, '')]
			})
	return diff


def response(status: Union[str, bool], message: str = '', content: any = None) -> dict[str, Union[bool, str, dict]]:
	if not content:
		content = {}
	return {
		'status': status,
		'message': message,
		'content': content
	}


class Parameter:
	__default: Any
	__format: str
	__name: str
	__required: bool
	__type: type
	__value: Any

	__slots__: tuple[str] = ('__default', '__format', '__name', '__required', '__type', '__value')

	def __init__(self, name_: str, source_: dict[str, Any], type_: type, required_: bool = False, default_: Any = None, format_: str = None, check_: dict[str, Union[callable, str]] = None):
		self.__name = name_
		self.__type = type_
		self.__required = required_
		self.__default = default_
		self.__format = format_
		self.__value = self.__get_value(source_)
		if check_:
			self.__check(check_['func'], check_['error'])

	def __get_value(self, source) -> Any:
		if self.__required and self.__name not in source:
			raise ValueError(Errors.NO_INPUT.format(key=self.__name))
		return self.__convert(source)

	def __convert(self, source) -> Any:
		__value = source.get(self.__name, self.__default)
		if __value is None:
			return None
		match self.__type:
			case d.time:
				return d.datetime.strptime(__value, self.__format).time()
			case d.datetime:
				return d.datetime.strptime(__value, self.__format)
			case d.date:
				return d.datetime.strptime(__value, self.__format).date()
			case _:
				return self.__type(__value)

	def __check(self, func, error) -> None:
		if not func(self.__value):
			raise ValueError(error.format(key=self.__name, value=self.__value))

	@property
	def name(self) -> str:
		return self.__name

	@property
	def type(self) -> type:
		return self.__type

	@property
	def required(self) -> bool:
		return self.__required

	@property
	def default(self) -> Any:
		return self.__default

	@property
	def format(self) -> str:
		return self.__format

	@property
	def value(self) -> Any:
		return self.__value

	def __repr__(self) -> Any:
		return f'{self.__name}: {self.__value}'

	def __str__(self) -> str:
		return str(self.__value)

	def __bool__(self) -> bool:
		return self.__required or bool(self.__value)

	def __eq__(self, other) -> bool:
		return self.__value == other

	def __hash__(self) -> int:
		return hash(self.__value)
