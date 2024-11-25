import os
import sys

root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_path)

CONTENT_XPATH="/html/body/section/section[2]/div/div[2]/div[2]/div/div[3]/div/div"
ID_XPATH = '/html/body/section/section[2]/div/div[2]/div[2]/div/div[2]/div[1]/div[2]/div' 
SUBJECT_XPATH = '//*[@id="page-title"]' 
DATE_XPATH='/html/body/section/section[2]/div/div[2]/div[2]/div/div[2]/div[2]/div[2]/div/span' 
DOWNLOAD_XPATH='//*[@id="download-pdf"]/a'
BASE_URL = "https://www.gib.gov.tr" 


