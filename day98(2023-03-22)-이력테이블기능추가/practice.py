from Filter import UserInput, FindSql, ShowTables, fmt, sqlAction

def saleMinSum() : 
    try :
        print('조회할 ',end=''); in_code = UserInput().codeInput()
        sql = f"SELECT New_unitPrice FROM product_history WHERE pCode = '{in_code}'"
        rows = sqlAction(sql) ; min_unitPrice = int(min([i for row in rows for i in row]))
        sql = f"SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y.%m.%d') as date, s.qty FROM sales AS s JOIN product AS p ON s.sCode = p.pCode WHERE p.pCode = '{in_code}'" 
        rows = sqlAction(sql) 
        print('===판매조회(코드별-세무자료용)===')
        print(f"{fmt('No',6,'l')}{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('판매등록일자',22,'l')}{fmt('판매수량',16,'l')}{fmt('총 판매가격',5,'l')}") ; print('-'*90)
        for row in rows :
            min_amt = row[4] * min_unitPrice
            print(f"{fmt(row[0],6,'l')}{fmt(row[1],10,'l')}{fmt(row[2],20,'l')}{fmt(row[3],10,'l')}{float(fmt(row[4],7,'l')):20,.2f}{float(fmt(min_amt,5,'l')):20,.2f}")
        print('-'*90)
        print(f"{fmt('판매금액합계',66,'l')}{float(fmt(min_amt*int(len(rows)),10,'l')):20,.2f}")
        
    except Exception as e :
        print('db 연동 실패 : ', e)
        
def saleMaxSum() : 
    try :
        print('조회할 ',end=''); in_code = UserInput().codeInput()
        sql = f"SELECT New_unitPrice FROM product_history WHERE pCode = '{in_code}'"
        rows = sqlAction(sql) ; min_unitPrice = int(max([i for row in rows for i in row]))
        sql = f"SELECT s.seqNo, s.sCode, p.pName, date_format(s.sDate,'%Y.%m.%d') as date, s.qty FROM sales AS s JOIN product AS p ON s.sCode = p.pCode WHERE p.pCode = '{in_code}'" 
        rows = sqlAction(sql) 
        print('===판매조회(코드별-세무자료용)===')
        print(f"{fmt('No',6,'l')}{fmt('제품코드',10,'l')}{fmt('제품명',20,'l')}{fmt('판매등록일자',22,'l')}{fmt('판매수량',16,'l')}{fmt('총 판매가격',5,'l')}") ; print('-'*90)
        for row in rows :
            min_amt = row[4] * min_unitPrice
            print(f"{fmt(row[0],6,'l')}{fmt(row[1],10,'l')}{fmt(row[2],20,'l')}{fmt(row[3],10,'l')}{float(fmt(row[4],7,'l')):20,.2f}{float(fmt(min_amt,5,'l')):20,.2f}")
        print('-'*90)
        print(f"{fmt('판매금액합계',66,'l')}{float(fmt(min_amt*int(len(rows)),10,'l')):20,.2f}")
        
    except Exception as e :
        print('db 연동 실패 : ', e)
        
saleMinSum()

saleMaxSum()