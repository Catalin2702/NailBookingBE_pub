from supabase import create_client, Client
from utils.env import SupabaseEnv
from utils.constants import ConstTheme


class SupabaseBucket:

	client: Client = create_client(SupabaseEnv.URL, SupabaseEnv.KEY)
	media_bucket = client.storage.from_(SupabaseEnv.MEDIA_BUCKET)

	@classmethod
	def get_image_url(cls, filename: str) -> str:
		return cls.media_bucket.get_public_url(filename)

	@classmethod
	def logo(cls, theme=ConstTheme.get_label(ConstTheme.LIGHT)) -> str:
		return cls.media_bucket.get_public_url(f'Logo/{theme}.png')
