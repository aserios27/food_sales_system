import os
import sys
from Product import startProd
from Sales import startSale
from DataManage import startData
from Filter import TableCreate

def manageSys():
    TableCreate('p'); TableCreate('s')          
    while True:
        os.system('cls')
        print("---관리 시스템 실행---")
        print("제품 관리 실행  : 1 ")
        print("판매 관리 실행  : 2 ")
        print("데이터관리 실행 : 3 ")
        print("서비스     종료 : 0 ")
        sys_sel = input("작업을 선택하세요 : ")
        if sys_sel == '1':
            startProd()
        elif sys_sel == '2':    
            startSale()
        elif sys_sel == '3':
            startData()
        elif sys_sel == '0':
            print("시스템을 종료합니다. ") 
            os.system("pause")
            os.system('cls')
            sys.exit(0)
        else :
            print("잘못 선택했습니다. ")
            os.system("pause")
        
            
if __name__ == "__main__" :
    manageSys()
    