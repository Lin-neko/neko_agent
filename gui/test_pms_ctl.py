import sys
from PyQt6.QtWidgets import QApplication
from neko_pms_ctl import NekoPMS

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_app = NekoPMS()
    res = test_app.file_write_check("123")
    res2 = test_app.file_read_check("1")
    res3 = test_app.cmd_exec_check("ls")
    res4 = test_app.popen_check("qwer")
    print(f"Result: {res} \n {res2} \n {res3} \n {res4}")