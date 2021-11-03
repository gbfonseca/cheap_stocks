from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


url = 'https://www.investsite.com.br/seleciona_acoes.php'

option = Options()
option.headless = False
driver = webdriver.Firefox(options=option)


def get_actions():
    driver.get(url)
    select = Select(driver.find_element(
        By.XPATH, "//select[@id='num_result']"))
    select.select_by_visible_text('Todos')

    driver.find_element(
        By.XPATH, "//*[@id='form_seleciona_acoes']/input[1]").click()

    filter_select = Select(driver.find_element(
        By.XPATH, "//*[@id='tabela_selecao_acoes_length']/select"))

    filter_select.select_by_visible_text('Todos')

    element = driver.find_element(
        By.XPATH, "//*[@id='tabela_selecao_acoes_wrapper']/div[2]/div[1]/div/table")

    html_content = element.get_attribute('outerHTML')

    driver.close()


get_actions()
