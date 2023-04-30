# 빅데이터_모의평가3 제품관리시스템
# product 테이블에 대한 제품의 CRUD 및 sales 테이블과 product 테이블을 활용하여 판매기록 관리를 위한 CRUD 시스템
import os
import sys
from re import findall, match, sub   
import pymysql 
from wcwidth import wcswidth # 간격 맞춤 함수 라이브러리 / 2023-02-09
config = {                  
    'host' : '127.0.0.1',   
    'user' : 'root',        
    'passwd' : 'root1234',  
    'database' : 'test_db', 
    'port' : 3306,   
    'charset' : 'utf8',     
    'use_unicode' : True   
    }


#--------------------------
# 2023-02-13 
# <sql인젝션을 방지하기 위한 블랙리스트 함수>
# sql을 활용한 해킹 문제를 방지하기 위한 방법을 고민했습니다.
# sql의 명령어 뿐만 아니라 주석, 특수문자를 입력할 경우 ' '으로 변경되도록 필터링했습니다.
# ''을 통해 빈칸으로 만들 경우 SESELECTLET 같은 입력에 문제가 발생 할 수 있습니다.
# 그렇기 때문에 ' '으로 띄어쓰기로 변경했습니다. 
def sqlBlackList(st):
    ls_1 = ['char','nchar','varchar','--',';--',';','/*','*/','@@','@',\
        'nvarchar','alter','begin','cast','create','cursor','declare','delete',\
        'drop','end','exec','execute','fetch','insert','kill','open','select',\
        'sys','sysobjects','syscolumns''table','update','union','except','intersect',\
        'join','and','or','=','+','unionall','from','where',' information_schema',\
        'table_schema','!','?','^','#','~','$','%','&','*','(',')','+','=','like']
    for i in range(len(ls_1)):
        st = st.lower().replace(ls_1[i],' ')
    return st


#--------------------------
# 시스템 입력값 관리 클래스
class SelectOption() : 
    def __init__(self, option) :
        self.option = option                                # option = 사용자가 입력한 값 
        self.num_lst = ['1', '2', '3', '4', '5', '6', '9']  # 작업번호. (Key값으로 사용.)
        alpha_lst = ['C', 'R', 'RC', 'RN', 'U', 'D', 'X']   # 작업영어. (Value값으로 사용.)
        self.op_dict = dict(zip(self.num_lst, alpha_lst))   # 작업번호와 영어를 dictionary로 구성.
        self.select = ""    # 작업번호 최종출력.
        self.getOption()    # 클래스를 통해 객체를 만들 때 마지막 작업으로 getOption 메서드 실행.
      
    def getOption(self) :           # 작업(옵션)번호 획득 메서드.
        if self.option.isalpha() :  # 작업번호가 영어라면,
            self.option = self.option.upper()   # 작업번호(영어)를 전부 대문자로 바꾼다.
                                                # rc, rC, Rc, RC >> RC 로 바뀐다.
            reop_dict = dict(map(reversed, self.op_dict.items()))   
            print('reop_dict',reop_dict)
            print(self.op_dict.items())

            self.select = reop_dict.get(self.option, 0)     
            
        else : #작업번호가 숫자라면,
            self.select = self.option # 별도의 작업없이 진행한다.
      
    def startOption(self) :                 # 옵션 시작번호 메서드.
        if self.select in self.num_lst :    # getOption 메서드에서 작업한 self.select 변수가 self.num_lst에 존재할 경우,
            return self.select              # self.select를 반환한다.
        else :                              # 존재하지 않을 경우,
            return 0                        # 0(False)를 반환한다.


#--------------------------
# 출력 데이터 간격 맞춤 함수 / 2023-02-09
# 2byte의 데이터를 출력 시 출력데이터가 밀리는 현상이 발생합니다.
# 이런 문제를 방지하기 위한 함수입니다.
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
# 사용자가 입력한 데이터를 검사하는 필터 클래스
class InputFilter() : 
    def __init__(self):   
        self.inputValueFilter_result = False # 필터 결과
        self.no = ''    # sales테이블 인덱스
        self.scode = '' # code - 제품코드
        self.qty = ''   # qty - 제품 판매 수량
        self.pname = '' # pname = 제품명
        self.price = '' # price - 제품 가격 변수
        self.discrate = '' # discrate - 할인율 변수
        

    # 1. 인덱스(순서) 필터
    # 인덱스는 판매를 등록하면 자동으로 생성되는 데이터입니다.
    # 판매관리 시스템에서 특정 데이터를 선택하기 위한 기준을 고민했습니다.
    # 단 하나의 데이터로 식별 가능하면서 쉽게 입력이 가능한 데이터는
    # 인덱스(seqNo)컬럼으로 생각했습니다. 
    # 인덱스는 정수만 존재하는 컬럼입니다.
    # 기호, 공백 및 문자가 입력되지 않는 필터를 적용했습니다.
    
    def setNo(self, no):
        # sql 인젝션 블랙리스트 함수
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
    # 제품코드는 소문자 알파벳 하나와 숫자 3개 총 4자리로 존재합니다.
    # 기본적으로 입력값의 공백과 기호를 방지하는 필터를 적용합니다.
    # 그 후 정규식과 len함수를 이용하여 길이와 조건이 맞는지 필터링 합니다.
    # 정규식은 소문자 알파벳 1개와 이후 정수3자리를 확인하는 식 입니다.
    def setScode(self, scode):
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
    # 판매 수량 컬럼에는 정수만 존재하는 컬럼입니다.
    # 기호, 공백 및 문자가 입력되지 않는 필터를 적용했습니다.
    def setQty(self, qty):
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
    # 제품명에는 다양한 값이 입력될 수 있습니다.
    # 예를 들어 소니의 'wh-1000xm5'이나 삼성의 NT960XFG-K71A 2023 등
    # 소대문자 알파벳, 숫자, 기호, 한글 등 제품명에 모두 입력이 가능합니다.
    # 제품명에 입력될 수 없는 값은 무엇이 있을지 고민했습니다.
    # 그러다 오타를 필터링 하는 조건을 생각했습니다.
    # 오타의 종류에 공백값(빈칸)과 단모음, 단자음의 오타만을 사용했습니다.
    def setPname(self, pname) :
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
    # 제품가격에는 숫자만 입력이 가능합니다.
    # 필터의 조건으로 공백과 기호를 입력하지 못하게 하고 숫자만을 입력하도록 사용했습니다.
    def setPrice(self, price) :
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
    # 제품 할인율에는 실수만 입력이가능합니다.
    # 컴퓨터는 소수점 '.'를 기호로 판별합니다.
    # 그래서 정규표현식을 사용하여 실수의 형태의 형태로만 출력하려고 했습니다.
    # 하지만 정수를 입력하는 사용자도 있으며 꼭 실수의 할인율만 존재하는 경우는 없습니다.
    # 에를 들어 5% 할인의 경우 5를 입력하는 경우가 대부분입니다.
    # 그래서 정규표현식을 이용하여 정수와 실수를 입력한 경우에만 조건 True를 부여하고
    # 나머지 입력값에 False를 부여하는 반대의 상황으로 필터를 제작했습니다.
    def setDiscRate(self, discrate) :
        discrate = sqlBlackList(discrate)
        # 1) 정수와 실수를 입력한 경우 
        if findall('\d', discrate):
            self.discrate= discrate  
            self.inputValueFilter_result = True
        
        # 2) 해당 조건을 만족하지 못한 경우
        else:
            print('입력값 ' +str(discrate)+ ' 에는 정수와 실수만 입력이 가능합니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False # 필터 결과
            
        return self.inputValueFilter_result # 필터 결과 반환 


#--------------------------
# 사용자 입력 클래스 / 2023-02-09
# 입력값 데이터로 가져오기 위해서는 InputFilter클래스의 필터를 거쳐야 합니다.
# 매법 InputFilter를 호출하기보다는 필터 클래스를 상속받는 방법으로 변경했습니다.
# 사용자 입력값 매서드들은 현재 서비스에서는 매번 다르게 필요합니다.
# 그래서 클래스의 매서드로 만들어 필요할 경우에만 호출하도록 변경했습니다.
class UserInput(InputFilter):
    def __init__(self):
        super().__init__()
    #--------------------------    
    # 인덱스 입력 매서드
    # 제품코드는 제품관리 시스템에서는 등록,조회, 수정, 삭제 시 기준이 되는 컬럼이지만
    # 판매관리 시스템에서는 중복된 값이 존재합니다. 
    # 중복이 없는 seqNo 컬럼으로 삭제 기능을 구현하기 위해 만들었습니다..
    def noInput(self):
        while True:
            if super().setNo(input("No를 입력하세요 : ")) :
                in_no = self.no
                break
            else:
                continue
        return in_no


    #--------------------------    
    # 제품명 입력 매서드
    def nameInput(self):
        while True:
            if super().setPname(input("제품명을 입력하세요 : ")) : # 이름 필터 매서드 실행
                in_pname = self.pname
                break
            else:
                continue
        return in_pname


    #--------------------------    
    # 제품코드 입력 매서드
    def codeInput(self):
        while True:
            if super().setScode(input("제품코드를 입력하세요 : ")) :
                in_code = self.scode
                break
            else:
                continue
        return in_code


    #--------------------------
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
    
    
    #--------------------------
    # 제품 가격 입력 매서드
    def priceInput(self):
        while True:
            if super().setPrice(input("제품가격을 입력하세요 : ")) :
                in_price = self.price
                break
            else:
                continue
        return  in_price
    
    
    #--------------------------        
    # 할인율 입력 매서드
    def discRateInput(self):
        while True:
            if super().setDiscRate(input("제품 할인율을 입력하세요 : ")) :
                in_discrate = self.discrate
                break
            else:
                continue
        return  in_discrate
    
    
    #--------------------------
    # 입력 매서드 동시 호출
    def userInput(self):
        ls = []
        ls.append(self.nameInput())
        ls.append(self.priceInput())
        ls.append(self.discRateInput())
        return ls
    
    
#--------------------------      
# sales 테이블 SQL관리 클래스 / 2023-02-09
# <변경사항> 
# 사용하지 않는 SQL과 기존 SQL을 활용하는 방법을 사용하여
# 기존의 SQL문을 2개 줄였습니다.

# 매번 실행 매서드에 SQL을 입력하는 것에 불편을 느꼈습니다.
# SQL을 클래스로 만들어 간편하게 관리하고 클래스매서드를 이용해 실행하는 방법을 생각했습니다.
# 사용한 SQL식과 목적을 간단하게 기술했습니다.
class SalFind : 
    def __init__(self,find_sel): # 매개변수 (self, 찾을 SQL번호, SQL의 조건컬럼)     
        self.read_sel = find_sel
        
        # 1) 제품코드로 판매관리 필요 데이터 전체조회
        if find_sel == 3 or find_sel == '코드': 
            self.find_sql = "SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y.%m.%d %H:%i:%s') as date, s.qty, s.amt FROM sales AS s JOIN product AS p ON s.sCode = p.pCode WHERE p.pCode " 
        # 2) 제품명으로 판매관리 필요 데이터 전체조회
        elif find_sel == 4 or find_sel == '제품명': 
            self.find_sql = "SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y.%m.%d %H:%i:%s') as date, s.qty, s.amt FROM sales AS s JOIN product AS p ON s.sCode = p.pCode WHERE p.pName "
        # 3) 판매관리 필요 데이터 전체조회
        elif find_sel == 0:
            self.find_sql = "SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y.%m.%d %H:%i:%s') as date, s.qty, s.amt FROM sales AS s LEFT OUTER JOIN product AS p ON s.sCode = p.pCode"
        # 4) product테이블에서 제품가격과 할인율 가져오기
        # 판매관리 데이터에 입력 될 가격은 판매수량과 제품 가격의 곱입니다.
        # 그러다 원 제품 가격에 할인율을 적용해서 계산하는 방법을 생각했습니다.
        # 이 방법을 위해 필요한 데이터는 제품의 가격과 제품의 할인율 입니다.
        # 할인율과 제품 가격이 변동되어도 판매수량만 입력하면 자동으로 판매가격이 계산됩니다. 
        elif find_sel == 1:
            self.find_sql = "SELECT unitPrice, discountRate FROM product WHERE pCode" 
        # 5) 인덱스로 제품코드 조회
        elif find_sel == 2:
            self.find_sql = "SELECT sCode FROM sales WHERE seqNo" 
        
        
    # SQL 실행 매서드        
    def salFind(self, find_in_data='') : 
        try :
            conn = pymysql.connect(**config)    # 딕셔너리 config를 인수로 사용하여 conn 객체를 만듬.
            cursor = conn.cursor()
            # 데이터 전체 조회 
            if self.read_sel == 0: 
                sql = self.find_sql       
            # 제품명으로 조회    
            elif self.read_sel == '제품명': 
                sql = self.find_sql + f"like '%{find_in_data}%'" + "ORDER BY s.sDate"

            elif self.read_sel == '코드': 
                sql = self.find_sql + f"= '{find_in_data}'" + "ORDER BY s.sDate"
            
            else:
                sql = self.find_sql + f"= '{find_in_data}'"
                
            cursor.execute(sql)                 # sql명령 실행
            return cursor.fetchall()            # select 쿼리문의 실행 결과를 return함
                                                # 쿼리의 실행결과가 없으면 요소의 갯수가 0인 리스트가 반환됨
        except Exception as e :                 # 에러 발생 시
            print('db 연동 실패 : ', e)         # 에러 메시지 리턴
            conn.rollback()                     # 실행 취소 
            
        finally:                                # 실행 순서에 반대로 닫기
            cursor.close()                      # cursor 객체 닫기
            conn.close()                        # conn 객체 닫기 
            
    # 특정 조건의 판매기록 검색 레코드        
    def salReadOne(self) :
        try :
            conn = pymysql.connect(**config)    # 딕셔너리 config를 인수로 사용하여 conn 객체를 만듬.
            cursor = conn.cursor()    # conn 객체로부터 cursor() 메소드를 호출하여 cursor 참조변수를 만듬.
            # 클래스 호출 삭제, 클래스 매서드로 변경되어 self로 호출 가능 / 2023-02-10
            # 더미 코드 삭제 / 2023-02-10
            # os.system('cls') # 실행결과 스샷을 위해 주석처리
            
            salReadAll() # sales테이블의 전체 데이터 출력 
            c1 = UserInput()

            if self.read_sel == '코드' :
                print("<<<제품 개별 조회({})입니다>>>".format(self.read_sel))
                print("조회할 ",end='')
                in_code = c1.codeInput()

            elif self.read_sel == '제품명' : 
                print("<<<제품 개별 조회({})입니다>>>".format(self.read_sel))
                print("조회할 ",end='')
                in_code = c1.nameInput()
            
            rows = self.salFind(in_code)
            # 전체데이터 출력조건 삭제 (기존 코드와 중복) / 2023-02-10 
                
            if self.read_sel == '코드' or self.read_sel == '제품명' :
                if len(rows) > 0 :
                    print("===테이블 조회2({})===".format(self.read_sel))
                    # 출력 데이터 정렬 함수 사용 / 2023-02-09 
                     # SQL 입력 후 결과 출력 / 2023-02-10 
                    print(f"{fmt('No',6,'l')}{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('판매등록일자',25,'l')}{fmt('판매수량',16,'l')}{fmt('총 판매가격',5,'l')}")
                    for row in rows :
                        print(f"{fmt(row[0],6,'l')}{fmt(row[1],10,'l')}{fmt(row[2],20,'l')}{fmt(row[3],28,'l')}{fmt(row[4],13,'l')}{fmt(row[5],5,'l')}")
                else:
                    print("조회결과 입력한 {}에 맞는 제품이 없습니다".format(self.read_sel))
                    
                    
                       
        except Exception as e :
            print('db 연동 실패 : ', e)
            conn.rollback() # 실행 취소 
        finally:
            cursor.close()
            conn.close()    
 
 
#--------------------------
#   판매 관리 기능 시작   #
#--------------------------
# (1) 판매기록 등록 함수      
def salCreate() :
    try :
        conn = pymysql.connect(**config)    # 딕셔너리 config를 인수로 사용하여 conn 객체를 만듬.
        cursor = conn.cursor()        # conn 객체로부터 cursor() 메소드를 호출하여 cursor 참조변수를 만듬.
        
        # os.system('cls') # 실행결과 스샷을 위해 주석처리
        # SalFind 클래스 호출 삭제 / 2023-02-10
        # 요구사항에 따라 전체목록 출력문 삭제
        c2 = UserInput() # 사용자 입력 클래스 호출
        print("<<<판매기록 등록입니다>>>")
        print('등록할 데이터의 ',end='') 
        in_code = c2.codeInput() # 제품코드 입력함수 호출
                                 # 제품코드 입력 시 필터링도 같이 수행됩니다.
                                 # InputFilter클래스의 setScode 매서드 참조
        c1 = SalFind(3)
        rows_c1 = c1.salFind(in_code)
        # 코드 입력값이 공백이 아닌 경우 
        if in_code != '' :
            # SQL 할인율과 제품가격 조회 / 2023-02-08         
            # product테이블에서 할인율과 가격 정보를 가져온다.
            

            #1) product 테이블에 해당 제품코드의 상품이 존재하지 않는 경우            
            if len(rows_c1) == 0:
                iValue = c2.userInput() # 사용자 입력 함수 호출
                sql = f"INSERT INTO product(pCode, pName, UnitPrice, discountRate) VALUES('{in_code}','{iValue[0]}', '{iValue[1]}', '{iValue[2]}')" 
                cursor.execute(sql)
                conn.commit()
                print("제품등록을 성공했습니다.")
            
            #2) product 테이블에 해당 제품코드의 상품이 존재하는 경우
            else :
                c3 = SalFind(1)
                rows_c3 = c3.salFind(in_code)
                ##############################################################
                # 가격 계산 / 2023-02-08
                ##############################################################
                # 할인율을 계산하는 방식을 고민했습니다.
                # 문제에 주어진 방법은 할인율을 적용하지 않고 제품 가격에 판매수량을 곱한 방법입니다.
                # 만약 할인율이 적용된다면 원래 제품 가격에 할인율을 적용한 가격을 가져와야합니다.
                # 방법<1>에서는 원 제품 가격에 할인율을 적용 한 가격을 가져오는 코드입니다.
                # <1> 할인율이 적용된 가격 계산
                dis_price = round(((rows_c3[0][0]) * (100 - round(rows_c3[0][1])))/100)
                print(dis_price)
                # <2> 할인율이 적용되지 않은 가격 계산 <요구사항>
                # price = rows_c3[0][0] # 제품 가격 출력 / 2023-02-08
                ##############################################################
                
                iValue = c2.qtyInput() # 사용자 입력 함수 호출
                # <1>할인율이 적용된 총 가격
                total_price = dis_price * int(iValue[0])
                
                # <2>할인율이 적용되지 않은 총 가격
                # total_price = price * int(iValue[0])
                
                sql = f"INSERT INTO sales(sCode, Qty, Amt) VALUES('{in_code}','{iValue[0]}', '{total_price}')" 
                cursor.execute(sql)
                conn.commit()
                print("판매기록 등록을 성공했습니다.")

                print("<<<판매기록 목록 조회입니다>>>")
                
        # SQL조회 결과가 없는 경우
        else :
            print("판매기록이 없습니다.")
            
    except Exception as e :
        print('오류 : ', e)
        conn.rollback() # 실행 취소 
        
    finally:
        cursor.close()
        conn.close()
        
        
#--------------------------   
# (2) 판매기록 수정 함수
def salUpdate() : 
    # os.system('cls') # 실행결과 스샷을 위해 주석처리
    print("<<<판매기록을 수정합니다>>>")
    # 필요 없는 코드 삭제 / 2023-02-09
    # 클래스 호출 코드 삭제 / 2023-02-10
    salReadAll() # 전체 데이터 출력
    c2 = UserInput()
    print('수정할 데이터의 ',end='')
    in_code = c2.codeInput() # 제품코드 입력 매서드 호출
    c1 = SalFind(3)
    rows = c1.salFind(in_code)
    
    try :
        conn = pymysql.connect(**config)    
        cursor = conn.cursor()
        # SELECT 쿼리 실행결과가 있는 경우               
        if rows : 
            print("<<<판매기록 목록 조회입니다>>>")
            print(f"{fmt('No',6,'l')}{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('판매등록일자',25,'l')}{fmt('판매수량',16,'l')}{fmt('총 판매가격',5,'l')}")
            for row in rows :
                print(f"{fmt(row[0],6,'l')}{fmt(row[1],10,'l')}{fmt(row[2],20,'l')}{fmt(row[3],28,'l')}{fmt(row[4],13,'l')}{fmt(row[5],5,'l')}")
            print('수정할 데이터의 ',end='')
            in_no = c2.noInput()
            # 제품 수정 확인문
            yesNo = input('수정하시겠습니까>(y/n) : ')
            # 제품 수정 확인 입력값에서 y 입력 시 대문자 입력 상황도 가정했습니다.
            # 또한 한글로 입력할 경우도 가정하여 조건식을 추가했습니다.
            if yesNo.upper() == "Y" or yesNo == "ㅛ": 
                print("<<<수정할 데이터를 입력하세요.>>>")
                in_qty = c2.qtyInput()  # 사용자 입력 함수를 호출 / 2023-02-09
                # 입력한 인덱스(순번)을 이용하여 제품 코드를 찾는 SQL / 2023-02-09
                search_code = SalFind(5)
                # 찾은 제품코드를 실행하는 매서드 호출 / 2023-02-09
                rows1 = search_code.salFind(in_no)
                # 제품코드를 이용하여 제품의 가격과 할인율을 가져오는 SQL / 2023-02-09
                c1 = SalFind(1)
                # SQL을 실행하는 매서드 호출 / 2023-02-09
                rows = c1.salFind(rows1[0][0])
                # 구매 수량에 따른 총 가격 계산 
                price = rows[0][0] # 제품코드를 이용하여 찾은 제품의 가격 / 2023-02-09
                total_price = price * int(in_qty) # 제품 가격과 판매 수량을 계산한 총 판매 가격 / 2023-02-09
                # 판매 기록을 수정하는 SQL / 2023-02-09 
                sql = f"UPDATE sales SET Qty = '{in_qty}', Amt = '{total_price}' WHERE seqNo = '{in_no}'"
                cursor.execute(sql) 
                conn.commit()       
                print("<<<수정을 완료했습니다>>>")
                print("<<<수정 결과입니다>>>")
                salReadAll()
                # 판매관리를 위한 데이터를 가져오는 SQL을 호출하는 클래스 / 2023-02-09
                

            else:
                print("<<<수정을 취소했습니다.>>>")
        # SELECT 쿼리 실행결과가 없는 경우        
        else : 
            print('수정할 제품코드가 없습니다.')
            pass
        
    except Exception as e :
        print('db 연동 실패 : ', e)
        conn.rollback() # 실행 취소 
    finally:
        cursor.close()
        conn.close()
        
#--------------------------
# (3) 판매기록 삭제 함수
def salDelete() : 
    # os.system('cls') # 실행결과 스샷을 위해 주석처리
    print("<<<판매기록 삭제합니다>>>")
    # ProdFind클래스에서 호출 삭제 2023-02-10 / 제품 테이블 전체 
    salReadAll()
    c2 = UserInput()
    print('삭제할 데이터의 ',end='') 
    in_code = c2.codeInput() # 제품코드 입력 매서드 호출
    c1 = SalFind(3)
    rows = c1.salFind(in_code)
    
    try :
        conn = pymysql.connect(**config)    
        cursor = conn.cursor()              
        if rows : 
            print("<<<선택한 제품코드의 판매기록 목록 조회입니다>>>")
            print(f"{fmt('No',6,'l')}{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('판매등록일자',25,'l')}{fmt('판매수량',16,'l')}{fmt('총 판매가격',5,'l')}")
            for row in rows :
                print(f"{fmt(row[0],6,'l')}{fmt(row[1],10,'l')}{fmt(row[2],20,'l')}{fmt(row[3],28,'l')}{fmt(row[4],13,'l')}{fmt(row[5],5,'l')}")
            print('수정할 데이터의 ',end='')
            in_no = c2.noInput()
            search_code = SalFind(2)
            # 찾은 제품코드를 실행하는 매서드 호출 / 2023-02-09
            rows1 = search_code.salFind(in_no)
            if rows1:
                sql = f"DELETE FROM sales WHERE seqNo = '{in_no}'"
                cursor.execute(sql) # SQL문 실행
                conn.commit()       # DB에 실행결과 저장
                print('삭제 성공했습니다.')
                print()
            else :
                print('삭제 실패했습니다.')
                os.system("pause")
            
    except Exception as e :
        print('db 연동 실패 : ', e)
        conn.rollback() # 실행 취소 
    
    finally:
        cursor.close()
        conn.close()
    
    salReadAll()

  
#--------------------------
#(4) 제품코드의 전체 목록조회 함수
# 출력 데이터 맞춤 함수 사용 / 2023-02-10
def salReadAll() :
    # os.system('cls') # 출력결과 스샷을 위해 주석처리
    print("<<<제품 목록 조회입니다>>>")
    c1 = SalFind(0)
    rows_c1 = c1.salFind()
    # SQL 입력 후 결과 출력 / 2023-02-10 
    print(f"{fmt('No',6,'l')}{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('판매등록일자',25,'l')}{fmt('판매수량',16,'l')}{fmt('총 판매가격',5,'l')}")
    for row in rows_c1 :
        print(f"{fmt(row[0],6,'l')}{fmt(row[1],10,'l')}{fmt(row[2],20,'l')}{fmt(row[3],28,'l')}{fmt(row[4],13,'l')}{fmt(row[5],5,'l')}")


#################################################################
    #--------------------------
    #   제품 관리 기능 시작   #
    #--------------------------
#################################################################
# product 테이블 SQL관리 클래스 / 2023-02-09
# <변경사항> 
# 사용하지 않는 SQL과 기존 SQL을 활용하는 방법을 사용하여
# 기존의 SQL문을 2개 줄였습니다.

# 매번 실행 매서드에 SQL을 입력하는 것에 불편을 느꼈습니다.
# SQL을 클래스로 만들어 간편하게 관리하고 클래스매서드를 이용해 실행하는 방법을 생각했습니다.
# 사용한 SQL식과 목적을 간단하게 기술했습니다.
class ProdFind :
    def __init__(self,find_sel): # 매개변수 (찾을 SQL번호, 조건컬럼)  
        self.read_sel = find_sel

        # 1) 제품코드를 이용하여 product테이블의 해당 데이터 호출
        if find_sel == 3 or find_sel == '코드': 
            self.find_sql = "SELECT * FROM product WHERE pCode "
        # 2) 제품명를 이용하여 product테이블의 해당 데이터 호출
        elif find_sel == 4 or find_sel == '제품명': 
            self.find_sql = "SELECT * FROM product WHERE pName " 
        # 3)product테이블의 전체 데이터 호출
        elif find_sel == 0:
            self.find_sql = "SELECT * FROM product"
    
    # 제품 검색 SQL 실행 매서드    
    def prodFind(self, find_in_data = '') : 
        try :
            conn = pymysql.connect(**config)    # 딕셔너리 config를 인수로 사용하여 conn 객체를 만듬.
            cursor = conn.cursor()              # conn 객체로부터 cursor() 메소드를 호출하여 cursor 참조변수를 만듬.
            if self.read_sel == 0: 
                sql = self.find_sql
            # 특정 문자열만으로 제품명 검색 / 2023-02-10
            elif self.read_sel == '제품명':
                sql = self.find_sql + f"like '%{find_in_data}%'" # like함수를 통해서 일부의 제품명으로 
                                                                 # 제품 검색이 가능합니다.                 
            else:
                sql = self.find_sql + f"= '{find_in_data}'"
            cursor.execute(sql)                 # sql명령 실행
            return cursor.fetchall()            # select 쿼리문의 실행 결과를 return함
                                                # 쿼리의 실행결과가 없으면 요소의 갯수가 0인 리스트가 반환됨
        except Exception as e :                 # 에러 발생 시
            print('db 연동 실패 : ', e)         # 에러 메시지 리턴
            conn.rollback()                     # 실행 취소 
            
        finally:                                # 실행 순서에 반대로 닫기
            cursor.close()                      # cursor 객체 닫기
            conn.close()                        # conn 객체 닫기 

    # 특정 조건의 제품 검색 레코드
    def prodReadOne(self) :
        try :
            conn = pymysql.connect(**config)    
            cursor = conn.cursor()    
            # os.system('cls') # 실행결과 스샷을 위해 주석처리
            # 더미 코디 삭제 / 2023-02-09
            
            # 전체 로우 출력 / 2023-02-09
            prodReadAll()
            c1 = UserInput()
            
            # 1) 제품코드에 해당하는 로우를 가져올 경우 
            if self.read_sel == '코드' :
                print("<<<제품 개별 조회({})입니다>>>".format(self.read_sel))
                print("조회할 ",end='')
                in_code = c1.codeInput()
                
            # 2) 제품명 해당하는 로우를 가져올 경우    
            elif self.read_sel == '제품명' : 
                print("<<<제품 개별 조회({})입니다>>>".format(self.read_sel))
                print("조회할 ",end='')
                in_code = c1.nameInput()
                
            rows = self.prodFind(in_code)    
            #     
            if self.read_sel == '코드' or self.read_sel == '제품명' :
                if len(rows) > 0 :
                    print("===테이블 조회2({})===".format(self.read_sel))
                    print(f"{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('제품가격',11,'l')}{fmt('할인율',20,'l')}")
                    for row in rows :
                        print(f"{fmt(row[0],10,'l')}{fmt(row[1],20,'l')}{fmt(row[2],11,'l')}{fmt(row[3],20,'l')}")  
                else:
                    print("조회결과 입력한 {}에 맞는 제품이 없습니다".format(self.read_sel))
                       
        except Exception as e :
            print('db 연동 실패 : ', e)
            conn.rollback() # 실행 취소 
        finally:
            cursor.close()
            conn.close()


# (1) 제품 생성 함수 
def prodCreate():
    try :
        conn = pymysql.connect(**config)    # 딕셔너리 config를 인수로 사용하여 conn 객체를 만듬.
        cursor = conn.cursor()        # conn 객체로부터 cursor() 메소드를 호출하여 cursor 참조변수를 만듬.
        
        # os.system('cls') # 실행결과 스샷을 위해 주석처리
        print("<<<제품 등록입니다>>>")
        c2 = UserInput() # 2023-02-09 사용자 입력 클래스 호출
        in_code = c2.codeInput() # 제품코드 입력 매서드 호출
                                # 제품코드 입력 시 필터링도 같이 수행됩니다.
                                # InputFilter클래스의 setScode 매서드 참조 / 2023-02-09 설명 내용 수정
        
        # 코드 입력값이 공백이 아닌 경우 
        # 입력값을 입력 시 필터의 기능에 공백값을 제한하는 기능이 포함되어 있다.   
        if in_code != '' :
            # SQL관리 클래스 호출 3번
            # 3번은 제품코드를 입력하여 PRODUCT  
            c1 = ProdFind(3)
            rows = c1.prodFind(in_code) 
            #1) 같은 제품코드가 존재하는 상황
            if len(rows) :
                print("해당 제품코드는 이미 존재하고 있습니다. 다른 제품코드를 입력하세요")
            
            #2) 같은 제품코드가 존재하지 않는 상황
            else :
                iValue = c2.userInput() # 사용자 입력 함수 호출
                #
                sql = f"INSERT INTO product(pCode, pName, UnitPrice, discountRate) VALUES('{in_code}','{iValue[0]}', '{iValue[1]}', '{iValue[2]}')" 
                cursor.execute(sql)
                conn.commit()
                print("제품등록을 성공했습니다.")
                print()
                
        # 코드 입력값이 ''인 경우
        else :
            print("제품 등록을 위해 제품코드를 입력해 주세요")
            
    except Exception as e :
        print('오류 : ', e)
        conn.rollback() # 실행 취소 
        
    finally:
        cursor.close()
        conn.close()
        
        
#--------------------------   
# (2) 제품 수정 함수
def prodUpdate() : 
    # os.system('cls') # 실행결과 스샷을 위해 주석처리
    # 전체 목록 조회 함수 호출 / 2023-02-09
    prodReadAll()
    # 사용자 입력 클래스 호출
    c2 = UserInput()
    # 제품 검색 SQL에서 3번 실행
    # 제품 코드를 이용하여 해당 제품코드에 해당하는 로우를 호출
    print("<<<제품 수정입니다>>>")
    in_code = c2.codeInput() # 제품 코드 입력 매섣, 호출
    c1 = ProdFind(3)  
    # SQL을 실행 후 호출한 데이터 
    rows_c1 = c1.prodFind(in_code) # 제품 검색 매서드 실행
    try :
        conn = pymysql.connect(**config)    
        cursor = conn.cursor()
        # SELECT 쿼리 실행결과가 존재하는 경우               
        if rows_c1 : 
            print("<<<제품코드 조회결과입니다>>>")
            # SQL 실행결과 반환
            print(f"{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('제품가격',11,'l')}{fmt('할인율',20,'l')}")
            for row in rows_c1 :
                print(f"{fmt(row[0],10,'l')}{fmt(row[1],20,'l')}{fmt(row[2],11,'l')}{fmt(row[3],20,'l')}")
            # 제품 수정 확인문
            yesNo = input('수정하시겠습니까>(y/n) : ')
            # 조건 수정 / 2023-02-04
            # 제품 수정 확인 입력값에서 y 입력 시 대문자 입력 상황도 가정했습니다.
            # 또한 한글로 입력할 경우도 가정하여 조건식을 추가했습니다.
            if yesNo.upper() == "Y" or yesNo == "ㅛ": 
                print("<<<수정할 내용을 입력하세요.>>>")
                iValue = c2.userInput()  # 사용자 입력 함수를 호출
                sql = f"UPDATE product SET pName = '{iValue[0]}', UnitPrice = '{iValue[1]}', discountRate ='{iValue[2]}' WHERE pCode = '{in_code}'"
                cursor.execute(sql) 
                conn.commit()       
                print("<<<수정을 완료했습니다>>>")
                print("<<<수정 결과입니다>>>")
                print(f"{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('제품가격',11,'l')}{fmt('할인율',20,'l')}")
                print(f"{fmt(in_code,10,'l')}{fmt(iValue[0],20,'l')}{fmt(iValue[1],11,'l')}{fmt(iValue[2],20,'l')}")
            else:
                print("<<<수정을 취소했습니다.>>>")
        # SELECT 쿼리 실행결과가 없는 경우        
        else : 
            print('수정할 제품코드가 없습니다.')
            pass
        
    except Exception as e :
        print('db 연동 실패 : ', e)
        conn.rollback() # 실행 취소 
    finally:
        cursor.close()
        conn.close()
        
#--------------------------
# (3) 제품 삭제 함수
def prodDelete() : 
    # os.system('cls') # 실행결과 스샷을 위해 주석처리
    # 제품 전체 출력 함수 호출 / 2023-02-09
    prodReadAll()
    
    try :
        conn = pymysql.connect(**config)    
        cursor = conn.cursor()              
        print("<<<삭제할 제품코드를 입력하세요>>>")
        c2 = UserInput()
        in_code = c2.codeInput() # 제품 코드 입력 함수 호출
        # 제품 테이블에서 입력한 값에 해당하는 학번에 해당하는 값을 찾는 SQL 
        sql = f"SELECT * FROM product WHERE pCode = '{in_code}'" 
                                                            
        cursor.execute(sql) # SQL문 실행 
        rows = cursor.fetchall() # SQL문에 해당하는 값 리턴
        
        # 1) 데이터가 존재하는 경우
        if rows :
            # 테이블 레코드 삭제 SQL 
            sql = f"DELETE FROM product WHERE pCode = '{in_code}'" 
            cursor.execute(sql) # SQL문 실행
            conn.commit()       # DB에 실행결과 저장
            print('삭제 성공했습니다.')
            # os.system("pause") # 기능 진행 시 부자연스러운 멈춤이라 생각하여 코드 삭제 / 2023-02-09
            
        # 2) 데이터가 존재하지 않는 경우
        else :
            print('삭제 실패했습니다.')
            print('입력한 값에 해당하는 데이터가 존재하지 않습니다.')
            os.system("pause")
            
    except Exception as e :
        print('db 연동 실패 : ', e)
        conn.rollback() # 실행 취소 
    
    finally:
        cursor.close()
        conn.close()
    
    print("<<<목록 조회입니다>>>")
    # SQL을 다시 실행하는 이유
    # 로우를 삭제하여 기존 SQL실행결과를 다시 출력하면
    # 삭제전의 SQL결과가 출력되므로 다시 SQL을 실행 한후에
    # 출력결과를 보여주어야 한다. / 2023-02-09
    
    # 제품 전체 출력 함수 호출 / 2023-02-09
    prodReadAll()
        


#--------------------------
# ProdRead클래스는 ProdFind 클래스의 하위 매서드로 흡수 후 해당 코드 삭제 / 2023-02-10
#--------------------------
# 제품코드의 전체 목록조회 함수
def prodReadAll() :
    # os.system('cls') # 실행결과 확인을 위해 주석 처리
    print("<<<제품 전체 목록 조회입니다>>>")
    c1 = ProdFind(0)
    rows_c1 = c1.prodFind()
    # SQL 입력 후 결과 출력 / 2023-02-09 
    print(f"{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('제품가격',11,'l')}{fmt('할인율',20,'l')}")
    for row in rows_c1 :
        print(f"{fmt(row[0],10,'l')}{fmt(row[1],20,'l')}{fmt(row[2],11,'l')}{fmt(row[3],20,'l')}")

################################################################

#--------------------------        
# 테이블 생성 함수
def tableCreate() :  
    try :
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        sql = """CREATE table if not exists sales (
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
if __name__ == "__main__" :
    tableCreate() # 테이블이 없는 경우 테이블 생성코드 주석해제 / 2023-02-08
    
    while True:
        os.system('cls')
        print("---관리 시스템 실행---")
        print("제품관리실행 : 1 ")
        print("판매관리실행 : 2 ")
        print("서비스  종료 : 3 ")
        sys_sel = int(input("작업을 선택하세요 : "))
    
        if sys_sel == 1:
            # 제품관리 서비스 실행
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
                selnum = input("작업을 선택하세요 : ") # 사용자가 작업을 선택한다. (rn, rN, Rn, RN, 4 등등)
                so = SelectOption(selnum) # 사용자가 선택한 작업을 클래스에 적용시킨다.
                sel = int(so.startOption()) # 선택한 작업에 맞는 번호를 반환받고, 아래 if문들에 적용하기 위하여 type: int로 바꾼다.
                if sel == 1 :
                    prodCreate()
                    os.system("pause")
                elif sel == 2 :
                    prodReadAll()
                    os.system("pause")
                elif sel == 3 :
                    r3 = ProdFind('코드')
                    r3.prodReadOne()
                    os.system("pause")

                elif sel == 4 :
                    r4 = ProdFind('제품명')
                    r4.prodReadOne()
                    os.system("pause")
                elif sel == 5 :
                    prodUpdate()
                    os.system("pause")
                elif sel == 6 :
                    prodDelete()
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
            
        elif sys_sel == 2:    
            # 판매관리 서비스 실행
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
                if sel == 1 :
                    salCreate()
                    os.system("pause")
                elif sel == 2 :
                    salReadAll()
                    os.system("pause")
                elif sel == 3 :
                    r3 = SalFind('코드1')
                    r3.salReadOne()
                    os.system("pause")
                elif sel == 4 :
                    r4 = SalFind('제품명1')
                    r4.salReadOne()
                    os.system("pause")
                elif sel == 5 :
                    salUpdate()
                    os.system("pause")
                elif sel == 6 :
                    salDelete()
                    os.system("pause")
                elif sel == 9 :
                    print("판매관리를 종료합니다. ") # 시스템에 맞게 출력문 수정 / 2023-02-09
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
        
        elif sys_sel == 3:
            print("시스템을 종료합니다. ") 
            os.system("pause")
            os.system('cls')
            sys.exit(0)
            
        else :
            print("잘못 선택했습니다. ")
            os.system("pause")
            
        