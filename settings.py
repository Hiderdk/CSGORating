import os

#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
bucket_name = "firstpythonbucket3f7e1192-c034-426d-a997-f317a0031083"
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
COMM_SOCKET='/tmp/socket'

local_file_path = r"C:\Users\Mathias\PycharmProjects\Ratings\Files"

EXEC_PERIOD=3600
MYSQL_HOST = os.environ.get('MYSQL_HOST', '138.68.101.79')
MYSQL_PORT = os.environ.get('MYSQL_PORT', 3306)
MYSQL_USER = os.environ.get('MYSQL_USER', 'grid_csgo_prediction_data')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'ee0302aa03eef67ad400be763a64b5eb')
MYSQL_NAME = os.environ.get('MYSQL_NAME', 'grid_csgo_prediction_data')

SECRET_KEY='6d05126166cd852a33d6d500f5daa82ba7cca4b6ee75769b13e51046b46ed750e5b9daf5acc7ce6a5db8d2d8cb668cd2fd993a8885c2a2c10dfd28588dd38bef'

#try:
    #from local_settings import *
#except ImportError as e:
    #pass

