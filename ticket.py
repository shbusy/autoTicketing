from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException
import time
import easyocr

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

wait = WebDriverWait(driver, 1800)

print("**********************************************************************")
print("******************************티켓 매수입력*****************************")
print("**********************************************************************")
ticket_cnt = input("ex) 1매 (X) -> 1 (O) / 2매 (X) -> 2 (O)\n>>>>>>>>> ")

print("**********************************************************************")
print("******************************공연날짜입력******************************")
print("**********************************************************************")
want_day = input("ex) 23일 (X) -> 23 (O) / 01일 (X) -> 1 (O)\n>>>>>>>>> ")

print("**********************************************************************")
print("****************************원하는 구역 입력****************************")
print("**********************************************************************")
BlockNumbers_str = input("숫자를 공백으로 구분해서 입력 ex) 036 037 035 038 034 039 236 237 235 238 234 239\n>>>>>>>>> ")
BlockNumbers = BlockNumbers_str.split()

print("**********************************************************************")
print("***************************예매시작시간 대기중***************************")
print("**********************************************************************")

wait.until(EC.visibility_of_element_located((By.XPATH, "//li[text()='"+str(want_day)+"']"))).click()
print("**********************************************************************")
print("****************************입력한날짜선택됨****************************")
print("**********************************************************************")

wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".sideBtn.is-primary"))).click()
print("**********************************************************************")
print("*****************************예매하기클릭됨*****************************")
print("**********************************************************************")

# 새창전환
wait.until(EC.number_of_windows_to_be(2))
driver.switch_to.window(driver.window_handles[1])
print("**********************************************************************")
print("***************************팝업창 포커스전환됨***************************")
print("**********************************************************************")

print("**********************************************************************")
print("*********************************대기중********************************")
print("**********************************************************************")

# iframe으로 이동
wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='ifrmSeat']")))
print("**********************************************************************")
print("**************************구역선택 포커스이동됨**************************")
print("**********************************************************************")

# 좌석 탐색
def select():
    time.sleep(0.1)
    driver.switch_to.window(driver.window_handles[-1])
    print("**********************************************************************")
    print("**************************좌석탐색시작 select()*************************")
    print("**********************************************************************")

    wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='ifrmSeat']")))
    print("**********************************************************************")
    print("**************************구역선택 포커스이동됨**************************")
    print("**********************************************************************")

    # 세부구역 선택
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='ifrmSeatDetail']")))
    print("**********************************************************************")
    print("***************************좌석창 포커스이동됨***************************")
    print("**********************************************************************")

    # 좌석선택
    findSeats()

    # 결제
    payment()

def findSeats(): # 좌석선택

    print("**********************************************************************")
    print("**************************좌석선택 findSeats()**************************")
    print("**********************************************************************")

    while True:
        chk = 0

        for BlockNumber in BlockNumbers:

            time.sleep(0.5)
            script = f"GetBlockSeatList('', '', '{BlockNumber}')"
            print("**********************************************************************")
            print(f"*****************************{BlockNumber}구역 클릭됨***************************")
            print("**********************************************************************")
            driver.execute_script(script)

            # 좌석선택
            time.sleep(0.1)

            # 빈자리
            wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "SeatT")))
            seatNs = driver.find_elements(By.CLASS_NAME, "SeatN")

            if ticket_cnt == "1":
                if len(seatNs) >= 1:
                    for i in range(len(seatNs)):
                        actions = ActionChains(driver)
                        actions.click(seatNs[i])
                        actions.perform()

                        time.sleep(0.1)
                        driver.switch_to.window(driver.window_handles[-1])
                        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='ifrmSeat']")))

                        try:
                            # 좌석선택완료 클릭
                            driver.execute_script("fnSelect()")

                            # 만약 이선좌가 뜬다면 확인처리
                            driver.switch_to.alert.accept()
                            continue

                        except NoAlertPresentException:
                            # 이선좌 없이 정상처리될경우를 예외로 처리
                            chk = 1
                            break

            elif ticket_cnt == "2":
                # 빈자리 두개 이상일 때
                if len(seatNs) >= 2:
                    for i in range(len(seatNs)-1):
                        pos_current = seatNs[i].location_once_scrolled_into_view
                        pos_next = seatNs[i+1].location_once_scrolled_into_view

                        # 연석일때
                        if pos_current['x'] + seatNs[i].size['width'] + 2 == pos_next['x']:
                            actions = ActionChains(driver)

                            actions.click(seatNs[i])
                            actions.click(seatNs[i+1])

                            actions.perform()

                            time.sleep(0.1)
                            driver.switch_to.window(driver.window_handles[-1])
                            wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='ifrmSeat']")))

                            try:
                                # 좌석선택완료 클릭
                                driver.execute_script("fnSelect()")

                                # 만약 이선좌가 뜬다면 확인처리
                                driver.switch_to.alert.accept()
                                continue

                            except NoAlertPresentException:
                                # 이선좌 없이 정상처리될경우를 예외로 처리
                                chk = 1
                                break

            if chk == 1:
                print("**********************************************************************")
                print("*****************************좌석선택 완료됨1***************************")
                print("**********************************************************************")
                break

            elif chk == 0:
                # 자리가 없을때 전체구역보기 눌러서 구역선택으로 돌아감
                print("**********************************************************************")
                print("**********************자리없음 구역선택으로 되돌아감**********************")
                print("**********************************************************************")
                wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='divSeatBox']"))).click()
                continue

        if chk == 1:
            print("**********************************************************************")
            print("*****************************좌석선택 완료됨2***************************")
            print("**********************************************************************")
            break

def payment():
    # 결제
    print("**********************************************************************")
    print("****************************결제 payment()*****************************")
    print("**********************************************************************")

    time.sleep(0.1)
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='ifrmBookStep']")))

    print("**********************************************************************")
    print("******************************매수 선택********************************")
    print("**********************************************************************")
    if ticket_cnt == "1":
        select = Select(wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="PriceRow001"]/td[3]/select'))))
        select.select_by_index(1)
    elif ticket_cnt == "2":
        select = Select(wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="PriceRow002"]/td[3]/select'))))
        select.select_by_index(2)

    driver.switch_to.default_content()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='SmallNextBtnImage']"))).click()

    print("**********************************************************************")
    print("*****************************주문자 확인*******************************")
    print("**********************************************************************")
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='ifrmBookStep']")))
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="YYMMDD"]'))).send_keys('950804')

    driver.switch_to.default_content()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='SmallNextBtnImage']"))).click()

    print("**********************************************************************")
    print("*****************************결제수단선택*******************************")
    print("**********************************************************************")
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='ifrmBookStep']")))

    print("**********************************************************************")
    print("*****************************무통장 선택*******************************")
    print("**********************************************************************")
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="Payment_22004"]/td/input'))).click()

    print("**********************************************************************")
    print("******************************은행 선택********************************")
    print("**********************************************************************")
    select2 = Select(wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="BankCode"]'))))
    select2.select_by_index(1)

    driver.switch_to.default_content()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='SmallNextBtnImage']"))).click()

    wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='ifrmBookStep']")))

    print("**********************************************************************")
    print("******************************전체 선택********************************")
    print("**********************************************************************")
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="checkAll"]'))).click()

    driver.switch_to.default_content()
    #wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="LargeNextBtnImage"]'))).click()

    input("**********************************************************************\n"
          "***********************예매완료됨 엔터를누르면 창을닫음*******************\n"
          "**********************************************************************")

# 부정예매방지 문자
print("**********************************************************************")
print("**************************매크로방지 입력중*****************************")
print("**********************************************************************")
reader = easyocr.Reader(['en'])
capchaPng = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="imgCaptcha"]')))

while capchaPng:
    result = reader.readtext(capchaPng.screenshot_as_png, detail=0)
    capchaValue = result[0].replace(' ', '').replace('5', 'S').replace('0', 'O').replace('$', 'S').replace(',', '') \
        .replace(':', '').replace('.', '').replace('+', 'T').replace("'", '').replace('`', '') \
        .replace('1', 'L').replace('e', 'Q').replace('3', 'S').replace('€', 'C').replace('{', '').replace('-', '')

    # 입력
    #driver.find_element(By.XPATH,'//*[@id="divRecaptcha"]/div[1]/div[3]').click()
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="divRecaptcha"]/div[1]/div[3]'))).click()

    #chapchaText = driver.find_element(By.XPATH,'//*[@id="txtCaptcha"]')
    chapchaText = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="txtCaptcha"]')))
    chapchaText.send_keys(capchaValue)

    #입력완료 버튼 클릭
    #driver.find_element(By.XPATH,'//*[@id="divRecaptcha"]/div[1]/div[4]/a[2]').click()
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="divRecaptcha"]/div[1]/div[4]/a[2]'))).click()

    display = driver.find_element(By.XPATH,'//*[@id="divRecaptcha"]').is_displayed()
    if display:
        # 새로고침
        driver.find_element(By.XPATH,'//*[@id="divRecaptcha"]/div[1]/div[1]/a[1]').click()
    else:
        select()
        break