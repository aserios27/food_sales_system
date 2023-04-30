from Filter import FindSql, sqlAction

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


# 식단테이블 이력관리 클래스 / 2023-03-21
class HisFunc :   
    # (1) 식단 생성 이력 매서드 
    def prodHisCreate(self, code, iValue, menu_class):
        try :
            sql = f"INSERT INTO menu_planner_history(pCode, pClass, pName, unitPrice, discountRate, Event) VALUES('{code}', '{menu_class}', '{iValue[0]}', '{iValue[1]}', '{iValue[2]}','Insert');"
            sqlAction(sql, True)
        except Exception as e :
            print('오류 : ', e)

    #--------------------------
    # (2) 식단 삭제 이력 매서드
    def prodHisDelete(self, code) : 
        try :
            rows = FindSql('p', 3, code).sqlFind() # 조건에 맞는 SQL실행
            iValue = [i for row in rows for i in row]
            sql = f"INSERT INTO menu_planner_history(pCode, pClass, pName, unitPrice, discountRate, Event) VALUES('{iValue[0]}', '{iValue[1]}', '{iValue[2]}', '{iValue[3]}', '{iValue[4]}', 'Delete');"
            sqlAction(sql, True)
        except Exception as e :
            print('db 연동 실패 : ', e)


    #--------------------------   
    # (3) 식단 수정 이력 매서드
    def prodHisUpdate(self, code) : 
        try :
            rows = FindSql('p', 3, code).sqlFind() # 조건에 맞는 SQL실행
            iValue = [i for row in rows for i in row]
            sql = f"INSERT INTO menu_planner_history(pCode, pClass, pName, unitPrice, discountRate, Event) VALUES('{iValue[0]}','{iValue[1]}', '{iValue[2]}', '{iValue[3]}', '{iValue[4]}','Update');"
            sqlAction(sql, True)
        except Exception as e :
            print('db 연동 실패 : ', e)
    
    #--------------------------
    # (4) 식단메뉴 생성 이력 매서드 
    def prodDetailHisCreate(self, code, iMenu):
        try :
            sql = f"INSERT INTO menu_planner_detail_history(dCode, dMain, dSoup, dSub1, dSub2, dSub3, dEvent) VALUES('{code}','{iMenu[0]}', '{iMenu[1]}', '{iMenu[2]}', '{iMenu[3]}', '{iMenu[4]}', 'Insert');"
            sqlAction(sql, True)
        except Exception as e :
            print('오류 : ', e)

    #--------------------------
    # (5) 식단메뉴 삭제 이력 매서드
    def prodDetailHisDelete(self, code) : 
        try :
            rows = FindSql('m', 3, code).sqlFind() # 조건에 맞는 SQL실행
            iValue = [i for row in rows for i in row]
            sql = f"INSERT INTO menu_planner_detail_history(dCode, dMain, dSoup, dSub1, dSub2, dSub3, dEvent) VALUES('{iValue[0]}', '{iValue[1]}', '{iValue[2]}', '{iValue[3]}', '{iValue[4]}', '{iValue[5]}','Delete');"
            sqlAction(sql, True)
        except Exception as e :
            print('db 연동 실패 : ', e)


    #--------------------------   
    # (6) 식단메뉴 수정 이력 매서드
    def prodDetailHisUpdate(self, code) : 
        try :
            rows = FindSql('m', 3, code).sqlFind() # 조건에 맞는 SQL실행
            iValue = [i for row in rows for i in row]
            sql = f"INSERT INTO menu_planner_detail_history(dCode, dMain, dSoup, dSub1, dSub2, dSub3, dEvent) VALUES('{iValue[0]}', '{iValue[1]}', '{iValue[2]}', '{iValue[3]}', '{iValue[4]}', '{iValue[5]}','Update');"
            sqlAction(sql, True)
        except Exception as e :
            print('db 연동 실패 : ', e)
            
# 판매테이블 삭제관리 클래스 / 2023-03-28            
class BackFunc :
    def __init__(self, task, code):
        self.task = task
        if self.task == '단종': self.disContinueSale(code)
        elif task == '취소': self.cancelSale(code)
        
    def disContinueSale(self, code):
        try :
            sql = f"SELECT seqNo, sCode, date_format(s.sDate,'%Y.%m.%d') as date, s.qty, s.amt FROM menu_sales AS s WHERE sCode = '{code}'" 
            rows = sqlAction(sql, True)
            iValue = [row for row in rows]
            sql = "INSERT INTO menu_sales_backup(seqNo, sCode, sDate, Qty, Amt, Event) VALUES(%s, %s, %s, %s, %s, '단종')"
            sqlAction(sql, True, False, iValue)
        
        except Exception as e :
            print('db 연동 실패 : ', e)

    def cancelSale(self, code):
        try :
            sql = f"SELECT * FROM menu_sales WHERE seqNo = '{code}'"
            rows = sqlAction(sql); iValue = [i for row in rows for i in row]
            sql = f"INSERT INTO menu_sales_backup(seqNo, sCode, sDate, Qty, Amt, Event) VALUES('{iValue[0]}', '{iValue[1]}', '{iValue[2]}', '{iValue[3]}', '{iValue[4]}', '취소');"
            sqlAction(sql, True)
        
        except Exception as e :
            print('db 연동 실패 : ', e)
