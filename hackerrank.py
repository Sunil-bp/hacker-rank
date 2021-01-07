"""
Check the scraping functionality of python
Get a hackerrank class to get all your data

get all the challenges under any wing
get solutions submitted by you
"""

from bs4 import BeautifulSoup
import json
import os
import requests
import types
import pickle
import time
from getpass import getpass
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time 

HACKER_RANK = "https://www.hackerrank.com/login"
HACKER_RANK_POST = "https://www.hackerrank.com/auth/login"
DASHBOARD = "https://www.hackerrank.com/dashboard"
PATH = "https://www.hackerrank.com/rest/contests/master/tracks/"
PROBLEMS = "https://www.hackerrank.com/rest/contests/master/challenges/"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'


class Hackerrank:
    '''
    Connect to server to get data
    '''

    def __init__(self, credentials=None):
        """
        Constructs and returns an :class:`Hackerrank <Hackerrank>`. This
        will use a cookie jar stored, by default, in the home directory.

        :param credentials: Two-element array of username/password or lambda that will return such.
        """
        self.local_dir = os.path.dirname(os.path.realpath(__file__))
        self.__c = credentials
        self.session = requests.Session()
        self.pickel_path = os.path.join(self.local_dir, "_hacker_rank_cookies.p")

        if os.path.exists((os.path.join(self.local_dir,"config.json"))):
            with open(os.path.join(self.local_dir,"config.json"),'r') as f:
                self.header  = json.load(f).get("query_header")
        else:
            raise Exception(f"Config fle not found at: {self.local_dir}")

        if os.path.exists(self.pickel_path):
            print("Loading cookies data")
            self.session.cookies = pickle.load(open(self.pickel_path, 'rb'))

        response = self.http_connector(HACKER_RANK)
        if len(response.history) <= 1:
            print("Needs to load cookies from browser")
            self.cookies = self.get_cookies(self.__c)
            for cookie in self.cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])

        with open(self.pickel_path, 'wb') as f:
            pickle.dump(self.session.cookies, f)
        self.__c = None

    def get_cookies(self, creds):
        _driver_path = os.path.join(self.local_dir, "chromedriver.exe")
        if not os.path.exists(_driver_path):
            raise Exception(f"Unable to find Driver file at {_driver_path}")

        if isinstance(self.__c, types.FunctionType):
            self.__c = self.__c()

        if not isinstance(self.__c, list) or len(self.__c) != 2:
            raise Exception(f"Invalid self.__c : expected list of two elements, but got {type(self.__c)}")

        option = Options()
        option.headless = True
        option.add_argument("--incognito")
        option.add_argument('user-agent={0}'.format(USER_AGENT))
        driver = webdriver.Chrome(_driver_path, options=option)

        driver.get(HACKER_RANK_POST)
        print(driver.title)
        print("Initialised chrome headless ")
        # login here
        user_name = driver.find_element_by_id("input-1")
        password = driver.find_element_by_id("input-2")
        check_box = driver.find_element_by_class_name("checkbox-input")
        submit = driver.find_element_by_xpath(
            "/html/body/div[4]/div/div/div/div[2]/div[2]/div/div/div[2]/div/div/div[2]/div[1]/form/div[4]/button")
        user_name.clear()
        password.clear()

        user_name.send_keys(self.__c[0])
        password.send_keys(self.__c[1])
        check_box.click()
        submit.click()
        # load next page and let chrome set all cookies
        time.sleep(10)

        cookies = driver.get_cookies()
        driver.close()
        return cookies

    def http_connector(self,url):
        response = self.session.get(url,
                                    headers=self.header,
                                    timeout=10)
        if response:
            return response
        else:
            # print(response.text)
            print(f"\nError connecting to : {url} \n return code : {response.status_code}")
            time.sleep(15)
            # recurse back 
            return self.http_connector(url)


    def learning_paths(self, path="my-skills"):
        '''
        Get all the learning paths avilable at hacker rank
        :param path: "class to track"
        :return: path
        '''
        print(f"Fetching all the path for : {path}")
        r = self.http_connector(DASHBOARD)
        soup = BeautifulSoup(r.content, "html.parser")
        data = soup.find("div", {"class": path})
        rows = data.find_all("li")
        paths = [i.text for i in rows]
        return paths

    def get_problem_list(self, path):
        '''
        Get the list of all the problems in a perticular learning path
        :param path:
        :return:  problem list
        '''
        print(f"Fetching all problems from {path}")
        total = 0
        offset = 0
        problem = []
        while offset <= total:
            url = PATH + path + "/challenges?" + "offset=" + str(offset) + "&limit=50&track_login=true"
            print(f"Connecting to url : {url}")
            r = self.http_connector(url)
            data = r.json()
            offset += 50
            total = data.get('total')
            for ep in data.get("models"):
                problem.append(ep.get("slug"))
        print(f"Number of total probs {len(problem)}")
        return problem

    def get_details(self, problem):
        '''
        Get each problem details given problem name
        :param problem:
        :return:
        '''
        print(problem.ljust(50), end="")

        # Dealing with folder and organising files
        url = PROBLEMS + problem
        response = self.http_connector(url)
        # print(f"problem name  is {response.json().get('model').get('slug')}")
        # print(f"problem status  is {response.json().get('model').get('solved', 'not known ')}")
        path_name = response.json().get("model").get("track").get("track_name")
        folder = response.json().get("model").get("track").get("name")
        if not os.path.exists(os.path.join(self.local_dir, path_name, folder)):
            # print(f"creating folder {os.path.join(self.local_dir,path_name,folder)}")
            os.makedirs(os.path.join(self.local_dir, path_name, folder))
        path = os.path.join(self.local_dir, path_name, folder)

        #Get problem as pdf
        url = PROBLEMS + problem + "/download_pdf?language=English"
        r = self.http_connector(url)
        print("\tProblem code : ", r.status_code, end="")
        if r:
            with open(os.path.join(path, problem + ".pdf"), 'wb') as f:
                f.write(r.content)

        ## get successful submissino data
        url = PROBLEMS + problem + "/submissions"
        r = self.http_connector(url)
        print("\tSolution code : ", r.status_code, end='')
        if r:
            ID = None
            # print("getting each sub")
            submissions = r.json().get("models")
            print("\t submissions : ", len(submissions), end='')
            for submission in submissions:
                if submission.get("status") == 'Accepted' and submission.get("language") in ["python3", "python"]:
                    ID = submission.get("id", None)
                    break

            if ID:
                url = PROBLEMS + problem + "/submissions/" + str(ID)
                # print(url)
                r = self.http_connector(url)
                print("\tSolution txt code : ", r.status_code)
                if r:
                    # print(r.json().get("model").get('code'))
                    with open(
                            os.path.join(os.path.join(self.local_dir, path_name, folder), problem + "_submission.txt"),
                            "wb") as f:
                        f.write((r.json().get("model").get('code')).encode())
        return problem


hr = Hackerrank(credentials = lambda: [input('Email: '), getpass('Password: ')])
# paths = hr.get_paths()
problems = hr.get_problem_list("Python")
print("Fetching details for all problems")
for problem in problems:
    data = hr.get_details(problem)
    #avoid maximum connection error
    #time.sleep(10)
