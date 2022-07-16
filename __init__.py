# 실행은 이 파일로만 한다.
# from (파일 위치) import 클래스 명 (여러개일 경우 *)
    # import ui.ui as eee 형태로 쓸 수도 있음

from ui.ui import Ui_class

class Main():
    def __init__(self):
        print("실행할 메인 클래스")

        Ui_class()

if __name__=="__main__":
    #위의 것은 실행 용도의 파일이라고 지정하는 것.
    # 즉 실행 용 파일이 여러 개이면 명시적으로 한번 더 지정해준다.
    Main()
    
    import os

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import QTest

from config.errorCode import *

from config.kiwoomType import *

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        print("kiwoom 클래스 입니다")

        self.realType = RealType()



        ####################이벤트루프 모듈#################
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()
        ###################

        ###변수모음###
        self.account_num=None
        #######

        ####스크린 번호##
        self.screen_my_info="2000"
        self.screen_calculation_stock="4000"

        ###실시간 스크린 번호
        self.screen_real_stock = "5000" #종목별 할당할 스크린 번호
        self.screen_meme_stock = "6000" #종목별 할당할 주문용 스크린 번호

        self.screen_start_stop_real = "1000"

        ############계좌관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5

        ##########딕셔너리

        self.portfolio_stock_dict = {}
        self.account_stock_dict={}
        self.not_account_stock_dict = {}
        self.jango_dict = {}

        ### 종목 분석 용
        self.calcul_data=[]






        self.get_ocx_instance()
        self.event_slots()
        self.real_event_slots()



        self.signal_login_CommConnect()
        self.get_account_info()
        # self.detail_account_info() # 예수금을 가져오기.
        # self.detail_account_mystock()
        self.not_concluded_account() #미체결 가져오기
        # self.get_code_list_by_market()
        # self.calculator_fnc() # 종목 분석용 임시용으로 / 주식창이 끝나면 수행하는 것이므로

        self.read_code() #저장된 것 불러옴
        self.screen_number_setting()


        #조건 검색 - send Real Reg 등록

        self.dynamicCall("SetRealReg(QString,QString,QString,QString)",self.screen_start_stop_real, '', self.realType.REALTYPE['장시작시간']['장운영구분'], "0")

        for code in self.portfolio_stock_dict.keys():
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            fids = self.realType.REALTYPE['주식체결']['체결시간'] #1틱봉이 생길때마다
            self.dynamicCall("SetRealReg(QString,QString,QString,QString)", screen_num, code, fids, "1") #최초등록이 아니므로 "1"
            print("실시간 등록 코드 : %s, 번호: %s" % (code,fids))

        #아래 함수로 응용프로그램을 제어할 수 있음

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

#이벤트 슬롯으로 정보 받도록할것
    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot) #모든 tr요청은 여기서만!!
        #티알 요청에[ 대한 슬롯을 티알데이터_슬롯으료 받음))


#실시간 정보를 가지고 오도록 하는 것
    def real_event_slots(self):
        self.OnReceiveRealData.connect(self.realdata_slot)




    def login_slot(self, errCode):
        print(errors(errCode))

        self.login_event_loop.exit()

    def signal_login_CommConnect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

#계좌번호가져오기
    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCNO")

        self.account_num=account_list.split(';')[0]
        print("나의 보유 계좌번호 %s" %self.account_num)


    def detail_account_info(self):
        print("예수금 요청 부분")
        # 1. Open API 조회 함수 입력값을 설정합니다.
        self.dynamicCall("SetInputValue(String, String)","계좌번호",self.account_num)
        self.dynamicCall("SetInputValue(String, String)","비밀번호","0000")
        self.dynamicCall("SetInputValue(String, String)","비밀번호입력매체구분","00")
        self.dynamicCall("SetInputValue(String, String)","조회구분","2")
        # 2. Open API 조회 함수를 호출해서 전문을 서버로 전송합니다.
        # "내가 지은 요청이름" "tr번호" "PRETEXT", "화면번호"(screen Number)
        self.dynamicCall("CommRqData(String, String,int,String)","예수금상세현황요청","opw00001","0",self.screen_my_info)

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()

    def detail_account_mystock(self, sPrevNext="0"):#sPervNext
        print("계좌평가 잔고내역 요청")
        self.dynamicCall("SetInputValue(String, String)","계좌번호",self.account_num)
        self.dynamicCall("SetInputValue(String, String)","비밀번호","0000")
        self.dynamicCall("SetInputValue(String, String)","비밀번호입력매체구분","00")
        self.dynamicCall("SetInputValue(String, String)","조회구분", "2")
        self.dynamicCall("CommRqData(String, String,int,String)","계좌평가잔고내역요청","opw00018",sPrevNext,self.screen_my_info)

        self.detail_account_info_event_loop.exec_()


    #
    def not_concluded_account(self, sPrevNext="0"):
        print("미체결 요청")

        self.dynamicCall("SetInputValue(QString, QString)","계좌번호",self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)","체결구분","1") #1:미채결
        self.dynamicCall("SetInputValue(QString, QString)","매매구분","0") #0 : 매수매도 전부
        self.dynamicCall("CommRqData(QString,QString,int,QString)","실시간미체결요청","opt10075",sPrevNext,self.screen_my_info)
        self.detail_account_info_event_loop.exec_()

    # #요청을 아래로 받을 것임
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        '''

        :param sScrNo:스크린 번호
        :param sRQName:내가 요청 시 지은 이름
        :param sTrCode: 요청 아이디 티알 코드
        :param sRecordName:사용안함
        :param sPrevNext:다음페이지 있는지
        :return:
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(string, string, int, string)",sTrCode, sRQName, 0, "예수금")
            # print("예수금 %s" % type(deposit))
            print("예수금 %s" % int(deposit))

            # self.use_money = int(deposit) * self.use_money_percent # 예수금 중 투자금 만큼 곱하는 것 100000*0.5
            # self.use_money = sel
            # f.use_money / 4
            #
            # int(deposit)#형변환 원래는 문자열 --> 숫자로 바꿔줌
            # #GetCommData로 데이터 꺼내온다 (뭔가 이벤트 루프에 걸려있는 데이터를 꺼내옴

            ok_deposit = self.dynamicCall("GetCommData(string, string, int, string)", sTrCode, sRQName, 0, "출금가능금액")
            print("출금가능금액 %s" % int(ok_deposit))

            self.detail_account_info_event_loop.exit()

        if sRQName == "계좌평가잔고내역요청":
            #총 매입금과 총 수익률 궁금쓰
            total_buy_money = self.dynamicCall("GetCommData(string, string, int, string)",sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result=int(total_buy_money)

            print("총매입금액 %s" %total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(string, string, int, string)",sTrCode, sRQName, 0, "총수익률(%)")
            total_profit_loss_rate_result=float(total_profit_loss_rate)

            print("총수익률(%%) %s" %total_profit_loss_rate_result)

            rows =self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                code = code.strip()
                # "A2309" [1:] == "2309"
                # "A2309" [:1] == "A"

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                #dkfna ryddbeg .strip()
                stock_quantity=self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                #"000000010"와 같이 나오므로 int 안에 넣어주면 됨
                buy_price=self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                learn_rate=self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                current_price=self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                total_chegual_price=self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                possible_quantity=self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")

                # 이 값들의 계산을 편리하게 하기위해 딕셔너리로 만듬

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})

                code_nm = code_nm.strip()
                stock_quantity=int(stock_quantity.strip())
                buy_price=int(buy_price.strip())
                learn_rate=float(learn_rate.strip()) #소숫점이므로 플로트
                current_price=int(current_price.strip())
                total_chegual_price=int(total_chegual_price.strip())
                possible_quantity=int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt += 1
                #20개 까지만 가능함 --> sPrevNext 를 이용해야 함 (TRDATA sLOT 확인)

            print("계좌에 가지고 있는 종목 %s"% self.account_stock_dict)
            print("계좌에 가지고 있는 종목 수 %s"% cnt)

            if sPrevNext == "2":#2로 된 값이 위로 올라감! <-- 다음페이지 없으면 0아니면 ""
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_info_event_loop.exit()
            #self.detail_account_info_event_loop.exit()

            # 계좌평가 잔고 내역 중 아래 종목별로 값을 가져와야 함

        elif sRQName == "실시간미체결요청":

            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                #dkfna ryddbeg .strip()
                order_status=self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태")
                order_quantity=self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                #"000000010"와 같이 나오므로 int 안에 넣어주면 됨
                order_price=self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                order_gubun=self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분")
                not_quantity=self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                ok_quantity=self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}

                #nasd = self.not_account_stock_dict[order_no]
                #nasd.update ~ 로 바꿔서 쓰기 가능



                self.not_account_stock_dict[order_no].update({"종목번호":code})
                self.not_account_stock_dict[order_no].update({"종목명":code_nm})
                self.not_account_stock_dict[order_no].update({"주문번호" :order_no})
                self.not_account_stock_dict[order_no].update({"주문상태" :order_status })
                self.not_account_stock_dict[order_no].update({"보유수량" : order_quantity})
                self.not_account_stock_dict[order_no].update({"주문가격" :order_price})
                self.not_account_stock_dict[order_no].update({"주문구분" :order_gubun})
                self.not_account_stock_dict[order_no].update({"미체결수량" :not_quantity })
                self.not_account_stock_dict[order_no].update({"체결량" :ok_quantity})

                print("미체결 종목 :%s " % self.not_account_stock_dict[order_no])
            self.detail_account_info_event_loop.exit()

        elif "주식일봉차트조회" == sRQName:

            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("%s 주식일봉차트조회" % code)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print("데이터 일수 %s" % cnt)

            # data = self.dynamicCall("GetCommDataEx(QString,QString)", sTrCode,sRQName)
            # 위 함수를 사용하면 600일 치를 한번에 가져오는데 아래 처럼 형식을 가져온다 따라서, 우리는 아래 적은 코드처럼 작성한다.
            # [[ '', 'ㅕㄴ재가','거래량','거래대음','날짜 ~~~

            for i in range(cnt):
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                data.append("") # 빈값을 넣는 이유는
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())

            print(self.calcul_data)


            if sPrevNext == "2":
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)

            else:

                print("총 일수 %s" % len(self.calcul_data))

                pass_success = False #체크 값을 기본 값으로 두고 트루 여부에 따라 계속 진행

                # 120일 이평선을 그릴만큼 데이터가 있는지 체크
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False
                else:
                    #120일 이상되면,

                    total_price=0
                    for value in self.calcul_data[:120]: #나오는 ㅇ값은 [오늘,하루전,하루하루전, ..... 120일전]
                        total_price += int(value[1]) # 종가기준이 됨

                    moving_average_price = total_price / 120
                    #오늘자 주가가 120일 이평선에 걸쳐있는지 확인

                    bottom_stock_price = False
                    check_price= None

                    if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(self.calcul_data[0][6]):
                        #오늘앞의 [0]  일자의 저가가 이평선 보다 낮아야 하고 , 고가 [6] 보다 높아야 함
                        print("오늘 주가 120이평선에 걸쳐 있는 것 확인")
                        bottom_stock_price = True
                        check_price=int(self.calcul_data[0][6])

                    # 과거 일봉들이 120일 이평선보다 밑에 있는지 확인
                    # 그렇게 확인 후 일봉이 120일 이평선보다 위에 있으면 계산 진행

                    prev_price = None #과거의 일봉 저가
                    if bottom_stock_price == True:
                        moving_average_price_prev = 0
                        print_top_moving = False

                        idx = 1
                        while True:

                            if len(self.calcul_data[idx:]) < 120: #120일치가 있는지 계속 확인
                                print("120일치가 없음")
                                break

                            total_price = 0
                            for value in self.calcul_data[idx:120+idx]: #idx가 특정일 부터 예를 들면 0~120 표기
                                total_price += int(value[1])
                            moving_average_price_prev = total_price / 120

                            if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 20:
                                print("20일 동안 주가가 120일 이평선과 같거나 위에 있으면 조건 통과 못함")
                                price_top_moving = False
                                break

                            elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx > 20: #7은 저가
                                print("120일 이평선 위에 있는 일봉 확인됨")
                                price_top_moving = True
                                prev_price = int(self.calcul_data[idx][7])
                                break

                            idx += 1

                            #해당부분 이평선이 가장 최근 일자의 이평선 가격보다 낮은 지 확인
                        if price_top_moving == True:
                            if moving_average_price > moving_average_price_prev and check_price > prev_price:
                                print("포착된 이평선의 가격이 오늘자(최근일자) 이평선 가격보다 낮은 것 확인됨")
                                print("포착된 부분의 일봉 저가가 오늘자 일봉의 고가보다 낮은지 확인됨")
                                pass_success = True


                if pass_success == True:
                    print("조건부 통과됨")

                    code_nm = self.dynamicCall("GetMasterCodeName(Qstring)",code)

                    f = open("files/condition_stock.txt","a",encoding="utf8") #"a"는 이어씀 , "w"는 덮어씀
                    f.write("%s\t%\t%\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()

                elif pass_success == False:
                    print("조건부 통과 못")

                self.calcul_data.clear()
                self.calculator_event_loop.exit()




    def get_code_list_by_market(self, market_code): #시장에 있는 코드를 가지고 오는 것
        '''
        종목 코드를 반환
        :param market_code:
        :return:
        '''

        code_list = self.dynamicCall("GetCodeListByMarket (QString)", market_code)
        code_list = code_list.split(";")[:-1] # ; 기준으로 짜르되 마지막 글자 하나는 지우는 것
        # "109012;239482;2319;0239123;" --> -1은 마지막 "" 이 남는다 따라서 없애기
        return code_list

    def calculator_fnc(self):
        '''
        종목 분석 실행용 함수
        :return:
        '''

        code_list = self.get_code_list_by_market("10")
        print("kosdaq 갯수 %s" % len(code_list))

        for idx, code in enumerate(code_list):#idx index의 자릿수 [a, b] a는 0번째 인덱스, ㅇㅇ
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock) # DisconnectRealdata : 스크린 번호를 끊어주는 것

            print("%s / %s : KOSDAQ Stock code : %s is updating... " % (idx+1, len(code_list), code))

            self.day_kiwoom_db(code=code)


    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):

        # QTest.qWait(3600)
        QTest.qWait(3600)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")  # 1:수정주가

        if date != None: #빈 값인 경우는 오늘 날짜 따라서, none 일 경우 날짜를 입력해야 함
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)

        self.calculator_event_loop.exec_()







    def read_code(self):
        if os.path.exists("files/condition_stock.txt"): #운영체재 내 파일이 존재하는 지 :: 있으면 True / 없으면 False
            f = open("files/condition_stock.txt","r",encoding="utf8") #r은 읽는다는 것

            lines = f.readlines()
            for line in lines: #한줄씩 포문 돌리기
                if line != "": #라인이 비어있지 않으면
                    ls = line.split("\t")        # f.write("%s\t%\t%\n" % 분리 시ㅕ줌 print(ls) 하면 결과 확인 가능
                    # print("Debug")
                    # print(ls)
                    stock_code = ls[0]
                    stock_name = ls[1]
                    # print("Debug")
                    # print(ls[2])
                    stock_price = int(ls[2].split("\n")[0])  #스플릿해서 \n을 떼내고 앞에것 [0]만 가져옴
                    stock_price = abs(stock_price)

                    self.portfolio_stock_dict.update({stock_code:{"종목명":stock_name, "현재가":stock_price}})
                    #{"2090932":["종목명":"삼성","현재가":"2000"}, "091092":{"종목명" ~~
            f.close() #메모리 잡아먹으니 종료해둠
            print(self.portfolio_stock_dict)


    def screen_number_setting(self ):

        #겹치는 종목이 있는지 확인
        screen_overwrite  = []

        # 계좌평가 잔고내역 종목들
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #미체결에 있는 종목돌
        for order_number in self.not_account_stock_dict.keys():
            code = self.net_account_stock_dict[order_number]['종목코드']

            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #포트폴리오 담겨있는 종목들
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #스크린번호 할당
        cnt = 0
        for code in screen_overwrite:

            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            if(cnt % 50) == 0:
                temp_screen += 1 #"5000" --> "5001" 스크린번호 하나에 매매 내역 100개만 가능한데, 여기선 50개 기준으로 넘긴다다
                self.screen_real_stock = str(temp_screen)

            if(cnt % 50) == 0:
                temp_screen += 1
                self.screen_meme_stock = str(meme_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({"스크린번호":str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호":str(self.screen_meme_stock)})

            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({code: {"스크린번호":str(self.screen_real_stock),"주문용스크린번호":str(self.screen_meme_stock)}})

            cnt += 1
        print(self.portfolio_stock_dict)

    #실시간 데이터 받아오는 함수 만들기
    def realdata_slot(self,sCode,sRealType,sRealData):

        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']
            value = self.dynamicCall("GetCommRealData(QString, int)",sCode, fid)

            if value == '0':
                print ("장 시작 전")

            elif value == '3':
                print ("Market Started")

            elif value == "2":
                print ("Market Closing, simultaneous bids and offers ")

            elif value == "4":
                print ("3:30 Market Closed")

        elif sRealType == "주식체결":
            a = self.dynamicCall("GetCommRealData(QSring, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간'])
            b = self.dynamicCall("GetCommRealData(QSring, int)", sCode, self.realType.REALTYPE[sRealType]['현재가'])
            b = abs(int(b))

            c = self.dynamicCall("GetCommRealData(QSring, int)", sCode, self.realType.REALTYPE[sRealType]['전일대비']) #전일대비 상승률/하락률
            c = abs(int(c))

            d = self.dynamicCall("GetCommRealData(QSring, int)", sCode, self.realType.REALTYPE[sRealType]['등락율'])
            d = float(d)

            e = self.dynamicCall("GetCommRealData(QSring, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매도호가'])
            e = abs(int(e))

            f = self.dynamicCall("GetCommRealData(QSring, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매수호가'])
            f = abs(int(f))

            g = self.dynamicCall("GetCommRealData(QSring, int)", sCode, self.realType.REALTYPE[sRealType]['거래량'])
            g = abs(int(g))

            h = self.dynamicCall("GetCommRealData(QSring, nt)", sCode, self.realType.REALTYPE[sRealType]['누적거래량'])
            h = abs(int(h))

            i = self.dynamicCall("GetCommRealData(QSring, int)", sCode, self.realType.REALTYPE[sRealType]['고가'])
            i = abs(int(i))

            j = self.dynamicCall("GetCommRealData(QSring, int)", sCode, self.realType.REALTYPE[sRealType]['시가'])
            j = abs(int(j))

            k = self.dynamicCall("GetCommRealData(QSring, int)", sCode, self.realType.REALTYPE[sRealType]['저가'])
            k = abs(int(k))

            if sCode not in self.portfolio_stock_dict:
                self.portfolio_stock_dict.update({sCode:{}})

            self.portfolio_stock_dict[sCode].update({"체결시간": a})
            self.portfolio_stock_dict[sCode].update({"현재가": b})
            self.portfolio_stock_dict[sCode].update({"전일대비": c})
            self.portfolio_stock_dict[sCode].update({"등락율": d})
            self.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
            self.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
            self.portfolio_stock_dict[sCode].update({"거래량": g})
            self.portfolio_stock_dict[sCode].update({"누적거래량": h})
            self.portfolio_stock_dict[sCode].update({"고가": i})
            self.portfolio_stock_dict[sCode].update({"시가": j})
            self.portfolio_stock_dict[sCode].update({"저가": k})

            print(self.portfolio_stock_dict[sCode])


            #계좌잔고평가내역에 있고, 오늘 산 잔고에는 없을 경우
            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
                print("%s %s" % ("신규매도를 한다", sCode))


            elif sCode in self.jango_dict.keys():
                print("%s %s" % ("신규매도를 한다2", sCode))

            # 등락률이 2% 이상이고 오늘 산 잔고에 없을 경우
            elif d > 2.0 and sCode not in self.jango_dict:
                print("%s %s" %("신규매수를 한다", sCode))

            not_meme_list = list(self.not_account_stock_dict) #매매 갯수가 변화되어 에러가 나지 않도록 복사함
            for order_num in not_meme_list:
                code = self.not_account_stock_dict[order_num]["종목코드"]
                meme_price = self.not_account_stock_dict[order_num]["주문가격"]
                not_quantity = self.not_account_stock_dict[order_num]["미체결수량"]
                meme_gubun = self.not_account_stock_dict[order_num]["매도수구분"]

                if meme_gubun == "매수" and not_quantity > 0 and e > meme_price:
                    print("%s %s" % ("매수취소 한다", sCode))

                elif not_quantity == 0: #미체결이 0이면 데이터를 지워주는게 좋음
                    del self.not_account_stock_dict[order_num]
