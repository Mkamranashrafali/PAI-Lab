import os

APP_KEY = os.environ.get('SECRET_KEY') or 'xyz-secret-789'
FILE_FOLDER = 'uploads'
SIZE_LIMIT = 500 * 1024 * 1024
TYPES_OK = ['png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov']

MODEL_WT = 'models/yolov3.weights'
MODEL_CFG = 'models/yolov3.cfg'
MODEL_NM = 'models/coco.names'

CONF_MIN = 0.5
NMS_VAL = 0.4

LAT_DEF = 40.7128
LON_DEF = -74.0060

ZOOM_LVL = 12
ZONE_RAD = 500

class Settings:
    SECRET_KEY = APP_KEY
    UPLOAD_FOLDER = FILE_FOLDER
    MAX_CONTENT_LENGTH = SIZE_LIMIT
    DEBUG = True
    
class DevSettings(Settings):
    DEBUG = True
    TESTING = False

class ProdSettings(Settings):
    DEBUG = False
    TESTING = False

class TestSettings(Settings):
    DEBUG = True
    TESTING = True
    UPLOAD_FOLDER = 'test_uploads'

settings_map = {
    'dev': DevSettings,
    'prod': ProdSettings,
    'test': TestSettings,
    'default': DevSettings
}
