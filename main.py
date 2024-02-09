import os
import shutil
import sqlite3
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

# Caminho para o ChromeDriver
DRIVER_PATH = "./chromedriver.exe"
LOGIN_PATH = "./login_info.txt"
BASES_PATH = "./bases"
JSON_PATH = "./telefones.json"
PROCESSED_PATH = "./bases/processed"
PHRASES_PATH = "./frases.txt"
phones = []

service = Service(executable_path=DRIVER_PATH)

driver = webdriver.Chrome(service=service)

driver.get("https://www.google.com/")
time.sleep(0.3)


def get_login_info(LOGIN_PATH):
    driver.get("https://kolmeya.com.br/sms")

    with open(LOGIN_PATH, "r") as f:
        email, password = f.readline().strip().split(',')
    return email, password


def make_login(email, password):

    email_field = driver.find_element(By.NAME, "email")
    email_field.send_keys(email)

    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(password)

    remember_me = driver.find_element(By.ID, "customCheckLogin")
    driver.execute_script("arguments[0].click();", remember_me)

    login_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Login')]") # noqa
    login_button.click()
    time.sleep(0.5)

def select_shipping():# noqa
    shippings_button = driver.find_element(
        By.XPATH, "//a[contains(@class, 'btn-success') and contains(., 'NOVO ENVIO')]" # noqa
        )
    shippings_button.click()

    time.sleep(0.5)

    shipping_button = driver.find_element(
        By.XPATH, "//a[contains(., 'SMS Encurtador de Whatsapp (short code)')]" # noqa
        )
    shipping_button.click()
    time.sleep(0.5)


def get_file_path(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))] # noqa

    if files:
        file_path = os.path.abspath(os.path.join(path, files[0]))
        return file_path
    else:
        print("No files found")
        return None


def move_processed_file(file_path, processed_path):
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)
    shutil.move(file_path, os.path.join(processed_path, os.path.basename(file_path))) # noqa


def get_phrase(file):
    with open(file, "r") as f:
        sms_text, whatsapp_text = f.readline().strip().split(',')
    return sms_text, whatsapp_text


def make_jobs(telefone, file, processed_path):
    sms_text, whatsapp_text = get_phrase(PHRASES_PATH)

    input_file = driver.find_element(By.ID, "files[0][file]")
    input_file.send_keys(file)
    time.sleep(0.05)

    cust_center = driver.find_element(By.ID, "files[0][segment_id]")
    select = Select(cust_center)
    select.select_by_value("4135")
    time.sleep(0.05)

    remove_dup = driver.find_element(By.ID, "remove_duplicates")
    select = Select(remove_dup)
    select.select_by_value("telefones")
    time.sleep(0.05)

    whatsapp = driver.find_element(By.ID, "phone_whatsapp")
    whatsapp.clear()
    for numero in telefone:
        whatsapp.send_keys(numero)
        time.sleep(0.005)
    time.sleep(0.05)

    layout = driver.find_element(By.ID, "layout_id")
    select = Select(layout)
    select.select_by_value("2978")
    time.sleep(0.05)

    sms_text_element = driver.find_element(By.ID, "message")
    sms_text_element.send_keys(sms_text)
    time.sleep(0.05)

    whatsapp_text_element = driver.find_element(By.ID, "message_whatsapp")
    whatsapp_text_element.send_keys(whatsapp_text)
    time.sleep(0.05)

    create = driver.find_element(
        By.XPATH, "//button[contains(text(), 'criar')]" # noqa
        )
    create.click()
    time.sleep(0.05)

    move_processed_file(file, processed_path)


def get_phone_number(nome):
    conn = sqlite3.connect('telefones.db')
    cursor = conn.cursor()
    cursor.execute('SELECT telefone FROM contatos WHERE nome = ?', (nome,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


email, password = get_login_info(LOGIN_PATH)
print(email, password)
make_login(email, password)


for file in os.listdir(BASES_PATH):
    file_path = get_file_path(BASES_PATH)
    file_name, file_extension = os.path.splitext(file)
    if file_extension == '.csv':
        telefone = get_phone_number(file_name)
        if telefone:
            select_shipping()
            make_jobs(telefone, file_path, PROCESSED_PATH)
        else:
            print("No phone number found for", file_name)
    else:
        print("Skipping non-csv file:", file)

    time.sleep(0.5)

time.sleep(0.5)
driver.quit()
