import pytest
import time
import logging
from dotenv import load_dotenv, dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


WAIT = 1


def assert_not_error_page(title):
    if ('Error' in title) or ('Page not found' in title):
        logging.error('Encountered error page')
        assert False

def assert_element_exists_xpath(browser, xpath):
    try:
        browser.find_element(By.XPATH, xpath)
    except Exception as e:
        logging.error(f'Element {xpath} does not exist: {e}')
        assert False

def home(browser):
    pass

@pytest.fixture()
def browser():
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    yield driver
    driver.quit()

@pytest.fixture()
def login(browser):
    config = dotenv_values('.env')
    url = config['URL']
    if not url:
        raise Exception('.env file does not contain deployment url [URL]')
    browser.get(url)
    title = config['TITLE']
    if not title:
        raise Exception('.env file does not contain portal title [TITLE]')
    assert browser.title == f'Log in | {title}'

    # login
    username = config['USERNAME']
    password = config['PASSWORD']
    if (not username) or (not password):
        raise Exception('.env file does not contain portal login credentials [USERNAME, PASSWORD]')
    username_form = browser.find_element(By.ID, value="id_username")
    password_form = browser.find_element(By.ID, value="id_password")
    username_form.send_keys(username)
    password_form.send_keys(password + Keys.RETURN)
    assert '/admin/' in browser.current_url
    time.sleep(WAIT)
    yield browser

def test_pages(login):
    """Test can access view only pages"""
    viewlinks = login.find_elements(By.CLASS_NAME, 'viewlink')
    for idx in range(len(viewlinks)):
        viewlinks[idx].click()
        time.sleep(WAIT)
        assert_not_error_page(login.title)
        login.find_element(By.XPATH, '//a[contains(@href, "admin")]').click()
        time.sleep(WAIT)
        viewlinks = login.find_elements(By.CLASS_NAME, 'viewlink')

def test_comment(login):
    """CRUD for comments table"""
    # Create + read
    comment = 'This is a test comment'
    login.find_element(By.XPATH, '//a[contains(@href, "admin/survey/comment/add")]').click()
    comment_form = login.find_element(By.ID, value='id_comment')
    comment_form.send_keys(comment)
    detection_select = Select(login.find_element(By.XPATH, '//select[contains(@id, "id_detection")]'))
    detection_select.select_by_index(1)
    login.find_element(By.XPATH, '//a[contains(@href, "/admin/survey/comment/")]').click()
    # login.find_element(By.XPATH, '//input[contains(@value, "Save")]').click()
    time.sleep(WAIT)
    assert_element_exists_xpath(login, f'//a[contains(., "{comment}")]')

    # Update
    update_comment = 'Updated the comment'
    comment_obj = login.find_element(By.XPATH, f'//a[contains(., "{comment}")]').click()
    comment_form = login.find_element(By.ID, value='id_comment')
    comment_form.clear()
    comment_form.send_keys(update_comment)
    login.find_element(By.XPATH, '//input[contains(@value, "Save")]').click()
    time.sleep(WAIT)
    assert_element_exists_xpath(login, f'//a[contains(., "{update_comment}")]')

    # Delete
    login.find_element(By.XPATH, '//input[contains(@class, "action-select")]').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "delete_selected")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    login.find_element(By.XPATH, '//input[contains(@type, "submit")]').click()
    time.sleep(WAIT)

def test_tag(login):
    """CRUD for tag table"""
    tag = {
        'name': 'Test',
        'description': 'This is a test tag created by functional tests.',
        'type': 'Test'
    }

    # Create
    login.find_element(By.XPATH, '//a[contains(@href, "admin/survey/tag/add")]').click()
    tag_name_form = login.find_element(By.ID, value='id_name')
    tag_description_form = login.find_element(By.ID, value='id_description')
    tag_type_form = login.find_element(By.ID, value='id_type')
    tag_name_form.send_keys(tag['name])
    tag_description_form.send_keys(tag['description'])
    tag_type_form.send_keys(tag['type])
    login.find_element(By.XPATH, '//input[contains(@value, "Save")]').click()

    # Read
    login.find_element(By.XPATH, '//a[contains(@href, "admin/survey/tag")]').click()
    time.sleep(WAIT)
    assert_element_exists_xpath(login, '//td[contains(@class, "field-description")]')
    element = login.find_element(By.XPATH, '//td[contains(@class, "field-description")]')
    assert element.text == tag['description']

    # Delete
    login.find_element(By.XPATH, '//input[contains(@class, "action-select")]').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "delete_selected")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    login.find_element(By.XPATH, '//input[contains(@type, "submit")]').click()
