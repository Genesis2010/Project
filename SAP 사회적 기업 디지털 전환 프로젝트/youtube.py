from bs4 import BeautifulSoup
from selenium import webdriver
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import time
import datetime

# 스프레드시트 연결에 대한 중요한 내용이 있어 삭제했습니다.

driver = webdriver.Chrome('/Users/genesis/PycharmProjects/socproject/chromedriver')

def scroll():  # 웹 사이트에서 마지막 까지 스크롤하는 함수
    SCROLL_PAUSE_TIME = 1 # 기다리는 시간 2초
    last_height = driver.execute_script("return document.documentElement.scrollHeight") # 마지막 스크롤의 위치
    while True:
        # 가장 하단까지 스크롤 하기
        driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")

        # 웹 페이지가 로딩 될때 까지 기다림
        time.sleep(SCROLL_PAUSE_TIME)

        # 스크롤 한 후의 위치를 저장하고 기존 값과 같을 경우 더이상 스크롤 할게 없다고 판단
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            print("웹사이트 스크롤 완료")
            break
        last_height = new_height

# The BunduBallerina 크롤링 (34번째 줄부터 102번째 줄까지)
def first(): # 함수명 : first
    print("웹사이트 크롤링 중입니다")
    # 문서 불러오기
    doc = gc.open_by_url(spreadsheet_url)

    # TheBunduBallerina 시트 불러오기
    worksheet = doc.worksheet('TheBunduBallerina')

    # 기존에 크롤링 했던 모든 자료 삭제
    worksheet.clear();

    # 시작 시간 출력
    Start_now = datetime.datetime.now()
    worksheet.append_row(["시작 시간", "완료 시간"])
    worksheet.append_row([str(Start_now)]) # 시작 시간을 출력

    #목차 출력
    worksheet.append_row(["TheBunduBallerina 영상 소스", "제목", "영상 주소"])


    # TheBunduBallerina 주소
    url = 'https://www.youtube.com/user/TheBunduBallerina/videos'

    driver.get(url)

    # 크롬이 켜지고 제일 하단까지 스크롤
    scroll()

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    temp_url = []  # 임시 url
    href_list = []  # href 에서 뽑아낸 url
    url_list = []  # 최종 url
    video_list = []  # 영상 주소 url
    name_list = []  # 제목 리스트

    dismissable = soup.select('#dismissable')

    # id 값이 dismissable인 태그 안에 있는 href 값을 temp_url 에 저장
    for i in dismissable:
        temp_url.append(i.a.attrs['href'])

    # temp_url에 저장된 값에 불필요한 데이터를 없애기 위해 9번째부터 마지막 까지의 데이터를 href_list에 저장
    for i in temp_url:
        href_list.append(i[9:])

    # 공통 적인 영상 소스 주소에 기존의 url을 붙여서 url_list에 저장
    for i in href_list:
        url_list.append('www.youtube.com/embed/' + i)

    for i in href_list:
        video_list.append('www.youtube.com/watch?v=' + i)

    # id 값이 video-title인 태그 안에 있는 영상 제목을 videotitle에 저장
    videotitle = soup.select('#video-title')

    # 텍스트만 추출해서 name_list에 저장
    for i in videotitle:
        name_list.append(i.text)

    # 각 데이터들을 영상소스, 제목, 영상주소 순으로 출력
    for i in range(len(url_list)):
        worksheet.append_row([url_list[i], name_list[i], video_list[i]])
        time.sleep(1) # 구글 API한계로 인해 1초 기다리고 출력

    # C3셀에 끝난 시간 출력
    End_now = datetime.datetime.now()
    worksheet.update_acell('B2', str(End_now))

# The SuperBalletgirl101 크롤링 ( 104번째 줄 부터 168번쨰 줄까지)
def second(): # 함수명 : second
    # 문서 불러오기
    doc = gc.open_by_url(spreadsheet_url)

    # SuperBalletgirl101 시트 불러오기
    worksheet = doc.worksheet('SuperBalletgirl101')

    # 기존에 크롤링 했던 모든 자료 삭제
    worksheet.clear();

    # 시작 시간 출력
    Start_now = datetime.datetime.now()
    worksheet.append_row(["시작 시간", "완료 시간"])
    worksheet.append_row([str(Start_now)])

    # 목차 출력
    worksheet.append_row(["SuperBalletgirl101 영상 소스", "제목", "영상 주소"])

    # SuperBalletgiral101 주소
    url = 'https://www.youtube.com/user/SuperBalletgirl101/videos'

    driver.get(url)

    # 크롬이 켜지고 제일 하단까지 스크롤
    scroll()

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    temp_url = []  # 임시 url
    href_list = []  # href 에서 뽑아낸 url
    url_list = []  # 최종 url
    video_list = []  # 영상 주소 url
    name_list = []  # 제목 리스트

    dismissable = soup.select('#dismissable')

    # id 값이 dismissable인 태그 안에 있는 href 값을 temp_url 에 저장
    for i in dismissable:
        temp_url.append(i.a.attrs['href'])

    for i in temp_url:
        href_list.append(i[9:])

    for i in href_list:
        url_list.append('www.youtube.com/embed/' + i)

    for i in href_list:
        video_list.append('www.youtube.com/watch?v=' + i)

    # id 값이 video-title인 태그 안에 있는 영상 제목을 videotitle에 저장
    videotitle = soup.select('#video-title')

    for i in videotitle:
        name_list.append(i.text)

    # 각 데이터들을 영상소스, 제목, 영상주소 순으로 출력
    for i in range(len(url_list)):
        worksheet.append_row([url_list[i], name_list[i], video_list[i]])
        time.sleep(1) # 구글 API한계로 인해 1초 기다리고 출력

    # C3셀에 끝난 시간 출력
    End_now = datetime.datetime.now()
    worksheet.update_acell('B2', str(End_now))

# 크롤링 실행
first()
second()
print("크롤링 완료")

# 크롤링 프로그램 끄기
driver.close()
