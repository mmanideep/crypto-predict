from apscheduler.schedulers.background import BackgroundScheduler

from crypto_predict.app import app, db
from crypto_predict.models.custom_exception import ValidationError


LOGGER = app.logger


class BaseTask(object):

    MINUTES = 0

    def task(self):
        raise NotImplementedError

    def commit_task(self):
        self.task()
        db.session.commit()

    def schedule(self):
        scheduler = BackgroundScheduler()
        if not getattr(self.__class__, "PAUSE", False):
            if self.__class__.MINUTES < 30:
                raise ValidationError("Minutes can not be less than 30")
            job = scheduler.add_job(self.commit_task, 'interval', minutes=self.__class__.MINUTES)
            scheduler.start()
            LOGGER.info("Scheduled task {} with a period of {} minutes".format(
                self.__class__.__name__, self.__class__.MINUTES))
