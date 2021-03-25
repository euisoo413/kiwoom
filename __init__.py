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