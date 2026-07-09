import os
import sys
import signal
import logging
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

from scheduler import SchedulerManager
from agent import NotificationWorkflow

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SchedulerApplication:
    def __init__(self):
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.scheduler_manager = SchedulerManager(self.api_base_url)
        self.notification_workflow = NotificationWorkflow()
        self.setup_callbacks()
        self.setup_signal_handlers()

    def setup_callbacks(self):
        def send_notification_callback(event, students):
            logger.info(f"Processing event: {event.get('title')}")
            result = self.notification_workflow.process_event(event, students)
            
            if result.get("status") == "logged":
                logger.info(f"Notification prepared for {len(students)} students")
            else:
                logger.error(f"Failed to process event: {result.get('error')}")
        
        self.scheduler_manager.register_notification_callback(send_notification_callback)

    def setup_signal_handlers(self):
        def signal_handler(signum, frame):
            logger.info("Shutdown signal received")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def run(self):
        logger.info(f"Starting Scheduler with API URL: {self.api_base_url}")
        self.scheduler_manager.start()
        
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        logger.info("Shutting down scheduler")
        self.scheduler_manager.stop()

    def get_status(self):
        return {
            "api_url": self.api_base_url,
            "jobs": self.scheduler_manager.get_job_status()
        }


if __name__ == "__main__":
    app = SchedulerApplication()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            print(app.get_status())
        elif sys.argv[1] == "run":
            app.run()
    else:
        app.run()
