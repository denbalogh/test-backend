import sys
import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

import config
from database import db
from main import app
from model.Roles import SystemRole
from model.User import User
from modules.user import controller as user_controller

def _test_connection():
    try:
        db.session.query("is_alive").from_statement(text("SELECT 1 as is_alive")).all()
        return True
    except OperationalError:
        return False

def mock_data():    
    print("Register test users.")
    user_controller.create_user("coach@fableplus.com", SystemRole.USER, "test123", "Test Coach")
    user_controller.create_user("coach2@fableplus.com", SystemRole.USER, "test123", "Test Coach2")
    user_controller.create_user("user@fableplus.com", SystemRole.PARTICIPANT, "test456", "Test Member")

    if config.ENVIRONMENT == "dev":
        user_controller.create_user("admin@fableplus.com", SystemRole.GLOBAL_ADMIN, "adminTest", "Admin")


if __name__ == "__main__":
    with app.app_context():
        print("Waiting for database connection.", end="", flush=True)
        while not _test_connection():
            time.sleep(1)
            print(".", end="", flush=True)

        print("")
        print("Database connection established.")

        if len(sys.argv) > 1 and sys.argv[1].lower() == "force":
            print("Forced recreation requested!")
            print("Dropping current database.")
            db.drop_all()
            print("Creating database schema")
            db.create_all()

            print("Create test data")
            mock_data()
        else:
            try:
                user_count = User.query.count()
            except (OperationalError, ProgrammingError):
                print("No database found, creating schema")
                db.create_all()
                db.session.commit()

                print("Create test data")
                mock_data()
            else:
                if user_count == 0:
                    print("Database found, but empty. Generating data.")
                    mock_data()

