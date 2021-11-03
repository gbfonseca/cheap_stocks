import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


URL = 'https://www.investsite.com.br/seleciona_acoes.php'

option = Options()
option.headless = True
driver = webdriver.Firefox(options=option)


def get_stocks():
    """ Method to get stocks"""

    driver.get(URL)
    select = Select(driver.find_element(
        By.XPATH, "//select[@id='num_result']"))
    select.select_by_visible_text('Todos')

    driver.find_element(
        By.XPATH, "//*[@id='form_seleciona_acoes']/input[1]").click()

    filter_select = Select(driver.find_element(
        By.XPATH, "//*[@id='tabela_selecao_acoes_length']/select"))

    filter_select.select_by_visible_text('Todos')

    header = driver.find_element(
        By.XPATH, "//*[@id='tabela_selecao_acoes_wrapper']/div[2]/div[1]/div/table")

    data = driver.find_element(
        By.XPATH, "//*[@id='tabela_selecao_acoes_wrapper']/div[2]/div[2]")

    header_content = header.get_attribute('outerHTML')
    data_content = data.get_attribute('outerHTML')

    header_parsed = BeautifulSoup(header_content, 'html.parser')
    data_parsed = BeautifulSoup(data_content, 'html.parser')

    table_header = header_parsed.find(name="table")
    table_data = data_parsed.find(name="table")

    header_data_frame = pd.read_html(str(table_header), index_col=0)[0]
    actions_data_frame = pd.read_html(str(table_data), index_col=0)[0]

    columns = header_data_frame.columns

    stocks = actions_data_frame.set_axis(columns, axis=1)

    driver.close()
    return stocks.to_csv('cheap_stocks.csv')


get_stocks()
