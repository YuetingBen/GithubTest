import xlrd

def main():
  xlsfile = r"C:\Users\beny\Desktop\New Microsoft Excel Worksheet.xlsx"
  book = xlrd.open_workbook(xlsfile)
  dtcSheet = book.sheet_by_name("DTC")
  
  lineMaxNums = dtcSheet.nrows
  columnMaxNums = dtcSheet.ncols
  
  maxLenElement = [0] * columnMaxNums
  dtcInfo_list = []

  for line in range(1, lineMaxNums):
    dtcInfo_dic = {}
    for col in range(1, columnMaxNums):   
      dtcInfo_dic[col] = str(dtcSheet.cell(line, col).value).strip()
      if(maxLenElement[col] < len(dtcInfo_dic[col])):
        maxLenElement[col] = len(dtcInfo_dic[col])
    dtcInfo_list.append(dtcInfo_dic)

  targetFile = open('test.txt','w')
  
  for dtc in dtcInfo_list:
    targetFile.writelines(',{')
    for (key, value) in dtc.items():
      if(len(dtc.items()) != key):
        if(len(dtc.items()) - 1 == key):
          targetFile.writelines(value)
        else:
          targetFile.writelines(value + ',')
          temp = 0
          
          while(temp + len(value) < maxLenElement[key] + 2):
            targetFile.writelines(' ')
            temp  = temp + 1
        
      else:
        targetFile.writelines('}  ')
        targetFile.writelines('/*' + value + '*/')
    targetFile.writelines('\n')

  targetFile.close()
  
  raw_input('over')

if __name__ == '__main__':
    main()
