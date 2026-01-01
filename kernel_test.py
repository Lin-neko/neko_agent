from Nkernel import NekoAgentKernel
a = NekoAgentKernel()
a.main_loop(str(input("给neko下达命令:")))
exit = None
while exit != "y" :
    exit = str(input("exit? (y/n)"))
    if exit != "n" :
        print(f'任务完成,共计{a.runtime + 1}步')
    else :
        a.feedback = ""
        a.main_loop(str(input("追加命令:")))
