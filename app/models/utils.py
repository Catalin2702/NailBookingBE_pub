def _repr(cls: object) -> str:
	"""
		Return a string representation of the object.
	"""
	_exclude = ('_sa_class_manager', '_sa_registry', 'registry', 'metadata', 'engine')
	cond = lambda attr: attr not in _exclude and not attr.startswith("__") and not callable(getattr(cls, attr))
	return f'{type(cls).__name__}\n{"".join([f"\t{attr}: {str(getattr(cls, attr))}\n" for attr in dir(cls) if cond(attr)])}'
