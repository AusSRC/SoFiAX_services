import pytest
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


WAIT = 1


def is_error_page(title):
    if ('Error' in title) or ('Page not found' in title):
        logging.error('Encountered error page')
        return True
    return False

@pytest.fixture()
def browser():
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    yield driver
    driver.quit()

@pytest.fixture()
def login(browser):
    browser.get('https://146.118.69.200/')
    assert browser.title == 'Log in | WALLABY Dev Catalog'

    # login
    username_form = browser.find_element(By.ID, value="id_username")
    password_form = browser.find_element(By.ID, value="id_password")
    username_form.send_keys('admin')
    password_form.send_keys('admin' + Keys.RETURN)
    assert '/admin/' in browser.current_url
    yield browser

def test_pages(login):
    """Test can view all pages

    """
    time.sleep(WAIT)

    # view link pages
    viewlinks = login.find_elements(By.CLASS_NAME, 'viewlink')
    for idx in range(len(viewlinks)):
        viewlinks[idx].click()
        time.sleep(WAIT)
        assert not is_error_page(login.title)
        login.find_element(By.XPATH, '//a[contains(@href, "admin")]').click()
        time.sleep(WAIT)
        viewlinks = login.find_elements(By.CLASS_NAME, 'viewlink')
