from apscheduler.schedulers.background import BackgroundScheduler
from importlib import import_module
from yaml import safe_load

from app.cronjobs.utils import cron_to_dict
from utils.env import SettingsEnv


class Cron:
	scheduler = BackgroundScheduler(timezone=SettingsEnv.TIMEZONE)

	@classmethod
	def start_process(cls):
		with open(f'crontabs/{str(SettingsEnv.RUNNING_MODE).lower()}.yml', 'r') as crontab:
			crontab = safe_load(crontab.read())
			for cronjob in crontab:
				program = vars(import_module(cronjob['job']['path'])).get(cronjob['job']['program'])
				cls.scheduler.add_job(program(), 'cron', id=cronjob['name'], name=cronjob['name'], **cron_to_dict(cronjob['schedule']))
		cls.scheduler.start()
