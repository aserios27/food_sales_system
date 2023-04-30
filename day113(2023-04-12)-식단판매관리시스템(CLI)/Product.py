import os
import sys
import pymysql # MySQL데이터베이스를 사용하기 위한 라이브러리 / 2023-02-07
from Filter import UserInput, FindSql, SelOpt, ShowTables, TableReset, Read, sqlAction
from History import HisFunc, BackFunc

# 데이터베이스 환경변수
config = {                  
    'host' : '127.0.0.1',    
    'user' : 'root',         
    'passwd' : 'root1234',   
    'database' : 'test_db4', 
    'port' : 3306,           
    'charset' : 'utf8',      
    'use_unicode' : True     
    }


# 식단관리 클래스 / 2023-02-17 / 2023-03-22 이력 관리 기능 추가
class ProdFunc(UserInput, HisFunc) :
    def __init__(self):
        super().__init__()
        
# (1) 식단 생성 매서드 
    def prodCreate(self):
        try :
            while True:
                conn = pymysql.connect(**config)   
                cursor = conn.cursor()        
                print("<<<식단 등록입니다>>>\n등록할 데이터의 ",end='') 
                in_code = super().codeInput() 

                # 코드 입력값이 공백이 아닌 경우   
                if in_code != '' :
                    rows = FindSql('p', 3, in_code).sqlFind() # 조건에 맞는 SQL실행 
                    
                    #1) 같은 식단코드가 존재하는 경우
                    if len(rows) :
                        print("해당 식단코드는 이미 존재하고 있습니다. 다른 식단코드를 입력하세요")
                        continue

                    #2) 같은 식단코드가 존재하지 않는 경우
                    else :
                        menu_class = super().pclassInput(in_code) # 식단분류값 호출
                        iValue = super().userInput() # 사용자 입력값 호출
                        print("<<<식단 메뉴 등록입니다>>>")
                        iMenu = super().menuInput() # 메뉴 입력값 호출
                        sql = f"INSERT INTO menu_planner(pCode, pClass, pName, unitPrice, discountRate) VALUES('{in_code}', '{menu_class}', '{iValue[0]}', '{iValue[1]}', '{iValue[2]}')" 
                        sqlAction(sql, True) # 2023-03-02 접속함수 실행
                        sql = f"INSERT INTO menu_planner_detail(dCode, dMain, dSoup, dSub1, dSub2, dSub3) VALUES('{in_code}','{iMenu[0]}', '{iMenu[1]}','{iMenu[2]}', '{iMenu[3]}', '{iMenu[4]}')"
                        sqlAction(sql, True) # 2023-03-02 접속함수 실행
                        super().prodHisCreate(in_code, iValue, menu_class) # 2023-03-23 history 테이블 데이터 추가 / 2023-03-26 트리거로 구현
                        super().prodDetailHisCreate(in_code, iMenu) # 2023-03-23 history 테이블 데이터 추가 / 2023-03-26 트리거로 구현
                        print("식단등록을 성공했습니다.")
                        break

                # 코드 입력값이 ''인 경우
                else :
                    print("식단 등록을 위해 식단코드를 입력해 주세요")
                    continue
                
        except Exception as e :
            print('오류 : ', e)
            conn.rollback() 

        finally:
            cursor.close()
            conn.close()


    #--------------------------
    # (2) 식단 삭제 매서드
    def prodDelete(self) : 
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()
                Read('p').readAll()                
                print("<<<삭제할 식단코드를 입력하세요>>>\n 삭제할 데이터의 ",end='')
                in_code = super().codeInput()             
                rows_c1 = FindSql('p', 3, in_code).sqlFind() 
                
                # 1) 데이터가 존재하는 경우
                if rows_c1 :
                    # 식단 삭제 확인문
                    yesNo = input('삭제하시겠습니까>(y/n) : ')
                    os.system('cls')
                    if SelOpt(yesNo).startOpt():
                        super().prodHisDelete(in_code) # 2023-03-23 / 식단 이력 테이블 데이터 추가
                        super().prodDetailHisDelete(in_code) # 2023-03-23 / 메뉴 이력 테이블 데이터 추가
                        BackFunc('단종', in_code)      # 2023-03-29 / 판매 삭제 테이블 데이터 추가
                        sql = f"DELETE FROM menu_planner WHERE pCode = '{in_code}'" # 테이블 레코드 삭제 SQL 
                        sqlAction(sql, True) # 2023-03-02 접속함수 실행      
                        print('삭제 성공했습니다.')
                        Read('p').readAll() 
                        break
                    elif SelOpt(yesNo).select == 'N':
                        print('삭제를 취소합니다.')
                        break
                    else:
                        print('잘못입력했습니다. 다시 입력해주세요.')
                        continue
                        
                # 2) 데이터가 존재하지 않는 경우
                else :
                    print('삭제 실패했습니다.\n입력한 값에 해당하는 데이터가 존재하지 않습니다.')
                    break
                
        except Exception as e :
            print('db 연동 실패 : ', e)
            conn.rollback()  

        finally:
            cursor.close()
            conn.close()


    #--------------------------   
    # (3) 식단 수정 매서드
    def prodUpdate(self) : 
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()
                Read('p').readAll()
                print("<<<식단 수정입니다>>>\n수정할 데이터의 ",end='') 
                in_code = super().codeInput() 
                rows_c1 = FindSql('p', 3, in_code).sqlFind()
                if rows_c1 :
                    os.system('cls') 
                    print("<<<식단코드 조회결과입니다>>>")
                    ShowTables().showProd(rows_c1)
            
                    # 식단 수정 확인문
                    yesNo = input('수정하시겠습니까>(y/n) : ')
                    if SelOpt(yesNo).startOpt(): 
                        print("<<<수정할 내용을 입력하세요.>>>")
                        iValue = super().userInput()
                        sql = f"UPDATE menu_planner SET pName = '{iValue[0]}', UnitPrice = '{iValue[1]}', discountRate ='{iValue[2]}' WHERE pCode = '{in_code}'"
                        sqlAction(sql, True) # 2023-03-02 접속함수 실행
                        super().prodHisUpdate(in_code) # 2023-03-23 / 이력관리 테이블 추가       
                        print("수정을 완료했습니다\n수정 결과입니다")
                        Read('p').readAll() 
                        break
                    elif SelOpt(yesNo).select == 'N':
                        print("수정을 취소했습니다.")
                        break
                    else:
                        print('잘못입력했습니다. 다시 입력해주세요.')
                        continue
  
                # SELECT 쿼리 실행결과가 없는 경우        
                else : 
                    print('수정할 식단이 없습니다.')
                    continue
                
        except Exception as e :
            print('db 연동 실패 : ', e)
            conn.rollback() 
            
        finally:
            cursor.close()
            conn.close()
    
    
    # (4) 식단 메뉴 수정 매서드
    def prodDetailUpdate(self) : 
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()
                Read('m').readAll()
                print("<<<식단메뉴 수정입니다>>>\n수정할 데이터의 ",end='') 
                in_code = super().codeInput() 
                rows_c1 = FindSql('m', 3, in_code).sqlFind()
                if rows_c1 :
                    os.system('cls') 
                    print("<<<식단메뉴 조회결과입니다>>>")
                    ShowTables().showMenu(rows_c1)
            
                    # 식단 수정 확인문
                    yesNo = input('수정하시겠습니까>(y/n) : ')
                    if SelOpt(yesNo).startOpt(): 
                        print("<<<수정할 내용을 입력하세요.>>>")
                        iMenu = super().menuInput() # 메뉴 입력값 호출
                        sql = f"UPDATE menu_planner_detail SET dMain = '{iMenu[0]}', dSoup = '{iMenu[1]}', dSub1 = '{iMenu[2]}', dSub2 = '{iMenu[3]}', dSub3 = '{iMenu[4]}' WHERE dCode = '{in_code}'"
                        sqlAction(sql, True) # 2023-03-02 접속함수 실행
                        super().prodDetailHisUpdate(in_code) # 2023-03-23 / 메뉴 이력 테이블 데이터 추가      
                        print("수정을 완료했습니다\n수정 결과입니다")
                        Read('m').readAll() 
                        break
                    elif SelOpt(yesNo).select == 'N':
                        print("수정을 취소했습니다.")
                        break
                    else:
                        print('잘못입력했습니다. 다시 입력해주세요.')
                        continue
  
                # SELECT 쿼리 실행결과가 없는 경우        
                else : 
                    print('수정할 식단메뉴가 없습니다.')
                    continue
                
        except Exception as e :
            print('db 연동 실패 : ', e)
            conn.rollback() 
            
        finally:
            cursor.close()
            conn.close()        
    
    
    # (5) 2023-03-29 식단 삭제 정보 조회 매서드                         
    def abolitionProdRead(self) :
        print(f"단종된 식단 조회")
        sql = "SELECT pCode, pClass, pName, unitPrice, discountRate FROM menu_planner_history WHERE Event = 'Delete'"
        rows = sqlAction(sql)
        ShowTables().showProd(rows)
        while True:
            yesNo = input('식단 메뉴도 조회하시겠습니까>(y/n) : ')
            os.system('cls')
            if SelOpt(yesNo).startOpt(): 
                self.abolitionProdDetailRead()
                break
            elif SelOpt(yesNo).select == 'N':
                break
            else:
                print('잘못입력했습니다. 다시 입력해주세요.')
                continue
        
    # 수정 필요    
    # (6) 2023-03-29 식단 삭제 메뉴 정보 조회 매서드                 
    def abolitionProdDetailRead(self) :
        print(f"단종된 식단메뉴 조회")
        sql = "SELECT dCode, dMain, dSoup, dSub1, dSub2, dSub3 FROM menu_planner_detail_history WHERE dEvent = 'Delete'"
        rows = sqlAction(sql)
        ShowTables().showMenu(rows)

        
def startProd():        
    while True:
        os.system('cls')
        print("-------식단 관리-------")
        print("식단          등록 : 1 ")
        print("식단   목록   조회 : 2 ")
        print("코드별        조회 : 3 ")
        print("식단명별      조회 : 4 ")
        print("식단 삭제정보 조회 : 5 ")
        print("식단          수정 : 6 ")
        print("식단          삭제 : 7 ")
        print("식단  테이블  리셋 : 8 ")
        print("식단   관리   종료 : 9 ")
        print("시스템        종료 : 0 ")
        sel = input("작업을 선택하세요 : ")
        os.system('cls')
        c0 = ProdFunc()
        if sel == '1' :
            c0.prodCreate()
            os.system("pause")
        elif sel == '2' :
            Read('p').readAll()
            os.system("pause")
        elif sel == '3' :
            while True:
                print("---식단 정보 코드별조회---")
                print("식단     정보 조회   : 1  ")
                print("식단메뉴 정보 조회   : 2  ")
                print("뒤로          가기   : 0  ")  
                sel = input("작업을 선택하세요 : "  )
                os.system('cls')
                if sel == '1':
                    Read('p').readOne('코드')
                    os.system("pause")
                    os.system('cls')
                elif sel == '2':
                    Read('m').readOne('코드')
                    os.system("pause")
                    os.system('cls')
                elif sel == '0':
                    os.system('cls')
                    break
                else :
                    print("잘못 선택했습니다. ")
                    os.system("pause")
        elif sel == '4' :
            Read('p').readOne('식단명')
            os.system("pause")
        elif sel == '5' :
            while True:
                print("----식단 삭제정보 조회----")
                print("식단     정보 조회   : 1  ")
                print("식단메뉴 정보 조회   : 2  ")
                print("뒤로          가기   : 0  ")  
                sel = input("작업을 선택하세요 : "  )
                os.system('cls')
                if sel == '1':
                    c0.abolitionProdRead()
                    os.system("pause")
                    os.system('cls')
                elif sel == '2':
                    c0.abolitionProdDetailRead()    
                    os.system("pause")
                    os.system('cls')
                elif sel == '0':
                    os.system('cls')
                    break
                else :
                    print("잘못 선택했습니다. ")
                    os.system("pause")
        elif sel == '6' :
            while True:
                print("------식단 정보 수정------")
                print("식단     정보 수정   : 1  ")
                print("식단메뉴 정보 수정   : 2  ")
                print("뒤로          가기   : 0  ")  
                sel = input("작업을 선택하세요 : "  )
                os.system('cls')
                if sel == '1':
                    c0.prodUpdate()
                    os.system("pause")
                    os.system('cls')
                elif sel == '2':
                    c0.prodDetailUpdate()    
                    os.system("pause")
                    os.system('cls')
                elif sel == '0':
                    os.system('cls')
                    break
                else :
                    print("잘못 선택했습니다. ")
                    os.system("pause")
        elif sel == '7' :
            c0.prodDelete()
            os.system("pause")
        elif sel == '8' :
            TableReset('p').tableReset()
            os.system("pause")
        elif sel == '9' :
            print("식단관리를 종료합니다. ")
            os.system("pause")
            os.system('cls')
            break
        elif sel == '0':
            print("시스템을 종료합니다. ") 
            os.system("pause")
            os.system('cls')
            sys.exit(0)
        else :
            print("잘못 선택했습니다. ")
            os.system("pause")
            
if __name__ == "__main__" :
    startProd()