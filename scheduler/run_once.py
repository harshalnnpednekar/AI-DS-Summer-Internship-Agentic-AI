import os
from dotenv import load_dotenv

# Load env before importing app modules
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)
load_dotenv()

from main import SchedulerApplication
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_once():
    logger.info("Initializing SchedulerApplication for a single run...")
    app = SchedulerApplication()
    
    logger.info("Triggering check_events manually...")
    app.scheduler_manager.check_events()
    logger.info("Run complete.")

if __name__ == "__main__":
    run_once()
