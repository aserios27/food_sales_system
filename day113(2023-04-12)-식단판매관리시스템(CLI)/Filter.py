import os
from re import findall, match   # 정규 표현식 사용을 위한 라이브러리 (findall, match) / 2023-02-07
import pymysql                  # MySQL데이터베이스를 사용하기 위한 라이브러리 / 2023-02-07
from wcwidth import wcswidth    # 2byte 글자 간격 맞춤을 제공하는 라이브러리 / 2023-02-09

# 데이터베이스 환경변수
config = {                  
    'host' : '127.0.0.1',   # ipv4주소
    'user' : 'root',        # MySQL 계정
    'passwd' : 'root1234',  # MySQL 비밀번호
    'database' : 'test_db4', # MySQL 데이터베이스명
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
    def __init__(self,table, find_sel, find_in_data = ''): # 매개변수 (테이블, 찾을 SQL번호, 조건값) 
        self.table = table
        self.read_sel = find_sel
        if self.table == 'p': self.table_name = '식단'
        elif self.table == 'm': self.table_name = '메뉴'
        else : self.table_name = '식단판매'
        
        # 식단 테이블 sql
        if self.table.lower() == 'p':
            # 1) 식단코드를 이용하여 menu_planner테이블의 해당 데이터 호출
            if find_sel == 3 or find_sel == '코드': 
                self.find_sql = f"SELECT * FROM menu_planner WHERE pCode = '{find_in_data}'"
            # 2) 식단명를 이용하여 menu_planner테이블의 해당 데이터 호출
            elif find_sel == 4 or find_sel == '식단명': 
                self.find_sql = f"SELECT * FROM menu_planner WHERE pName like '%{find_in_data}%'"
            # 3) 분류를 이용하여 menu_planner테이블의 해당 데이터 호출
            elif find_sel == 5 or find_sel == '분류': 
                self.find_sql = f"SELECT * FROM menu_planner WHERE pClass like '%{find_in_data}%'"  
            # 4)menu_planner 테이블의 전체 데이터 호출
            elif find_sel == 0:
                self.find_sql = "SELECT * FROM menu_planner"
        
        # 메뉴 테이블 sql
        elif self.table.lower() == 'm':
            # 1) 식단코드를 이용하여 menu_planner_detail 테이블의 해당 데이터 호출
            if find_sel == 3 or find_sel == '코드': 
                self.find_sql = f"SELECT * FROM menu_planner_detail WHERE dcode = '{find_in_data}'"
            # 2)menu_planner_detail 테이블의 전체 데이터 호출
            elif find_sel == 0:
                self.find_sql = "SELECT * FROM menu_planner_detail"
                
        # 판매 테이블 sql
        elif self.table.lower() == 's':
            # 1) 식단코드로 판매관리 필요 데이터 전체조회
            if find_sel == 3 or find_sel == '코드': 
                self.find_sql = f"SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y.%m.%d') as date, s.qty, s.amt FROM menu_sales AS s JOIN menu_planner AS p ON s.sCode = p.pCode WHERE p.pCode = '{find_in_data}'" 
            # 2) 식단명으로 판매관리 필요 데이터 전체조회
            elif find_sel == 4 or find_sel == '식단명': 
                self.find_sql = f"SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y.%m.%d') as date, s.qty, s.amt FROM menu_sales AS s JOIN menu_planner AS p ON s.sCode = p.pCode WHERE p.pName like '%{find_in_data}%'"
            # 3) 판매관리 필요 데이터 전체조회
            elif find_sel == 0:
                self.find_sql = "SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y%m%d') as date, s.qty, s.amt FROM menu_sales AS s LEFT OUTER JOIN menu_planner AS p ON s.sCode = p.pCode"
            # 4) menu_planner테이블에서 식단가격과 할인율 가져오기
            elif find_sel == 1:
                self.find_sql = f"SELECT unitPrice, discountRate FROM menu_planner WHERE pCode = '{find_in_data}'" 
            # 5) 인덱스로 식단코드 조회
            elif find_sel == 2:
                self.find_sql = f"SELECT sCode FROM menu_sales WHERE seqNo = '{find_in_data}'"
            # 2) 분류명으로 판매관리 필요 데이터 전체조회
            elif find_sel == 5 or find_sel == '분류': 
                self.find_sql = f"SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y.%m.%d') as date, s.qty, s.amt FROM menu_sales AS s JOIN menu_planner AS p ON s.sCode = p.pCode WHERE p.pClass like '%{find_in_data}%'"    
        else:
            print('입력한 테이블은 존재하지 않습니다. 다시 입력해 주세요.')
    
    def sqlFind(self):
        return sqlAction(self.find_sql) 


#--------------------------
# 사용자가 입력한 데이터를 검사하는 필터 클래스
class InputFilter() : 
    def __init__(self):   
        self.inputValueFilter_result = False # 필터 결과
        self.no = ''                         # menu_sales 테이블 인덱스
        self.scode = ''                      # code - 식단코드
        self.qty = ''                        # qty - 식단 판매 수량
        self.pname = ''                      # pname = 식단명
        self.price = ''                      # price - 식단 가격
        self.discrate = ''                   # discrate - 할인율
        self.pclass = ''                     # pclass - 식단 분류 
        
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
    
    # 2. 식단코드 필터
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
    
    # 4. 식단명 필터 
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

    # 5. 식단 가격 필터
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
    
    # 6. 식단 할인율 필터
    def setDiscRate(self, discrate) :
        # 0) SQL Injecsion 블랙리스트 매서드 / 2023-02-13 / 2023-03-02
        discrate = self.sqlBlackList(discrate)
        # 1) 입력한 값에 예약어, 특수문자가 있을 경우
        if discrate == True:
            print('입력값을 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 2) 공백을 입력한 경우 / # 2023-03-01 할인율 필터 추가
        elif discrate == '' or len(discrate) < 0 :
            print("할인율이 미입력되면 자동으로 '0'이 기입됩니다.")
            self.discrate = '0' ; self.inputValueFilter_result = True
        # 3) 정수와 실수를 입력한 경우 
        elif findall('\d', discrate):
            self.discrate= discrate  
            self.inputValueFilter_result = True
        # 4) 해당 조건을 만족하지 못한 경우
        else:
            print('입력값 ' +str(discrate)+ ' 에는 정수와 실수만 입력이 가능합니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        return self.inputValueFilter_result
    
    # 7. 식단 분류 필터
    def setClass(self, in_code) :
        # 1) 식단코드가 'a'로 시작하는 경우
        if len(findall('[a]', in_code)) != 0:
            print("입력한 식단코드는 일반식 입니다."); self.pclass = '일반식'
        # 2) 식단코드가 'a'로 시작하는 경우
        elif len(findall('[b]', in_code)) != 0:
            print("입력한 식단코드는 일반식 입니다."); self.pclass = '병원식'
        # 3) 식단코드가 'd'로 시작하는 경우
        elif len(findall('[d]', in_code)) != 0:
            print("입력한 식단코드는 다이어트식 입니다."); self.pclass = '다이어트식'
        # 4) 식단코드가 'r'로 시작하는 경우
        elif len(findall('[r]', in_code)) != 0:
            print("입력한 식단코드는 과체중식 입니다."); self.pclass = '과체중식'
        # 5) 해당 조건을 만족하지 못한 경우
        else: print("입력한 식단코드는 미분류 입니다."); self.pclass = '미분류' 
        self.inputValueFilter_result = True
        return self.inputValueFilter_result 

    # 8. 식단명 필터 
    def setPmenu(self, pmenu) :
        # 0) SQL Injecsion 블랙리스트 매서드 / 2023-02-13 / 2023-03-02
        pmenu = self.sqlBlackList(pmenu)
        # 1) 입력한 값에 예약어, 특수문자가 있을 경우
        if pmenu == True:
            print('입력값을 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 2) 입력한 값이 공백(빈칸)인 경우
        elif pmenu == '' or len(pmenu) < 0:
            print('입력값 ' + str(pmenu)+ ' 에는 빈칸을 입력하실 수 없습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        # 3) 입력한 값에 단모음, 단자음이 있는 경우
        elif findall('[ㄱ-ㅎ|ㅏ-ㅣ]', pmenu): 
            print('입력값 ' + str(pmenu)+ ' 에는 단모음, 단자음을 입력할 수 없습니다.  다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 4) 입력한 값에 영문이 있는 경우
        elif findall('[a-z|A-Z]', pmenu): 
            print('입력값 ' + str(pmenu)+ ' 에는 영문을 입력할 수 없습니다.  다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 5) 입력한 값에 숫자가 있는 경우
        elif pmenu.isdigit(): 
            print('입력값 ' + str(pmenu)+ ' 에는 숫자를 입력할 수 없습니다.  다시 입력해주세요.')
            self.inputValueFilter_result = False    
        # 6) 모든 조건을 만족하는 경우
        else:
            self.inputValueFilter_result = True 
            self.pmenu = pmenu                          
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
                in_no = self.no; break
            else: continue
        return in_no
  
    # 식단명 입력 매서드
    def nameInput(self):
        while True:
            if super().setPname(input("식단명을 입력하세요 : ")) : 
                in_pname = self.pname ; break
            else: continue
        return in_pname

    # 식단코드 입력 매서드
    def codeInput(self):
        while True:
            if super().setScode(input("식단코드를 입력하세요 : ")) :
                in_code = self.scode; break
            else: continue
        return in_code
    
    # 식단분류 입력 매서드 / 2023-04-11
    def pclassInput(self, in_code):
        super().setClass(in_code)
        pclass = self.pclass
        return pclass
    
    # 메뉴 입력 매서드 / 2023-04-11 
    def menuInput(self):
        while True:
            if super().setPmenu(input("메인메뉴을 입력하세요 : ")) : 
                in_pmain = self.pmenu; break
            else: continue
        while True:
            if super().setPmenu(input("국(음료)메뉴을 입력하세요 : ")) : 
                in_psoup = self.pmenu; break
            else: continue
        while True:
            if super().setPmenu(input("반찬1 메뉴을 입력하세요 : ")) : 
                in_psub1 = self.pmenu; break
            else: continue
        while True:
            if super().setPmenu(input("반찬2 메뉴을 입력하세요 : ")) : 
                in_psub2 = self.pmenu; break
            else: continue
        while True:
            if super().setPmenu(input("반찬3 메뉴을 입력하세요 : ")) : 
                in_psub3 = self.pmenu; break
            else: continue
        return in_pmain, in_psoup, in_psub1, in_psub2, in_psub3

    # 판매 수량 입력 매서드
    def qtyInput(self):
    # 수량 입력 
        while True:
            if super().setQty(input("식단 수량을 입력하세요 : ")) :
                in_qty = self.qty; break
            else: continue    
        return in_qty
    
    # 식단 가격 입력 매서드
    def priceInput(self):
        while True:
            if super().setPrice(input("식단가격을 입력하세요 : ")) :
                in_price = self.price; break
            else: continue
        return  in_price
      
    # 할인율 입력 매서드
    def discRateInput(self):
        while True:
            if super().setDiscRate(input("식단 할인율을 입력하세요 : ")) :
                in_discrate = self.discrate; break
            else: continue
        return  in_discrate

    # 입력 매서드 동시 호출 (식단명, 분류, 가격, 할인율)
    def userInput(self):
        return [self.nameInput(), self.priceInput(), self.discRateInput()]
     
     
#--------------------------
# FindSql클래스에서 분리 2023-03-07 / 상호호출배제원칙
class Read(UserInput):
    table = '' ; table_name = ''
    def __init__(self, table):
        super().__init__()
        self.table = table
        if self.table == 'p': self.table_name = '식단'
        elif self.table == 'm': self.table_name = '식단메뉴'
        else : self.table_name = '식단판매'
        
    def readAll(self) :
        print(f"<<<{self.table_name} 전체 목록 조회입니다>>>")
        rows = FindSql(self.table, 0).sqlFind()
        if self.table == 'p': 
            ShowTables().showProd(rows)
        elif self.table == 's':
            ShowTables().showSale(rows)
        elif self.table == 'm':
            ShowTables().showMenu(rows)
            
    # 테이블 조회
    # <변경사항> / 2023-02-20 CodeInspection 
    # 2023-03-07 매서드 위치 변경
    # 기존의 menu_planner, menu_sales 매서드 통합
    # self.table 조건문을 이용하여 두 테이블 분류
    def readOne(self, read_sel) :
        self.read_sel = read_sel
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()
                self.readAll() # 클래스 매개변수 활용하여 테이블의 전체목록 조회
                print(f"<<<{self.table_name}테이블 {self.read_sel} 조회 입니다>>>\n조회할 ",end='') 
                # 1) 식단코드에 해당하는 데이터를 가져올 경우
                if self.read_sel == '코드': 
                    in_code = super().codeInput()
                    rows = FindSql(self.table, 3, in_code).sqlFind()
                # 2) 식단명 해당하는 데이터를 가져올 경우
                elif self.read_sel == '식단명' : 
                    in_code = super().nameInput()
                    rows = FindSql(self.table, 4, in_code).sqlFind()
                elif self.read_sel == '분류' : 
                    in_code = super().nameInput()
                    rows = FindSql(self.table, 5, in_code).sqlFind()
                     
                # 2023-02-21 menu_planner, menu_sales테이블 각각의 출력문
                # 조건문을 이용하여 통합
                # 1) 조회할 데이터가 존재할 경우   
                if len(rows) > 0 :
                    os.system('cls')
                    print(f"===테이블 조회2({self.read_sel})===")
                    if self.table == 'p':
                        ShowTables().showProd(rows)
                        break
                    elif self.table == 's':
                        ShowTables().showSale(rows) 
                        break
                    elif self.table == 'm':
                        ShowTables().showMenu(rows) 
                        break
                # 2) 조회할 로우가 존재하지 않을경우
                else:
                    print(f"조회결과 입력한 {self.read_sel}에 맞는 식단이 없습니다")
                    continue             
                    
        except Exception as e :
            print('db 연동 실패 : ', e)
            conn.rollback()
            
        finally:
            cursor.close()                      
            conn.close()    
                         

#--------------------------
# 2023-03-08 사용자 입력 확인 클래스  
# 2023-03-11 로직 변경 / 비교연산자 삭제
class SelOpt() :
    def __init__(self, yesno) :
        self.option = yesno # 사용자가 입력한 값
        self.eng_lst = ['Y', 'N'] # 입력값 영어. (Key값으로 사용)
        alpha_lst = ['ㅛ', 'ㅜ'] # 입력값 한글. (Value값으로 사용)
        self.op_dict = dict(zip(self.eng_lst, alpha_lst)) # 입력값인 영어와 한글을 dict로 구성
        self.select = "" # 입력값 최종출력
        self.getOpt() # 클래스를 통해 객체를 만들 때 마지막 작업으로 getOption 메서드 실행
    
    # 작업옵션 획득 메서드.
    def getOpt(self) :
        if findall('[ㅏ-ㅣ]', self.option): # 한글을 입력했을 경우
            reop_dict = dict(map(reversed, self.op_dict.items()))                                                
            self.select = reop_dict.get(self.option, 0) 
            
        elif findall('[a-z|A-Z]', self.option): # 영문을 입력했을 경우
            self.select = self.option.upper()
    
    # 입력값 반환 메서드
    def startOpt(self) : 
        if self.select in self.eng_lst[0]: return True    # 리턴값 참
        elif self.select in self.eng_lst[1]: return False # 리턴값 False
        else: return 0                                    # 잘못 입력 시 0
        

#--------------------------
# 2023-02-18 SQL 로우 출력 클래스 
# 2023-03-09 showSale매서드 로직변경 / 판매금액 합계 코드 추가   
class ShowTables:
    # 식단 테이블 출력
    def showProd(self, rows):
        print(f"{fmt('식단코드',10,'l')}{fmt('분류',14,'l')}{fmt('식단명',22,'l')}{fmt('식단가격',11,'l')}{fmt('할인율',20,'l')}")
        print('-'*64)
        for row in rows:
            print(f"{fmt(row[0],10,'l')}{fmt(row[1],14,'l')}{fmt(row[2],22,'l')}{fmt(row[3],11,'l')}{fmt(row[4],20,'l')}")
    
    # 메뉴 테이블 출력        
    def showMenu(self, rows):
        print(f"{fmt('식단코드',10,'l')}{fmt('메인메뉴',14,'l')}{fmt('국(음료)',14,'l')}{fmt('반찬1',14,'l')}{fmt('반찬2',14,'l')}{fmt('반찬3',14,'l')}")
        print('-'*78)
        for row in rows:
            print(f"{fmt(row[0],10,'l')}{fmt(row[1],14,'l')}{fmt(row[2],14,'l')}{fmt(row[3],14,'l')}{fmt(row[4],14,'l')}{fmt(row[5],14,'l')}")
            
    # 판매 테이블 출력
    def showSale(self, rows):
        print(f"{fmt('No',6,'l')}{fmt('식단코드',10,'l')}{fmt('식단명',20,'l')}{fmt('판매등록일자',22,'l')}{fmt('판매수량',16,'l')}{fmt('총 판매가격',5,'l')}")
        print('-'*90)
        for row in rows :
            print(f"{fmt(row[0],6,'l')}{fmt(row[1],10,'l')}{fmt(row[2],20,'l')}{fmt(row[3],10,'l')}{float(fmt(row[4],7,'l')):20,.2f}{float(fmt(row[5],5,'l')):20,.2f}")
        print('-'*90)
        rows_amt = [row for row in rows] ; sum_amt = sum([rows_amt[i][5] for i in range(len(rows_amt))])
        print(f"{fmt('판매금액합계',66,'l')}{float(fmt(sum_amt,10,'l')):20,.2f}")


#--------------------------
# 2023-02-18 테이블 관리 클래스 / 2022-03-22 매서드 추가 / 2023-03-29 매서드 추가
# 2023-03-22 이력테이블 생성 매서드 추가 
# 2023-03-29 백업테이블 생성 매서드 추가     
class TableCreate:
    def __init__(self, table):
        self.table = table
        if self.table == 'p': self.prodCreate(), self.prodDetailCreate()
        elif self.table == 's': self.salesTableCreate()    
    
    # 식단 테이블 생성 매서드
    def prodCreate(self) :  
        try :
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            sql = """CREATE table if not exists menu_planner(
                pCode VARCHAR(4) PRIMARY KEY,
                pClass VARCHAR(20) NOT NULL,
                pName VARCHAR(20) NOT NULL,
                unitPrice INT NOT NULL,
                discountRate decimal(5,2) NOT NULL DEFAULT 0.00)
                """
            sqlAction(sql, True) ; self.prodHisCreate()
        except Exception as e :
            print("오류 : ",e)
            conn.rollback()
        finally :
            conn.close()
            cursor.close()
    
    # 식단 메뉴 테이블 생성 매서드
    def prodDetailCreate(self) :  
        try :
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            sql = """CREATE table if not exists menu_planner_detail(
                dCode varchar(4) NOT NULL,
                dMain varchar(20) NOT NULL,
                dSoup varchar(20) NOT NULL,
                dSub1 varchar(20) NOT NULL,
                dSub2 varchar(20) NOT NULL,
                dSub3 varchar(20) NOT NULL,
                PRIMARY KEY (dCode),
                FOREIGN KEY (dCode) REFERENCES menu_planner(pCode)
                ON DELETE CASCADE)
                """
            sqlAction(sql, True) ; self.prodDetailHisCreate()
        except Exception as e :
            print("오류 : ",e)
            conn.rollback()
        finally :
            conn.close()
            cursor.close()                
      
    # 판매 테이블 생성 매서드 
    def salesTableCreate(self) :  
        try :
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            sql = """CREATE table if not exists menu_sales(
                seqNo INT(10) NOT NULL AUTO_INCREMENT, 
                sCode VARCHAR(4) NOT NULL,
                sDate TIMESTAMP DEFAULT now() ON UPDATE CURRENT_TIMESTAMP,
                Qty INT NOT NULL,
                Amt decimal(12, 2) DEFAULT 0.0,
                PRIMARY KEY(seqNo,sCode),
                FOREIGN KEY (sCode) REFERENCES menu_planner(pCode)
                ON DELETE CASCADE)
                """
            sqlAction(sql, True)  ; self.salebackupCreate()
        except Exception as e :
            print("오류 : ",e)
            conn.rollback()
        finally :
            conn.close()
            cursor.close()
    
    # 2023-03-22 식단 이력 테이블 생성 매서드 
    def prodHisCreate(self):  
        try :
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            sql = """CREATE table if not exists menu_planner_history(
                seqNo int auto_increment,
                pCode varchar(4) not null, 
                pClass VARCHAR(20) not null,
                pName varchar(20) not null,
                unitPrice int not null,
                discountRate decimal(5,2) not null,
                Event varchar(20) not null,
                Pdate timestamp not null DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(seqNo,pCode)
                )"""
            sqlAction(sql, True)
                        
        except Exception as e :
            print("오류 : ",e)
            conn.rollback()
        finally :
            conn.close()
            cursor.close()
            
            
    # 2023-03-22 식단 메뉴 이력 테이블 생성 매서드 
    def prodDetailHisCreate(self):  
        try :
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            sql = """CREATE table if not exists menu_planner_detail_history(
                seqNo int auto_increment,
                dCode varchar(4) NOT NULL,
                dMain varchar(20) NOT NULL,
                dSoup varchar(20) NOT NULL,
                dSub1 varchar(20) NOT NULL,
                dSub2 varchar(20) NOT NULL,
                dSub3 varchar(20) NOT NULL,
                dEvent varchar(20) not null,
                dDate timestamp not null DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(seqNo,dCode))"""
            sqlAction(sql, True)
                        
        except Exception as e :
            print("오류 : ",e)
            conn.rollback()
        finally :
            conn.close()
            cursor.close()        
    
    # 2023-03-29 판매 삭제 관리 테이블 매서드       
    def salebackupCreate(self) :  
        try :
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            sql = """CREATE TABLE if not exists menu_sales_backup (
                seqNo int NOT NULL,
                sCode varchar(4) NOT NULL,
                sDate timestamp NOT NULL,
                Qty int NOT NULL,
                Amt decimal(12,2) not null,
                Event varchar(16) not null,
                Delete_Date timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (seqNo));
                """
            sqlAction(sql, True) # 2023-03-02 접속함수 
            self.saleViewCreate()
        except Exception as e :
            print("오류 : ",e)
            conn.rollback()
        finally :
            conn.close()
            cursor.close()
    
    # 2023-03-29 판매 삭제 조회 뷰 매서드        
    def saleViewCreate(self) :
        try :
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            sql = """CREATE VIEW menu_all_sales as
            SELECT seqNo, sCode, sDate, Qty, Amt
            FROM menu_sales 
            union
            SELECT seqNo, sCode, sDate, Qty, Amt
            FROM menu_sales_backup
            where Event = '단종'
            """
            sqlAction(sql, True) # 2023-03-02 접속함수  
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
        if self.table == 'p': self.table_name = 'menu_planner'
        elif self.table == 's' : self.table_name = 'menu_sales'
    
    def prodReset(self):
        prod_insert = [('a001', '일반식', '일반식1', '4500', '1.00'),('d001', '다이어트식', '연어스테이크', '6000', '12.00'),
                       ('a002', '일반식', '일반식2', '3200', '0.00'),('b001', '병원식', '병원식1', '4800', '0.00'),
                       ('b002', '병원식', '병원식2', '5500', '10.00'),('r001', '과체중식', '돈까스정식', '8800', '3.00'),
                       ('d002', '다이어트식', '호밀다이어트', '7000', '10.00'),('s001', '미분류', '저염식1', '3800', '1.00'),
                       ('r002', '과체중식', '떡볶이튀김','9000', '5.00'),('a003', '일반식', '일반식3','4700', '3.00')]
        # 식단 테이블 입력
        sql = "INSERT INTO menu_planner(pCode, pClass, pName, unitPrice, discountRate) VALUES(%s, %s, %s, %s, %s)"
        sqlAction(sql, True, False, prod_insert)
        # 식단 이력 테이블 입력
        sql = "INSERT INTO menu_planner_history(pCode, pClass, pName, unitPrice, discountRate, Event) VALUES (%s, %s, %s, %s, %s, 'Insert')"
        sqlAction(sql, True, False, prod_insert)
        
    def prodDetailReset(self):
        prod_detail_insert = [('a001', '숙주돼지볶음', '육개장', '연근샐러드', '무나물', '배추김치'),('d001', '연어샐러드', '탄산수', '구운양파', '레몬', '양상추샐러드'),
                       ('a002', '춘천닭갈비볶음', '북어국', '무쌈세트', '배추김치', '게맛살튀김'),('b001', '잡채', '동태탕', '배추김치', '버섯간장조림', '연두부'),
                       ('b002', '떡갈비', '시금치된장국', '배추김치', '감자조림', '브로콜리'),('r001', '등심돈까스', '우동', '양배추샐러드', '깍두기', '고추절임'),
                       ('d002', '호밀빵', '두유', '달걀후라이', '방울토마토', '양상추샐러드'),('s001', '버섯조림', '콩나물국', '호박무침', '백김치', '고사리무침'),
                       ('r002', '떡볶이', '어묵','고구마튀김', '순대', '김밥'),('a003', '탕수육', '짬뽕탕','마늘쫑무침', '열무김치', '된장배추무침')]
        sql = "INSERT INTO menu_planner_detail(dCode, dMain, dSoup, dSub1, dSub2, dSub3) VALUES(%s, %s, %s, %s, %s, %s);"
        sqlAction(sql, True, False, prod_detail_insert)
        sql = "INSERT INTO menu_planner_detail_history(dCode, dMain, dSoup, dSub1, dSub2, dSub3, dEvent) VALUES (%s, %s, %s, %s, %s, %s, 'Insert');"
        sqlAction(sql, True, False, prod_detail_insert)    
    
    
    def saleReset(self):
        sale_insert = [('a001', '20220922', '1', '4500'),('a002', '20220922', '2', '6400'),('a002', '20220922', '3', '9600'),('a003', '20220922', '1', '4700'),
                       ('a003', '20220922', '2', '9400'),('a003', '20220922', '3', '14100'),('a003', '20220922', '4', '18800'),('b001', '20220922', '1', '4800'),
                       ('b001', '20220922', '2', '9600'),('b001', '20220922', '3', '14400'),('b001', '20220922', '4', '19200'),('b002', '20220922', '1', '5500'),
                       ('b002', '20220922', '2', '11000'),('b002', '20220922', '3', '16500'),('b002', '20220922', '4', '22000'),('d001', '20220922', '1', '6000'),
                       ('d001', '20220922', '2', '12000'),('d001', '20220922', '3', '18000'),('d001', '20220922', '4', '24000'),('d002', '20220922', '1', '7000'),
                       ('d002', '20220922', '2', '14000'),('d002', '20220922', '3', '21000'),('d002', '20220922', '4', '28000'),('r001', '20220922', '1', '8800'),
                       ('r001', '20220922', '2', '17600'),('r001', '20220922', '3', '26400'),('r001', '20220922', '4', '35200'),('r002', '20220922', '1', '9000'),
                       ('r002', '20220922', '2', '18000'),('r002', '20220922', '3', '27000'),('r002', '20220922', '4', '36000'),('s001', '20220922', '1', '3800'),
                       ('s001', '20220922', '2', '7600'),('s001', '20220922', '3', '11400'),('s001', '20220922', '4', '15200')]
        sql = "INSERT INTO menu_sales(sCode, sDate, Qty, Amt) VALUES(%s, %s, %s, %s);"
        sqlAction(sql, True, False, sale_insert)
        
        
    def tableReset(self):
        # 테이블 데이터 확인
        find_rows = FindSql(self.table, 0).sqlFind()
        # 테이블 전체 출력
        Read(self.table).readAll()

        # 1) 테이블 데이터가 존재하는 경우
        if find_rows : 
            print(f'\n<<<{self.table_name} 테이블 초기화입니다>>>')
            while True:
                yesNo = input('모두 삭제하고 초기화 하시겠습니까?(y/n) : ')
                if SelOpt(yesNo).startOpt():  
                    try:
                        conn = pymysql.connect(**config)
                        cursor = conn.cursor()

                        # 테이블 전체 내용 삭제
                        sql = f"DELETE FROM {self.table_name}"
                        sqlAction(sql, True)
                        # 대상이 sales 테이블일경우 seqNo가 1부터 시작되도록 초기화
                        if self.table == 'p' :
                            sql = f"DELETE FROM {self.table_name}_history" # 2023-03-21 / 접속함수 실행
                            sqlAction(sql, True)
                            sql = f"DELETE FROM {self.table_name}_detail_history" # 2023-03-21 / 접속함수 실행
                            sqlAction(sql, True)
                            sql = f"ALTER TABLE {self.table_name}_history auto_increment = 1" # 2023-03-02 / seqNo 컬럼 초기화
                            sqlAction(sql, True)
                            sql = f"ALTER TABLE {self.table_name}_detail_history auto_increment = 1" # 2023-03-02 / seqNo 컬럼 초기화
                            sqlAction(sql, True) 
                            
                        elif self.table == 's' :
                            sql = f"DELETE FROM {self.table_name}_backup" # 2023-03-21 / 접속함수 실행
                            sqlAction(sql, True)
                            sql = f"ALTER TABLE {self.table_name}_backup auto_increment = 1" # 2023-03-02 / seqNo 컬럼 초기화
                            sqlAction(sql, True) 
                            sql = "ALTER TABLE menu_sales auto_increment = 1"
                            sqlAction(sql, True) # 2023-03-02 / 접속함수 실행
                            print(f"{self.table_name} 테이블 초기화에 성공했습니다.")
                            
                        yesNo = input('식단테이블에 임시 데이터를 추가하시겠습니까?(y/n) : ')
                        if SelOpt(yesNo).startOpt() and self.table == 'p': self.prodReset(), self.prodDetailReset()
                        elif SelOpt(yesNo).startOpt() and self.table == 's': self.saleReset()
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