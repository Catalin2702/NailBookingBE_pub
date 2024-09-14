from typing import Union

from app.entities.account import AccountEntity
from app.services.service import Service


class AccountService(Service):
	"""
		Account Service
		ATTRIBUTES:
			entity: AccountEntity
			actionName: str
			actionParams: dict
		METHODS:
			fulfill_request: fulfill request
			make_response: make response
	"""

	entity: AccountEntity = AccountEntity()

	mapped_data = {'actionName'}
	o_mapped_data = {'actionParams'}

	@classmethod
	async def login(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		return await cls.entity.execute('login', **kwargs)

	@classmethod
	async def register(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		return await cls.entity.execute('register', **kwargs)

	@classmethod
	async def logout(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		return await cls.entity.execute('logout', **kwargs)

	@classmethod
	async def delete(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		return await cls.entity.execute('delete', **kwargs)

	@classmethod
	async def get_user_data(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		return await cls.entity.execute('userData', **kwargs)

	@classmethod
	async def update(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		return await cls.entity.execute('update', **kwargs)

	@classmethod
	def get_user(cls, id_user) -> AccountEntity.User:
		return cls.entity.get_user(id_user)
