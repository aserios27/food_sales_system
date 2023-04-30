import os
import sys
import pymysql                  # MySQL데이터베이스를 사용하기 위한 라이브러리 / 2023-02-07
from Filter import UserInput, FindSql, SelOpt, ShowTables, TableCreate, Read, sqlAction

# 데이터베이스 환경변수
config = {                  
    'host' : '127.0.0.1',   # ipv4주소
    'user' : 'root',        # MySQL 계정
    'passwd' : 'root1234',  # MySQL 비밀번호
    'database' : 'test_db', # MySQL 데이터베이스명
    'port' : 3306,          # MySQL 통신코드 리터럴 / 정수값 사용
    'charset' : 'utf8',     # MySQL에서 한글 사용 설정
    'use_unicode' : True    # MySQL에서 한글 사용 설정
    }


# 제품관리 클래스 / 2023-02-17 
class ProdFunc(UserInput) :
    def __init__(self):
        super().__init__()
        
# (1) 제품 생성 매서드 
    def prodCreate(self):
        try :
            while True:
                conn = pymysql.connect(**config)   
                cursor = conn.cursor()        
                print("<<<제품 등록입니다>>>\n등록할 데이터의 ",end='') 
                in_code = super().codeInput() 

                # 코드 입력값이 공백이 아닌 경우   
                if in_code != '' :
                    rows = FindSql('p', 3, in_code).sqlFind() # 조건에 맞는 SQL실행 
                    
                    #1) 같은 제품코드가 존재하는 경우
                    if len(rows) :
                        print("해당 제품코드는 이미 존재하고 있습니다. 다른 제품코드를 입력하세요")
                        continue

                    #2) 같은 제품코드가 존재하지 않는 경우
                    else :
                        iValue = super().userInput() # 사용자 입력값 호출 
                        sql = f"INSERT INTO product(pCode, pName, UnitPrice, discountRate) VALUES('{in_code}','{iValue[0]}', '{iValue[1]}', '{iValue[2]}')" 
                        sqlAction(sql, True) # 2023-03-02 접속함수 실행
                        print("제품등록을 성공했습니다.")
                        break

                # 코드 입력값이 ''인 경우
                else :
                    print("제품 등록을 위해 제품코드를 입력해 주세요")
                    continue
                
        except Exception as e :
            print('오류 : ', e)
            conn.rollback() 

        finally:
            cursor.close()
            conn.close()


    #--------------------------
    # (2) 제품 삭제 매서드
    def prodDelete(self) : 
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()
                Read('p').ReadAll()                
                print("<<<삭제할 제품코드를 입력하세요>>>\n 삭제할 데이터의 ",end='')
                in_code = super().codeInput()             # 제품 코드 입력 함수 호출
                rows_c1 = FindSql('p', 3, in_code).sqlFind() # 조건에 맞는 SQL실행
                
                # 1) 데이터가 존재하는 경우
                if rows_c1 :
                    # 제품 삭제 확인문
                    yesNo = input('삭제하시겠습니까>(y/n) : ')
                    if SelOpt(yesNo).startOpt() == "Y":   
                        sql = f"DELETE FROM product WHERE pCode = '{in_code}'" # 테이블 레코드 삭제 SQL 
                        sqlAction(sql, True) # 2023-03-02 접속함수 실행      
                        print('삭제 성공했습니다.')
                        Read('p').ReadAll() 
                        break
                    elif SelOpt(yesNo).startOpt() == "N":
                        print("<<<삭제를 취소했습니다.>>>")
                        break
                    else:
                        print("<<<잘못 입력했습니다 다시 입력해주세요.>>>")
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
    # (3) 제품 수정 매서드
    def prodUpdate(self) : 
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()
                Read('p').ReadAll()
                print("<<<제품 수정입니다>>>\n수정할 데이터의 ",end='') 
                in_code = super().codeInput() 
                rows_c1 = FindSql('p', 3, in_code).sqlFind()
                if rows_c1 : 
                    print("<<<제품코드 조회결과입니다>>>")
                    ShowTables().showProd(rows_c1)
            
                    # 제품 수정 확인문
                    yesNo = input('수정하시겠습니까>(y/n) : ')
                    if SelOpt(yesNo).startOpt() == "Y": 
                        print("<<<수정할 내용을 입력하세요.>>>")
                        iValue = super().userInput()
                        sql = f"UPDATE product SET pName = '{iValue[0]}', UnitPrice = '{iValue[1]}', discountRate ='{iValue[2]}' WHERE pCode = '{in_code}'"
                        sqlAction(sql, True) # 2023-03-02 접속함수 실행      
                        print("<<<수정을 완료했습니다>>>\n<<<수정 결과입니다>>>")
                        Read('p').ReadAll() 
                        break
                    elif SelOpt(yesNo).startOpt() == "N":
                        print("<<<수정을 취소했습니다.>>>")
                        break
                    else:
                        print('잘못 입력했습니다. 다시 입력해주세요.')
                        continue
                # SELECT 쿼리 실행결과가 없는 경우        
                else : 
                    print('수정할 제품코드가 없습니다.')
                    continue
                
        except Exception as e :
            print('db 연동 실패 : ', e)
            conn.rollback() 
            
        finally:
            cursor.close()
            conn.close()

        
def startProd():
    TableCreate('p')          
    while True:
        os.system('cls')
        print("---제품관리---")
        print("제품      등록 : 1")
        print("제품 목록 조회 : 2")
        print("코드별    조회 : 3")
        print("제품명별  조회 : 4")
        print("제품      수정 : 5")
        print("제품      삭제 : 6")
        print("제품 관리 종료 : 9")
        print("시스템    종료 : 0 ")
        sel = int(input("작업을 선택하세요 : "))
        c0 = ProdFunc()
        if sel == 1 :
            c0.prodCreate()
            os.system("pause")
        elif sel == 2 :
            Read('p').ReadAll()
            os.system("pause")
        elif sel == 3 :
            Read('p').ReadOne('코드')
            os.system("pause")
        elif sel == 4 :
            Read('p').ReadOne('제품명')
            os.system("pause")
        elif sel == 5 :
            c0.prodUpdate()
            os.system("pause")
        elif sel == 6 :
            c0.prodDelete()
            os.system("pause")
        elif sel == 9 :
            print("제품관리를 종료합니다. ")
            os.system("pause")
            os.system('cls')
            break
        elif sel == 0:
            print("시스템을 종료합니다. ") 
            os.system("pause")
            os.system('cls')
            sys.exit(0)
        else :
            print("잘못 선택했습니다. ")
            os.system("pause")
            
if __name__ == "__main__" :
    startProd()