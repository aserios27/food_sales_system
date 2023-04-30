import os
import sys
import pymysql                  # MySQL데이터베이스를 사용하기 위한 라이브러리 / 2023-02-07
from re import findall, match   # 정규 표현식 사용을 위한 라이브러리 (findall, match) / 2023-02-07
import pandas as pd             # DataFrame을 만들어 활용하기 위한 라이브러리 / 2023-02-14
import matplotlib.pyplot as plt # 그래프 출력 및 세부 설정을 위한 라이브러리 / 2023-02-14
import calendar as cd           # 날짜 확인 캘린더 라이브러리 / 2023-02-28
from Filter2 import FindSql, SelOpt, sqlAction

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
            chk_ls = [content[i] for i in range(len(content)) if sqlAction(f"SELECT unitPrice FROM product2 WHERE pCode = '{content[i][0]}'")]

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
            sql = f"SELECT sCode, date_format(sDate,'%Y%m%d') as date, Qty FROM sales2 ORDER BY seqNo"
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
                    sql = f"SELECT unitPrice FROM product2 WHERE pCode = '{content_code_chk[i][0]}'"
                    rows = sqlAction(sql)
                    code = content_code_chk[i][0]   #--> 제품 코드
                    unitPrice = rows[0][0]          #--> 제품 가격
                    date = content_code_chk[i][1]   #--> 제품 날짜
                    qty = content_code_chk[i][2]    #--> 제품 수량
                    total_price = int(unitPrice) * int(qty)
                    if content_duplicate_chk == 0:
                        sql = f"INSERT INTO sales2(sCode, sDate, Qty, Amt) VALUES('{code}','{date}','{qty}','{total_price}')" 
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
            if SelOpt(yesNo).startOpt() == "Y": 
                rows = FindSql('s',0).sqlFind()
                ls_t1 = [row[:6] for row in rows]
                df = pd.DataFrame(ls_t1)
                print("<<<테이블 데이터를 텍스트 파일로 저장합니다. 구분자: ',' >>>")
                print('저장할',end=''); path = super().pathInput()
                print('저장할',end=''); file_name = super().nameInput()
                df.to_csv(f'{path}/{file_name}', sep = ',', header = False, index=False)
                break
            elif SelOpt(yesNo).startOpt() == "N":
                print('저장을 취소합니다.')
                break
            else:
                print('잘못 입력했습니다. 다시 입력해주세요.')
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
            sql = "SELECT pCode, pName FROM product2"
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
        # 1) 필드의 데이터타입 인트타입으로 변경
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
            plt.title("2023년 02월 일별 판매금액 합계")             #그래프에 제목 넣기
            plt.bar(df_day.index,df_day['Amt'], label = '판매량')   # 막대그래프 생성
            plt.xticks(fontsize = 10, rotation=45)                  # x축 폰트 사이즈 및 눈금 회전
            plt.xlim(13, 16)                                        # x축 범위
            plt.xlabel('판매 시간대')                               # x축 레이블
            
        # 2번 실행(모델 별 판매금액)
        elif sel == 2:
            df_Name = test_data.groupby(['Name']).sum()
            plt.rc("font", family='Malgun Gothic')                  #한글 폰트 설정
            plt.title("2023년 02월 제품별 판매금액 합계")            #그래프에 제목 넣기
            plt.bar(df_Name.index,df_Name['Amt'], label = '판매량') # 막대그래프 생성
            plt.xticks(fontsize = 10, rotation=45)                  # x축 폰트 사이즈 및 눈금 회전
            plt.xlabel('제품명')                                    # x축 눈금 회전
            plt.ylabel('판매가격')                                  # y 축 레이블
            
        plt.legend()                                                # 범례 표시
        yesNo = input('그래프를 저장하시겠습니까>(y/n) : ')
        while True:
            if SelOpt(yesNo).startOpt() == "Y":  
                print('그래프를 저장 할',end=''); path = super().pathInput()
                plt.savefig(path) # 파일로 저장
                break
            elif SelOpt(yesNo).startOpt() == "N":
                print('저장을 취소합니다.')
                break
            else:
                print('잘못 입력했습니다. 다시 입력해주세요.')
                continue
        
        plt.show() # 그래프 그리기 
        
        
def startData():
    while True:
        os.system('cls')
        print("---데이터 관리---")
        print("외부  데이터  등록 : 1 ")
        print("날짜  별  판매금액 : 2 ")
        print("모델  별  판매금액 : 3 ")
        print("데이터  관리  종료 : 9 ")
        print("시스템        종료 : 0 ")
        sel = input("작업을 선택하세요 : ")
        if sel == '1' :
            FileInsert()
            os.system("pause")
            break
        elif sel == '2' :
            c3 = GraphsPreProcessing()
            c3.saleGraphShow(1)
            os.system("pause")
            break
        elif sel == '3' :
            c4 = GraphsPreProcessing()
            c4.saleGraphShow(2)
            os.system("pause")
            break
        elif sel == '9' :
            print("데이터 관리를 종료합니다. ")
            os.system("pause")
            os.system('cls')
            break
        elif sel == '0' :
            print("시스템을 종료합니다. ") 
            os.system("pause")
            os.system('cls')
            sys.exit(0)
        else :
            print("잘못 선택했습니다. ")
            os.system("pause")
            
if __name__ == "__main__" :
    startData()