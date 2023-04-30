# product 테이블에 대한 제품의 CRUD 및 sales 테이블과 product 테이블을 활용하여 판매기록 관리를 위한 CRUD 시스템
# <변경사항>
# SelOpt 클래스 로직 변경

import os
import sys
from re import findall, match   # 정규 표현식 사용을 위한 라이브러리 (findall, match) / 2023-02-07
import pymysql                  # MySQL데이터베이스를 사용하기 위한 라이브러리 / 2023-02-07
from wcwidth import wcswidth    # 2byte 글자 간격 맞춤을 제공하는 라이브러리 / 2023-02-09
import pandas as pd             # DataFrame을 만들어 활용하기 위한 라이브러리 / 2023-02-14
import matplotlib.pyplot as plt # 그래프 출력 및 세부 설정을 위한 라이브러리 / 2023-02-14
import calendar as cd           # 날짜 확인 캘린더 라이브러리 / 2023-02-28

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


# DB의 row를 프린트하는 클래스
class ShowTables:
    # 제품 테이블 출력
    def showProd(self, rows):
        print(f"{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('제품가격',11,'l')}{fmt('할인율',20,'l')}")
        print('-'*60)
        for row in rows:
            print(f"{fmt(row[0],10,'l')}{fmt(row[1],20,'l')}{fmt(row[2],11,'l')}{fmt(row[3],20,'l')}")
    # 판매 테이블 출력
    def showSale(self, rows):
        print(f"{fmt('No',6,'l')}{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('판매등록일자',25,'l')}{fmt('판매수량',16,'l')}{fmt('총 판매가격',5,'l')}")
        print('-'*60)
        for row in rows :
            print(f"{fmt(row[0],6,'l')}{fmt(row[1],10,'l')}{fmt(row[2],20,'l')}{fmt(row[3],28,'l')}{fmt(row[4],13,'l')}{fmt(row[5],5,'l')}")


#-------------------------- 
### <요구사항-5> 반영 ###
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
# 파일 필터 클래스 / 2023-02-21
# 파일 저장 및 로드 시 사용자 입력값 필터
class FileFilter():
    def __init__(self):
        self.inputFilter_result = False
        self.file_path = ''
        self.file_name = ''
        
    # 파일 경로 필터 매서드
    def setFilePath(self, file_path):
        # 1) 현재 경로 입력
        if file_path == '' or len(file_path) < 0:
            file_path = os.path.dirname(os.path.abspath(__file__))
            
        # 2) 경로 직접 입력 
        else: file_path =file_path.replace('\\','/')
        
        self.inputFilter_result = True
        self.file_path = file_path
        return self.inputFilter_result
                
    # 파일 이름 필터 매서드            
    def setFileName(self, file_name):
        # 1) 파일명에 빈칸을 입력한 경우
        if file_name == '' or len(file_name) < 0:
            print("파일명을 입력해야 합니다. 다시 입력해주세요.")
            self.inputFilter_result = False
        else:
            chk_extention = ['.txt','.csv'] ; chk = 0
            chk = [chk == 1 for i in chk_extention if i in file_name]
            # 파일명 확인
            if chk == 0:                       
                print("파일명에 확장자를 입력해야 합니다.")
                self.inputFilter_result = False
            else:
                self.inputFilter_result = True
                self.file_name = file_name    
        
        return self.inputFilter_result
  
  
#--------------------------
# 파일 사용자 입력 클래스 / 2023-02-21
# 사용자 입력 값 호출   
class FileInput(FileFilter):
    def __init__(self):
        super().__init__()
    # 파일 경로 입력 매서드
    def pathInput(self):
        while True:
            print("파일의 경로를 입력해주세요")
            if super().setFilePath(input("파일 경로 : ")) :
                in_file_path = self.file_path
                break
            else:
                continue
        return in_file_path
    
    # 파일 이름 입력 매서드
    def nameInput(self):
        while True:
            print("파일의 이름를 입력해주세요")
            if super().setFileName(input("파일 이름 : ")) :
                in_file_name = self.file_name
                break
            else:
                continue
        return in_file_name
    

#--------------------------
# 파일 내용 전처리 클래스 / 2023-02-21
# 불러온 파일 내용을 활용하기 위한 전처리 
class FilePreProcessing(FileInput):
    def __init__(self):
        super().__init__()
        self.full_text = ''
              
    def readFile(self):
        try:
            print('DB에 등록할',end=''); file_path = super().pathInput()
            print('DB에 등록할',end=''); file_name = super().nameInput()
            # file_path = 'D:\\Download\\테스트 공간' ; file_name = 'sales_2.txt' / 테스트 코드
            t1 = open(f"{file_path}/{file_name}", mode = 'r', encoding='utf8') # 한글 파일 인코딩 UTF8
            text = t1.read()
            # 텍스트 파일 전처리(구분자 별로 전처리)
            temp1_t1 = findall('[^,\n]+',text)
            full_text = [(temp1_t1[i],)+(temp1_t1[i+1],)+(temp1_t1[i+2],) for i in range(len(temp1_t1)) if i % 3 == 0]
            self.full_text = full_text
        except Exception as e:
            print(e, '\n경로 : ', f"{file_path}/{file_name}", '- 해당 경로에 입력한 파일이 없습니다. 다시 확인해주세요.')
        
        finally :
            t1.close()
            return self.full_text # 텍스트 파일 반환 
        
    # 2023-03-02 / salePreProcessing 코드 매서드화    
    def saleReadFile(self):
        try:
            print('사용할',end=''); file_path = super().pathInput()
            print('사용할',end=''); file_name = super().nameInput()
            t1 = open(f'{file_path}/{file_name}', mode = 'r', encoding='utf8')
            test_t1 = t1.read()
            temp1_t1 = findall('[^,\n]+',test_t1)
            full_text = [((temp1_t1[i+1],)+(temp1_t1[i+3],)+(temp1_t1[i+4],)+(temp1_t1[i+5],)) for i in range(len(temp1_t1)) if i % 6 == 0 ]
            self.full_text = full_text
        except Exception as e:
            print(e,'\n경로 : ', file_path, '해당 경로에 입력한 파일이 없습니다. 다시 확인해주세요.')
        
        finally :
            t1.close()
            return self.full_text # 텍스트 파일 반환 
        
            
#--------------------------
# 테이블 등록을 위한 필터 클래스 / 2023-02-21
# sales테이블 등록을 위한 연월일, 제품코드 필터 
class FileTextFilter():
    def __init__(self):
        self.content = ''
        self.code = ''
        self.st = ''
# 2023-02-28 calender라이브러리 활용한 매서드로 변경 / 이현준 코드 참조        
# 연월일 필터 매서드
# 데이터 전처리 시 년월일이 올바른 지 확인
# 윤년, 월, 일 확인 
    def dateFilter(self, st) :
        self.dayValueFilter = False
        year = st[:4] ; month = st[4:6] ; day = st[6:] # 데이터 년, 월, 일 분배
        self.year, self.month, self.day = map(int, (year, month, day)) # int함수 적용 
        return self.dateChk()
            
    def dateChk(self) :
        try :
            last = cd.monthrange(self.year, self.month)[1]
            if self.day > last or self.day == 0 : self.dayValueFilter = False
            else : self.dayValueFilter = True
            return self.dayValueFilter
        except :
            return False
    
    # 제품테이블에 제품코드 존재 확인
    def codeFilter(self, content):
        try:
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            ### <요구사항-4> 반영 ###      
            chk_ls = [content[i] for i in range(len(content)) if sqlAction(f"SELECT unitPrice FROM product WHERE pCode = '{content[i][0]}'")]

            return chk_ls # 필터링 한 값 리턴
        
        except Exception as e:
            print('Error 발생 :', e)
            conn.rollback()

        finally :
            conn.close()
            cursor.close()
            
    # 기존 테이블 중복 확인
    def tableChk(self, contents):
        try:
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            sql = f"SELECT sCode, date_format(sDate,'%Y%m%d') as date, Qty FROM sales ORDER BY seqNo"
            test_rows = sqlAction(sql)
            data = tuple(map(str, [i for content in contents for i in content])) # 매개변수 전처리 / ### <요구사항-4,6> 반영 ###
            ### <요구사항-6> 반영 ###
            table_chk = [1 for i in range(len(test_rows)-len(contents)+1) if tuple(map(str, [chk_db for chk_dbs in test_rows[0+i:len(contents)+i] for chk_db in chk_dbs])) == data][0] 
            
            return table_chk
                
        except Exception as e:
            print('Error 발생 :', e)
            conn.rollback()

        finally :
            conn.close()
            cursor.close()        

#--------------------------
# 외부파일 추가 클래스
# 파일을 DB에 등록하기 위한 기능        
class FileInsert(FilePreProcessing, FileTextFilter):    
    def __init__(self):
        super().__init__()
        self.fileInsert() # fileInsert 매서드 자동 호출

    def fileInsert(self):
        try:
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            print(f'\n<<<제품 테이블에 외부 파일 등록입니다>>>')
            contents = super().readFile()
            
            # 1) 년월일 필터 ### <요구사항-4> 반영 ### 
            content_year_chk = [content for content in contents if FileTextFilter().dateFilter(content[1])]

            # 2) 제품코드 필터
            content_code_chk = super().codeFilter(content_year_chk)
            
            # 3) 테이블 중복 확인 필터
            content_duplicate_chk = super().tableChk(content_code_chk)

            # 4) 테이블에 등록
            if content_duplicate_chk == 1:
                print("데이터를 추가하지 못했습니다.\n이미 존재하는데이터입니다.")
                for i in range(len(content_code_chk)):
                    sql = f"SELECT unitPrice FROM product WHERE pCode = '{content_code_chk[i][0]}'"
                    rows = sqlAction(sql)
                    code = content_code_chk[i][0]   #--> 제품 코드
                    unitPrice = rows[0][0]          #--> 제품 가격
                    date = content_code_chk[i][1]   #--> 제품 날짜
                    qty = content_code_chk[i][2]    #--> 제품 수량
                    total_price = int(unitPrice) * int(qty)
                    if content_duplicate_chk == 0:
                        sql = f"INSERT INTO sales(sCode, sDate, Qty, Amt) VALUES('{code}','{date}','{qty}','{total_price}')" 
                        sqlAction(sql, True)

            else:
                print("데이터를 추가완료 했습니다")

        except Exception as e:
            print('Error 발생 :', e)
            conn.rollback()

        finally :
            conn.close()
            cursor.close()
            

 
#--------------------------      
# 데이터 시각화
# sales테이블의 전체 데이터를 가져온 후 년월일, 제품코드를 필터링합니다.
# 데이터 기간은 2023년 2월 한달 1066, 1067라인에서 수정 가능
class GraphsPreProcessing(FilePreProcessing, FileTextFilter):
    def __init__(self):
        super().__init__()
        self.saleDataCreate()
    
    # sales테이블 텍스트파일로 저장
    # 2023-03-03 조건문 추가 
    def saleDataCreate(self):
        while True:
            yesNo = input('sales테이블을 텍스트파일로 저장하시겠습니까>(y/n) : ')
            if SelOpt(yesNo).startOpt(): 
                rows = FindSql('s',0).sqlFind()
                ls_t1 = [row[:6] for row in rows]
                df = pd.DataFrame(ls_t1)
                print("<<<테이블 데이터를 텍스트 파일로 저장합니다. 구분자: ',' >>>")
                print('저장할',end=''); path = super().pathInput()
                print('저장할',end=''); file_name = super().nameInput()
                df.to_csv(f'{path}/{file_name}', sep = ',', header = False, index=False)
                break
            elif SelOpt(yesNo).select == 'N':
                print('저장을 취소합니다.')
                break
            else:
                print('잘못입력했습니다. 다시 입력해주세요.')
                continue
                
        
    # 데이터 프레임 만들기 위한 전처리 매서드        
    def salePreProcessing(self):
        try:
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            contents = super().saleReadFile() 

            # 1) 년월일 필터 / 2023-03-03 년월일 필터 변경 적용 ### <요구사항-4> 반영 ###
            content_year_chk = [content for content in contents if FileTextFilter().dateFilter(content[1])]

            # 2) 제품코드 필터
            content_code_chk = super().codeFilter(content_year_chk)

            # 3) 데이터 프레임화
            df = pd.DataFrame(content_code_chk)
            df.columns = ['Code', 'Date', 'Qty', 'Amt'] # 데이터 프레임 컬럼 추가

            # 4) 데이터에 제품명 추가후 데이터 프레임
            sql = "SELECT pCode, pName FROM product"
            rows = sqlAction(sql) # 2023-03-03 접속함수 사용
            df_name = pd.DataFrame(rows)
            df_name.columns = ['Code','Name']
            df_all = pd.merge(df, df_name, how='inner', on = 'Code')
            
            return df_all # 완성된 데이터프레임 
        
        except Exception as e:
            print('Error 발생 :', e)
            conn.rollback()
        
        finally :
            conn.close()
            cursor.close()

    # 데이터프레임 그래프 표현 매서드
    def saleGraphShow(self, sel):
        # 데이터 시각화 전처리
        # 1) 필드의 데이터타입 인트타입으로 변경) 
        df_all = self.salePreProcessing()
        df_all['Qty'] = pd.to_numeric(df_all['Qty'])
        df_all['Amt'] = pd.to_numeric(df_all['Amt'])

        # 2) 날짜필드의 데이터타입 날짜타입으로 변경 
        df_all['Date'] = pd.to_datetime(df_all['Date'])

        # 3) 기간 설정 / (2023년 2월) 추후에 Input으로 날짜 변경 가능
        set_time1 = pd.Timestamp(2023, 2, 1, 8, 00, 0) # 년, 월, 일, 시, 분, 초
        set_time2 = pd.Timestamp(2023, 2, 28, 23, 59, 59)
        test_data = df_all[(df_all['Date']>set_time1)&(df_all['Date']<set_time2)].reset_index(drop=True)

        # 그래프 기능 실행
        # 1번 실행(날짜 별 판매금액)
        if sel == 1:
            test_data['Day'] = test_data['Date'].dt.day
            df_day = test_data.groupby(['Day']).sum()
            plt.rc("font", family='Malgun Gothic')                  #한글 폰트 설정
            plt.title("2023년 02월 14일 시간별 총 판매합계")        #그래프에 제목 넣기
            plt.bar(df_day.index,df_day['Amt'], label = '판매량')   # 막대그래프 생성
            plt.xticks(fontsize = 10)                               # x축 폰트 사이즈
            plt.xticks(rotation=45)                                 # x축 눈금 회전
            plt.xlim(13, 16)                                        # x축 간견
            plt.xlabel('판매 시간대')                               # x축 레이블
            
        # 2번 실행(모델 별 판매금액)
        elif sel == 2:
            df_Name = test_data.groupby(['Name']).sum()
            plt.rc("font", family='Malgun Gothic')                  #한글 폰트 설정
            plt.title("2023년 02월 14일 제품별 판매합계")           #그래프에 제목 넣기
            plt.bar(df_Name.index,df_Name['Amt'], label = '판매량') # 막대그래프 생성
            plt.xticks(fontsize = 10)                               # x축 폰트 사이즈
            plt.xticks(rotation=45)                                 # x축 폰트 사이즈
            plt.xlabel('제품명')                                    # x축 눈금 회전
            plt.ylabel('판매가격')                                  # y 축 레이블
            
        plt.legend()                                                # 범례 표시
        yesNo = input('그래프를 저장하시겠습니까>(y/n) : ')
        while True:
            if SelOpt(yesNo).startOpt():  
                print('그래프를 저장 할',end=''); path = super().pathInput()
                plt.savefig(path) # 파일로 저장
                break
            elif SelOpt(yesNo).select == 'N':
                print('저장을 취소합니다.')
                break
            else:
                print('잘못입력했습니다. 다시 입력해주세요.')
                continue
        
        plt.show() # 그래프 그리기


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
        if stchk not in 'SQLInjecsion': st = False
        return st       
        
    # 1. 인덱스(순서) 필터
    def setNo(self, no):
        # 0) SQL Injecsion 블랙리스트 매서드 / 2023-02-13 / 2023-03-02 
        no = self.sqlBlackList(no)
        # 1) 입력한 값에 예약어, 특수문자가 있을 경우
        if no == False:
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
        if scode == False:
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
        if qty == False:
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
        if pname == False:
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
        if price == False:
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
        if discrate == False:
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
        ls = []
        ls.append(self.nameInput())
        ls.append(self.priceInput())
        ls.append(self.discRateInput())
        return ls
    
#--------------------------
# SQL관리 클래스
# <변경사항> / 2023-02-20
# ProdFind클래스와 SalFind클래스 병합
class FindSql():
    table = '' ; table_name = ''
    def __init__(self,table, find_sel, find_in_data = ''): # 매개변수 (테이블, 찾을 SQL번호) / ### <요구사항-3> 반영 ### 
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

# FindSql에서 분리 2023-03-07
class Read(UserInput):
    table = '' ; table_name = ''
    def __init__(self, table):
        super().__init__()
        self.table = table
        if self.table == 'p': self.table_name = '제품'
        else : self.table_name = '판매'
        
    def ReadAll(self) :
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
    def ReadOne(self, read_sel) :
        self.read_sel = read_sel
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()
                self.ReadAll() # 클래스 매개변수 활용하여 테이블의 전체목록 조회
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
                    print(f"===테이블 조회2({self.read_sel})===")
                    if self.table == 'p':
                        ShowTables().showProd(rows)
                        break
                    elif self.table == 's':
                        ShowTables().showSale(rows)
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

    
#--------------------------
#   제품 관리 기능 시작   #
#--------------------------
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
                    if SelOpt(yesNo).startOpt():   
                        sql = f"DELETE FROM product WHERE pCode = '{in_code}'" # 테이블 레코드 삭제 SQL 
                        sqlAction(sql, True) # 2023-03-02 접속함수 실행      
                        print('삭제 성공했습니다.')
                        Read('p').ReadAll() 
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
                    if SelOpt(yesNo).startOpt(): 
                        print("<<<수정할 내용을 입력하세요.>>>")
                        iValue = super().userInput()
                        sql = f"UPDATE product SET pName = '{iValue[0]}', UnitPrice = '{iValue[1]}', discountRate ='{iValue[2]}' WHERE pCode = '{in_code}'"
                        sqlAction(sql, True) # 2023-03-02 접속함수 실행      
                        print("수정을 완료했습니다\n수정 결과입니다")
                        Read('p').ReadAll() 
                        break
                    elif SelOpt(yesNo).select == 'N':
                        print("수정을 취소했습니다.")
                        break
                    else:
                        print('잘못입력했습니다. 다시 입력해주세요.')
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
            

#--------------------------             
# 테이블 리셋 클래스 / 2023-02-15
class TableReset:
    table = ''
    table_name = ''
    def __init__(self, table):
        self.table = table
        if self.table == 'p':
            self.table_name = 'product'
        elif self.table == 's' :
            self.table_name = 'sales'
        
    def tableReset(self):
        # 테이블 데이터 확인
        find_rows = FindSql(self.table, 0).sqlFind()
        # 테이블 전체 출력
        Read(self.table).ReadAll()

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
                        sqlAction(sql, True) # 2023-03-02 / 접속함수 실행 

                        # 대상이 sales 테이블일경우 seqNo가 1부터 시작되도록 초기화
                        if self.table == 's' :
                            sql = "ALTER TABLE sales auto_increment = 1"
                            sqlAction(sql, True) # 2023-03-02 / 접속함수 실행
                        print("초기화 성공했습니다.")

                    except Exception as e :
                        print('db 연동 실패 : ', e)
                        conn.rollback()

                    finally:
                        cursor.close()
                        conn.close()
                        break
                # 사용자 확인문에서 y를 입력하지 않았을 경우
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
#   판매 관리 기능 시작   #
#--------------------------
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
                        sql = f"INSERT INTO product(pCode, pName, UnitPrice, discountRate) VALUES('{in_code}','{iValue[0]}', '{iValue[1]}', '{iValue[2]}')" 
                        sqlAction(sql, True)
                        print("제품등록을 성공했습니다.")
                        break

                    # 2) product 테이블에 해당 제품코드의 상품이 존재하는 경우
                    else :
                        qty = super().qtyInput() # 제품 가격 출력 / 2023-02-08 / ### <요구사항-1> 반영 ###
                        sql = f"INSERT INTO sales(sCode, Qty, Amt) VALUES('{in_code}','{qty}', '{getPrice(in_code, qty)}')" 
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
                Read('s').ReadAll() 
                print('삭제할 데이터의 ',end='') 
                in_code = super().codeInput() 
                rows = FindSql('s', 3, in_code).sqlFind()
                # 1) 제품코드가 존재하는 경우
                if rows : 
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
                                sql = f"DELETE FROM sales WHERE seqNo = '{in_no}'"
                                sqlAction(sql, True) # 2023-03-02 접속함수 실행         
                                print('삭제 성공했습니다.')
                                Read('s').ReadAll()
                                break
                            # 판매 확인문 취소 입력
                            elif SelOpt(yesNo).startOpt() and len(rows1) == 0:
                                print("<<<조회한 목록에 입력한 No가 존재하지 않습니다.>>>")
                                os.system("pause")
                                continue
                            else:
                                print("<<<삭제를 취소했습니다.>>>")
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
                Read('s').ReadAll() # 전체 데이터 출력
                print('<<<판매기록을 수정합니다>>>\n수정할 데이터의 ',end='')
                in_code = super().codeInput() # 제품코드 입력 매서드 호출
                rows = FindSql('s', 3, in_code).sqlFind()

                # SELECT 쿼리 실행결과가 있는 경우               
                if rows : 
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
                        sql = f"UPDATE sales SET Qty = '{in_qty}', Amt = '{getPrice(in_code ,in_qty)}' WHERE seqNo = '{in_no}'"
                        sqlAction(sql, True) # 2023-03-02 /접속함수 실행       
                        print("<<<수정을 완료했습니다>>>\n<<<수정 결과입니다>>>")
                        Read('s').ReadAll()
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
# 테이블 생성 클래스 /2023-02-20
class TableCreate:
    # 테이블 생성 함수1(product)    
    def productTableCreate(self) :  
        try :
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            sql = """
            CREATE table if not exists product (
            pCode VARCHAR(4) PRIMARY KEY ,
            pName VARCHAR(20) NOT NULL,
            unitPrice INT NOT NULL,
            discountRate decimal(5,2) NOT NULL DEFAUL 1.00)
            """
            sqlAction(sql, True)
        except Exception as e :
            print("오류 : ",e)
            conn.rollback()
        finally :
            conn.close()
            cursor.close()        
      
    # 테이블 생성 함수2(sales)
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
# 접속함수 
# <변경사항> 2023-02-28
# FindSql 클래스에서 분리
def sqlAction(sql, com= '') : # 매개변수 : sql문, Commit 결정
    try :
        conn = pymysql.connect(**config)    
        cursor = conn.cursor()
        cursor.execute(sql)
        if com :
            conn.commit()                
        return cursor.fetchall()            
    except Exception as e :                 
        print('db 연동 실패 : ', e)         
        conn.rollback()                     
    finally:                                
        cursor.close()                      
        conn.close()


#--------------------------
# 계산함수 
# <변경사항> 2023-03-02
# 매서드마다 사용하던 계산을 함수로 설계             
def getPrice(in_Code, qty):
    sql = f"SELECT unitPrice, discountRate FROM product WHERE pCode = '{in_Code}'" # product 테이블에서 row_data에 맞는 제품가격을 불러온다.
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
# 시스템 실행
if __name__ == "__main__" :
    t0 = TableCreate()
    t0.productTableCreate() # 테이블이 없는 경우 product테이블 생성 / 2023-02-17
    t0.salesTableCreate()   # 테이블이 없는 경우 sales테이블 생성 / 2023-02-17
    
    while True:
        os.system('cls')
        print("---관리 시스템 실행---")
        print("제품  관리  실행 : 1 ")
        print("판매  관리  실행 : 2 ")
        print("데이터 관리 실행 : 3 ")
        print("서비스      종료 : 0 ")
        sys_sel = int(input("작업을 선택하세요 : "))
        
        # 제품 관리 서비스
        if sys_sel == 1:
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
            
        # 판매 관리 서비스
        elif sys_sel == 2:    
            while True:
                os.system('cls')
                print("---판매관리---")
                print("판매    등록 : 1 ")
                print("판매목록조회 : 2 ")
                print("코드별  조회 : 3 ")
                print("제품명별조회 : 4 ")
                print("판매    수정 : 5 ")
                print("판매    삭제 : 6 ")
                print("판매관리종료 : 9 ")
                print("시스템  종료 : 0 ")
                sel = int(input("작업을 선택하세요 : "))
                c0 = SaleFunc()
                if sel == 1 :
                    c0.saleCreate()
                    os.system("pause")
                elif sel == 2 :
                    Read('s').ReadAll()
                    os.system("pause")
                elif sel == 3 :
                    Read('s').ReadOne('코드')
                    os.system("pause")
                elif sel == 4 :
                    Read('s').ReadOne('제품명')
                    os.system("pause")
                elif sel == 5 :
                    c0.saleUpdate()
                    os.system("pause")
                elif sel == 6 :
                    c0.saleDelete()
                    os.system("pause")
                elif sel == 9 :
                    print("판매관리를 종료합니다. ") 
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
        
        # 데이터 추가 서비스
        elif sys_sel == 3:
            while True:
                os.system('cls')
                print("---데이터 관리---")
                print("테이블 데이터 삭제 : 1 ")
                print("외부  데이터  등록 : 2 ")
                print("날짜  별  판매금액 : 3 ")
                print("모델  별  판매금액 : 4 ")
                print("데이터  관리  종료 : 9 ")
                print("시스템        종료 : 0 ")
                sel = int(input("작업을 선택하세요 : "))
                if sel ==  1:
                    print('제품테이블 : p / 판매테이블 : s')
                    table_sel = input('삭제하실 테이블을 입력하세요.')
                    c0 = TableReset(table_sel)
                    c0.tableReset()
                    os.system("pause")
                elif sel == 2 :
                    FileInsert()
                    os.system("pause")
                elif sel == 3 :
                    c3 = GraphsPreProcessing()
                    c3.saleGraphShow(1)
                    os.system("pause")
                elif sel == 4 :
                    c4 = GraphsPreProcessing()
                    c4.saleGraphShow(2)
                    os.system("pause")
                elif sel ==  8:
                    print("Test ")
                    FilePreProcessing().readFile()
                    os.system("pause")
                    os.system('cls')
                    break
                elif sel == 9 :
                    print("데이터 관리를 종료합니다. ")
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
        
        # 시스템 종료
        elif sys_sel == 0:
            print("시스템을 종료합니다. ") 
            os.system("pause")
            os.system('cls')
            sys.exit(0)
            
        else :
            print("잘못 선택했습니다. ")
            os.system("pause")