#!/usr/bin/env python3
"""
    *******************************************************************************************
    FBGBot.
    Author: Ali Toori, Python Developer [Web-Automation Bot Developer | Web-Scraper Developer]
    LinkedIn: https://www.linkedin.com/in/alitoori/
    *******************************************************************************************
"""
import os
import time
import random
import pickle
import ntplib
import datetime
import pyfiglet
import pandas as pd
import logging.config
from time import sleep
from pathlib import Path
import concurrent.futures
from selenium import webdriver
from multiprocessing import freeze_support
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',  # colored output
            # --> %(log_color)s is very important, that's what colors the line
            'format': '[%(asctime)s] %(log_color)s%(message)s'
        },
    },
    "handlers": {
        "console": {
            "class": "colorlog.StreamHandler",
            "level": "INFO",
            "formatter": "colored",
            "stream": "ext://sys.stdout"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "console"
        ]
    }
})

LOGGER = logging.getLogger()


class FBGBot:
    def __init__(self):
        self.first_time = True
        self.PROJECT_FOLDER = os.path.abspath(os.path.dirname(__file__))
        self.PROJECT_ROOT = Path(self.PROJECT_FOLDER)
        self.FB_HOME_URL = "https://web.facebook.com/"
        self.FB_HOME_EXT = "https://web.facebook.com/?_rdc=1&_rdr"
        self.file_path_msgs = str(self.PROJECT_ROOT / 'FBGRes/Messages.csv')
        self.file_path_groups = str(self.PROJECT_ROOT / 'FBGRes/Groups.csv')
        self.file_path_members = str(self.PROJECT_ROOT / 'FBGRes/MemberProfiles.csv')
        self.file_path_uagent = str(self.PROJECT_ROOT / 'FBGRes/user_agents.txt')
        self.driver_bin = str(self.PROJECT_ROOT / "FBGRes/bin/chromedriver_win32.exe")
        self.file_timer_sec = self.PROJECT_ROOT / 'FbMRes/TimerSec.txt'
        self.file_path_keywords = self.PROJECT_ROOT / "FbMRes/Keywords.csv"
        self.file_path_comments = self.PROJECT_ROOT / "FbMRes/Comments.csv"
        self.file_path_posted_comments = self.PROJECT_ROOT / "FbMRes/PostedComments.csv"

    # Get random user-agent
    def get_random_user_agent(self):
        user_agents_list = []
        with open(self.file_path_uagent) as f:
            content = f.readlines()
        user_agents_list = [x.strip() for x in content]
        return random.choice(user_agents_list)

    # Login to the website for smooth processing
    def get_driver(self, account_num, headless=False):
        # For absolute chromedriver path
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features")
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument(F'--user-agent={self.get_random_user_agent()}')
        if headless:
            options.add_argument("--headless")
        # options.add_argument('--headless')
        driver = webdriver.Chrome(executable_path=self.driver_bin, options=options)
        return driver

    def close_popup(self, driver, email):
        try:
            LOGGER.info(f"[Waiting for possible pop-up][Account: {str(email)}]")
            self.wait_until_visible(driver=driver, element_id='u_0_k', duration=3)
            driver.find_element_by_id('u_0_k').click()
            LOGGER.info(f"[Cookies Accepted][Account: {str(email)}]")
            LOGGER.info(f"[Pop-up closed][Account: {str(email)}]")
        except:
            try:
                driver.find_element_by_tag_name('html').send_keys(Keys.ENTER)
                LOGGER.info(f"[Pop-up closed][Account: {str(email)}]")
            except:
                pass

    def wait_until_visible(self, driver, xpath=None, element_id=None, name=None, class_name=None, tag_name=None, css_selector=None, duration=10000, frequency=0.01):
        if xpath:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        elif element_id:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.ID, element_id)))
        elif name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.NAME, name)))
        elif class_name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
        elif tag_name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.TAG_NAME, tag_name)))
        elif css_selector:
            WebDriverWait(driver, duration, frequency).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))

    # Facebook login
    def login(self, driver, email, password):
        LOGGER.info(f"[Signing-in to the Facebook][Account {email}]")
        cookies = 'Cookies' + str(email) + '.pkl'
        file_cookies = self.PROJECT_ROOT / 'FBGRes' / cookies
        LOGGER.info(f"[Requesting: {str(self.FB_HOME_URL)}][Account {email}]")
        driver.get(self.FB_HOME_URL)
        if os.path.isfile(file_cookies):
            # try:
            LOGGER.info(f"[Loading cookies][Account {email}]")
            with open(file_cookies, 'rb') as cookies_file:
                cookies = pickle.load(cookies_file)
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.get(self.FB_HOME_EXT)
            LOGGER.info(f"[Waiting for FB profile to become visible][Account: {str(email)}]")
            sleep(5)
            if str(driver.current_url) == str(self.FB_HOME_EXT):
                LOGGER.info(f"[Successfully logged-in][Account: {str(email)}]")
                LOGGER.info(f"[Cookies login successful][Account: {str(email)}]")
                return
            else:
                LOGGER.info(f"[Cookies login failed][Account {email}]")
            os.remove(file_cookies)
        # Try closing pop-up
        try:
            self.close_popup(driver=driver, email=email)
        except:
            pass
        LOGGER.info(f"[Waiting for login fields to become visible]")
        self.wait_until_visible(driver=driver, name='email', duration=5)
        LOGGER.info(f"[Filling email]")
        driver.find_element_by_name('email').send_keys(email)
        LOGGER.info(f"[Filling password]")
        driver.find_element_by_name('pass').send_keys(password)
        driver.find_element_by_name('login').click()
        LOGGER.info(f"[Waiting for FB profile to become visible][Account: {str(email)}]")
        sleep(5)
        if str(driver.current_url) == str(self.FB_HOME_EXT):
            LOGGER.info(f"[Successfully logged-in][Account: {str(email)}]")
        # Store user cookies for later use
        try:
            LOGGER.info(f"[Saving cookies for][Account {email}]")
            with open(file_cookies, 'wb') as cookies_file:
                pickle.dump(driver.get_cookies(), cookies_file)
            LOGGER.info(f"Cookies have been saved][Account {email}]")
        except:
            pass

    def get_pages(self, driver, email):
        page_search_url = 'https://web.facebook.com/search/pages/?q='
        # Get keywords from Keywords.csv file
        df_keywords = pd.read_csv(self.file_path_keywords, index_col=None)
        businesses = [keyword['BusinessType'] for keyword in df_keywords.iloc]
        locations = [keyword['Location'] for keyword in df_keywords.iloc]
        LOGGER.info(f"[Searches to be made: {str(len(businesses) * len(locations))}][Account: {str(email)}]")
        for business in businesses:
            for location in locations:
                keyword = business + ' in ' + location
                url_final = page_search_url + keyword.replace(' ', "%20")
                LOGGER.info(f"[Requesting: {str(url_final)}][Account: {str(email)}]")
                driver.get(url_final)
                LOGGER.info(f"[Waiting for search result to become visible][Account: {str(email)}]")
                self.wait_until_visible(driver=driver, css_selector='.d2edcug0.glvd648r.o7dlgrpb')
                LOGGER.info("[Scrolling down the result]")
                html = driver.find_element_by_tag_name('html')
                while True:
                    html.send_keys(Keys.END)
                    html.send_keys(Keys.END)
                    html.send_keys(Keys.END)
                    sleep(1)
                    pages = [p.get_attribute('href') for p in
                             driver.find_elements_by_css_selector('.gpro0wi8.lrazzd5p.dkezsu63')]
                    LOGGER.info(f"[Pages found so far: {str(len(pages))}]")
                    # Scroll to the end and break
                    try:
                        end = str(driver.find_elements_by_css_selector(
                            '.rq0escxv.l9j0dhe7.du4w35lb.j83agx80.cbu4d94t.pfnyh3mw.d2edcug0.aahdfvyu.tvmbv18p')[
                                      -1].text)
                        if 'End of results' in end:
                            break
                    except:
                        pass
                LOGGER.info(f"[Pages found: {str(len(pages))}]")
                df_pages = pd.DataFrame({"PageLink": pages, "D1M1": 'None', "DateSent": '2030-11-11', "D1M2": 'None',
                                         "D2M1": 'None', "D2M2": 'None', "D3M1": 'None', "D3M2": 'None',
                                         "D4M1": 'None', "D4M2": 'None'})
                # if file does not exist write headers
                if not os.path.isfile(self.file_path_groups):
                    df_pages.to_csv(self.file_path_groups, index=False)
                else:  # else if exists so append without writing the header
                    df_pages.to_csv(self.file_path_groups, mode='a', header=False, index=False)
                LOGGER.info(f"[Page links has been saved to PageLinks.csv][Account: {str(email)}]")

    def send_dm(self, driver, email):
        LOGGER.info(f'[Sending DMs ...][Account {email}]')
        # Get group-link from input file
        group_df = pd.read_csv(self.file_path_groups, index_col=None)
        group_links = [group for group in group_df.iloc]
        for group_link in group_links:
            group_number = group_link[32:-8]
            LOGGER.info(f"[Group Number: {str(group_number)}")
            LOGGER.info(f"[Group Link: {str(group_link)}")
            # Get City name from input file
            with open(self.file_path_msgs) as f:
                content = f.readlines()
            messages = [x.strip().split(':') for x in content]
            LOGGER.info(f"[Messages: {str(messages)}")
            LOGGER.info(f"[Requesting group: {str(group_link)}]")
            driver.get(group_link)
            LOGGER.info("[Waiting for the group to become visible]")
            self.wait_until_visible(driver, xpath='//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[3]/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/a[4]/div[1]')
            LOGGER.info("[Group has been visible]")
            LOGGER.info("[Scrolling down the group members]")
            scrolls = 0
            while True:
                driver.find_element_by_tag_name('html').send_keys(Keys.END)
                scrolls += 1
                sleep(3)
                if scrolls >= 100:
                    break
            LOGGER.info("[Getting members]")
            members = [member.get_attribute('href') for member in driver.find_element_by_css_selector('.b20td4e0.muag1w35').find_elements_by_tag_name('a')]
            df = pd.DataFrame({"Profile": members})
            # if file does not exist write headers
            if not os.path.isfile(self.file_path_members):
                df.to_csv(self.file_path_members, index=False)
            else:  # else if exists so append without writing the header
                df.to_csv(self.file_path_members, mode='a', header=False, index=False)
            LOGGER.info(f"[Members record has been saved to MembersProfiles.csv]")
            LOGGER.info(f"[Members found: {str(len(members))}]")
            for member in members:
                message = random.choice(messages)
                LOGGER.info(f"[Requesting member profile: {str(member)}]")
                driver.get(member)
                LOGGER.info("[Waiting for member profile to become visible]")
                self.wait_until_visible(driver, xpath='//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/div/div/div/div')
                LOGGER.info("[Member profile has been visible]")
                LOGGER.info("[Waiting for message button to become visible]")
                self.wait_until_visible(driver, xpath='//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/div[1]/div/div')
                LOGGER.info("[Message button has been visible]")
                LOGGER.info("[Clicking Message button]")
                driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[3]/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/div[1]/div/div').click()
                LOGGER.info("[Message button has been clicked]")
                LOGGER.info("[Waiting for message box to become visible]")
                self.wait_until_visible(driver, xpath='//*[@id="mount_0_0"]/div/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div/div/div/div/div/div/div[2]/div/div[2]/form/div/div[3]/div[2]/div[1]/div/div/div/div/div[2]/div')
                LOGGER.info("[Sending message]")
                LOGGER.info(f"[Message to be sent: {message}]")
                message_box = driver.find_element_by_xpath('//*[@id="mount_0_0"]/div/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/div/div/div/div/div/div/div[2]/div/div[2]/form/div/div[3]/div[2]/div[1]/div/div/div/div/div[2]/div')
                message_box.send_keys(message)
                message_box.send_keys(Keys.ENTER)
                LOGGER.info(f"[Message has been sent]")
                LOGGER.info(f"[Waiting for 20 seconds]")
                sleep(5)

    # Checks if previous message has been responded
    def message_confirm(self, driver, message):
        LOGGER.info(f"[Confirming message: {str(message)}]")
        try:
            last_message = str(driver.find_elements_by_css_selector('.j83agx80.r8blr3vg')[-1].text).strip()
            if last_message == message:
                return True
            else:
                return False
        except:
            LOGGER.info("[No sent message found]")
            return False

    # Checks if previous message has been responded
    def message_answered(self, driver, message):
        LOGGER.info(f"[Checking message response for: {str(message)}]")
        try:
            self.wait_until_visible(driver, css_selector='.j83agx80.r8blr3vg', duration=5)
            last_message = str(driver.find_elements_by_css_selector('.j83agx80.r8blr3vg')[-1].text).strip()
            print(last_message)
            if last_message != message:
                LOGGER.info(f"[Message response found]")
                return True
            else:
                return False
        except:
            LOGGER.info("[No sent message found]")
            return False

    def post_comment(self, driver, page, comment):
        try:
            LOGGER.info("[Waiting for page to become visible]")
            self.wait_until_visible(driver, css_selector='.hnhda86s.oo9gr5id.hzawbc8m', duration=10)
            LOGGER.info("[Page has been visible]")
            page_name = str(driver.find_element_by_css_selector('.hnhda86s.oo9gr5id.hzawbc8m').text).strip()
            comment = page_name + ' ' + comment
            LOGGER.info("[Waiting for comment box to become visible]")
            self.wait_until_visible(driver, css_selector='._1mf._1mj', duration=10)
            LOGGER.info("[Comment box has been visible]")
            driver.find_element_by_css_selector('._1mf._1mj').send_keys(comment)
            LOGGER.info(f"[Comment has been posted]")
            posted_comment = {"PageLink": [page], "Comment": [comment]}
            df = pd.DataFrame(posted_comment)
            # if file does not exist write headers
            if not os.path.isfile(self.file_path_posted_comments):
                df.to_csv(self.file_path_posted_comments, index=False)
            else:  # else if exists so append without writing the header
                df.to_csv(self.file_path_posted_comments, mode='a', header=False, index=False)
            LOGGER.info(f"[Comments record has been saved to PostedComments.csv]")
            return comment
        except:
            pass

    def start(self, account):
        LOGGER.info(f'[FBGBot Launched]')
        account_num = str(account["AccountNo"])
        email = str(account["Email"])
        password = str(account["Password"])
        driver = self.get_driver(account_num=account_num)
        self.login(driver=driver, email=email, password=password)
        self.send_dm(driver=driver, email=email)

    def to_file(self, filename, row):
        with open(filename, "a+") as file:
            file.write(row + '\n')

    def finish(self, driver, account_num):
        try:
            LOGGER.info(f'[Closing the browser: [Account {account_num}]]')
            driver.close()
            driver.quit()
        except WebDriverException as exc:
            LOGGER.info(f'[Issue occurred while closing the browser: {str(exc.args)}]')


# Trial version logic
def trial(trial_date):
    ntp_client = ntplib.NTPClient()
    try:
        response = ntp_client.request('pool.ntp.org')
        local_time = time.localtime(response.ref_time)
        current_date = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
        current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
        return trial_date > current_date
    except:
        pass


def enable_cmd_colors():
    # Enables Windows New ANSI Support for Colored Printing on CMD
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


def main():
    freeze_support()
    enable_cmd_colors()
    trial_date = datetime.datetime.strptime('2021-03-30 23:59:59', '%Y-%m-%d %H:%M:%S')
    # Print ASCII Art
    print('************************************************************************')
    pyfiglet.print_figlet('____________               FBGBot ____________\n', colors='RED')
    print('Author: Ali Toori, Python Developer [Bot Builder]\n'
          'Website: https://botflocks.com/\nLinkedIn: https://www.linkedin.com/in/alitoori/\n************************************************************************')
    # Trial version logic
    if trial(trial_date):
        fb_bot = FBGBot()
        file_path_account = str(fb_bot.PROJECT_ROOT / "FBGRes/Accounts.csv")
        if os.path.isfile(file_path_account):
            account_df = pd.read_csv(file_path_account, index_col=None)
            # Get accounts from Accounts.csv
            account_list = [account for account in account_df.iloc]
            account = account_list[0]
            fb_bot.start(account)
            # print("Your trial will end on: ",
            #       str(trial_date) + ". To get full version, please contact fiverr.com/AliToori !")
            # Launch the tasks
            # We can use a with statement to ensure threads are cleaned up promptly
            # with concurrent.futures.ThreadPoolExecutor(max_workers=len(account_list)) as executor:
            #     executor.map(fb_bot.start, account_list)
    else:
        pass
        # print("Your trial has been expired, To get full version, please contact fiverr.com/AliToori !")


if __name__ == '__main__':
    freeze_support()
    main()