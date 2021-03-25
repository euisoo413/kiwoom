

#위의 것은 파이썬 실행을 위해

from kiwoom.kiwoom import *
from PyQt5.QtWidgets import *
import sys

class Ui_class():
    def __init__(self):
        print("UI_class입니다")

        #Qapplication 은 ui 실행을 위해(변수 등을) 초기화 시켜즌ㄴ 것
        self.app=QApplication(sys.argv)
        #어떤 파일을 ( ) 안에 넣을지에 대해 ~
        #리스트 형태로 잡혀있는 인자들을
        #sys.argv = ['파일 경로' 등등] 으로 들어가 있음

        self.kiwoom = Kiwoom()
        self.app.exec_()
        # print(self.app)
        # Kiwoom()
        #이벤트 루프를 뜻함. // 이벤트 루프를 종료시켜주지 않는 이상 다음 코드 실행 불가
        # self.app.exec_()