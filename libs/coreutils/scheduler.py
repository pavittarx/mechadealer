from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler  # type:ignore
from apscheduler.jobstores.memory import MemoryJobStore  # type:ignore

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor  # type:ignore


job_stores = {
    "default": MemoryJobStore(),
    # 'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

executors = {"default": ThreadPoolExecutor(20), "processpool": ProcessPoolExecutor(5)}

job_defaults = {"coalesce": False, "max_instances": 3}

scheduler = BackgroundScheduler(
    jobstores=job_stores, executors=executors, job_defaults=job_defaults, timezone=utc
)
scheduler.configure(
    jobstores=job_stores, executors=executors, job_defaults=job_defaults, timezone=utc
)
