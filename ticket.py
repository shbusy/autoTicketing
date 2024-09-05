from tkinter import messagebox
from seleniumbase import Driver
from tkinter import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException
import time
import easyocr
import requests
import tkinter.ttk as ttk

window = Tk()
window.title("Ticket")

window.geometry("330x400+1570+600")  # 960x1280+x좌표+y좌표
window.resizable(width=False, height=False)  # 창크기조절

frameData = Frame(window)
frameData.grid(row=0, column=0, sticky="W")

#생년월일
labelBirth = Label(frameData, text="생년월일")
labelBirth.grid(row=0, column=0, sticky=W, padx=5, pady=5)

eBirth = Entry(frameData, width=10)

def clear(event):
    if eBirth.get() == "ex)950101":
        eBirth.delete(0, len(eBirth.get()))

eBirth.bind("<Button-1>", clear)
eBirth.grid(row=0, column=1, sticky=W, padx=5, pady=5)
eBirth.insert(0, "ex)950101")

#공연리스트
labelPlay = Label(frameData, text="공연")
labelPlay.grid(row=1, column=0, sticky=W, padx=5, pady=5)

playsResponse = requests.get(
    '콘서트리스트URL')

playsName = []
playsCode = []

if playsResponse.status_code == 200:
    rs = playsResponse.json()
    playsArr = rs['concert']

    for p in playsArr:
        playsName.append(p['goodsName'])
        playsCode.append(p['goodsCode'])

else:
    print(f"Error: {playsResponse.status_code}")

playList = ttk.Combobox(frameData, height=20, values=playsName, state="readonly")

#날짜
days = []
idx = None
def getDays(event):
    global days, idx
    days = []
    idx = playsName.index(playList.get())

    daysResponse = requests.get(
        '상품정보URL')

    if daysResponse.status_code == 200:
        rs = daysResponse.json()
        daysArr = rs['data']

        for p in daysArr:
            days.append(p['playDate'])
            dayList['values'] = days
    else:
        print(f"Error: {daysResponse.status_code}")

playList.set("선택하세요")
playList.grid(row=1, column=1, padx=5, pady=5)
playList.bind("<<ComboboxSelected>>", getDays)

labelDay = Label(frameData, text="날짜")
labelDay.grid(row=2, column=0, sticky=W, padx=5, pady=5)

dayList = ttk.Combobox(frameData, height=1, state="readonly")
dayList.grid(row=2, column=1, padx=5, pady=5)
dayList.set("")

#매수
labelTicketCnt = Label(frameData, text="매수")
labelTicketCnt.grid(row=3, column=0, sticky=W, padx=5, pady=5)

ticketCntList = []
ticketCntList.insert(1, "1")
ticketCntList.insert(2, "2")

ticketCnt = ttk.Combobox(frameData, height=1, values=ticketCntList, state="readonly")
ticketCnt.grid(row=3, column=1, padx=5, pady=5)
ticketCnt.set("")

driver = wait = birth = play = day = ticket = None

def submit():
    global driver, wait, birth, play, day, ticket, idx

    birth = eBirth.get()
    if not birth:
        messagebox.showwarning("필수값", "생년월일을 입력하세요.")
        return

    try:
        play = playsCode[idx]
    except TypeError:
        messagebox.showwarning("필수값", "공연을 선택하세요.")
        return

    day = dayList.get()
    if not day:
        messagebox.showwarning("필수값", "날짜를 선택하세요.")
        return

    ticket = ticketCnt.get()
    if not ticket:
        messagebox.showwarning("필수값", "티켓 수량을 선택하세요.")
        return

    """print(birth)
    print(play)
    print(day)
    print(ticket_cnt)"""

    labelNotice = Label(frameData, pady=5, text="로그인 완료 후 예매시작버튼을 눌러주세요", fg="blue", font=("Helvetica", 12, "bold"))
    labelNotice.grid(row=5, column=0, columnspan=2)

    driver = Driver()
    driver.get("예매창URL")
    wait = WebDriverWait(driver, 1800)

frameBtn = Frame(window)
frameBtn.grid(row=1, column=0)

# 버튼위젯 생성 padx가변 width고정
btnSubmit = Button(frameBtn, text="전송", command=submit, width=20)
btnSubmit.grid(row=0, column=0, padx=5)
#btnSubmit.pack(side=LEFT, padx=5, pady=5) # GUI에 버튼위젯 포함

def close_window():
    window.destroy()

btnRes = Button(frameBtn, text="예매시작", command=close_window, width=20)
btnRes.grid(row=0, column=1, padx=5)
#btnRes.pack(side=LEFT, padx=5, pady=5) # GUI에 버튼위젯 포함

window.mainloop()

print("**********************************************************************")
print("****************************원하는 구역 입력****************************")
print("**********************************************************************")
BlockNumbers_str = input(
    "숫자를 공백으로 구분해서 입력 ex) 핸드볼: 036 037 035 038 034 039 236 237 235 238 234 239 올림픽홀: RGN003 RGN002 RGN004\n>>>>>>>>> ")
BlockNumbers = BlockNumbers_str.split()

print("**********************************************************************")
print("***************************예매시작시간 대기중***************************")
print("**********************************************************************")

wait.until(EC.visibility_of_element_located((By.XPATH, "//li[text()='" + str(day[-2:]) + "']"))).click()
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

def findSeats():  # 좌석선택

    print("**********************************************************************")
    print("**************************좌석선택 findSeats()**************************")
    print("**********************************************************************")

    while True:
        chk = "N"

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

            if ticket == "1":
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
                            chk = "Y"
                            break

            elif ticket == "2":
                # 빈자리 두개 이상일 때
                if len(seatNs) >= 2:
                    for i in range(len(seatNs) - 1):
                        pos_current = seatNs[i].location_once_scrolled_into_view
                        pos_next = seatNs[i + 1].location_once_scrolled_into_view

                        # 연석일때
                        if pos_current['x'] + seatNs[i].size['width'] + 2 == pos_next['x']:
                            actions = ActionChains(driver)

                            actions.click(seatNs[i])
                            actions.click(seatNs[i + 1])

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
                                chk = "Y"
                                break

            if chk == "Y":
                print("**********************************************************************")
                print("*****************************좌석선택 완료됨1***************************")
                print("**********************************************************************")
                break

            elif chk == "N":
                # 자리가 없을때 전체구역보기 눌러서 구역선택으로 돌아감
                print("**********************************************************************")
                print("**********************자리없음 구역선택으로 되돌아감**********************")
                print("**********************************************************************")
                wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='divSeatBox']"))).click()
                continue

        if chk == "Y":
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
    if ticket == "1":
        select = Select(wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="PriceRow001"]/td[3]/select'))))
        select.select_by_index(1)
    elif ticket == "2":
        select = Select(wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="PriceRow002"]/td[3]/select'))))
        select.select_by_index(2)

    driver.switch_to.default_content()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='SmallNextBtnImage']"))).click()

    print("**********************************************************************")
    print("*****************************주문자 확인*******************************")
    print("**********************************************************************")
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='ifrmBookStep']")))
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="YYMMDD"]'))).send_keys(birth)

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
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="LargeNextBtnImage"]'))).click()

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
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="divRecaptcha"]/div[1]/div[3]'))).click()

    chapchaText = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="txtCaptcha"]')))
    chapchaText.send_keys(capchaValue)

    # 입력완료 버튼 클릭
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="divRecaptcha"]/div[1]/div[4]/a[2]'))).click()

    display = driver.find_element(By.XPATH, '//*[@id="divRecaptcha"]').is_displayed()
    if display:
        # 새로고침
        driver.find_element(By.XPATH, '//*[@id="divRecaptcha"]/div[1]/div[1]/a[1]').click()
    else:
        select()
        break