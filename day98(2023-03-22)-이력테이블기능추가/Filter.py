import os
from re import findall, match   # 정규 표현식 사용을 위한 라이브러리 (findall, match) / 2023-02-07
import pymysql                  # MySQL데이터베이스를 사용하기 위한 라이브러리 / 2023-02-07
from wcwidth import wcswidth    # 2byte 글자 간격 맞춤을 제공하는 라이브러리 / 2023-02-09


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


#--------------------------
# SQL관리 클래스
# <변경사항> / 2023-02-20
# ProdFind클래스와 SalFind클래스 병합
class FindSql():
    table = '' ; table_name = ''
    def __init__(self,table, find_sel, find_in_data = ''): # 매개변수 (테이블, 찾을 SQL번호, 조건값) / ### <요구사항-3> 반영 ### 
        self.table = table
        self.read_sel = find_sel
        if self.table == 'p': self.table_name = '제품'
        else : self.table_name = '판매'
        
        # 제품 테이블 sql
        if self.table.lower() == 'p':
            # 1) 제품코드를 이용하여 product테이블의 해당 데이터 호출
            if find_sel == 3 or find_sel == '코드': 
                self.find_sql = f"SELECT * FROM product WHERE pCode = '{find_in_data}'"
            # 2) 제품명를 이용하여 product테이블의 해당 데이터 호출
            elif find_sel == 4 or find_sel == '제품명': 
                self.find_sql = f"SELECT * FROM product WHERE pName like '%{find_in_data}%'" 
            # 3)product테이블의 전체 데이터 호출
            elif find_sel == 0:
                self.find_sql = "SELECT * FROM product"
                
        # 판매 테이블 sql
        elif self.table.lower() == 's':
            # 1) 제품코드로 판매관리 필요 데이터 전체조회
            if find_sel == 3 or find_sel == '코드': 
                self.find_sql = f"SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y.%m.%d') as date, s.qty, s.amt FROM sales AS s JOIN product AS p ON s.sCode = p.pCode WHERE p.pCode = '{find_in_data}'" 
            # 2) 제품명으로 판매관리 필요 데이터 전체조회
            elif find_sel == 4 or find_sel == '제품명': 
                self.find_sql = f"SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y.%m.%d') as date, s.qty, s.amt FROM sales AS s JOIN product AS p ON s.sCode = p.pCode WHERE p.pName like '%{find_in_data}%'"
            # 3) 판매관리 필요 데이터 전체조회
            elif find_sel == 0:
                self.find_sql = "SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y%m%d') as date, s.qty, s.amt FROM sales AS s LEFT OUTER JOIN product AS p ON s.sCode = p.pCode"
            # 4) product테이블에서 제품가격과 할인율 가져오기
            elif find_sel == 1:
                self.find_sql = f"SELECT unitPrice, discountRate FROM product WHERE pCode = '{find_in_data}'" 
            # 5) 인덱스로 제품코드 조회
            elif find_sel == 2:
                self.find_sql = f"SELECT sCode FROM sales WHERE seqNo = '{find_in_data}'"
        else:
            print('입력한 테이블은 존재하지 않습니다. 다시 입력해 주세요.')
    
    def sqlFind(self):
        return sqlAction(self.find_sql) 


#--------------------------
# 사용자가 입력한 데이터를 검사하는 필터 클래스
class InputFilter() : 
    def __init__(self):   
        self.inputValueFilter_result = False # 필터 결과
        self.no = ''                         # sales테이블 인덱스
        self.scode = ''                      # code - 제품코드
        self.qty = ''                        # qty - 제품 판매 수량
        self.pname = ''                      # pname = 제품명
        self.price = ''                      # price - 제품 가격 변수
        self.discrate = ''                   # discrate - 할인율 변수
        
        
    # 2023-02-13 / 2023-03-02 매서드로 위치변경 / 2023-03-09 코드 수정
    # <sql인젝션을 방지하기 위한 블랙리스트 매서드>
    def sqlBlackList(self, st):
        ls_1 = ['--',';--',';','/*','*/','@','!','?','~','$','%','&','*','(',')','+','=','`','/','^','#',\
        'ADD', 'ALL', 'ALTER', 'ANALYZE','AND', 'AS', 'ASC', 'ASENSITIVE', 'BEFORE', 'BETWEEN', 'BIGINT', 'BINARY', 'BLOB', 'BOTH', 'BY', 'CALL', 'CASCADE', 'CASE', 'CHANGE', 'CHAR', 'CHARACTER', 'CHECK', 'COLLATE', 'COLUMN', 'CONDITION', 'CONSTRAINT', 'CONTINUE', 'CONVERT', 'CREATE', 'CROSS', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'CURRENT_USER', 'CURSOR', 'DATABASE', 'DATABASES', 'DAY_HOUR', 'DAY_MICROSECOND', 'DAY_MINUTE', 'DAY_SECOND', 'DEC', 'DECIMAL', 'DECLARE', 'DEFAULT', 'DELAYED', 'DELETE', 'DESC', 'DESCRIBE', 'DETERMINISTIC', 'DISTINCT', 'DISTINCTROW', 'DIV', 'DOUBLE', 'DROP', 'DUAL', 'EACH', 'ELSE', 'ELSEIF', 'ENCLOSED', 'ESCAPED', 'EXISTS', 'EXIT', 'EXPLAIN', 'FALSE', 'FETCH', 'FLOAT', 'FLOAT4', 'FLOAT8', 'FOR', 'FORCE', 'FOREIGN', 'FROM', 'FULLTEXT', 'GRANT', 'GROUP', 'HAVING', 'HIGH_PRIORITY', 'HOUR_MICROSECOND', 'HOUR_MINUTE', 'HOUR_SECOND', 'IF', 'IGNORE', 'IN', 'INDEX', 'INFILE', 'INNER', 'INOUT', 'INSENSITIVE', 'INSERT', 'INT', 'INT1', 'INT2', 'INT3', 'INT4', 'INT8', 'INTEGER', 'INTERVAL', 'INTO', 'IS', 'ITERATE', 'JOIN', 'KEY', 'KEYS', 'KILL', 'LEADING', 'LEAVE', 'LEFT', 'LIKE', 'LIMIT', 'LINES', 'LOAD', 'LOCALTIME', 'LOCALTIMESTAMP', 'LOCK', 'LONG', 'LONGBLOB', 'LONGTEXT', 'LOOP', 'LOW_PRIORITY', 'MATCH', 'MEDIUMBLOB', 'MEDIUMINT', 'MEDIUMTEXT', 'MIDDLEINT', 'MINUTE_MICROSECOND', 'MINUTE_SECOND', 'MOD', 'MODIFIES', 'NATURAL', 'NOT', 'NO_WRITE_TO_BINLOG', 'NULL', 'NUMERIC', 'ON', 'OPTIMIZE', 'OPTION', 'OPTIONALLY', 'OR', 'ORDER', 'OUT', 'OUTER', 'OUTFILE', 'PRECISION', 'PRIMARY', 'PROCEDURE', 'PURGE', 'READ', 'READS', 'REAL', 'REFERENCES', 'REGEXP', 'RELEASE', 'RENAME', 'REPEAT', 'REPLACE', 'REQUIRE', 'RESTRICT', 'RETURN', 'REVOKE', 'RIGHT', 'RLIKE', 'SCHEMA', 'SCHEMAS', 'SECOND_MICROSECOND', 'SELECT', 'SENSITIVE', 'SEPARATOR', 'SET', 'SHOW', 'SMALLINT', 'SONAME', 'SPATIAL', 'SPECIFIC', 'SQL', 'SQLEXCEPTION', 'SQLSTATE', 'SQLWARNING', 'SQL_BIG_RESULT', 'SQL_CALC_FOUND_ROWS', 'SQL_SMALL_RESULT', 'SSL', 'STARTING', 'STRAIGHT_JOIN', 'TABLE', 'TERMINATED', 'THEN', 'TINYBLOB', 'TINYINT', 'TINYTEXT', 'TO', 'TRAILING', 'TRIGGER', 'TRUE', 'UNDO', 'UNION', 'UNIQUE', 'UNLOCK', 'UNSIGNED', 'UPDATE', 'USAGE', 'USE', 'USING', 'UTC_DATE', 'UTC_TIME', 'UTC_TIMESTAMP', 'VALUES', 'VARBINARY', 'VARCHAR', 'VARCHARACTER', 'VARYING', 'WHEN', 'WHERE', 'WHILE', 'WITH', 'WRITE', 'XOR', 'YEAR_MONTH', 'ZEROFILL']
        stchk = ''.join(['SQLInjecsion' for i in range(len(ls_1)) if '  ' in st.upper().replace(ls_1[i],'  ')])
        if stchk == 'SQLInjecsion': st = True
        return st       
        
    # 1. 인덱스(순서) 필터
    def setNo(self, no):
        # 0) SQL Injecsion 블랙리스트 매서드 / 2023-02-13 / 2023-03-02 
        no = self.sqlBlackList(no)
        # 1) 입력한 값에 예약어, 특수문자가 있을 경우
        if no == True:
            print('입력값을 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        # 2) 입력한 값이 공백이나 기호가 있을 경우
        elif no.isalnum() == False: 
            print('입력값 ' +str(no)+ ' 에 공백이나 기호가 있습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        # 3) 입력한 값이 정수가 아닌 경우    
        elif no.isdigit() == False: 
            print('입력값 ' +str(no)+ ' 에는 정수만 입력이 가능합니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 4) 모든 조건을 만족하는 경우        
        else:
            self.inputValueFilter_result = True 
            self.no = no
                           
        return self.inputValueFilter_result
    
    # 2. 제품코드 필터
    def setScode(self, scode):
        # 0) SQL Injecsion 블랙리스트 매서드 / 2023-02-13 / 2023-03-02
        scode = self.sqlBlackList(scode)
        # 1) 입력한 값에 예약어, 특수문자가 있을 경우
        if scode == True:
            print('입력값을 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 2) 입력한 값이 공백이나 기호가 있을 경우
        elif scode.isalnum() == False: 
            print('입력값 ' +str(scode)+ ' 에 공백이나 기호가 있습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        # 3) 입력한 값이 소문자 알파벳1개와 정수3개로 되어 있으며 길이가 4자리인지 필터링    
        elif not (match('[a-z][0-9]{3}', scode) and len(scode)==4): 
            print('입력값 ' +str(scode)+ ' 에는 a001 과 같이 소문자와 숫자를 조합한 4자리의 값만 입력이 가능합니다.  다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 4) 모든 조건을 만족하는 경우        
        else:
            self.inputValueFilter_result = True 
            self.scode = scode                  
        return self.inputValueFilter_result 
    
    # 3. 판매 수량 필터
    def setQty(self, qty):
        # 0) SQL Injecsion 블랙리스트 매서드 / 2023-02-13 / 2023-03-02
        qty = self.sqlBlackList(qty)
        # 1) 입력한 값에 예약어, 특수문자가 있을 경우
        if qty == True:
            print('입력값을 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 2) 입력한 값이 공백이나 기호가 있을 경우
        elif qty.isalnum() == False: 
            print('입력값 ' +str(qty)+ ' 에 공백이나 기호가 있습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        # 3) 입력한 값이 정수가 아닌 경우    
        elif qty.isdigit() == False: 
            print('입력값 ' +str(qty)+ ' 에는 정수만 입력이 가능합니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 4) 모든 조건을 만족하는 경우        
        else:
            self.inputValueFilter_result = True 
            self.qty = qty                     
        return self.inputValueFilter_result
    
    # 4. 제품명 필터 
    def setPname(self, pname) :
        # 0) SQL Injecsion 블랙리스트 매서드 / 2023-02-13 / 2023-03-02
        pname = self.sqlBlackList(pname)
        # 1) 입력한 값에 예약어, 특수문자가 있을 경우
        if pname == True:
            print('입력값을 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 2) 입력한 값이 공백(빈칸)인 경우
        elif pname == '' or len(pname) < 0:
            print('입력값 ' + str(pname)+ ' 에는 빈칸을 입력하실 수 없습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        # 3) 입력한 값에 단모음, 단자음이 있는 경우
        elif findall('[ㄱ-ㅎ|ㅏ-ㅣ]', pname): 
            print('입력값 ' + str(pname)+ ' 에는 단모음, 단자음을 입력할 수 없습니다.  다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 4) 모든 조건을 만족하는 경우
        else:
            self.inputValueFilter_result = True 
            self.pname = pname                          
        return self.inputValueFilter_result

    # 5. 제품 가격 필터
    def setPrice(self, price) :
        # 0) SQL Injecsion 블랙리스트 매서드 / 2023-02-13 / 2023-03-02
        price = self.sqlBlackList(price)
        # 1) 입력한 값에 예약어, 특수문자가 있을 경우
        if price == True:
            print('입력값을 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 2) 입력한 값이 공백이나 기호가 있을 경우
        elif price.isalnum() == False: 
            print('입력값 ' +str(price)+ ' 에 공백이나 기호가 있습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 3) 입력한 값이 숫자가 아닌 경우
        elif price.isdigit() == False: 
            print('입력값 ' +str(price)+ ' 에는 숫자만 입력이 가능합니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 4) 모든 조건을 만족하는 경우    
        else:
            self.inputValueFilter_result = True 
            self.price= price
        return self.inputValueFilter_result 
    
    # 6. 제품 할인율 필터
    def setDiscRate(self, discrate) :
        # 0) SQL Injecsion 블랙리스트 매서드 / 2023-02-13 / 2023-03-02
        discrate = self.sqlBlackList(discrate)
        # 1) 입력한 값에 예약어, 특수문자가 있을 경우
        if discrate == True:
            print('입력값을 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 2) 공백을 입력한 경우 / # 2023-03-01 할인율 필터 추가
        elif discrate == '' or len(discrate) < 0 :
            print("할인율이 미입력되면 자동으로 '1'이 기입됩니다.")
            self.discrate = 1 ; self.inputValueFilter_result = True
        # 3) 정수와 실수를 입력한 경우 
        elif findall('\d', discrate):
            self.discrate= discrate  
            self.inputValueFilter_result = True
        # 4) 해당 조건을 만족하지 못한 경우
        else:
            print('입력값 ' +str(discrate)+ ' 에는 정수와 실수만 입력이 가능합니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        return self.inputValueFilter_result 


#--------------------------
# 사용자 입력 클래스 / 2023-02-09
class UserInput(InputFilter): # 필터클래스 상속
    def __init__(self):
        super().__init__()
    # 인덱스 입력 매서드 2023-02-07
    def noInput(self):
        while True:
            if super().setNo(input("No를 입력하세요 : ")) :
                in_no = self.no
                break
            else:
                continue
        return in_no
  
    # 제품명 입력 매서드
    def nameInput(self):
        while True:
            if super().setPname(input("제품명을 입력하세요 : ")) : 
                in_pname = self.pname
                break
            else:
                continue
        return in_pname

    # 제품코드 입력 매서드
    def codeInput(self):
        while True:
            if super().setScode(input("제품코드를 입력하세요 : ")) :
                in_code = self.scode
                break
            else:
                continue
        return in_code

    # 판매 수량 입력 매서드
    def qtyInput(self):
    # 수량 입력 
        while True:
            if super().setQty(input("제품 수량을 입력하세요 : ")) :
                in_qty = self.qty
                break
            else:
                continue    
        return in_qty
    
    # 제품 가격 입력 매서드
    def priceInput(self):
        while True:
            if super().setPrice(input("제품가격을 입력하세요 : ")) :
                in_price = self.price
                break
            else:
                continue
        return  in_price
      
    # 할인율 입력 매서드
    def discRateInput(self):
        while True:
            if super().setDiscRate(input("제품 할인율을 입력하세요 : ")) :
                in_discrate = self.discrate
                break
            else:
                continue
        return  in_discrate

    # 입력 매서드 동시 호출 (제품명, 가격, 할인율)
    def userInput(self):
        return [self.nameInput(), self.priceInput(), self.discRateInput()]


#--------------------------
# FindSql에서 분리 2023-03-07
class Read(UserInput):
    table = '' ; table_name = ''
    def __init__(self, table):
        super().__init__()
        self.table = table
        if self.table == 'p': self.table_name = '제품'
        else : self.table_name = '판매'
        
    def readAll(self) :
        print(f"<<<{self.table_name} 전체 목록 조회입니다>>>")
        rows = FindSql(self.table, 0).sqlFind()
        if self.table == 'p': 
            ShowTables().showProd(rows)
        elif self.table == 's':
            ShowTables().showSale(rows)
            
    # 테이블 조회
    # <변경사항> / 2023-02-20 CodeInspection 
    # 2023-03-07 매서드 위치 변경
    # 기존의 product, sales 매서드 통합
    # self.table 조건문을 이용하여 두 테이블 분류
    def readOne(self, read_sel) :
        self.read_sel = read_sel
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()
                self.readAll() # 클래스 매개변수 활용하여 테이블의 전체목록 조회
                print(f"<<<{self.table_name}테이블 {self.read_sel}조회 입니다>>>\n조회할 ",end='')    
                # 1) 제품코드에 해당하는 데이터를 가져올 경우
                if self.read_sel == '코드': 
                    in_code = super().codeInput()
                    rows = FindSql(self.table, 3, in_code).sqlFind()
                # 2) 제품명 해당하는 데이터를 가져올 경우
                elif self.read_sel == '제품명' : 
                    in_code = super().nameInput()
                    rows = FindSql(self.table, 4, in_code).sqlFind() 
                    
                # 2023-02-21 product, sales테이블 각각의 출력문
                # 조건문을 이용하여 통합
                # 1) 조회할 데이터가 존재할 경우   
                if len(rows) > 0 :
                    os.system('cls')
                    print(f"==={self.table_name}조회({self.read_sel}별)===")
                    if self.table == 'p':
                        ShowTables().showProd(rows)
                        break
                    elif self.table == 's':
                        ShowTables().showSale(rows)
                        print('-'*90)
                        rows_amt = [row for row in rows] ; sum_amt = sum([rows_amt[i][5] for i in range(len(rows_amt))])
                        print(f"{fmt('판매금액합계',66,'l')}{float(fmt(sum_amt,10,'l')):20,.2f}")
                        break
                # 2) 조회할 로우가 존재하지 않을경우
                else:
                    print(f"조회결과 입력한 {self.read_sel}에 맞는 제품이 없습니다")
                    continue             
                    
        except Exception as e :
            print('db 연동 실패 : ', e)
            conn.rollback()
            
        finally:
            cursor.close()                      
            conn.close()
            self.rows = rows    
                         

#--------------------------    
class SelOpt() :
    def __init__(self, yesno) :
        self.option = yesno # 사용자가 입력한 값
        self.eng_lst = ['Y', 'N'] # 입력값 영어. (Key값으로 사용.)
        alpha_lst = ['ㅛ', 'ㅜ'] # 입력값 한글. (Value값으로 사용.)
        self.op_dict = dict(zip(self.eng_lst, alpha_lst)) # 입력값인 영어와 한글을 dict로 구성.
        self.select = "" # 입력값 최종출력.
        self.getOpt() # 클래스를 통해 객체를 만들 때 마지막 작업으로 getOption 메서드 실행.

    def getOpt(self) : # 작업옵션 획득 메서드.
        if findall('[ㅏ-ㅣ]', self.option): # 한글을 입력했을 경우
            ### <요구사항-6> 반영 ###
            reop_dict = dict(map(reversed, self.op_dict.items())) # dict의 key, value를 변경하는 코드 / ### <요구사항-6> 반영 ###                                               
            self.select = reop_dict.get(self.option, 0) # get메서드로 Key에 대응되는 Value 추출
            
        elif findall('[a-z|A-Z]', self.option): # 알파벳을 입력했을 경우
            self.select = self.option.upper() # 'y', 'n'을 대문자로 변경
    
    def startOpt(self) : # 입력값 반환 메서드.
        if self.select in self.eng_lst[0]: return True
        elif self.select in self.eng_lst[1]: return False
        else: return 0             
        

#--------------------------
class ShowTables:
    # 제품 테이블 출력
    def showProd(self, rows):
        print(f"{fmt('제품코드',10,'l')}{fmt('제품명',24,'l')}{fmt('제품가격',20,'l')}{fmt('할인율',20,'l')}")
        print('-'*60)
        for row in rows:
            print(f"{fmt(row[0],10,'l')}{fmt(row[1],10,'l')}{float(fmt(row[2],5,'l')):20,.2f}{float(fmt(row[3],130,'l')):20,.2f}")
    # 판매 테이블 출력
    def showSale(self, rows):
        print(f"{fmt('No',6,'l')}{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('판매등록일자',22,'l')}{fmt('판매수량',16,'l')}{fmt('총 판매가격',5,'l')}")
        print('-'*90)
        for row in rows :
            print(f"{fmt(row[0],6,'l')}{fmt(row[1],10,'l')}{fmt(row[2],20,'l')}{fmt(row[3],10,'l')}{float(fmt(row[4],7,'l')):20,.2f}{float(fmt(row[5],5,'l')):20,.2f}")

    
#--------------------------    
class TableCreate:
    def __init__(self, table):
        self.table = table
        if self.table == 'p': self.productTableCreate()
        elif self.table == 's': self.salesTableCreate()    
    # 테이블 생성 함수(product)    
    def productTableCreate(self) :  
        try :
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            sql = """
            CREATE table if not exists product (
                pCode VARCHAR(4) PRIMARY KEY,
                pName VARCHAR(20) NOT NULL,
                unitPrice INT NOT NULL,
                discountRate decimal(5,2) NOT NULL DEFAULT 1.00)
                """
            sqlAction(sql, True)
            self.prodHistoryCreate()
                
        except Exception as e :
            print("오류 : ",e)
            conn.rollback()
        finally :
            conn.close()
            cursor.close()
    
    def prodHistoryCreate(self):  
        try :
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            sql = """
            CREATE table if not exists product_history(
                seqNo int auto_increment,
                pCode varchar(4), 
                pEvent varchar(20) not null,
                Pdate timestamp not null DEFAULT CURRENT_TIMESTAMP,
                New_pName varchar(20),
                New_unitPrice int,
                New_discountRate decimal(5,2),
                pName varchar(20),
                unitPrice int,
                discountRate decimal(5,2),
                PRIMARY KEY(seqNo,pCode));
                """
            sqlAction(sql, True)
                
        except Exception as e :
            print("오류 : ",e)
            conn.rollback()
        finally :
            conn.close()
            cursor.close()        
      
    # 테이블 생성 함수(sales)
    def salesTableCreate(self) :  
        try :
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            sql = """
            CREATE table if not exists sales (
                seqNo INT(10) NOT NULL AUTO_INCREMENT, ,
                sCode VARCHAR(4) NOT NULL,,
                sDate TIMESTAMP DEFAULT now() CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                Qty INT NOT NULL,,
                Amt decimal(12, 2) DEFAULT 0.0,
                PRIMARY KEY(seqNo,sCode))
                """
            sqlAction(sql, True) # 2023-03-02 접속함수 실행  
        except Exception as e :
            print("오류 : ",e)
            conn.rollback()
        finally :
            conn.close()
            cursor.close()
            
            
#--------------------------             
# 테이블 리셋 클래스 / 2023-02-15
class TableReset:
    table = ''
    table_name = ''
    def __init__(self, table):
        self.table = table
        if self.table == 'p': self.table_name = 'product'
        elif self.table == 's' : self.table_name = 'sales'
    
    def prodReset(self):
        prod_insert = [('a001', '마우스', '100', '1.00'),('a002', '키보드', '200', '1.00', ),
                       ('a003', '무선마우스', '300', '1.00'),('a004', '무선키보드', '400', '1.00'),
                       ('a005', '24형모니터', '500', '1.00'),('a006', '27형모니터', '600', '1.00'),
                       ('a007', '32형모니터', '700', '1.00'),('a008', '500GB-ssd', '800', '1.00'),
                       ('a009', '1TB-ssd', '900', '1.00'),('a010', '2TB-ssd', '1000', '1.00')]
        sql = "INSERT INTO product(pCode, pName, unitPrice, discountRate) VALUES(%s, %s, %s, %s);"
        sqlAction(sql, True, False, prod_insert)
        sql = "INSERT INTO product_history(pCode, pEvent, New_pName, New_unitPrice, New_discountRate) VALUES (%s, 'Insert', %s, %s, %s);"
        sqlAction(sql, True, False, prod_insert)
    
    
    def saleReset(self):
        sale_insert = [('a001', '20220922', '1', '100'),('a002', '20220922', '2', '400'),('a001', '20220922', '3', '300'),('a003', '20220922', '1', '300'),
                       ('a003', '20220922', '2', '600'),('a003', '20220922', '3', '900'),('a003', '20220922', '4', '1200'),('a004', '20220922', '1', '400'),
                       ('a004', '20220922', '2', '800'),('a004', '20220922', '3', '1200'),('a004', '20220922', '4', '1600'),('a005', '20220922', '1', '500'),
                       ('a005', '20220922', '2', '1000'),('a005', '20220922', '3', '1500'),('a005', '20220922', '4', '2000'),('a006', '20220922', '1', '600'),
                       ('a006', '20220922', '2', '1200'),('a006', '20220922', '3', '1800'),('a006', '20220922', '4', '2400'),('a007', '20220922', '1', '700'),
                       ('a007', '20220922', '2', '1400'),('a007', '20220922', '3', '2100'),('a007', '20220922', '4', '2800'),('a008', '20220922', '1', '800'),
                       ('a008', '20220922', '2', '1600'),('a008', '20220922', '3', '2400'),('a008', '20220922', '4', '3200'),('a009', '20220922', '1', '900'),
                       ('a009', '20220922', '2', '1800'),('a009', '20220922', '3', '2700'),('a009', '20220922', '4', '3600'),('a010', '20220922', '1', '1000'),
                       ('a010', '20220922', '2', '2000'),('a010', '20220922', '3', '3000'),('a010', '20220922', '4', '4000')
                       ]
        sql = "INSERT INTO sales(sCode, sDate, Qty, Amt) VALUES(%s, %s, %s, %s);"
        sqlAction(sql, True, False, sale_insert)
        
    def tableReset(self):
        # 테이블 데이터 확인
        find_rows = FindSql(self.table, 0).sqlFind()
        # 테이블 전체 출력
        Read(self.table).readAll()

        # 1) 테이블 데이터가 존재하는 경우
        if find_rows : 
            print(f'\n<<<{self.table_name}테이블 초기화입니다>>>')
            while True:
                yesNo = input('모두 삭제하고 초기화 하시겠습니까?(y/n) : ')
                if SelOpt(yesNo).startOpt():  
                    try:
                        conn = pymysql.connect(**config)
                        cursor = conn.cursor()

                        # 테이블 전체 내용 삭제
                        sql = f"DELETE FROM {self.table_name}"
                        sqlAction(sql, True)
                        if self.table == 'p' :
                            sqlAction(sql, True, 2) # 2023-03-02 / 접속함수 실행
                            sql = f"DELETE FROM {self.table_name}_history" # 2023-03-21 / 접속함수 실행
                            sqlAction(sql, True)
                            sql = f"ALTER TABLE {self.table_name}_history auto_increment = 1" # 2023-03-02 / seqNo 컬럼 초기화
                            sqlAction(sql, True) 
                        # 대상이 sales 테이블일경우 seqNo가 1부터 시작되도록 초기화
                        elif self.table == 's' :
                            sql = "ALTER TABLE sales auto_increment = 1"
                            sqlAction(sql, True) # 2023-03-02 / 접속함수 실행
                            
                        yesNo = input('제품테이블에 기존 데이터를 추가하시겠습니까?(y/n) : ')
                        if SelOpt(yesNo).startOpt() and self.table == 'p':
                            self.prodReset()
                        
                        elif SelOpt(yesNo).startOpt() and self.table == 's':
                            self.saleReset()
  
                        print("초기화 성공했습니다.")

                    except Exception as e :
                        print('db 연동 실패 : ', e)
                        conn.rollback()

                    finally:
                        cursor.close()
                        conn.close()
                        break
                        
                elif SelOpt(yesNo).select == 'N':
                    print("초기화를 취소했습니다.")
                    break
                
                else:
                    print('잘못입력했습니다. 다시 입력해주세요.')
                    continue
        # 2) 테이블의 데이터가존재하지 않을 경우        
        else : 
            print("삭제할 데이터가 없습니다.\n<<<초기화를 취소합니다.>>>")
     
        
#-------------------------- 
# 출력 데이터 간격 맞춤 함수 / 2023-02-09
def fmt(txt, width, align='c'): 
    txt = str(txt)
    txt_width = wcswidth(txt)
    blank = width - txt_width
    if blank <= 0:
        return txt
    elif align == 'l':
        return txt + ' '* blank
    elif align == 'r':
        return ' ' * blank
    black_l = blank//2
    black_r = blank - black_l
    return ' ' * blank + txt + ' ' * black_r


#-------------------------- 
# 접속함수 / 2023-03-21 executemany 추가  
def sqlAction(sql, com= '', sel = True, val='') : # 매개변수 : sql문, Commit 결정, execute 결정, 연속형변수
    try :
        conn = pymysql.connect(**config)    
        cursor = conn.cursor()
        if sel:
            cursor.execute(sql) 
        else:
            cursor.executemany(sql, val) 
        if com :
            conn.commit()                
        return cursor.fetchall()            
    except Exception as e :                 
        print('db 연동 실패 : ', e)         
        conn.rollback()                     
    finally:                                
        cursor.close()                      
        conn.close()