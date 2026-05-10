# app_context.py
import os

# =====================================================
# HARD-WIRED BASE DIRECTORY
# =====================================================

BASE_DATA_DIR = "/var/Data"

CURRENT_USERNAME = None
CURRENT_DATA_DIR = None


def get_base_data_dir() -> str:
    return BASE_DATA_DIR


def set_user_context(username: str):
    global CURRENT_USERNAME, CURRENT_DATA_DIR

    user_dir = os.path.join(BASE_DATA_DIR, username)
    os.makedirs(user_dir, exist_ok=True)

    CURRENT_USERNAME = username
    CURRENT_DATA_DIR = user_dir


def clear_user_context():
    global CURRENT_USERNAME, CURRENT_DATA_DIR
    CURRENT_USERNAME = None
    CURRENT_DATA_DIR = None
