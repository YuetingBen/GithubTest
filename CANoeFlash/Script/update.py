#!/usr/bin/python 
# -*- coding: utf-8 -*-

def GenFlashDriver():
  filename = open(r'flashDriverData.txt', 'r')
  line = filename.readline()
  
  arrayDataList = []
  while line:
    arrayList = line.split('	')
    # print(arrayList)
    for data in arrayList:
      data = str(data).strip()
      
      if('' != data):
        if(1 == len(data)):
          arrayDataList.append(r'0x0' + data)
        elif(2 == len(data)):
          arrayDataList.append(r'0x' + data)
    
    line = filename.readline()
  filename.close()
  
  targetFile = open('test.txt','w')
  
  targetFile.writelines('  const dword BlockOnedataNum =' + str(len(arrayDataList)) + ';\n')
  targetFile.writelines('  byte BlockOneDataList[BlockOnedataNum] =\n')
  targetFile.writelines('  {\n')
  for i in range(0, len(arrayDataList)):
    if(i%8 == 0 and i != 0):
      targetFile.writelines('\n    ')
    elif(i == 0):
      targetFile.writelines('    ')
      
    targetFile.writelines(arrayDataList[i])
    if(i != (len(arrayDataList) - 1)):
      targetFile.writelines(', ')
    else:
      targetFile.writelines('\n')
  targetFile.writelines('  }')
  targetFile.close()
  
if __name__ == "__main__":
  GenFlashDriver()
  raw_input('Over')