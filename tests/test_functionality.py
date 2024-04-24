import pytest
import time
import re
import logging
from dotenv import load_dotenv, dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


CROSS_MATCH_WAIT = 5
WAIT = 2


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

def test_comment(login):
    """CRUD for comments table"""
    # Create + read
    comment = 'This is a test comment'
    login.find_element(By.XPATH, '//a[contains(@href, "admin/survey/comment/add")]').click()
    comment_form = login.find_element(By.ID, value='id_comment')
    comment_form.send_keys(comment)
    detection_select = Select(login.find_element(By.XPATH, '//select[contains(@id, "id_detection")]'))
    detection_select.select_by_index(1)
    login.find_element(By.XPATH, '//input[contains(@value, "Save")]').click()
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
    tag_name_form.send_keys(tag['name'])
    tag_description_form.send_keys(tag['description'])
    tag_type_form.send_keys(tag['type'])
    login.find_element(By.XPATH, '//input[contains(@value, "Save")]').click()

    # Read
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(@href, "admin/survey/tag")]').click()
    time.sleep(WAIT)
    element = login.find_element(By.XPATH, '//td[contains(@class, "field-description")]')
    assert element.text == tag['description']

    # Delete
    login.find_element(By.XPATH, '//input[contains(@class, "action-select")]').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "delete_selected")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    login.find_element(By.XPATH, '//input[contains(@type, "submit")]').click()

def test_inspection_navigation(login):
    """Test simple navigation through detections in a manual inspection view"""
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_elements(By.XPATH, '//a[contains(., "Manual inspection")]')[0].click()
    login.find_element(By.XPATH, '//input[contains(@id, "next")]').click()
    login.find_element(By.XPATH, '//input[contains(@id, "previous")]').click()
    login.find_element(By.XPATH, '//input[contains(@id, "last")]').click()
    login.find_element(By.XPATH, '//input[contains(@id, "first")]').click()
    login.find_element(By.XPATH, '//input[contains(@name, "index")]').send_keys(5)
    login.find_element(By.XPATH, '//input[contains(@id, "go_to_index")]').click()
    time.sleep(WAIT)

def test_survey_component(login):
    """Create survey components"""
    login.find_element(By.XPATH, '//a[contains(@href, "/admin/survey/surveycomponent/add")]').click()
    name_form = login.find_element(By.ID, value='id_name')
    name_form.send_keys('Pilot 1')
    login.find_element(By.XPATH, '//span[contains(@class, "select2-container")]').click()
    login.find_element(By.XPATH, '//li[contains(., "SB51506")]').click()
    login.find_element(By.XPATH, '//input[contains(@type, "submit")]').click()
    time.sleep(WAIT)
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(@href, "/admin/survey/surveycomponent/add")]').click()
    name_form = login.find_element(By.ID, value='id_name')
    name_form.send_keys('Pilot 2')
    login.find_element(By.XPATH, '//span[contains(@class, "select2-container")]').click()
    login.find_element(By.XPATH, '//li[contains(., "SB51535")]').click()
    login.find_element(By.XPATH, '//input[contains(@type, "submit")]').click()
    time.sleep(WAIT)

@pytest.mark.dependency()
def test_add_tag_comment_during_inspection(login):
    """Test adding tags and comments to detections in the manual inspection view"""
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51506")]]/td[contains(@class, "field-run_manual_inspection")]/a').click()
    login.find_element(By.XPATH, '//input[contains(@id, "tag_create")]').send_keys('Test tag from manual inspection')
    login.find_element(By.XPATH, '//textarea[contains(@id, "comment")]').send_keys('Test comment from manual inspection')
    login.find_element(By.XPATH, '//input[contains(@id, "submit")]').click()

@pytest.mark.dependency(depends=['test_add_tag_comment_during_inspection'])
def test_delete_all_tags(login):
    """Test delete all tag button"""
    login.find_element(By.XPATH, '//a[contains(@href, "admin/survey/tag")]').click()
    login.find_element(By.XPATH, '//input[contains(@id, "action-toggle")]').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "delete_selected")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    login.find_element(By.XPATH, '//input[contains(@type, "submit")]').click()

@pytest.mark.dependency(depends=['test_add_tag_comment_during_inspection'])
def test_delete_all_comments(login):
    """Test delete all comment button"""
    login.find_element(By.XPATH, '//a[contains(@href, "admin/survey/comment")]').click()
    login.find_element(By.XPATH, '//input[contains(@id, "action-toggle")]').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "delete_selected")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    login.find_element(By.XPATH, '//input[contains(@type, "submit")]').click()

@pytest.mark.dependency(depends=['test_add_tag_comment_during_inspection'])
def test_accepted_detections(login):
    """Test access to the accepted detections view and functionality for deselecting detections"""
    login.find_element(By.XPATH, '//a[contains(@href, "/admin/survey/accepteddetection")]').click()
    assert_element_exists_xpath(login, '//tr/td[contains(., "SB51506")]')

    # deselect all detections
    login.find_element(By.XPATH, '//input[contains(@id, "action-toggle")]').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "deselect")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    time.sleep(WAIT)

    # assert none
    list_items = login.find_elements(By.XPATH, '//tr/td[contains(., "SB51506")]')
    assert not list_items

@pytest.mark.dependency()
def test_select_sources(login):
    """Test the manual inspection workflow for selecting sources from a run.

    """
    SB1506_detection_names = [
        'SoFiA J210946.33-535431.7',
        'SoFiA J210732.62-545720.3',
        'SoFiA J210507.10-551140.3',
        'SoFiA J210523.75-560230.6',
        'SoFiA J205956.38-553345.8',
        'SoFiA J205858.04-552933.0',
        'SoFiA J205656.22-554311.5',
        'SoFiA J205506.40-555839.8',
        'SoFiA J210507.11-551140.2',  # additional detections due to random SoFiAX selection
        'SoFiA J205956.38-553345.5',
        'SoFiA J205858.05-552933.0',
        'SoFiA J210507.12-551140.4',
        'SoFiA J205956.37-553345.7',
        'SoFiA J205656.22-554311.4',
    ]
    SB51535_detection_names = [
        'SoFiA J210732.51-545717.5',
        'SoFiA J210507.11-551140.3',
        'SoFiA J205956.47-553339.6',
        'SoFiA J205727.53-534441.7',
        'SoFiA J205656.05-554311.1',
        'SoFiA J205505.52-555836.9',
        'SoFiA J205435.85-542654.3',
        'SoFiA J210732.52-545717.7',  # additional detections due to random SoFiAX selection
        'SoFiA J210507.12-551140.4',
        'SoFiA J205956.49-553339.9',
        'SoFiA J205656.05-554311.0',
        'SoFiA J210507.12-551140.4',
        'SoFiA J205445.30-553446.8'
    ]

    # Accept detections for run SB51506
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51506")]]/td[contains(@class, "field-run_manual_inspection")]/a').click()
    counter_string = login.find_element(By.XPATH, '//div[contains(@id, "content")]/h4').text
    counter = int(re.sub("[^0-9]", "", counter_string.split('/')[1]))
    for idx in range(counter):
        name = login.find_element(By.XPATH, '//div[contains(@id, "content")]/h1').text
        if name in SB1506_detection_names:
            login.find_element(By.XPATH, '//input[contains(@id, "submit")]').click()
        login.find_element(By.XPATH, '//input[contains(@id, "next")]').click()

    # Accept detections for run SB51535
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51535")]]/td[contains(@class, "field-run_manual_inspection")]/a').click()
    counter_string = login.find_element(By.XPATH, '//div[contains(@id, "content")]/h4').text
    counter = int(re.sub("[^0-9]", "", counter_string.split('/')[1]))
    for idx in range(counter):
        name = login.find_element(By.XPATH, '//div[contains(@id, "content")]/h1').text
        if name in SB51535_detection_names:
            login.find_element(By.XPATH, '//input[contains(@id, "submit")]').click()
        login.find_element(By.XPATH, '//input[contains(@id, "next")]').click()

    # Run internal cross match
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51506")]]/td[contains(@class, "action-checkbox")]/input').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51535")]]/td[contains(@class, "action-checkbox")]/input').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "_internal_cross_match")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    time.sleep(WAIT)

    # Assert tasks created exist
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Tasks")]').click()
    assert_element_exists_xpath(login, '//td[contains(., "internal_cross_match")]')


@pytest.mark.dependency(depends=['test_select_sources'])
def test_accept_first_run(login):
    """Release accepted detections for run SB51506. No external cross match required for the first accepted run.

    """
    # External cross match (to get source names)
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51506")]]/td[contains(@class, "action-checkbox")]/input').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "_external_cross_match")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    time.sleep(CROSS_MATCH_WAIT)

    # Release
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51506")]]/td[contains(@class, "action-checkbox")]/input').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "_release_sources")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    time.sleep(WAIT)
    login.find_element(By.XPATH, '//input[contains(@id, "tag_create")]').send_keys('Pilot 1')
    login.find_element(By.XPATH, '//input[contains(@id, "tag_description")]').send_keys('Tag for pilot 1 data release')
    login.find_element(By.XPATH, '//input[contains(@name, "confirm")]').click()
    time.sleep(WAIT)

    # Assert accepted detections with source name and release tag
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51506")]]/td[contains(@class, "field-run_accepted_detections")]/a').click()
    source_name = login.find_element(By.XPATH, '//td[contains(@class, "field-source_name")]')
    tags = login.find_element(By.XPATH, '//td[contains(@class, "field-tags")]')
    assert source_name.text != '-'
    assert tags.text == 'Pilot 1'


@pytest.mark.dependency(depends=['test_accept_first_run'])
def test_external_cross_matching(login):
    """Run external cross matching for the second run. This will generate conflicts in the database to resolve.

    """
    # Run external cross matching
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51535")]]/td[contains(@class, "action-checkbox")]/input').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "_external_cross_match")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    time.sleep(CROSS_MATCH_WAIT)

    # Verify cannot release accepted detections
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51535")]]/td[contains(@class, "action-checkbox")]/input').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "_release_sources")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    time.sleep(WAIT)
    login.find_element(By.XPATH, '//input[contains(@id, "tag_create")]').send_keys('Should not work')
    login.find_element(By.XPATH, '//input[contains(@id, "tag_description")]').send_keys('This action should fail')
    login.find_element(By.XPATH, '//input[contains(@name, "confirm")]').click()
    time.sleep(WAIT)
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Tasks")]').click()
    assert_element_exists_xpath(login, '//td[contains(., "There cannot be any external conflicts when creating release source names.")]')
    time.sleep(CROSS_MATCH_WAIT)

    # Conflict navigation
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51535")]]/td[contains(@class, "field-run_external_conflicts")]/a').click()
    login.find_element(By.XPATH, '//input[contains(@id, "next")]').click()
    login.find_element(By.XPATH, '//input[contains(@id, "previous")]').click()
    login.find_element(By.XPATH, '//input[contains(@id, "last")]').click()
    login.find_element(By.XPATH, '//input[contains(@id, "first")]').click()
    login.find_element(By.XPATH, '//input[contains(@name, "index")]').send_keys(1)
    login.find_element(By.XPATH, '//input[contains(@id, "go_to_index")]').click()

    # Resolve conflicts
    login.find_element(By.XPATH, '//input[contains(@id, "keep_new_source")]').click()
    time.sleep(WAIT)
    login.find_element(By.XPATH, '//input[contains(@id, "add_to_existing")]').click()
    time.sleep(WAIT)


@pytest.mark.dependency(depends=['test_external_cross_matching'])
def test_release_sources(login):
    """Release sources for second run under existing tag.

    """
    # Release
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51535")]]/td[contains(@class, "action-checkbox")]/input').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "_release_sources")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    time.sleep(WAIT)
    login.find_element(By.XPATH, '//input[contains(@id, "tag_create")]').send_keys('Pilot 2')
    login.find_element(By.XPATH, '//input[contains(@id, "tag_description")]').send_keys('Tag for pilot 2 data release')
    login.find_element(By.XPATH, '//input[contains(@name, "confirm")]').click()
    time.sleep(WAIT)

    # Assert accepted detections with source name and release tag
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//tr[.//*[contains(., "SB51535")]]/td[contains(@class, "field-run_accepted_detections")]/a').click()
    source_name = login.find_element(By.XPATH, '//td[contains(@class, "field-source_name")]')
    tags = login.find_element(By.XPATH, '//td[contains(@class, "field-tags")]')
    assert source_name.text != '-'
    assert tags.text == 'Pilot 2'


@pytest.mark.dependency(depends=['test_release_sources'])
def test_cleanup(login):
    """Delete the runs. Assert that no dangling database entries exist.
    Comments will cascade delete when their detections are deleted.

    """
    # Delete runs
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    login.find_element(By.XPATH, '//input[contains(@id, "action-toggle")]').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "_delete_run")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    login.find_element(By.XPATH, '//input[contains(@name, "confirmation")]').click()

    # Delete survey components
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Survey components")]').click()
    login.find_element(By.XPATH, '//input[contains(@id, "action-toggle")]').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "delete_selected")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    login.find_element(By.XPATH, '//input[contains(@type, "submit")]').click()

    # Delete tags
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Tags")]').click()
    login.find_element(By.XPATH, '//input[contains(@id, "action-toggle")]').click()
    login.find_element(By.XPATH, '//select[contains(@name, "action")]').click()
    login.find_element(By.XPATH, '//option[contains(@value, "delete_selected")]').click()
    login.find_element(By.XPATH, '//button[contains(@title, "Run the selected action")]').click()
    login.find_element(By.XPATH, '//input[contains(@type, "submit")]').click()

    # Assert no runs, instances, detections, tags or comments remain
    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Runs")]').click()
    results = login.find_element(By.XPATH, '//p[contains(@class, "paginator")]')
    assert results.text == '0 runs'

    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Instances")]').click()
    results = login.find_element(By.XPATH, '//p[contains(@class, "paginator")]')
    assert results.text == '0 instances'

    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Detections")]').click()
    results = login.find_element(By.XPATH, '//p[contains(@class, "paginator")]')
    assert results.text == '0 detections'

    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Tags")]').click()
    results = login.find_element(By.XPATH, '//p[contains(@class, "paginator")]')
    assert results.text == '0 tags'

    login.find_element(By.XPATH, '//a[contains(@href, "/admin")]').click()
    login.find_element(By.XPATH, '//a[contains(., "Comments")]').click()
    results = login.find_element(By.XPATH, '//p[contains(@class, "paginator")]')
    assert results.text == '0 comments'

@pytest.mark.dependency(depends=['test_cleanup'])
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
