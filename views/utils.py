from views.mapping import view_mapping


def create_view(view_name: str, **kwargs):
	return view_mapping[view_name](**kwargs)
