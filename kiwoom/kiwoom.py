from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        print("kiwoom 클래스 입니다")

        ####################이벤트루프 모듈#################
        self.login_event_loop = None
        ###################

        ###변수모음###
        self.account_num=None
        #######


        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_CommConnect()
        self.get_account_info()
        self.detail_account_info()


        #아래 함수로 응용프로그램을 제어할 수 있음

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

#이벤트 슬롯으로 정보 받도록할것
    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)
        #티알 요청에[ 대한 슬롯을 티알데이터_슬롯으료 받음))

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
        print("나의 보유 계좌번호 %s" % self.account_num)


    def detail_account_info(self):
        print("예수금 요청 부분")
        # 1. Open API 조회 함수 입력값을 설정합니다.
        self.dynamicCall("SetInputValue(String, String)","계좌번호",self.account_num)
        self.dynamicCall("SetInputValue(String, String)","비밀번호","0000")
        self.dynamicCall("SetInputValue(String, String)","비밀번호입력매체구분","00")
        self.dynamicCall("SetInputValue(String, String)","조회구분"	,  "2")
        # 2. Open API 조회 함수를 호출해서 전문을 서버로 전송합니다.
        # "내가 지은 요청이름" "tr번호" "PRETEXT", "화면번호"(screen Number)
        self.dynamicCall("CommRqData(String, String,int,String)","예수금상세현황요청","opw00001","0","2000")

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
            print("예수금 %s" % deposit)
            #GetCommData로 데이터 꺼내온다 (뭔가 이벤트 루프에 걸려있는 데이터를 꺼내옴