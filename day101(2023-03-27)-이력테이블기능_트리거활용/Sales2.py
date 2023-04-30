import os
import sys
import pymysql                  # MySQL데이터베이스를 사용하기 위한 라이브러리 / 2023-02-07
from Filter2 import UserInput, FindSql, SelOpt, ShowTables, TableReset, Read, sqlAction, fmt

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


# 판매 관리 클래스 / 2023-02-17 
class SaleFunc(UserInput) :
    def __init__(self):
        super().__init__()
# (1) 판매기록 등록 매서드      
    def saleCreate(self) :
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()        
                print("<<<판매기록 등록입니다>>>\n등록할 데이터의 ",end='')
                in_code = super().codeInput() 
                rows_c1 = FindSql('p', 3, in_code).sqlFind()
                # 코드 입력값이 공백이 아닌 경우 
                if in_code != '' :         
                    # 1) product 테이블에 해당 제품코드의 상품이 존재하지 않는 경우            
                    if len(rows_c1) == 0:
                        iValue = super().userInput() # 사용자 입력 값 호출
                        sql = f"INSERT INTO product2(pCode, pName, UnitPrice, discountRate) VALUES('{in_code}','{iValue[0]}', '{iValue[1]}', '{iValue[2]}')" 
                        sqlAction(sql, True)
                        print("제품등록을 성공했습니다.")
                        break

                    # 2) product 테이블에 해당 제품코드의 상품이 존재하는 경우
                    else :
                        qty = super().qtyInput() # 제품 가격 출력 / 2023-02-08 / ### <요구사항-1> 반영 ###
                        sql = f"INSERT INTO sales2(sCode, Qty, Amt) VALUES('{in_code}','{qty}', '{getPrice(in_code, qty)}')" 
                        sqlAction(sql, True) # 2023-03-02 접속함수 실행
                        print("판매기록 등록을 성공했습니다.")
                        break

                # SQL조회 결과가 없는 경우
                else :
                    print("판매기록이 없습니다.")
                    continue
                
        except Exception as e :
            print('오류 : ', e)
            conn.rollback()

        finally:
            cursor.close()
            conn.close()


    #--------------------------
    # (2) 판매기록 삭제 매서드
    def saleDelete(self) : 
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()  
                print("<<<판매기록 삭제합니다>>>")
                Read('s').readAll() 
                print('삭제할 데이터의 ',end='') 
                in_code = super().codeInput() 
                rows = FindSql('s', 3, in_code).sqlFind()
                # 1) 제품코드가 존재하는 경우
                if rows :
                    os.system('cls') 
                    print("<<<선택한 제품코드의 판매기록 목록 조회입니다>>>")
                    ShowTables().showSale(rows)
                    print('삭제할 데이터의 ',end='')
                    in_no = super().noInput()
                    rows1 = FindSql('s', 2, in_no).sqlFind()
                    # 1-1) 제품코드가 존재하면서 No가 존재하는 경우
                    if rows1:
                        # 판매 삭제 확인문
                        while True:
                            yesNo = input('삭제하시겠습니까>(y/n) : ')
                            if SelOpt(yesNo).startOpt() and len(rows1) != 0: 
                                sql = f"DELETE FROM sales2 WHERE seqNo = '{in_no}'"
                                sqlAction(sql, True) # 2023-03-02 접속함수 실행         
                                print('삭제 성공했습니다.')
                                Read('s').readAll()
                                break
                            # 판매 확인문 취소 입력
                            elif SelOpt(yesNo).startOpt() and len(rows1) == 0:
                                print("<<<조회한 목록에 입력한 No가 존재하지 않습니다.>>>")
                                os.system("pause")
                                continue
                            else:
                                print("<<<삭제를 취소했습니다.>>>")
                                break
                        break
                            
                    # 1-2) 제품코드가 존재하지만 No가 하지 않는 경우
                    else :
                        print('삭제 실패했습니다.\n입력한 값에 해당하는 데이터가 존재하지 않습니다.')
                        break
                # 2) 제품코드가 존재하지 않는 경우
                else:
                    print('입력한 값에 해당하는 데이터가 존재하지 않습니다.')
                    continue
                
        except Exception as e :
            print('db 연동 실패 : ', e)
            conn.rollback() 

        finally:
            cursor.close()
            conn.close()

    #--------------------------   
    # (3) 판매기록 수정 매서드
    def saleUpdate(self) : 
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()
                Read('s').readAll() # 전체 데이터 출력
                print('<<<판매기록을 수정합니다>>>\n수정할 데이터의 ',end='')
                in_code = super().codeInput() # 제품코드 입력 매서드 호출
                rows = FindSql('s', 3, in_code).sqlFind()

                # SELECT 쿼리 실행결과가 있는 경우               
                if rows :
                    os.system('cls') 
                    print("<<<입력한 제품코드의 판매기록 목록 조회입니다>>>")
                    ShowTables().showSale(rows)
                    print('수정할 데이터의 ',end='')
                    in_no = super().noInput()
                    rows1 = FindSql('s', 2, in_no).sqlFind() # 수정할 데이터의 No선택
                    # 판매 수정 확인문
                    yesNo = input('수정하시겠습니까>(y/n) : ')
                    if SelOpt(yesNo).startOpt() and len(rows1) != 0: 
                        print("<<<수정할 데이터를 입력하세요.>>>")
                        in_qty = super().qtyInput()                   
                        # 판매 기록을 수정하는 SQL / 2023-02-09 / ### <요구사항-1> 반영 ###
                        sql = f"UPDATE sales2 SET Qty = '{in_qty}', Amt = '{getPrice(in_code ,in_qty)}' WHERE seqNo = '{in_no}'"
                        sqlAction(sql, True) # 2023-03-02 /접속함수 실행
                        os.system('cls')       
                        print("<<<수정을 완료했습니다>>>\n<<<수정 결과입니다>>>")
                        Read('s').readAll()
                        break
                    elif SelOpt(yesNo).startOpt() and len(rows1) == 0:
                        print("<<<조회한 목록에 입력한 No가 존재하지 않습니다.>>>")
                        os.system("pause")
                        continue
                    else:
                        print("<<<수정을 취소했습니다.>>>")
                        os.system("pause")
                        break
                # SELECT 쿼리 실행결과가 없는 경우        
                else : 
                    print('수정할 제품코드가 없습니다.')
                    os.system("pause")
                    continue
                
        except Exception as e :
            print('db 연동 실패 : ', e)
            conn.rollback() 
            
        finally:
            cursor.close()
            conn.close()
            

#--------------------------            
class SaleSum(UserInput):
# 코드별 판매금액 합계 클래스 / 2023-03-26
# 기존 세무조사 매서드와 주주총회 매서드 분리 후 독립된 클래스화 
    def __init__(self, task):
        self.task = task; self.sel_unitPrice = 0
        self.commonTask()
        
    def commonTask(self):
        try :
            print('조회할 ',end=''); in_code = super().codeInput()
            sql = f"SELECT unitPrice FROM product_history2 WHERE Code = '{in_code}'"
            rows = sqlAction(sql)
            if self.task == '세무자료': self.sel_unitPrice = int(min([i for row in rows for i in row]))
            elif self.task == '주주총회': self.sel_unitPrice = int(max([i for row in rows for i in row]))
            rows = FindSql('s',3, in_code).sqlFind()
            os.system('cls')
            print(f"===트리거활용 판매조회2(코드별-{self.task}용)===")
            print(f"{fmt('No',6,'l')}{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('판매등록일자',22,'l')}{fmt('판매수량',16,'l')}{fmt('총 판매가격',5,'l')}") ; print('-'*90)
            sum_amt = 0
            for row in rows :
                sel_amt = row[4] * self.sel_unitPrice
                print(f"{fmt(row[0],6,'l')}{fmt(row[1],10,'l')}{fmt(row[2],20,'l')}{fmt(row[3],10,'l')}{float(fmt(row[4],7,'l')):20,.2f}{float(fmt(sel_amt,5,'l')):20,.2f}")
                sum_amt += sel_amt  
            print('-'*90)
            print(f"{fmt('판매금액합계',66,'l')}{float(fmt(sum_amt,10,'l')):20,.2f}")

        except Exception as e :
            print('db 연동 실패 : ', e)
            
            
#--------------------------
# 계산함수 
# <변경사항> 2023-03-02
# 매서드마다 사용하던 계산을 함수로 설계             
def getPrice(in_Code, qty):
    sql = f"SELECT unitPrice, discountRate FROM product2 WHERE pCode = '{in_Code}'" # product 테이블에서 row_data에 맞는 제품가격을 불러온다.
    pamt_tuples = sqlAction(sql)
    in_unitPrice = list(map(int,[pamt for pamt_tuple in pamt_tuples for pamt in pamt_tuple]))[0] ### <요구사항-6> 반영 ###
    in_disrate = list(map(int,[pamt for pamt_tuple in pamt_tuples for pamt in pamt_tuple]))[1] ### <요구사항-6> 반영 ###
    yesNo = input('판매가격에 할인율을 적용하시겠습니까? (y/n) : ')
    if SelOpt(yesNo).startOpt(): # <1> 할인율이 적용된 가격 계산 
        dis_price = round((in_unitPrice * (100 - round(in_disrate)))/100)
        total_price = dis_price * int(qty) 
    else:
        total_price = in_unitPrice * int(qty) # 할인율이 적용되지 않은 총 가격 
    return total_price    


#-------------------------- 
def startSale():
    while True:
        os.system('cls')
        print("---------판매관리---------")
        print("판매            등록 : 1  ")
        print("판매    목록    조회 : 2  ")
        print("코드     별     조회 : 3  ")
        print("제품명   별     조회 : 4  ")
        print("판매            수정 : 5  ")
        print("판매            삭제 : 6  ")
        print("판매조회(세무자료용) : 7  ")
        print("판매조회(주주총회용) : 8  ")
        print("판매   테이블   리셋 : 9  ")
        print("판매    관리    종료 : 99 ")
        print("시스템          종료 : 0  ")
        sel = input("작업을 선택하세요 : "  )
        c0 = SaleFunc()
        if sel == '1' :
            c0.saleCreate()
            os.system("pause")
        elif sel == '2' :
            Read('s').readAll()
            os.system("pause")
        elif sel == '3' :
            Read('s').readOne('코드')
            os.system("pause")
        elif sel == '4' :
            Read('s').readOne('제품명')
            os.system("pause")
        elif sel == '5' :
            c0.saleUpdate()
            os.system("pause")
        elif sel == '6' :
            c0.saleDelete()
            os.system("pause")
        elif sel == '7' :
            SaleSum('세무자료')
            os.system("pause")
        elif sel == '8' :
            SaleSum('주주총회')
            os.system("pause")
        elif sel == '9' :
            TableReset('s').tableReset()
            os.system("pause")
        elif sel == '99' :
            print("판매관리를 종료합니다. ") 
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
    startSale()