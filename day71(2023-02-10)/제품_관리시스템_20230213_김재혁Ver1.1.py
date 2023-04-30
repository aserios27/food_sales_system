# 빅데이터_모의평가3 제품관리시스템
# product 테이블에 대한 제품의 CRUD

import os
import sys
from re import findall, match # 2023-02-04 라이브러리 추가
from datetime import date     # 2023-02-04 라이브러리 추가
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
        return txt + ' '*blank

    elif align == 'r':
        return ' ' * blank
    
    black_l = blank//2
    black_r = blank - black_l
    return ' ' * blank + txt + ' ' * black_r


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
# 사용자가 입력한 데이터를 검사하는 필터 클래스
class InputFilter() : 
    def __init__(self):   
        self.inputValueFilter_result = False # 필터 결과  
        self.pcode = '' # code - 제품코드, 변수
        self.pname = ''  # pname  - 제품명 변수
        self.price = '' # price - 제품 가격 변수
        self.discrate = '' # discrate - 할인율 변수
    
    # 1. 제품코드 필터
    # 제품코드는 소문자 알파벳 하나와 숫자 3개 총 4자리로 존재합니다.
    # 기본적으로 입력값의 공백과 기호를 방지하는 필터를 적용합니다.
    # 그 후 정규식과 len함수를 이용하여 길이와 조건이 맞는지 필터링 합니다.
    # 정규식은 소문자 알파벳 1개와 이후 정수3자리를 확인하는 식 입니다.
    def setPcode(self, pcode):
        # 1) 입력한 값이 공백이나 기호가 있을 경우
        if pcode.isalnum() == False: 
            print('입력값 ' +str(pcode)+ ' 에 공백이나 기호가 있습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        
        # 2) 입력한 값이 소문자 알파벳1개와 정수3개로 되어 있으며 길이가 4자리인지 필터링    
        elif not (match('[a-z][0-9]{3}', pcode) and len(pcode)==4): 
            print('입력값 ' +str(pcode)+ ' 에는 a001 과 같이 소문자와 숫자를 조합한 4자리의 값만 입력이 가능합니다.')
            self.inputValueFilter_result = False
            
        # 3) 모든 조건을 만족하는 경우        
        else:
            self.inputValueFilter_result = True 
            self.pcode = pcode                     
        return self.inputValueFilter_result 

    
    # 2. 제품명 필터 
    # 제품명에는 소니의 'wh-1000xm5'나 삼성의 NT960XFG-K71A 2023 등
    # 소대문자 알파벳, 숫자, 기호, 한글 등 모두 입력이 가능합니다.
    # 필터의 조건으로 공백값과 단모음, 단자음의 오타만을 사용했습니다.
    def setPname(self, pname) :
        # 1) 입력한 값이 공백인 경우
        if pname == '' or len(pname) < 0:
            print('입력값 ' +str(pname)+ ' 에는 빈칸을 입력하실 수 없습니다. 다시 입력해주세요.')
            self.inputValueFilter_result = False 
        # 2) 입력한 값에 단모음, 단자음이 있는 경우
        elif findall('[ㄱ-ㅎ|ㅏ-ㅣ]', pname): 
            print('입력값 ' +str(pname)+ ' 에는 단모음, 단자음을 입력할 수 없습니다.')
            self.inputValueFilter_result = False
        # 3) 모든 조건을 만족하는 경우
        else:
            self.inputValueFilter_result = True 
            self.pname = pname                          
        return self.inputValueFilter_result 
    
    # 3. 제품 가격 필터
    # 제품가격에는 숫자만 입력이 가능합니다.
    # 필터의 조건으로 공백과 기호를 입력하지 못하게 하고 숫자만을 입력하도록 사용했습니다.
    def setPrice(self, price) :
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
    
    # 4. 제품 할인율 필터
    # 제품 할인율에는 실수만 입력이가능합니다.
    # 컴퓨터는 소수점 '.'를 기호로 판별합니다.
    # 그래서 정규표현식을 사용하여 실수의 형태의 형태로만 출력하려고 했습니다.
    # 하지만 정수를 입력하는 사용자도 있으며 꼭 실수의 할인율만 존재하는 경우는 없습니다.
    # 에를 들어 5% 할인의 경우 5를 입력하는 경우가 대부분입니다.
    # 그래서 정규표현식을 이용하여 정수와 실수를 입력한 경우에만 조건 True를 부여하고
    # 나머지 입력값에 False를 부여하는 반대의 상황으로 필터를 제작했습니다.
    def setDiscRate(self, discrate) :
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
# 매법 InputFilter클래스를 호출하여 사용하기보다는 
# 필터 클래스를 상속받는 방법으로 변경했습니다.
# 입력값 매서드를 각각의 매서드로 분리했습니다. --> 모듈 독립
# 클래스 매서드의 분리로 필요시 각각의 입력 매서드 호출이 가능하도록 변경했습니다.
# 등록이나 수정 기능 동작 시 모든 입력 매서드를 동작시키는 userInput매서드를 추가했습니다.
class UserInput(InputFilter):
    def __init__(self):
        super().__init__()
        
#--------------------------    
# 제품코드 입력 매서드
# 제품코드는 등록,조회, 수정, 삭제 시 기준이 되는 컬럼이자 primary key입니다.
# 그래서 사용자 입력 함수와 별도로 자주 호출됩니다. 
    def codeInput(self):
        while True:
            if super().setPcode(input("제품코드를 입력하세요 : ")) :
                in_code = self.pcode
                break
            else:
                continue
        return in_code

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
    
    # 입력 매서드 동시 호출
    def userInput(self):
        ls = []
        ls.append(self.nameInput())
        ls.append(self.priceInput())
        ls.append(self.discRateInput())
        return ls


#--------------------------      
# 제품 검색 SQL 클래스 / 2023-02-11

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
            
            
        #         # 6) 제품코드를 이용하여 product테이블의 해당 데이터 호출
        # if find_sel == 6 or find_sel == '코드2': 
        #     self.find_sql = "SELECT * FROM product WHERE pCode "
        # # 2) 제품명를 이용하여 product테이블의 해당 데이터 호출
        # elif find_sel == 7 or find_sel == '제품명2': 
        #     self.find_sql = "SELECT * FROM product WHERE pName " 
        # # 3)product테이블의 전체 데이터 호출
        # elif find_sel == 9:
        #     self.find_sql = "SELECT * FROM product"
    
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
            
            # 1) 제품코드에 해당하는 로우를 가져올 경우 
            if self.read_sel == '코드' :
                print("<<<제품 개별 조회({})입니다>>>".format(self.read_sel))
                in_code = input("조회할"+self.read_sel+"를 입력하세요 : ")
                rows = self.prodFind(in_code)
                
            # 2) 제품명 해당하는 로우를 가져올 경우    
            elif self.read_sel == '제품명' : 
                print("<<<제품 개별 조회({})입니다>>>".format(self.read_sel))
                in_code = input("조회할"+self.read_sel+"를 입력하세요 : ")
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

#--------------------------
#        기능 시작        #
#--------------------------
# (1) 제품 생성 함수      
def prodCreate() :
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
    c1 = ProdFind(3,in_code)  
    # SQL을 실행 후 호출한 데이터 
    rows_c1 = c1.prodFind() # 제품 검색 매서드 실행

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


#--------------------------        
# 테이블 생성 함수
def tableCreate() :  
    try :
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        sql = """CREATE table if not exists stud (
                studID char(8),
                sname char(8),
                jumin1 char(6),
                jumin2 char(7),
                addr1 char(20),
                addr2 char(20))"""
                
        cursor.execute(sql)
        conn.commit()
        
    except Exception as e :
        print("오류 : ",e)
        conn.rollback()
        
    finally :
        conn.close()
        cursor.close()        


#--------------------------
#서비스 실행
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
            sys.exit(0)
            
        else :
            print("잘못 선택했습니다. ")
            os.system("pause")