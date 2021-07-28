
from django.conf import settings
from project.celery import app
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

@app.task
def generate_report_task():
    logger.debug('generate_report_task `in progress` started at: %s' % datetime.now())
    print("BLANKAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",datetime.now())
    return {"a":1}
 