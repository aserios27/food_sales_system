from Filter import FindSql, sqlAction

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


# 제품테이블 이력관리 클래스 / 2023-03-21
class HisFunc :
        
# (1) 제품 생성 이력 매서드 
    def prodhisCreate(self, code, iValue):
        try :
            sql = f"INSERT INTO product_history(pCode, pEvent, New_pName, New_unitPrice, New_discountRate) VALUES('{code}','Insert','{iValue[0]}', '{iValue[1]}', '{iValue[2]}');"
            sqlAction(sql, True)
        except Exception as e :
            print('오류 : ', e)

    #--------------------------
    # (2) 제품 삭제 이력 매서드
    def prodHisDelete(self, code) : 
        try :
            rows = FindSql('p', 3, code).sqlFind() # 조건에 맞는 SQL실행
            iValue = [i for row in rows for i in row]
            sql = f"INSERT INTO product_history(pCode, pEvent, pName, unitPrice, discountRate) VALUES('{iValue[0]}', 'Delete', '{iValue[1]}', '{iValue[2]}', '{iValue[3]}');"
            sqlAction(sql, True)
        except Exception as e :
            print('db 연동 실패 : ', e)


    #--------------------------   
    # (3) 제품 수정 이력 매서드
    def prodHisUpdate(self, code, new_iValue) : 
        try :
            rows = FindSql('p', 3, code).sqlFind() # 조건에 맞는 SQL실행
            iValue = [i for row in rows for i in row]
            sql = f"INSERT INTO product_history(pCode, pEvent, New_pName, New_unitPrice, New_discountRate, pName, unitPrice, discountRate) VALUES('{iValue[0]}','Update','{new_iValue[0]}', '{new_iValue[1]}', '{new_iValue[2]}', '{iValue[1]}', '{iValue[2]}', '{iValue[3]}');"
            sqlAction(sql, True)
        except Exception as e :
            print('db 연동 실패 : ', e)
            