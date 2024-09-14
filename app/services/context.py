from uuid import uuid4


class ContextDict:

	context = {}

	def __init__(self):
		pass

	def __enter__(self):
		return self.context

	def __getitem__(self, key):
		return self.context.get(key, None)

	def __setitem__(self, key, value):
		self.context[key] = value

	def __exit__(self, exc_type, exc_value, traceback):
		pass

	def __repr__(self):
		return str(self.context)

	def __contains__(self, item):
		return item in self.context

	def __delitem__(self, key):
		if key in self.context:
			del self.context[key]

	def add_user(self, user) -> str:
		identifier = str(uuid4())
		while identifier in self.context:
			identifier = str(uuid4())
		self.context[identifier] = user
		return identifier

Context = ContextDict()
