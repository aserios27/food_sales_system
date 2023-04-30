from Filter import FindSql, sqlAction

# 데이터베이스 환경변수
config = {                  
    'host' : '127.0.0.1',   # ipv4주소
    'user' : 'root',        # MySQL 계정
    'passwd' : 'root1234',  # MySQL 비밀번호
    'database' : 'test_db2', # MySQL 데이터베이스명
    'port' : 3306,          # MySQL 통신코드 리터럴 / 정수값 사용
    'charset' : 'utf8',     # MySQL에서 한글 사용 설정
    'use_unicode' : True    # MySQL에서 한글 사용 설정
    }


# 제품테이블 이력관리 클래스 / 2023-03-21
class HisFunc :
        
# (1) 제품 생성 이력 매서드 
    def prodHisCreate(self, code, iValue):
        try :
            sql = f"INSERT INTO product_history(Code, Event, pName, unitPrice, discountRate) VALUES('{code}','Insert','{iValue[0]}', '{iValue[1]}', '{iValue[2]}');"
            sqlAction(sql, True)
        except Exception as e :
            print('오류 : ', e)

    #--------------------------
    # (2) 제품 삭제 이력 매서드
    def prodHisDelete(self, code) : 
        try :
            rows = FindSql('p', 3, code).sqlFind() # 조건에 맞는 SQL실행
            iValue = [i for row in rows for i in row]
            sql = f"INSERT INTO product_history(Code, Event, pName, unitPrice, discountRate) VALUES('{iValue[0]}', 'Delete', '{iValue[1]}', '{iValue[2]}', '{iValue[3]}');"
            sqlAction(sql, True)
        except Exception as e :
            print('db 연동 실패 : ', e)


    #--------------------------   
    # (3) 제품 수정 이력 매서드
    def prodHisUpdate(self, code) : 
        try :
            rows = FindSql('p', 3, code).sqlFind() # 조건에 맞는 SQL실행
            iValue = [i for row in rows for i in row]
            sql = f"INSERT INTO product_history(Code, Event, pName, unitPrice, discountRate) VALUES('{iValue[0]}','Update', '{iValue[1]}', '{iValue[2]}', '{iValue[3]}');"
            sqlAction(sql, True)
        except Exception as e :
            print('db 연동 실패 : ', e)
            
            
class BackFunc :
    def __init__(self, task, code):
        self.task = task
        if self.task == '단종': self.disContinueSale(code)
        elif task == '취소': self.cancelSale(code)
        
    def disContinueSale(self, code):
        try :
            sql = f"SELECT seqNo, sCode, date_format(s.sDate,'%Y.%m.%d') as date, s.qty, s.amt FROM sales AS s WHERE sCode = '{code}'" 
            rows = sqlAction(sql, True)
            iValue = [row for row in rows]
            sql = "INSERT INTO sales_backup(seqNo, sCode, sDate, Qty, Amt, Event) VALUES(%s, %s, %s, %s, %s, '단종')"
            sqlAction(sql, True, False, iValue)
        
        except Exception as e :
            print('db 연동 실패 : ', e)

    def cancelSale(self, code):
        try :
            sql = f"SELECT * FROM sales WHERE seqNo = '{code}'"
            rows = sqlAction(sql); iValue = [i for row in rows for i in row]
            sql = f"INSERT INTO sales_backup(seqNo, sCode, sDate, Qty, Amt, Event) VALUES('{iValue[0]}', '{iValue[1]}', '{iValue[2]}', '{iValue[3]}', '{iValue[4]}', '취소');"
            sqlAction(sql, True)
        
        except Exception as e :
            print('db 연동 실패 : ', e)
