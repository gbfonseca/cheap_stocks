import locale
from locale import atof
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import numpy as np
import re
from datetime import date
import time
URL = 'https://www.investsite.com.br/seleciona_acoes.php'

option = Options()
option.headless = True
driver = webdriver.Firefox(options=option)

black_list = ['SUL AMERICA', 'PORTO SEGURO', 'ETERNIT', 'FER HERINGER',
              'AZEVEDO', 'CEB', 'CSNMINERACAO', 'RANDON PART', 'CYRELA REALT', 'GRAZZIOTIN', 'EUCATEX']


def get_stocks():
    """ Method to get stocks"""
    print("Abrindo site...")
    driver.get(URL)
    select = Select(driver.find_element(
        By.XPATH, "//select[@id='select_data']"))
    select.select_by_index(0)

    print("Selecionando filtros...")

    driver.find_element(By.XPATH, "//*[@id='selectAll']").click()
    
    for i in range(7,34):
        driver.find_element(By.XPATH, f"//*[@id='itm{i}']").click()


    driver.find_element(By.XPATH, "//*[@id='itm13']").click()
    driver.find_element(By.XPATH, "//*[@id='itm26']").click()
    driver.find_element(By.XPATH, "//*[@id='itm29']").click()
    driver.find_element(By.XPATH, "//*[@id='itm30']").click()
    driver.find_element(
        By.XPATH, '//*[@id="tabela_seleciona_acoes"]/tbody/tr[28]/td[2]/input').send_keys(200000)

    driver.find_element(
        By.XPATH, "/html/body/div[1]/div[3]/div/form/input[1]").click()
    
    print("Buscando açoes...")

    time.sleep(5)

    print("Manipulando dados...")

    filter_select = Select(driver.find_element(
        By.XPATH, "/html/body/div[1]/div[3]/div[2]/div[1]/label/select"))

    filter_select.select_by_visible_text('Todos')

    header = driver.find_element(
        By.XPATH, "/html/body/div[1]/div[3]/div[2]/div[3]/div[1]/div/table")

    data = driver.find_element(
        By.XPATH, '//*[@id="tabela_selecao_acoes"]')

    header_content = header.get_attribute('outerHTML')
    data_content = data.get_attribute('outerHTML')

    header_parsed = BeautifulSoup(header_content, 'html.parser')
    data_parsed = BeautifulSoup(data_content, 'html.parser')

    table_header = header_parsed.find(name="table")
    table_data = data_parsed.find(name="table")

    header_data_frame = pd.read_html(str(table_header))[0]
    actions_data_frame = pd.read_html(str(table_data))[0]

    columns = header_data_frame.columns
    stocks = actions_data_frame.set_axis(columns, axis=1)

    locale.setlocale(locale.LC_NUMERIC, '')

    print("Organizando e manipulando dados...")

    stocks['Margem EBIT'] = stocks['Margem EBIT'].str.rstrip('%')
    stocks['Margem EBIT'] = stocks['Margem EBIT'].str.replace(',', '.')
    stocks['Margem EBIT'] = pd.to_numeric(
        stocks['Margem EBIT'], errors='coerce')
    stocks = stocks.applymap(lambda value: atof(
        str(value)) if str(value).isdigit() else value)
    stocks.drop(stocks[stocks['Margem EBIT'] < 0].index, inplace=True)
    stocks['Margem EBIT'].replace('', np.nan, inplace=True)
    stocks.dropna(subset=['Margem EBIT'], inplace=True)
    stocks.drop(stocks[stocks['Ação'].str.contains('33')].index, inplace=True)
    for stock in black_list:
        stocks.drop(stocks[stocks['Empresa'] == stock].index, inplace=True)
    stocks['Preço'] = stocks['Preço'] / 100
    stocks = stocks.sort_values(by='Volume Financ.(R$)')
    stocks = stocks.drop_duplicates('Empresa', keep='last')
    stocks['EV/EBIT'] = pd.to_numeric(
        stocks['EV/EBIT'], errors='coerce')
    stocks.dropna(subset=['EV/EBIT'], inplace=True)
    stocks = stocks.sort_values(by=['EV/EBIT'])
    driver.close()

    stocks = stocks.iloc[:20]
    print("Gerando arquivo excel...")
    today = date.today()
    formated_day = today.strftime("%d-%m-%y")
    return stocks.to_excel('cheap_stocks_{}.xlsx'.format(today))


get_stocks()
