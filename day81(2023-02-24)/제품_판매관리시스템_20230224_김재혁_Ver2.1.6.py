# product 테이블에 대한 제품의 CRUD 및 sales 테이블과 product 테이블을 활용하여 판매기록 관리를 위한 CRUD 시스템
# 버전 변경사항
# GraphsPreProcessing 클래스 상속 처리 
# 학습자 메일2의 1번 해결
# <할것>
# 학습자메일 1번의 조정 / 학습자메일 2번 전체
# - 1번 : 코드 중복 사용 / 클래스 단일원칙 어김
# - 2번 : 제품 조회 시 전역변수, 지역변수 오류 / 제품 수정 시 필터 오류
import os
import sys
from re import findall, match   # 정규 표현식 사용을 위한 라이브러리 (findall, match) / 2023-02-07
import pymysql                  # MySQL데이터베이스를 사용하기 위한 라이브러리 / 2023-02-07
from wcwidth import wcswidth    # 2byte 글자 간격 맞춤을 제공하는 라이브러리 / 2023-02-09
import pandas as pd             # DataFrame을 만들어 활용하기 위한 라이브러리 / 2023-02-14
import matplotlib.pyplot as plt # 그래프 출력 및 세부 설정을 위한 라이브러리 / 2023-02-14

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
# 2023-02-21 / 외부 파일 등록 기능 모듈화
# [29 ~ 431]라인 알파벳 순서가 안맞는 이유 
# 클래스를 알파벳 순으로 정의 후 상속을 하려고 하니
# 클래스가 정의되어 있지않다는 오류가 발생했습니다. 
# 클래스 상속을 위해 부득이하게 정렬 순서를 어김
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
        else:    
            file_path =file_path.replace('\\','/')
        
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
            for i in chk_extention:
                # 2-1) 파일명에 확장자를 입력하지 않은 경우
                if i not in file_name:
                    pass
                # 2-2) 파일명에 확장자를 정상적으로 입력한 경우
                else:
                    chk = 1
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
            # print('DB에 등록할',end=''); file_path = super().pathInput()
            # print('DB에 등록할',end=''); file_name = super().nameInput()
            file_path = "D:/Download/테스트 공간" ; file_name = "sales_2.txt"
            path = f"{file_path}/{file_name}"
            t1 = open(path, mode = 'r', encoding='utf8') # 한글 파일 인코딩 UTF8
            text = t1.read()
            # 텍스트 파일 전처리(구분자 별로 전처리)
            temp1_t1 = findall('[^,\n]+',text)
            full_text = [(temp1_t1[i],)+(temp1_t1[i+1],)+(temp1_t1[i+2],) if i % 3 == 0 else '' for i in range(len(temp1_t1))]
            # for i in range(len(temp1_t1)):
                # if i % 3 == 0:
                    # full_text.append((temp1_t1[i],)+(temp1_t1[i+1],)+(temp1_t1[i+2],))
            print(full_text)
            # self.full_text = full_text 
                     
        except Exception as e:
            print(e)
            print('경로 : ', path, '해당 경로에 입력한 파일이 없습니다. 다시 확인해주세요.')
        
        finally :
            t1.close()
            return full_text # 텍스트 파일 반환 
        
            
#-------------------------- 
# 테이블 등록을 위한 필터 클래스 / 2023-02-21
# sales테이블 등록을 위한 연월일, 제품코드 필터 
class FileTextFilter():
    def __init__(self):
        self.content = ''
        self.code = ''
        self.st = ''
# 연월일 필터 매서드
# 데이터 전처리 시 년월일이 올바른 지 확인
# 윤년, 월, 일 확인 
    def yearChk(self, st) :
        year = int(st[:4])   # 텍스트 파일의 연도
        month = int(st[4:6]) # 텍스트 파일의 월
        day = int(st[6:8])   # 텍스트 파일의 일
        year_st ='평년'
    
        #--윤년체크 시작 
        ls_month = [31,28,31,30,31,30,31,31,30,31,30,31]
        if year % 4 == 0 :
            if year % 100 == 0 :
                if year % 400 == 0:  year_st = '윤년'
                else:  year_st = '평년'
            else: year_st = '윤년'
        else: year_st = '평년'
        if year_st == '평년' : ls_month[1] = 28 
        else : ls_month[1] = 29    
        # 일 체크
        if day > 0: flag1 = True
        else: flag1 = False  
        # 월 체크
        if 1 <= month <= 12 : flag2 = True
        else: flag2 = False     
        if flag2 == True and year_st == '평년':
            if ls_month[int(month)-1] < int(day): flag4 = False
            else: flag4 = True
        if flag2 == True and year_st == '윤년':
            if ls_month[month-1] < day: flag4 = False
            else: flag4 = True
        # 필터링한 값이 모두 만족한 경우
        if flag1 and flag2 and flag4: 
            return st # 사용자라 입력한 값 리턴
        # 필터링한 값에 문제가 있는 경우
        else :
            return ''  # 공백 리턴
        
    # 매개변수의 연월일 필터 적용    
    def yearFilter(self, content):
        ls_content = []
        chk_ls = []
        for i in range(len(content)):
            ls_content.append(self.yearChk(content[i][1]))
            if ls_content[i] == '':   # 공백이 있는 경우 
                     chk_ls.append(i) # 공백이 있는 인덱스가 모여있는 리스트
        ls_text_t1 = []         
        for i in range(len(content)):  
            if i not in chk_ls:       
                ls_text_t1.append(content[i]) # 필터링 후 완전한 데이터
        self.content = ls_text_t1
        
        return self.content # 필터링 한 값 리턴
    
    # 제품테이블에 제품코드 존재 확인
    def codeFilter(self, content):
        try:
            conn = pymysql.connect(**config)
            cursor = conn.cursor()     
            chk_ls = []
            for i in range(len(content)):
                sql = f"SELECT unitPrice FROM product WHERE pCode = '{content[i][0]}'"
                cursor.execute(sql)
                rows = cursor.fetchall()
                # 제품코드가 존재한다면
                if rows:
                    chk_ls.append(content[i])
            self.code = chk_ls
        
            return self.code # 필터링 한 값 리턴
        
        except Exception as e:
            print('Error 발생 :', e)
            conn.rollback()

        finally :
            conn.close()
            cursor.close()
    
    # 기존 테이블 중복 확인
    def tableChk(self, content):
        try:
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            ls_chk_ls = []
            # 입력한 값이 순차적으로 등록이 되어 있는지 확인
            for i in range(len(content)):
                ls_chk_ls.append(((content[i][0],)+(int(content[i][2]),)))
            ls_chk_ls = tuple(ls_chk_ls)     
            sql = f"SELECT sCode, Qty FROM sales"
            cursor.execute(sql)
            test_rows = cursor.fetchall()
            st = 0
            for i in range(len(test_rows)-len(ls_chk_ls)+1): 
                if test_rows[0+i:len(ls_chk_ls)+i+1] == ls_chk_ls:
                    st = 1 # DB에 데이터가 존재하면 st = 1
                else:
                    pass
                
            self.st = st
            return self.st
                
        except Exception as e:
            print('Error 발생 :', e)
            conn.rollback()

        finally :
            conn.close()
            cursor.close()
            

#--------------------------
# 외부파일 추가 클래스
# 파일을 DB에 등록하기 위한 기능        
class FileInsert(FileTextFilter, FilePreProcessing):    
    def __init__(self):
        super().__init__()
        self.fileInsert() # fileInsert 매서드 자동 호출

    def fileInsert(self):
        try:
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            print(f'\n<<<제품 테이블에 외부 파일 등록입니다>>>')
            content = super().readFile()
            
            # 1) 년월일 필터
            content_year_chk = super().yearFilter(content)

            # 2) 제품코드 필터
            content_code_chk = super().codeFilter(content_year_chk)

            # 3) 테이블 중복 확인 필터
            st = super().tableChk(content_code_chk)

            # 텍스트 데이터 추가          
            for i in range(len(content_code_chk)):
                sql = f"SELECT unitPrice FROM product WHERE pCode = '{content_code_chk[i][0]}'"
                cursor.execute(sql)
                rows = cursor.fetchall()
                code = content_code_chk[i][0]   #--> 제품 코드
                price = rows[0][0]              #--> 제품 가격
                date = content_code_chk[i][1]   #--> 제품 날짜
                qty = content_code_chk[i][2]    #--> 제품 수량
                total_price = int(price) * int(qty)
                if st == 0 and rows:
                    sql = f"INSERT INTO sales(sCode, sDate, Qty, Amt) VALUES('{code}','{date}','{qty}','{total_price}')" 
                    cursor.execute(sql)
                    rows = conn.commit()

            if st == 0:
                print("데이터를 추가완료 했습니다")
            else:
                print("데이터를 추가하지 못했습니다.")
                print("이미 존재하는데이터입니다.")

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
class GraphsPreProcessing(FileInput, FileTextFilter):
    def __init__(self):
        super().__init__()
        self.salDataCreate()
    
    # sales테이블 텍스트파일로
    def salDataCreate(self): 
        c0 = FindSql('s',0)
        c1 = FileInput()
        rows = c0.sqlFind()
        ls_t1 = []
        for row in rows:
            ls_t1.append(row[:6])
        df = pd.DataFrame(ls_t1)
        print("<<<테이블 데이터를 텍스트 파일로 저장합니다. 구분자: ',' >>>")
        print('저장할',end=''); path = super().pathInput()
        print('저장할',end=''); file_name = super().nameInput()
        df.to_csv(f'{path}/{file_name}', sep = ',', header = False, index=False)
        
    # 데이터 프레임 만들기 위한 전처리 매서드        
    def salPreProcessing(self):
        try:
            conn = pymysql.connect(**config)
            cursor = conn.cursor() 
            # c1 = FileInput() # 클래스 상속으로 참조변수 주석처리 2023-02-27
            print('사용할',end=''); path = super().pathInput()
            print('사용할',end=''); file_name = super().nameInput()
            t1 = open(f'{path}/{file_name}', mode = 'r', encoding='utf8')
            test_t1 = t1.read()
            temp1_t1 = findall('[^,\n]+',test_t1)
            content = []

            # c1 = FileTextFilter() # 클래스 상속으로 참조변수 주석처리 2023-02-27
            for i in range(len(temp1_t1)):
                if i % 6 == 0:
                    content.append(((temp1_t1[i+1],)+(temp1_t1[i+3],)+(temp1_t1[i+4],)+(temp1_t1[i+5],)))

            # 1) 년월일 필터
            content_year_chk = super().yearFilter(content)

            # 2) 제품코드 필터
            content_code_chk = super().codeFilter(content_year_chk)

            # 3) 데이터 프레임화
            df = pd.DataFrame(content_code_chk)
            df.columns = ['Code', 'Date', 'Qty', 'Amt'] # 데이터 프레임 컬럼 추가

            # 4) 데이터에 제품명 추가후 데이터 프레임
            sql = "SELECT pCode, pName FROM product"
            cursor.execute(sql)
            rows = cursor.fetchall()
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
    def salGraphShow(self, sel):
        # 데이터 시각화 전처리
        # 1) 필드의 데이터타입 인트타입으로 변경) 
        df_all = self.salPreProcessing()
        df_all['Qty'] = pd.to_numeric(df_all['Qty'])
        df_all['Amt'] = pd.to_numeric(df_all['Amt'])

        # 2) 날짜필드의 데이터타입 날짜타입으로 변경 
        df_all['Date'] = pd.to_datetime(df_all['Date'])

        # 3) 기간 설정 / (2023년 2월) 추후에 Input으로 날짜 변경 가능
        set_time1 = pd.Timestamp(2023, 2, 1, 8, 00, 0)
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
        if yesNo.upper() == "Y" or yesNo == "ㅛ":
            print('그래프를 저장 할',end=''); path = FileInput().pathInput()
            plt.savefig(path) # 파일로 저장
        else:
            pass
        
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
        
    # 1. 인덱스(순서) 필터
    def setNo(self, no):
        # 0) sql 인젝션 블랙리스트 함수 / 2023-02-13 
        no = sqlBlackList(no)
        # 1) 입력한 값이 공백이나 기호가 있을 경우
        if no.isalnum() == False: 
            print('입력값 ' +str(no)+ ' 에 공백이나 기호가 있습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        # 2) 입력한 값이 정수가 아닌 경우    
        elif no.isdigit() == False: 
            print('입력값 ' +str(no)+ ' 에는 정수만 입력이 가능합니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 3) 모든 조건을 만족하는 경우        
        else:
            self.inputValueFilter_result = True 
            self.no = no
                           
        return self.inputValueFilter_result
    
    
    # 2. 제품코드 필터
    def setScode(self, scode):
        # 0) sql 인젝션 블랙리스트 함수 / 2023-02-13
        scode = sqlBlackList(scode)
        # 1) 입력한 값이 공백이나 기호가 있을 경우
        if scode.isalnum() == False: 
            print('입력값 ' +str(scode)+ ' 에 공백이나 기호가 있습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        # 2) 입력한 값이 소문자 알파벳1개와 정수3개로 되어 있으며 길이가 4자리인지 필터링    
        elif not (match('[a-z][0-9]{3}', scode) and len(scode)==4): 
            print('입력값 ' +str(scode)+ ' 에는 a001 과 같이 소문자와 숫자를 조합한 4자리의 값만 입력이 가능합니다.  다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 3) 모든 조건을 만족하는 경우        
        else:
            self.inputValueFilter_result = True 
            self.scode = scode 
                                
        return self.inputValueFilter_result 
    
    
    # 3. 판매 수량 필터
    def setQty(self, qty):
        # 0) sql 인젝션 블랙리스트 함수 / 2023-02-13 
        qty = sqlBlackList(qty)
        # 1) 입력한 값이 공백이나 기호가 있을 경우
        if qty.isalnum() == False: 
            print('입력값 ' +str(qty)+ ' 에 공백이나 기호가 있습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        # 2) 입력한 값이 정수가 아닌 경우    
        elif qty.isdigit() == False: 
            print('입력값 ' +str(qty)+ ' 에는 정수만 입력이 가능합니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 3) 모든 조건을 만족하는 경우        
        else:
            self.inputValueFilter_result = True 
            self.qty = qty                     
        return self.inputValueFilter_result
    
    # 4. 제품명 필터 
    def setPname(self, pname) :
        # 0) sql 인젝션 블랙리스트 함수 / 2023-02-13 
        pname = sqlBlackList(pname)
        # 1) 입력한 값이 공백(빈칸)인 경우
        if pname == '' or len(pname) < 0:
            print('입력값 ' +str(pname)+ ' 에는 빈칸을 입력하실 수 없습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        # 2) 입력한 값에 단모음, 단자음이 있는 경우
        elif findall('[ㄱ-ㅎ|ㅏ-ㅣ]', pname): 
            print('입력값 ' +str(pname)+ ' 에는 단모음, 단자음을 입력할 수 없습니다.  다시 입력해주세요.')
        # 3) 모든 조건을 만족하는 경우
        else:
            self.inputValueFilter_result = True 
            self.pname = pname                          
        return self.inputValueFilter_result

    # 5. 제품 가격 필터
    def setPrice(self, price) :
        # 0) sql 인젝션 블랙리스트 함수 / 2023-02-13 
        price = sqlBlackList(price)
        # 1) 입력한 값이 공백이나 기호가 있을 경우
        if price.isalnum() == False: 
            print('입력값 ' +str(price)+ ' 에 공백이나 기호가 있습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 2) 입력한 값이 숫자가 아닌 경우
        elif price.isdigit() == False: 
            print('입력값 ' +str(price)+ ' 에는 숫자만 입력이 가능합니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False
        # 3) 모든 조건을 만족하는 경우    
        else:
            self.inputValueFilter_result = True 
            self.price= price
        return self.inputValueFilter_result 
    
    # 6. 제품 할인율 필터
    def setDiscRate(self, discrate) :
        # 0) sql 인젝션 블랙리스트 함수 / 2023-02-13 
        discrate = sqlBlackList(discrate)
        # 1) 정수와 실수를 입력한 경우 
        if findall('\d', discrate):
            self.discrate= discrate  
            self.inputValueFilter_result = True
        # 2) 해당 조건을 만족하지 못한 경우
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
class FindSql(UserInput):
    table = ''
    table_name = ''
    def __init__(self,table, find_sel): # 매개변수 (테이블, 찾을 SQL번호)  
        super().__init__()
        self.table = table
        self.read_sel = find_sel
        if self.table == 'p': self.table_name = '제품'
        else : self.table_name = '판매'
        
        # 제품 테이블 sql
        if self.table.lower() == 'p':
            # 1) 제품코드를 이용하여 product테이블의 해당 데이터 호출
            if find_sel == 3 or find_sel == '코드': 
                self.find_sql = "SELECT * FROM product WHERE pCode "
            # 2) 제품명를 이용하여 product테이블의 해당 데이터 호출
            elif find_sel == 4 or find_sel == '제품명': 
                self.find_sql = "SELECT * FROM product WHERE pName " 
            # 3)product테이블의 전체 데이터 호출
            elif find_sel == 0:
                self.find_sql = "SELECT * FROM product"
                
        # 판매 테이블 sql
        elif self.table.lower() == 's':
            # 1) 제품코드로 판매관리 필요 데이터 전체조회
            if find_sel == 3 or find_sel == '코드': 
                self.find_sql = "SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y.%m.%d') as date, s.qty, s.amt FROM sales AS s JOIN product AS p ON s.sCode = p.pCode WHERE p.pCode " 
            # 2) 제품명으로 판매관리 필요 데이터 전체조회
            elif find_sel == 4 or find_sel == '제품명': 
                self.find_sql = "SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y.%m.%d') as date, s.qty, s.amt FROM sales AS s JOIN product AS p ON s.sCode = p.pCode WHERE p.pName "
            # 3) 판매관리 필요 데이터 전체조회
            elif find_sel == 0:
                self.find_sql = "SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y%m%d') as date, s.qty, s.amt FROM sales AS s LEFT OUTER JOIN product AS p ON s.sCode = p.pCode"
            # 4) product테이블에서 제품가격과 할인율 가져오기
            elif find_sel == 1:
                self.find_sql = "SELECT unitPrice, discountRate FROM product WHERE pCode" 
            # 5) 인덱스로 제품코드 조회
            elif find_sel == 2:
                self.find_sql = "SELECT sCode FROM sales WHERE seqNo"
        else:
            print('입력한 테이블은 존재하지 않습니다. 다시 입력해 주세요.')

    # 제품 검색 SQL 실행 매서드 
    # <변경사항> / 2023-02-20 
    # ProdFind클래스와 SalFind클래스 병합  
    def sqlFind(self, find_in_data = '') : # 매개변수 (SQL의 WHERE조건)
        try :
            global sql
            conn = pymysql.connect(**config)    
            cursor = conn.cursor()
            # 1) 제품 테이블
            if self.table == 'p' : 
                # 1-1) 제품 테이블 전체 조회             
                if self.read_sel == 0: 
                    sql = self.find_sql
                # 1-2) 제품명으로 조회
                elif self.read_sel == 4 or self.read_sel == '제품명':
                    sql = self.find_sql + f"like '%{find_in_data}%'" # like함수를 통해서 일부의 제품명으로 
                                                                     # 제품 검색이 가능               
                # 1-3) 제품 코드로 조회
                elif self.read_sel == 3 or self.read_sel == '코드':
                    sql = self.find_sql + f"= '{find_in_data}'"
                    
            # 2) 판매 테이블        
            elif self.table == 's':
                # 2-1) 제품 테이블 전체 조회 
                if self.read_sel == 0: 
                    sql = self.find_sql       
                # 2-2) 제품명으로 조회    
                elif self.read_sel == 4 or self.read_sel == '제품명': 
                    sql = self.find_sql + f"like '%{find_in_data}%'" + "ORDER BY s.sDate"
                # 2-3) 제품코드로 조회
                elif self.read_sel == 3 or self.read_sel == '코드': 
                    sql = self.find_sql + f"= '{find_in_data}'" + "ORDER BY s.sDate"
                else:
                    sql = self.find_sql + f"= '{find_in_data}'"
                    
            cursor.execute(sql)                
            return cursor.fetchall()            
        
        except Exception as e :                 
            print('db 연동 실패 : ', e)         
            conn.rollback()                     
        
        finally:                                
            cursor.close()                      
            conn.close()                        
 
    # 테이블 조회
    # <변경사항> / 2023-02-20 
    # 2023-02-20 CodeInspection
    # 기존의 product, sales 매서드 통합
    # self.table 조건문을 이용하여 두 테이블 분류
    def sqlReadOne(self) :
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()
                # 1) 제품테이블
                if self.table == 'p' :   
                    ProdFunc().prodReadAll() # SQL관리 클래스 호출 및 product 테이블 전체 출력 
                # 2) 판매 테이블
                elif self.table == 's':
                    SalFunc().salReadAll()  # SQL관리 클래스 호출 및 sales테이블의 전체 데이터 출력  
                    
                # 1) 제품코드에 해당하는 데이터를 가져올 경우
                if self.read_sel == '코드' :
                    print("<<<제품 개별 조회({})입니다>>>".format(self.read_sel))
                    print("조회할 ",end='')
                    in_code = super().codeInput()
                # 2) 제품명 해당하는 데이터를 가져올 경우
                elif self.read_sel == '제품명' : 
                    print("<<<제품 개별 조회({})입니다>>>".format(self.read_sel))
                    print("조회할 ",end='')
                    in_code = super().nameInput()

                rows = self.sqlFind(in_code) # 사용자 입력 클래스 호출 및 조건변수 매서드 실행

                # 2023-02-21 product, sales테이블 각각의 출력문
                # 조건문을 이용하여 통합
                # 1) 조회할 데이터가 존재할 경우   
                if len(rows) > 0 :
                    print("===테이블 조회2({})===".format(self.read_sel))
                    if self.table == 'p':
                        ShowTables().showProd(rows)
                        break
                    elif self.table == 's':
                        ShowTables().showSal(rows)
                        break
                # 2) 조회할 로우가 존재하지 않을경우
                else:
                    print("조회결과 입력한 {}에 맞는 제품이 없습니다".format(self.read_sel))
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
    sql = ''
    def __init__(self):
        super().__init__()
        
# (1) 제품 생성 매서드 
    def prodCreate(self):
        try :
            global sql
            while True:
                conn = pymysql.connect(**config)   
                cursor = conn.cursor()        
                # os.system('cls') # 실행결과 스샷을 위해 주석처리
                print("<<<제품 등록입니다>>>")
                # c2 = UserInput() # 2023-02-09 사용자 입력 클래스 호출 
                                   # 2023-02-24 클래스 상속으로 주석처리
                print('등록할 데이터의 ',end='') 
                in_code = super().codeInput() 

                # 코드 입력값이 공백이 아닌 경우   
                if in_code != '' :
                    c1 = FindSql('p',3) # product 테이블의 제품코드에 맞는 데이터 출력 
                    rows = c1.sqlFind(in_code) # 조건에 맞는 SQL실행 
                    
                    #1) 같은 제품코드가 존재하는 경우
                    if len(rows) :
                        print("해당 제품코드는 이미 존재하고 있습니다. 다른 제품코드를 입력하세요")
                        continue

                    #2) 같은 제품코드가 존재하지 않는 경우
                    else :
                        iValue = super().userInput() # 사용자 입력값 호출 
                        sql = f"INSERT INTO product(pCode, pName, UnitPrice, discountRate) VALUES('{in_code}','{iValue[0]}', '{iValue[1]}', '{iValue[2]}')" 
                        cursor.execute(sql)
                        conn.commit()
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
                # os.system('cls') # 실행결과 스샷을 위해 주석처리
                # 제품 전체 출력 함수 호출 / 2023-02-09
                self.prodReadAll()              
                print("<<<삭제할 제품코드를 입력하세요>>>")
                # c2 = UserInput()               # 사용자 입력 클래스 호출
                                                 # 2023-02-24 클래스 상속으로 주석처리
                print('삭제할 데이터의 ',end='')
                in_code = super().codeInput()       # 제품 코드 입력 함수 호출
                c1 = FindSql('p',3)            # product 테이블의 제품코드에 맞는 데이터 출력 
                                               # 3번은 제품코드를 입력하여 product 테이블 데이터 출력 
                rows_c1 = c1.sqlFind(in_code) # 조건에 맞는 SQL실행
                
                # 1) 데이터가 존재하는 경우
                if rows_c1 :
                    # 제품 삭제 확인문
                    yesNo = input('삭제하시겠습니까>(y/n) : ')
                    # 조건 수정 (소문자, 대문자, 한글 조건 추가) / 2023-02-04
                    if yesNo.upper() == "Y" or yesNo == "ㅛ": 
                        sql = f"DELETE FROM product WHERE pCode = '{in_code}'" # 테이블 레코드 삭제 SQL 
                        cursor.execute(sql) 
                        conn.commit()       
                        print('삭제 성공했습니다.')
                        self.prodReadAll() # 데이터 삭제 후 테이블 데이터 전체 출력 매서드 호출 / 2023-02-09
                        break
                    else:
                        print("<<<삭제를 취소했습니다.>>>")
                        break
                        
                # 2) 데이터가 존재하지 않는 경우
                else :
                    print('삭제 실패했습니다.')
                    print('입력한 값에 해당하는 데이터가 존재하지 않습니다.')
                    break
                
        except Exception as e :
            print('db 연동 실패 : ', e)
            conn.rollback()  

        finally:
            cursor.close()
            conn.close()


    #--------------------------
    # (3) 제품 테이블 전체 목록조회 매서드
    # ProdRead클래스는 ProdFind 클래스의 하위 매서드로 흡수 후 해당 코드 삭제 / 2023-02-10
    # 매서드 만든 이유 : 빈번한 사용으로 반정규화
    def prodReadAll(self) :
        print("<<<제품 전체 목록 조회입니다>>>")
        c1 = FindSql('p',0)
        rows_c1 = c1.sqlFind()
        # SQL 입력 후 결과 출력 / 2023-02-09
        # ShowTables클래스로 결과 출력 / 2023-02-20 
        ShowTables().showProd(rows_c1)


    #--------------------------   
    # (4) 제품 수정 매서드
    def prodUpdate(self) : 
        try :
            global sql
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()
                # SELECT 쿼리 실행결과가 존재하는 경우
                # os.system('cls') # 실행결과 스샷을 위해 주석처리
                # 전체 목록 조회 함수 호출 / 2023-02-09
                self.prodReadAll()
                # c2 = UserInput() # 2023-02-24 클래스 상속으로 주석처리
                print("<<<제품 수정입니다>>>")
                print('수정할 데이터의 ',end='') 
                in_code = super().codeInput() 
                c1 = FindSql('p',3)
                # SQL을 실행 후 호출한 데이터 
                rows_c1 = c1.sqlFind(in_code)
                if rows_c1 : 
                    print("<<<제품코드 조회결과입니다>>>")
                    # SQL 실행결과 반환 / 2023-02-21 
                    # 기존 출력문에서 클래스 출력문으로 변경
                    ShowTables().showProd(rows_c1)
            
                    # 제품 수정 확인문
                    yesNo = input('수정하시겠습니까>(y/n) : ')
                    # 조건 수정 (소문자, 대문자, 한글 조건 추가) / 2023-02-04
                    if yesNo.upper() == "Y" or yesNo == "ㅛ": 
                        print("<<<수정할 내용을 입력하세요.>>>")
                        iValue = super().userInput()  # 사용자 입력 함수를 호출
                        print('확인1')
                        print(iValue)
                        sql = f"UPDATE product SET pName = '{iValue[0]}', UnitPrice = '{iValue[1]}', discountRate ='{iValue[2]}' WHERE pCode = '{in_code}'"
                        cursor.execute(sql) 
                        conn.commit()       
                        print("<<<수정을 완료했습니다>>>")
                        print("<<<수정 결과입니다>>>")
                        self.prodReadAll() # product테이블 전체 출력
                        break
                    else:
                        print("<<<수정을 취소했습니다.>>>")
                        break
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
        c0 = FindSql(self.table, 0)
        find_rows = c0.sqlFind()
        # 테이블 전체 출력
        # 1) product 테이블
        if self.table == 'p':
            ProdFunc().prodReadAll()
        # 2) sales 테이블
        elif self.table == 's':
            SalFunc().salReadAll() 
            
        print(find_rows)
        # 1) 테이블 데이터가 존재하는 경우
        if find_rows : 
            yesNo = input('수정하시겠습니까>(y/n) : ')  
            print(f'\n<<<{self.table_name}테이블 초기화입니다>>>')
            yesNo = input('모두 삭제하고 초기화 하시겠습니까?(y/n) : ')
            if yesNo.upper() == "Y" or yesNo == "ㅛ": 
                try:
                    conn = pymysql.connect(**config)
                    cursor = conn.cursor()

                    # 테이블 전체 내용 삭제
                    sql = f"DELETE FROM {self.table_name}"
                    cursor.execute(sql)
                    conn.commit()

                    # 대상이 sales 테이블일경우 seqNo가 1부터 시작되도록 초기화
                    if self.table == 's' :
                        sql = "ALTER TABLE sales auto_increment = 1"
                        cursor.execute(sql)
                        conn.commit()
                    print("초기화 성공했습니다.")

                except Exception as e :
                    print('db 연동 실패 : ', e)
                    conn.rollback()
                    
                finally:
                    cursor.close()
                    conn.close()
            # 사용자 확인문에서 y를 입력하지 않았을 경우        
            else : 
                print("<<<초기화를 취소했습니다.>>>")
        # 2) 테이블의 데이터가존재하지 않을 경우        
        else : 
            print("삭제할 데이터가 없습니다.")
            print("<<<초기화를 취소합니다.>>>")

   
#--------------------------
#   판매 관리 기능 시작   #
#--------------------------
# 판매 관리 클래스 / 2023-02-17 
class SalFunc(UserInput) :
    def __init__(self):
        super().__init__()
# (1) 판매기록 등록 매서드      
    def salCreate(self) :
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()        
                # SalFind 클래스 호출 삭제 / 2023-02-10
                # 2023-02-08 / 요구사항에 따라 전체목록 출력문 삭제
                # c2 = UserInput() # 사용자 입력 함수호출 / # 2023-02-24 클래스 상속으로 주석처리
                print("<<<판매기록 등록입니다>>>")
                print('등록할 데이터의 ',end='') 
                in_code = super().codeInput() 
                c1 = FindSql('s',3)
                rows_c1 = c1.sqlFind(in_code)
                # 코드 입력값이 공백이 아닌 경우 
                if in_code != '' :         
                    # 1) product 테이블에 해당 제품코드의 상품이 존재하지 않는 경우            
                    if len(rows_c1) == 0:
                        iValue = super().userInput() # 사용자 입력 값 호출
                        sql = f"INSERT INTO product(pCode, pName, UnitPrice, discountRate) VALUES('{in_code}','{iValue[0]}', '{iValue[1]}', '{iValue[2]}')" 
                        cursor.execute(sql)
                        conn.commit()
                        print("제품등록을 성공했습니다.")
                        break

                    # 2) product 테이블에 해당 제품코드의 상품이 존재하는 경우
                    else :
                        c3 = FindSql('s',1)
                        rows_c3 = c3.sqlFind(in_code)
                        ##############################################################
                        # 가격 계산 / 2023-02-08
                        ##############################################################
                        # <1> 할인율이 적용된 가격 계산
                        # dis_price = round(((rows_c3[0][0]) * (100 - round(rows_c3[0][1])))/100)
                        # total_price = dis_price * int(iValue[0]) # 할인율이 적용된 총 가격
                        
                        # <2> 할인율이 적용되지 않은 가격 계산 <요구사항>
                        price = rows_c3[0][0] # 제품 가격 출력 / 2023-02-08
                        in_qty = super().qtyInput() # 사용자 입력 함수 호출
                        total_price = price * int(in_qty) # 할인율이 적용되지 않은 총 가격
                        sql = f"INSERT INTO sales(sCode, Qty, Amt) VALUES('{in_code}','{in_qty}', '{total_price}')" 
                        cursor.execute(sql)
                        conn.commit()
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
    def salDelete(self) : 
        try :
            while True:
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()  
                # os.system('cls') # 실행결과 스샷을 위해 주석처리
                print("<<<판매기록 삭제합니다>>>")
                # ProdFind클래스에서 호출 삭제 / 2023-02-10
                self.salReadAll() # sales테이블 전체 출력
                # c2 = UserInput()  # 사용자 입력 클래스 호출 / # 2023-02-24 클래스 상속으로 주석처리
                print('삭제할 데이터의 ',end='') 
                in_code = super().codeInput() # 제품코드 입력 매서드 호출
                c1 = FindSql('s', 3)     # SQL실행 3번 / 제품명에 맞는 데이터 출력
                rows = c1.sqlFind(in_code)
                # 1) 제품코드가 존재하는 경우
                if rows : 
                    print("<<<선택한 제품코드의 판매기록 목록 조회입니다>>>")
                    ShowTables().showSal(rows)
                    print('삭제할 데이터의 ',end='')
                    in_no = super().noInput()
                    search_code = FindSql('s',2)
                    # 찾은 제품코드를 실행하는 매서드 호출 / 2023-02-09
                    rows1 = search_code.sqlFind(in_no)
                    # 1-1) 제품코드가 존재하면서 No가 존재하는 경우
                    if rows1:
                        # 판매 삭제 확인문
                        yesNo = input('삭제하시겠습니까>(y/n) : ')
                        # 조건 수정 (소문자, 대문자, 한글 조건 추가) / 2023-02-04
                        if yesNo.upper() == "Y" or yesNo == "ㅛ": 
                            sql = f"DELETE FROM sales WHERE seqNo = '{in_no}'"
                            cursor.execute(sql) 
                            conn.commit()       
                            print('삭제 성공했습니다.')
                            self.salReadAll()
                            break
                        # 판매 확인문 취소 입력
                        else:
                            print("<<<삭제를 취소했습니다.>>>")
                            break
                    # 1-2) 제품코드가 존재하지만 No가 하지 않는 경우
                    else :
                        print('삭제 실패했습니다.')
                        print('입력한 값에 해당하는 데이터가 존재하지 않습니다.')
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
    # (3) sales테이블 전체 목록조회 매서드
    # 매서드 만든 이유 : 빈번한 사용으로 반정규화
    # 출력 데이터 맞춤 함수 사용 / 2023-02-10
    def salReadAll(self) :
        print("<<<판매 목록 조회입니다>>>")
        c1 = FindSql('s', 0)
        rows_c1 = c1.sqlFind()
        # SQL 입력 후 결과 출력 / 2023-02-10 
        # ShowTables클래스로 결과 출력 / 2023-02-20  
        ShowTables().showSal(rows_c1)


    #--------------------------   
    # (4) 판매기록 수정 매서드
    def salUpdate(self) : 
        try :
            while True:
                # os.system('cls') # 실행결과 스샷을 위해 주석처리
                print("<<<판매기록을 수정합니다>>>")
                # 필요 없는 코드 삭제 / 2023-02-09
                # 클래스 호출 코드 삭제 / 2023-02-10
                self.salReadAll() # 전체 데이터 출력
                # c2 = UserInput() # 2023-02-24 클래스 상속으로 주석처리
                print('수정할 데이터의 ',end='')
                in_code = super().codeInput() # 제품코드 입력 매서드 호출
                c1 = FindSql('s', 3)
                rows = c1.sqlFind(in_code)
                conn = pymysql.connect(**config)    
                cursor = conn.cursor()
                # SELECT 쿼리 실행결과가 있는 경우               
                if rows : 
                    print("<<<판매기록 목록 조회입니다>>>")
                    ShowTables().showSal(rows)
                    print('수정할 데이터의 ',end='')
                    in_no = super().noInput()
                    # 판매 수정 확인문
                    yesNo = input('수정하시겠습니까>(y/n) : ')
                    # 조건 수정 (소문자, 대문자, 한글 조건 추가) / 2023-02-04
                    if yesNo.upper() == "Y" or yesNo == "ㅛ": 
                        print("<<<수정할 데이터를 입력하세요.>>>")
                        in_qty = super().qtyInput()  # 사용자 입력 함수를 호출 / 2023-02-09
                        # 입력한 인덱스(순번)을 이용하여 제품 코드를 찾는 SQL / 2023-02-09
                        search_code = FindSql('s',2)
                        # 찾은 제품코드를 실행하는 매서드 호출 / 2023-02-09
                        rows1 = search_code.sqlFind(in_no)
                        # 제품코드를 이용하여 제품의 가격과 할인율을 가져오는 SQL / 2023-02-09
                        c1 = FindSql('s', 1)
                        # SQL을 실행하는 매서드 호출 / 2023-02-09
                        rows = c1.sqlFind(rows1[0][0])
                        # 구매 수량에 따른 총 가격 계산 
                        price = rows[0][0] # 제품코드를 이용하여 찾은 제품의 가격 / 2023-02-09
                        total_price = price * int(in_qty) # 제품 가격과 판매 수량을 계산한 총 판매 가격 / 2023-02-09
                        # 판매 기록을 수정하는 SQL / 2023-02-09 
                        sql = f"UPDATE sales SET Qty = '{in_qty}', Amt = '{total_price}' WHERE seqNo = '{in_no}'"
                        cursor.execute(sql) 
                        conn.commit()       
                        print("<<<수정을 완료했습니다>>>")
                        print("<<<수정 결과입니다>>>")
                        self.salReadAll()
                        break

                    else:
                        print("<<<수정을 취소했습니다.>>>")
                        break
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
class ShowTables:
    # 제품 테이블 출력
    def showProd(self, rows):
        print(f"{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('제품가격',11,'l')}{fmt('할인율',20,'l')}")
        print('-'*60)
        for row in rows:
            print(f"{fmt(row[0],10,'l')}{fmt(row[1],20,'l')}{fmt(row[2],11,'l')}{fmt(row[3],20,'l')}")
    # 판매 테이블 출력
    def showSal(self, rows):
        print(f"{fmt('No',6,'l')}{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('판매등록일자',25,'l')}{fmt('판매수량',16,'l')}{fmt('총 판매가격',5,'l')}")
        print('-'*60)
        for row in rows :
            print(f"{fmt(row[0],6,'l')}{fmt(row[1],10,'l')}{fmt(row[2],20,'l')}{fmt(row[3],28,'l')}{fmt(row[4],13,'l')}{fmt(row[5],5,'l')}")
            

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
            cursor.execute(sql)
            conn.commit()
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
            cursor.execute(sql)
            conn.commit()  
        except Exception as e :
            print("오류 : ",e)
            conn.rollback()
        finally :
            conn.close()
            cursor.close() 
        

#--------------------------             
# 출력 데이터 간격 맞춤 함수 / 2023-02-09
# 2byte의 데이터를 출력 시 출력데이터가 밀리는 현상이 발생합니다.
# 이런 문제를 방지하기 위한 함수
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
# 판매가격 생성 함수 / CodeInspection 통한 분리 2023-02-27
# def createAmt:





#--------------------------       
# 2023-02-13 
# <sql인젝션을 방지하기 위한 블랙리스트 함수>
def sqlBlackList(st):
    ls_1 = ['char','nchar','varchar','--',';--',';','/*','*/','@@','@',\
        'nvarchar','alter','begin','cast','create','cursor','declare','delete',\
        'drop','end','exec','execute','fetch','insert','kill','open','select',\
        'sys','sysobjects','syscolumns''table','update','union','except','intersect',\
        'join','and','or','=','+','unionall','from','where',' information_schema',\
        'table_schema','!','?','^','#','~','$','%','&','*','(',')','+','=','like','/']
    for i in range(len(ls_1)):
        st = st.lower().replace(ls_1[i],' ')
    return st

               
#--------------------------
# 시스템 실행
if __name__ == "__main__" :
    t0 = TableCreate()
    t0.productTableCreate() # 테이블이 없는 경우 product테이블 생성 / 2023-02-17
    t0.salesTableCreate()   # 테이블이 없는 경우 sales테이블 생성 / 2023-02-17
    
    while True:
        os.system('cls')
        print("---관리 시스템 실행---")
        print("제품 관리 실행  : 1 ")
        print("판매 관리 실행  : 2 ")
        print("데이터관리 실행 : 3 ")
        print("서비스     종료 : 0 ")
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
                    c0.prodReadAll()
                    os.system("pause")
                elif sel == 3 :
                    r3 = FindSql('p','코드')
                    r3.sqlReadOne()
                    os.system("pause")
                elif sel == 4 :
                    r4 = FindSql('p','제품명')
                    r4.sqlReadOne()
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
                c0 = SalFunc()
                if sel == 1 :
                    c0.salCreate()
                    os.system("pause")
                elif sel == 2 :
                    c0.salReadAll()
                    os.system("pause")
                elif sel == 3 :
                    r3 = FindSql('s','코드')
                    r3.sqlReadOne()
                    os.system("pause")
                elif sel == 4 :
                    r4 = FindSql('s','제품명')
                    r4.sqlReadOne()
                    os.system("pause")
                elif sel == 5 :
                    c0.salUpdate()
                    os.system("pause")
                elif sel == 6 :
                    c0.salDelete()
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
                    c3.salGraphShow(1)
                    os.system("pause")
                elif sel == 4 :
                    c4 = GraphsPreProcessing()
                    c4.salGraphShow(2)
                    os.system("pause")
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