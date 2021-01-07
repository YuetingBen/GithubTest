import xlrd
import re
import xml.dom.minidom

# XML structure
'''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<ODX MODEL-VERSION="2.2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="odx.xsd">
<!--created by CANdelaStudio::ODXExport220.dll 8.0.100 on 2018-01-30T18:48:15+08:00-->
  <?CANdelaTemplateManufacturer 0?>
  <?SpecificationOwner Vector Informatik?>
  <?CANdelaTemplateName UDS DiagnosticsOnCAN?>
  <?CANdelaTemplateVersion 1.0?>
  <?CANdelaProtocolStandard UDS?>
  <?ASAMOdxExport220.dll 8.0.100?>
  <DIAG-LAYER-CONTAINER ID="_AVAS_133">
    <SHORT-NAME>AVAS</SHORT-NAME>
    <LONG-NAME>AVAS</LONG-NAME>
    <DESC>
    <ADMIN-DATA>
    <PROTOCOLS>
    <ECU-SHARED-DATAS>
    <BASE-VARIANTS>
      <BASE-VARIANT ID="AVAS">
        <SHORT-NAME>AVAS</SHORT-NAME>
        <LONG-NAME>AVAS</LONG-NAME>
        <FUNCT-CLASSS>
        <DIAG-DATA-DICTIONARY-SPEC>
        <DIAG-COMMS>
        <REQUESTS>
        <POS-RESPONSES>
        <NEG-RESPONSES>
        <GLOBAL-NEG-RESPONSES>
        <IMPORT-REFS>
        <STATE-CHARTS>
        <COMPARAM-REFS>
        <PARENT-REFS>
      </BASE-VARIANT>
    </BASE-VARIANTS>
  </DIAG-LAYER-CONTAINER>
</ODX>
'''

class ODXGENERATE():
    def __init__(self):
        self.DTClists = []
        
        # 0-PIDNumber, 1-PIDName, 2-ReadFlag
        # 3-WriteFlag, 4-ControlFlag, 5-byteSize, 6-SignalList
        #
        # SignalList incluede:
        # 00-SignalName, 01-SignalStartbyte, 02-SignalBitSize, 
        # 03-SignalStartBit, 04-SignalUnit, 05-SignalDefaultValue, 
        # 06-SignalResolution, 07-SignalType, 08-SignalCategory        
        self.PIDlists = []
        
        # self.UDSlists: 0-ServiceID, 1-ServiceName, 2-SubServiceList, 3-FunctClass, 4-NRCs
        self.UDSlists = []
        
        # self.UDSParameterlists: 0-name, 1-value, 2-ISOtype, 3-comment
        self.UDSParameterlists = []
        
        # self.NRCslists: NRCID: NRCname
        self.NRCslists = {}
        
        # self.UDSRoutineslists: 0-RoutineID, 1-RoutineName
        self.UDSRoutineslists = []
        
        self.PIDSignallists = []
        # UDSServicelists: 0-ServiceID, 1-ServiceName, 2-SubServiceID, 3-SubServiceName, 4-SubServiceLen
        self.UDSServicelists = []
        
        self.DTCStatuslists = [\
        [{'0':'TestFailed'},
        {'1': 'TestFailedThisMonitoringCycle'}, 
        {'2': 'PendingDtc'},
        {'3': 'ConfirmedDtc'}, 
        {'4': 'TestNotCompletedSinceLastClear'},
        {'5': 'TestFailedSinceLastClear'},
        {'6':'TestNotCompletedThisMonitoringCycle'}, 
        {'7': 'WarningIndicatorRequested'}]\
        ]
        self.DTCStatuslists = ['TestFailed', 'TestFailedThisMonitoringCycle', 'PendingDtc', 'ConfirmedDtc', 'TestNotCompletedSinceLastClear', 'TestFailedSinceLastClear', 'TestNotCompletedThisMonitoringCycle', 'WarningIndicatorRequested']
        
        self.ECUName = 'ACU'
        pass
        
    def ODXG_CreateElement(self, name, doc, attributeList, txt):
        # CreateElement node
        Node = doc.createElement(name)
        
        # Set attribute
        if('' != attributeList):
            for attribute in attributeList:
                Node.setAttribute(attribute[0], attribute[1])
                
        # Write txt
        if('' != txt):
            txtNode = doc.createTextNode(txt)
            Node.appendChild(txtNode)
        
        return(Node)
	
    def ODXG_AddNode(self, parent, name, doc, attributeList, txt):
        node = self.ODXG_CreateElement(name, doc, attributeList, txt)
        parent.appendChild(node)
        return(node)
    
    def ODXG_PARTII_DTCread(self, excel):
        # -------------------------------------------------
        # Function: Get DTC list form PARTII excel DTC sheet
        # Return DTC list:
        # 0-DTCdisplayNumber, 1-DTCNumber, 2-DTCName,  3-LampFlag
        # 4-RepairAction 5-MatureCondition, 6-DematureCondition      
        # -------------------------------------------------
        RET_DTCinfos = []
        
        DTC_Sheet = excel.sheet_by_name(u'DTC')
        
        LineNums = DTC_Sheet.nrows
        for line in range(10, LineNums):
            # Creat list for DTC information, list include     
            DTCinfo = []
            
            if('' != (DTC_Sheet.cell(line,1).value.strip())):
                DTCinfo.append(DTC_Sheet.cell(line, 1).value.strip().replace(' ','')) # 0-DTCdisplayNumber, and remove space  
                DTCinfo.append(DTC_Sheet.cell(line, 2).value.strip()) # 1-DTCNumber
                DTCName = DTC_Sheet.cell(line, 4).value.strip()
                DTCName = DTCName.replace(' ','_')
                DTCName = DTCName.replace('\n','')
                DTCName = DTCName.replace('(','_')
                DTCName = DTCName.replace(')','_')
                DTCName = DTCName.replace('/','_')
                DTCinfo.append(DTCName) # 2-DTCName
                DTCinfo.append(DTC_Sheet.cell(line, 5).value.strip()) # 3-LampFlag
                DTCinfo.append(DTC_Sheet.cell(line, 6).value.strip()) # 4-RepairAction
                DTCinfo.append(DTC_Sheet.cell(line, 10).value.strip()) # 5-MatureCondition
                DTCinfo.append(DTC_Sheet.cell(line, 11).value.strip()) # 6-DematureCondition
                
                # 3-LampFlag
                if('N' == DTCinfo[3]):
                    pass
                else:
                    DTCinfo[3] = 'Y'
                    
                RET_DTCinfos.append(DTCinfo)
                
        return(RET_DTCinfos)

    def ODXG_PARTII_PIDread(self, excel):
        # -------------------------------------------------
        # Function: Get PID list form PARTII excel PID sheet
        # Return PID list:
        # 0-PIDNumber, 1-PIDName, 2-ReadFlag
        # 3-WriteFlag, 4-ControlFlag, 5-byteSize, 6-SignalList
        #
        # SignalList incluede:
        # 00-SignalName, 01-SignalStartbyte, 02-SignalBitSize, 
        # 03-SignalStartBit, 04-SignalUnit, 05-SignalDefaultValue, 
        # 06-SignalResolution, 07-SignalType, 08-SignalCategory, 09-PIDName
        # -------------------------------------------------
        RET_PIDinfos = []
        
        PID_Sheet = excel.sheet_by_name(u'PID')
        
        LineNums = PID_Sheet.nrows
        for line in range(2, LineNums): 
            # Creat list for DTC information, list include     
            PIDinfo = []
            pidNumber = 0
            pidName = ''
            pidReadFlag = 0
            pidWriteFlag = 0
            pidConFlag = 0
            pidByteSize = 0
            
            if('' != PID_Sheet.cell(line, 0).value.strip()):
                pidNumber = PID_Sheet.cell(line, 0).value.strip() # PID number
                pidName = PID_Sheet.cell(line, 5).value.strip() # PID name
                pidName = pidName.replace(' ', '_')
                pidName = pidName.replace('\n','')
                pidName = pidName.replace('(','_')
                pidName = pidName.replace(')','_')
                pidName = pidName.replace('/','_')
                pidName = pidName.replace('\'','')
                pidName = pidName.replace('-','')
                
                # Read always can be read for every PID
                # Read/Write/Con Flag = 0 represent Read/Write/Con disable
                # Read/Write/Con Flag = 1 represent Read/Write/Con without security level
                # Read/Write/Con Flag = 2 represent Read/Write/Con with OEM security level
                # Read/Write/Con Flag = 3 represent Read/Write/Con with supplier security level
                pidReadFlag = 1
                if('X' != (PID_Sheet.cell(line, 2).value.strip())):
                    pidReadFlag = 2
                if('' != (PID_Sheet.cell(line, 2).value.strip())):
                    pidWriteFlag = 2
                if('' != (PID_Sheet.cell(line, 3).value.strip())):
                    pidConFlag = 2

                pidByteSize = int(PID_Sheet.cell(line, 6).value) # PID byte size
                
                signalLists = []
                childSignalLine = 0
                
                while(('' != (PID_Sheet.cell(line + childSignalLine, 9).value.strip())) and ((line + childSignalLine) < LineNums - 1)):
                    # Signal information include:
                    # 00-SignalName, 01-SignalStartbyte, 02-SignalBitSize, 03-SignalStartBit, 04-SignalUnit, 05-SignalDefaultValue, 06-SignalResolution, 07-SignalType, 08-SignalCategory
                    signalInfo = []
                    signalName = PID_Sheet.cell(line + childSignalLine, 9).value.strip()
                    signalName = signalName.replace(' ', '_')
                    signalName = signalName.replace('\n','')
                    signalName = signalName.replace('(','_')
                    signalName = signalName.replace(')','_')
                    signalName = signalName.replace('/','_')
                    signalName = signalName.replace('\'','')
                    signalName = signalName.replace('-','')
                    
                    SignalCategory = PID_Sheet.cell(line + childSignalLine, 17).value.strip()

                    if('' == (str(PID_Sheet.cell(line + childSignalLine, 10).value).strip())):
                        SignalStartbyte = 0
                        SignalBitSize = int(pidByteSize * 8)
                        SignalStartBit = 0
                        
                    else:               
                        SignalStartbyte = int(PID_Sheet.cell(line + childSignalLine, 10).value)
                        SignalBitSize = int(PID_Sheet.cell(line + childSignalLine, 12).value)
                        SignalStartBit =  int(SignalStartbyte * 8 +  PID_Sheet.cell(line + childSignalLine, 11).value)
                    
                    SignalUnit = PID_Sheet.cell(line + childSignalLine, 13).value.strip()
                    SignalDefaultValue = str(PID_Sheet.cell(line + childSignalLine, 14).value).strip()
                    SignalResolution = PID_Sheet.cell(line + childSignalLine, 15).value
                    SignalType = str(PID_Sheet.cell(line + childSignalLine, 16).value).strip()
                    
                    childSignalLine = childSignalLine + 1
                    signalLists.append([signalName, SignalStartbyte, SignalBitSize, SignalStartBit, SignalUnit, SignalDefaultValue, SignalResolution, SignalType, SignalCategory, pidName])
                    
                    
                else:
                    # Signal list name is Null
                    if('' != (PID_Sheet.cell(line + childSignalLine, 5).value.strip())):
                        signalName = pidName
                        SignalStartbyte = 0
                        SignalBitSize = int(pidByteSize * 8)
                        SignalStartBit = 0

                        SignalUnit = PID_Sheet.cell(line + childSignalLine, 13).value.strip()
                        SignalDefaultValue = str(PID_Sheet.cell(line + childSignalLine, 14).value).strip()
                        SignalResolution = PID_Sheet.cell(line + childSignalLine, 15).value
                        SignalType = str(PID_Sheet.cell(line + childSignalLine, 16).value).strip()
                        
                        signalLists.append([signalName, SignalStartbyte, SignalBitSize, SignalStartBit, SignalUnit, SignalDefaultValue, SignalResolution, SignalType, SignalCategory, pidName])
                
                PIDinfo.append(pidNumber)
                PIDinfo.append(pidName)
                PIDinfo.append(pidReadFlag)
                PIDinfo.append(pidWriteFlag)
                PIDinfo.append(pidConFlag)
                PIDinfo.append(pidByteSize)
                PIDinfo.append(signalLists)
                
                RET_PIDinfos.append(PIDinfo)
        return(RET_PIDinfos)
    
    def ODXG_PARTII_UDSread(self, excel):
        # -------------------------------------------------
        # Function: Get UDS list form PARTII excel UDS sheet
        # Return UDS list:  
        # 0-ServiceID, 1-ServiceName, 2-SubServiceList, 3-FunctClass, 4-NRCs
        #
        # SubServiceList include
        # 201-SubServiceID, 202-SubServiceName
        # -------------------------------------------------        
        RET_UDSinfos = []
        
        UDS_Sheet = excel.sheet_by_name(u'UDS')
        
        LineNums = UDS_Sheet.nrows
        for line in range(1, LineNums):
            ServiceID = ''
            ServiceName = ''
            SubServiceList = []
            FunctClass = ''

            if('' != str(UDS_Sheet.cell(line, 0).value).strip()):
                ServiceID = str(UDS_Sheet.cell(line, 0).value).strip() # 0-ServiceID
                ServiceName = str(UDS_Sheet.cell(line, 1).value).strip() # 1-ServiceName
                ServiceName = ServiceName.replace(' ', '_')
                SubServiceList = []
                FunctClass = str(UDS_Sheet.cell(line, 4).value).strip() # 3-FunctClass
                NRCs = str(UDS_Sheet.cell(line, 5).value).strip() # 4-NRCs
                NRCs = NRCs.split(',')
                
                SubServiceID = str(UDS_Sheet.cell(line, 2).value).strip() # 201-SubServiceID
                SubServiceName = str(UDS_Sheet.cell(line, 3).value).strip() # 202-SubServiceName
                SubServiceName = SubServiceName.replace(' ', '_')
                if('NA' != SubServiceID):
                    SubServiceList.append([SubServiceID, SubServiceName])
                    
                    # Add multi sub services
                    childSignalLine = 1
                    while(('' == (UDS_Sheet.cell(line + childSignalLine, 0).value.strip())) and ((line + childSignalLine) < LineNums - 1)):
                        SubServiceID = str(UDS_Sheet.cell(line + childSignalLine, 2).value).strip() # 201-SubServiceID
                        SubServiceName = str(UDS_Sheet.cell(line + childSignalLine, 3).value).strip() # 202-SubServiceName 
                        SubServiceName = SubServiceName.replace(' ', '_')
                        SubServiceList.append([SubServiceID, SubServiceName])
                        childSignalLine = childSignalLine + 1
                    
                RET_UDSinfos.append([ServiceID, ServiceName, SubServiceList, FunctClass, NRCs])
        return(RET_UDSinfos)
    
    def ODXG_PARTII_UDSRoutineread(self, excel):
        # -------------------------------------------------
        # Function: Get UDSRoutine list form PARTII excel UDSRoutine sheet
        # Return UDSRoutine list: 
        # 0-RoutineID, 1-RoutineName
        RET_UDSRoutineinfos = []
        
        UDS_Routine_Sheet = excel.sheet_by_name(u'UDS_Routine')
        LineNums = UDS_Routine_Sheet.nrows
        for line in range(1, LineNums):
            RoutineID = str(UDS_Routine_Sheet.cell(line, 4).value).strip() # 0-ServiceID
            RoutineName = str(UDS_Routine_Sheet.cell(line, 3).value).strip() # 1-ServiceName
            RoutineName = RoutineName.replace(' ', '_')
            RET_UDSRoutineinfos.append([RoutineID,RoutineName])
            
        return(RET_UDSRoutineinfos)
        
    def ODXG_PARTII_NRCSread(self, excel):
        # -------------------------------------------------
        # Function: Get NRC list form PARTII excel NRCs sheet
        # Return UDS list:  
        # 0-ServiceID, 0-NRCID, 1-NRCname
        # -------------------------------------------------   
        NRC_Sheet = excel.sheet_by_name(u'NRCs')
        LineNums = NRC_Sheet.nrows
        
        RET_NRClist = {}
        for line in range(1, LineNums):
            NRCID = str(NRC_Sheet.cell(line, 0).value).strip()
            NRCname = str(NRC_Sheet.cell(line, 1).value).strip()
            NRCname = NRCname.split('\n')[0].strip()
            RET_NRClist[NRCID] = NRCname
        
        return(RET_NRClist)
    
    def ODXG_PARTII_UDSParameter(self, excel):
        # -------------------------------------------------
        # Function: Get UDS Parameter form PARTII excel UDS_Parameter sheet
        # Return parameterData list:  
        # 0-name, 1-value, 2-ISOtype, 3-comment
        # -------------------------------------------------  
        UDSParameterSheet = excel.sheet_by_name(u'UDS_Parameter')
        LineNums = UDSParameterSheet.nrows
 
        RET_parameterData = []
        for line in range(1, LineNums):
            name = str(UDSParameterSheet.cell(line, 0).value).strip()
            try:
                value = str(int(UDSParameterSheet.cell(line, 2).value)).strip()
            except:
                value = str(UDSParameterSheet.cell(line, 2).value).strip()
            ISOtype = str(UDSParameterSheet.cell(line, 3).value).strip()
            comment = UDSParameterSheet.cell(line, 4).value.strip()
            if('' != name):
                RET_parameterData.append([name, value, ISOtype, comment])
        
        return(RET_parameterData)
    
    def ODXG_UDSServiceGet(self, UDSlist):
        # Get UDS service list form UDS list
        # RET_UDSService
        # 0-ServiceID, 1-ServiceName, 2-SubServiceID, 3-SubServiceName, 4-SubServiceLen, 5-FunctionClass, 6-NRCs
        RET_UDSService = []
        # UDSlist
        # 0-ServiceID, 1-ServiceName, 2-SubServiceList, 3-FunctClass, 4-NRCs
        # SubServiceList include
        # 201-SubServiceID, 202-SubServiceName
        # -------------------------------------------------    
        for uds in UDSlist:
            ServiceID = uds[0]
            ServiceName = uds[1]
            SubServiceList = uds[2]
            SubServiceID = ''
            SubServiceName = ''
            SubServiceLen = ''
            FunctionClass = uds[3]
            NRCs = uds[4]

            if([] != SubServiceList):
                for SubService in SubServiceList:
                    SubServiceID = SubService[0]
                    SubServiceName = SubService[1]
                    SubServiceLen = str((len(SubServiceID) - 3) * 8)
                    RET_UDSService.append([ServiceID, ServiceName, SubServiceID, SubServiceName, SubServiceLen, FunctionClass, NRCs])
            else:
                RET_UDSService.append([ServiceID, ServiceName, SubServiceID, SubServiceName, SubServiceLen, FunctionClass, NRCs])
    
        return(RET_UDSService)
    
    def ODXG_PIDSignalGet(self, PIDlist):
        # -------------------------------------------------
        # Function: Get Signal list form PID list
        # SignalList incluede:
        # 00-SignalName, 01-SignalStartbyte, 02-SignalBitSize, 
        # 03-SignalStartBit, 04-SignalUnit, 05-SignalDefaultValue, 
        # 06-SignalResolution, 07-SignalType, 08-SignalCategory, 09-PIDName
        # -------------------------------------------------   
        RET_SignalList = []
        
        # PIDlist 6-SignalList
        for pidlist in PIDlist:
            if([] != pidlist[6]):
                for signal in pidlist[6]:
                    RET_SignalList.append(signal)
        
        return(RET_SignalList)  
        
    def ODXG_ReadPartII(self):
        filename = 'NEVS_ODX_PartII.xlsx'
        Excel_NEVS_PARTII = xlrd.open_workbook(filename)
        
        self.DTClists = self.ODXG_PARTII_DTCread(Excel_NEVS_PARTII) # Read DTC list
        self.PIDlists = self.ODXG_PARTII_PIDread(Excel_NEVS_PARTII) # Read PID list
        self.UDSlists = self.ODXG_PARTII_UDSread(Excel_NEVS_PARTII) # Read UDS list
        self.UDSParameterlists = self.ODXG_PARTII_UDSParameter(Excel_NEVS_PARTII) # Read UDS Parameter
        self.UDSRoutineslists = self.ODXG_PARTII_UDSRoutineread(Excel_NEVS_PARTII) # Read UDS routine
        self.NRCslists = self.ODXG_PARTII_NRCSread(Excel_NEVS_PARTII) # Read NRCs Parameter
        
        self.PIDSignallists = self.ODXG_PIDSignalGet(self.PIDlists) # Get Signal list form PID list
        self.UDSServicelists = self.ODXG_UDSServiceGet(self.UDSlists) # Get UDS service list form UDS list

    def ODXG_DESC(self, doc, parent):
        DESC_Node = self.ODXG_AddNode(parent, "DESC", doc, '', '')
        self.ODXG_AddNode(DESC_Node, "p", doc, '', 'This CANdela Document Template excample provides the user with the possibility to test the features of CANdelaStudio. It does not claim to be complete.')
        p_Node = self.ODXG_AddNode(DESC_Node, "p", doc, '', '')
        self.ODXG_AddNode(p_Node, "br", doc, '', '')
        p_Txt = doc.createTextNode('This CANdela Document Template is based on the standards:')
        p_Node.appendChild(p_Txt)
        p_Node = self.ODXG_AddNode(DESC_Node, "p", doc, '', '')
        self.ODXG_AddNode(p_Node, "br", doc, '', '')
        ul_Node = self.ODXG_AddNode(DESC_Node, "ul", doc, '', '')
        self.ODXG_AddNode(ul_Node, "li", doc, '', 'Unified Diagnostic Services (ISO 14229-1:2006)')
        self.ODXG_AddNode(ul_Node, "li", doc, '', 'Diagnostics on CAN (ISO 15765-3)')    
    
    def ODXG_ADMIN_DATA(self, doc, parent):
        ADMIN_DATA_Node = self.ODXG_AddNode(parent, "ADMIN-DATA", doc, '', '')
    
    def ODXG_COMPANY_DATAS(self, doc, parent):
        COMPANY_DATAS_Node = self.ODXG_AddNode(parent, "COMPANY-DATAS", doc, '', '')
    
    def ODXG_PROTOCOLS(self, doc, parent):
        PROTOCOLS_Node = self.ODXG_AddNode(parent, "PROTOCOLS", doc, '', '')
        PROTOCOL_Node = self.ODXG_AddNode(PROTOCOLS_Node, "PROTOCOL", doc, [('ID', '__PROTOCOL_ISO_15765_3_on_ISO_15765_2')], '')
        self.ODXG_AddNode(PROTOCOL_Node, "SHORT-NAME", doc, '', 'DC')
        self.ODXG_AddNode(PROTOCOL_Node, "LONG-NAME", doc, '', 'Diagnose CAN')
        attribute = [('ID-REF', "ISO_15765_3_on_ISO_15765_2"), ('DOCREF', "ISO_15765_3_on_ISO_15765_2"), ('DOCTYPE',"COMPARAM-SPEC")]
        self.ODXG_AddNode(PROTOCOL_Node, "COMPARAM-SPEC-REF", doc, attribute, '')
        self.ODXG_AddNode(PROTOCOL_Node, "PROT-STACK-SNREF", doc, [('SHORT-NAME', "ISO_15765_3_on_ISO_15765_2_on_ISO_11898_2_DWCAN")], '')
    
    def odx_ECU_SHARED_DATAS_DTC(self, doc, parent):
        for dtc in self.DTClists:
            # DTC list
            # 0-DTCdisplayNumber, 1-DTCNumber, 2-DTCName,  3-LampFlag
            # 4-RepairAction 5-MatureCondition, 6-DematureCondition 
            
            # DTC ID = '__DTC_' + DTCName
            DTC_Node = self.ODXG_CreateElement("DTC", doc, [('ID', ('__DTC_' + dtc[2]))], '')
            self.ODXG_AddNode(DTC_Node, "SHORT-NAME", doc, '', ('DTC' + str(dtc[1])[2:])) # str(dtc[1]) = 0x123456  str(dtc[1])[2:] = 123456
            self.ODXG_AddNode(DTC_Node, "TROUBLE-CODE", doc, '', str(int(dtc[1], 16))) # Change DTC number to Dec from hex
            self.ODXG_AddNode(DTC_Node, "DISPLAY-TROUBLE-CODE", doc, '', dtc[0]) # 0-DTCdisplayNumber
            self.ODXG_AddNode(DTC_Node, "TEXT", doc, '', dtc[2])
            
            SDGS_Node = self.ODXG_CreateElement("SDGS", doc, '' , '')
            DTC_Node.appendChild(SDGS_Node)
            
            # Set DTC MatureCondition ---- SetCondition
            SDG_Node = self.ODXG_CreateElement("SDG", doc, '' , '')
            SDG_CAPTION = self.ODXG_CreateElement("SDG-CAPTION", doc, [('ID', ('__DTCSDG_CAPTION_SET_CONT_' + dtc[2]))], '')
            self.ODXG_AddNode(SDG_CAPTION, "SHORT-NAME", doc, '', 'SetCondition')
            self.ODXG_AddNode(SDG_CAPTION, "LONG-NAME", doc, '', 'Set Condition')
            SDG_Node.appendChild(SDG_CAPTION)
            self.ODXG_AddNode(SDG_Node, "SD", doc, '', dtc[5]) #5-MatureCondition
            SDGS_Node.appendChild(SDG_Node)
            
            # Set DTC DematureCondition ---- ResetCondition
            SDG_Node = self.ODXG_CreateElement("SDG", doc, '' , '')
            SDG_CAPTION = self.ODXG_CreateElement("SDG-CAPTION", doc, [('ID', ('__DTCSDG_CAPTION_RET_CONT_' + dtc[2]))], '')
            self.ODXG_AddNode(SDG_CAPTION, "SHORT-NAME", doc, '', 'ResetCondition')
            self.ODXG_AddNode(SDG_CAPTION, "LONG-NAME", doc, '', 'Reset Condition')
            SDG_Node.appendChild(SDG_CAPTION)
            self.ODXG_AddNode(SDG_Node, "SD", doc, '', dtc[6]) #6-DematureCondition
            SDGS_Node.appendChild(SDG_Node)

            # Set DTC RepairAction ---- CorrectiveAction
            SDG_Node = self.ODXG_CreateElement("SDG", doc, '' , '')
            SDG_CAPTION = self.ODXG_CreateElement("SDG-CAPTION", doc, [('ID', ('__DTCSDG_CAPTION_COR_ACT_' + dtc[2]))], '')
            self.ODXG_AddNode(SDG_CAPTION, "SHORT-NAME", doc, '', 'CorrectiveAction')
            self.ODXG_AddNode(SDG_CAPTION, "LONG-NAME", doc, '', 'Corrective Action')
            SDG_Node.appendChild(SDG_CAPTION)
            self.ODXG_AddNode(SDG_Node, "SD", doc, '', dtc[4]) #4-RepairAction
            SDGS_Node.appendChild(SDG_Node)

            # Set SpecialInstruction - None
            SDG_Node = self.ODXG_CreateElement("SDG", doc, '' , '')
            SDG_CAPTION = self.ODXG_CreateElement("SDG-CAPTION", doc, [('ID', ('__DTCSDG_CAPTION_SPEC_INSTR_' + dtc[2]))], '')
            self.ODXG_AddNode(SDG_CAPTION, "SHORT-NAME", doc, '', 'SpecialInstruction')
            self.ODXG_AddNode(SDG_CAPTION, "LONG-NAME", doc, '', 'Special Instruction')
            SDG_Node.appendChild(SDG_CAPTION)
            self.ODXG_AddNode(SDG_Node, "SD", doc, '', 'None') #4-RepairAction
            SDGS_Node.appendChild(SDG_Node)
            
            parent.appendChild(DTC_Node)
        
    def odx_ECU_SHARED_DATAS(self, doc, parent):
        ECU_SHARED_DATA_Node = self.ODXG_CreateElement("ECU-SHARED-DATA", doc, [('ID', '__ECU_SHARED_DATA_Node')], '')
        DIAG_DATA_DICTIONARY_SPEC_Node = self.ODXG_CreateElement("DIAG-DATA-DICTIONARY-SPEC", doc, '', '')
        
        DTC_DOPS_Node = self.ODXG_CreateElement("DTC-DOPS", doc, '', '')
        self.ODXG_AddNode(ECU_SHARED_DATA_Node, "SHORT-NAME", doc, '', 'faultMemory')
        
        DTC_DOP_Node = self.ODXG_CreateElement("DTC-DOP", doc, [('ID', '__DTC_DOP_Node')], '')       
        self.ODXG_AddNode(DTC_DOP_Node, "SHORT-NAME", doc, '', 'OBDRecordDataType')
        self.ODXG_AddNode(DTC_DOP_Node, "LONG-NAME", doc, '', 'OBDRecordDataType')
        
        attributeList = [('BASE-TYPE-ENCODING', 'NONE'), ('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")]
        DIAG_CODED_TYPE_Node = self.ODXG_CreateElement("DIAG-CODED-TYPE", doc, attributeList, '')
        self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '24')
        
        PHYSICAL_TYPE_Node = self.ODXG_CreateElement("PHYSICAL-TYPE", doc, [("BASE-DATA-TYPE", "A_UINT32"), ("DISPLAY-RADIX", "HEX")], '')
        COMPU_METHOD_Node = self.ODXG_CreateElement("COMPU-METHOD", doc, '', '')
        self.ODXG_AddNode(COMPU_METHOD_Node, "CATEGORY", doc, '', 'IDENTICAL')
        
        DTCS_Node = self.ODXG_CreateElement("DTCS", doc, '', '')
        
        self.odx_ECU_SHARED_DATAS_DTC(doc, DTCS_Node)
        
        #DTC_Node = self.ODXG_CreateElement("DTC", doc, '', '')
        
        parent.appendChild(ECU_SHARED_DATA_Node)
        
        ECU_SHARED_DATA_Node.appendChild(DIAG_DATA_DICTIONARY_SPEC_Node)
        DIAG_DATA_DICTIONARY_SPEC_Node.appendChild(DTC_DOPS_Node)
        DTC_DOPS_Node.appendChild(DTC_DOP_Node)
        
        DTC_DOP_Node.appendChild(DIAG_CODED_TYPE_Node)
        DTC_DOP_Node.appendChild(PHYSICAL_TYPE_Node)
        DTC_DOP_Node.appendChild(COMPU_METHOD_Node)
        DTC_DOP_Node.appendChild(DTCS_Node)
    
    def odx_BASE_VARIANT_FUNCT_CLASSS(self, doc, parent):
        # FUNCT-CLASS attribute: '__FUNCTCLASS' + functionClass
        functionClassList = []
        
        for uds in self.UDSlists:
            functionClassList.append(uds[3]) # Add function classes for every service
        
        functionClassList = list(set(functionClassList)) # Remove same function class    
        
        FUNCT_CLASSS_Node = self.ODXG_CreateElement("FUNCT-CLASSS", doc, '', '')
        parent.appendChild(FUNCT_CLASSS_Node)
        
        for functionClass in functionClassList:
            FUNCT_CLASS_Node = self.ODXG_CreateElement("FUNCT-CLASS", doc, [('ID', ('__FUNCTCLASS' + functionClass))], '')
            self.ODXG_AddNode(FUNCT_CLASS_Node, 'SHORT-NAME', doc, '', functionClass)
            self.ODXG_AddNode(FUNCT_CLASS_Node, 'LONG-NAME', doc, '', functionClass)
            FUNCT_CLASSS_Node.appendChild(FUNCT_CLASS_Node)

    def odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_DTC_DOPS(self, doc, parent):
        DTC_DOPS_Node = self.ODXG_CreateElement("DTC-DOPS", doc, '', '')
    
        DTC_DOP_Node = self.ODXG_CreateElement("DTC-DOP", doc, [('ID', '__BASE_VARIANT_DTC_DOP_Node')], '')
        DTC_DOPS_Node.appendChild(DTC_DOP_Node)
        
        self.ODXG_AddNode(DTC_DOP_Node, 'SHORT-NAME', doc, '', "RecordDataType")
        self.ODXG_AddNode(DTC_DOP_Node, 'LONG-NAME', doc, '', "RecordDataType")
        
        attributeList = [('BASE-TYPE-ENCODING',"NONE"), ('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type',"STANDARD-LENGTH-TYPE")]
        DIAG_CODED_TYPE_Node = self.ODXG_CreateElement("DIAG-CODED-TYPE", doc, attributeList, '')
        DTC_DOP_Node.appendChild(DIAG_CODED_TYPE_Node)
        self.ODXG_AddNode(DIAG_CODED_TYPE_Node, 'BIT-LENGTH', doc, '', "24")
        
        self.ODXG_AddNode(DTC_DOP_Node, "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('DISPLAY-RADIX', "HEX")], '')
        
        COMPU_METHOD_Node = self.ODXG_AddNode(DTC_DOP_Node, "COMPU-METHOD", doc, '', '')
        self.ODXG_AddNode(COMPU_METHOD_Node, 'CATEGORY', doc, '', "IDENTICAL")
        
        DTCS_Node = self.ODXG_CreateElement("DTCS", doc, '', '')
        DTC_DOP_Node.appendChild(DTCS_Node)
        
        for dtc in self.DTClists:
            # ID = '__DTC_' + DTCName(2-DTCName)
            self.ODXG_AddNode(DTCS_Node, 'DTC-REF', doc, [('ID-REF', ('__DTC_' + dtc[2]))], '') # 2-DTCName
        
        parent.appendChild(DTC_DOPS_Node)
    
    def odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_ENV_DATA_DESCS(self, doc, parent):
        '''
        ENV_DATA_DESCS_Node = self.ODXG_AddNode(parent, "ENV-DATA-DESCS", doc, '' , '')
        
        ENV_DATA_DESC_Node = self.ODXG_AddNode(ENV_DATA_DESCS_Node, "ENV-DATA-DESC", doc, [('ID', '_ENV_DATA_DESC_SnapshotRecord')], '')
        
        self.ODXG_AddNode(ENV_DATA_DESC_Node, "SHORT-NAME", doc, '', 'SnapshotRecord')
        self.ODXG_AddNode(ENV_DATA_DESC_Node, "LONG-NAME", doc, '', 'SnapshotRecord')

        # self.ODXG_AddNode(ENV_DATA_DESC_Node, "PARAM-SNREF", doc, [('SHORT-NAME', "DTC")], '')
        ENV_DATAS_Node = self.ODXG_AddNode(ENV_DATA_DESC_Node, "ENV-DATAS", doc, '', '')
        ENV_DATA_Node = self.ODXG_AddNode(ENV_DATAS_Node, "ENV-DATA", doc, [('ID', '_ENV_DATA_SnapshotRecord')], '')
        self.ODXG_AddNode(ENV_DATA_Node, "SHORT-NAME", doc, '', 'ENVDATA_ALLDTCS')
        
        PARAMS_Node = self.ODXG_AddNode(ENV_DATA_Node, "PARAMS", doc, '', '')
        
        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC',"DATA"),('xsi:type', "VALUE")], '')
        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SnapshotRecorddataIdentifier')
        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SnapshotRecorddataIdentifier')
        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', ('__DATA_OBJECT_PROP_DtcSnapshotRecord_dataIdentifier'))], '')
        
        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC',"DATA"),('xsi:type', "VALUE")], '')
        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SnapshotRecordsnapshotData')
        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SnapshotRecordsnapshotData')
        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', ('__DATA_OBJECT_PROP_DtcSnapshotRecord_snapshotData'))], '')
        
        self.ODXG_AddNode(ENV_DATA_Node, "ALL-VALUE", doc, '', '')        
        '''
        
    def odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_DATA_OBJECT_PROPS(self, doc, parent):
        # Add DATA-OBJECT-PROPS Node
        DATA_OBJECT_PROPS_Node = self.ODXG_AddNode(parent, "DATA-OBJECT-PROPS", doc, '', '')
        
        DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROP' + 'EnableDisable')], '')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', 'EnableDisable')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', 'EnableDisable')
        COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
        self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', 'TEXTTABLE')
        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "DIAG-CODED-TYPE", doc, [('BASE-TYPE-ENCODING', "NONE"),('BASE-DATA-TYPE', 'A_UINT32'), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
        self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', '8')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UNICODE2STRING")], '')
        COMPU_INTERNAL_TO_PHYS_Node = self.ODXG_AddNode(COMPU_METHOD_Node,  "COMPU-INTERNAL-TO-PHYS", doc, '', '')
        COMPU_SCALES_Node = self.ODXG_AddNode(COMPU_INTERNAL_TO_PHYS_Node,  "COMPU-SCALES", doc, '', '')
        COMPU_SCALE_Node = self.ODXG_AddNode(COMPU_SCALES_Node,  "COMPU-SCALE", doc, '', '')
        self.ODXG_AddNode(COMPU_SCALE_Node, "LOWER-LIMIT", doc, '', '0')
        self.ODXG_AddNode(COMPU_SCALE_Node, "UPPER-LIMIT", doc, '', '0')
        COMPU_CONST = self.ODXG_AddNode(COMPU_SCALE_Node, "COMPU-CONST", doc, '', '')
        self.ODXG_AddNode(COMPU_CONST, "VT", doc, '', 'Disable')
        COMPU_SCALE_Node = self.ODXG_AddNode(COMPU_SCALES_Node,  "COMPU-SCALE", doc, '', '')
        self.ODXG_AddNode(COMPU_SCALE_Node, "LOWER-LIMIT", doc, '', '1')
        self.ODXG_AddNode(COMPU_SCALE_Node, "UPPER-LIMIT", doc, '', '1')
        COMPU_CONST = self.ODXG_AddNode(COMPU_SCALE_Node, "COMPU-CONST", doc, '', '')
        self.ODXG_AddNode(COMPU_CONST, "VT", doc, '', 'Enable')   
        
            
        DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROP' + 'RoutineStatusRecord')], '')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', 'RoutineStatusRecord')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', 'RoutineStatusRecord')
        COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
        self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', 'IDENTICAL')
        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "DIAG-CODED-TYPE", doc, [('BASE-TYPE-ENCODING', "NONE"),('BASE-DATA-TYPE', 'A_UINT32'), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
        self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', '8')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UNICODE2STRING")], '')
            
        # Service 27
        DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROP' + 'SeedKey')], '')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', 'SeedKey')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', 'SeedKey')
        COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
        self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', 'IDENTICAL')
        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "DIAG-CODED-TYPE", doc, [('BASE-TYPE-ENCODING', "NONE"),('BASE-DATA-TYPE', 'A_UINT32'), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
        self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', '16')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"),('DISPLAY-RADIX',"HEX")], '')        
        
        # Service 19
        DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROPSnapshot')], '')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', 'DtcSnapshotRecordNumber')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', 'DtcSnapshotRecordNumber')
        COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
        self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', 'IDENTICAL')
        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "DIAG-CODED-TYPE", doc, [('BASE-TYPE-ENCODING', "NONE"),('BASE-DATA-TYPE', 'A_UINT32'), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
        self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', '8')   
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UNICODE2STRING")], '')
        
        # DtcSnapshotRecordNumber
        DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROP_DtcSnapshotRecordNumber')], '')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', 'DtcSnapshotRecordNumber')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', 'DtcSnapshotRecordNumber')
        COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
        self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', 'IDENTICAL')
        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "DIAG-CODED-TYPE", doc, [('BASE-TYPE-ENCODING', "NONE"),('BASE-DATA-TYPE', 'A_UINT32'), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
        self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', '8')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UNICODE2STRING")], '') 
        # DtcSnapshotRecordNumberOfIdentifiers
        DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROP_DtcSnapshotRecordNumberOfIdentifiers')], '')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', 'DtcSnapshotRecordNumberOfIdentifiers')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', 'DtcSnapshotRecordNumberOfIdentifiers')
        COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
        self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', 'IDENTICAL')
        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "DIAG-CODED-TYPE", doc, [('BASE-TYPE-ENCODING', "NONE"),('BASE-DATA-TYPE', 'A_UINT32'), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
        self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', '8')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UNICODE2STRING")], '') 
        # DtcSnapshotRecord_Data
        DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROP_DtcSnapshotRecord_dataIdentifier')], '')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', 'DtcSnapshotRecorddataIdentifier')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', 'DtcSnapshotRecorddataIdentifier')
        COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
        self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', 'IDENTICAL')
        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "DIAG-CODED-TYPE", doc, [('BASE-TYPE-ENCODING', "NONE"),('BASE-DATA-TYPE', 'A_UINT32'), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
        self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', '32')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UNICODE2STRING")], '')        
        
        # ExtendedDataRecordNumber
        DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROP_ExtendedDataRecordNumber')], '')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', 'ExtendedDataRecordNumber')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', 'ExtendedDataRecordNumber')
        COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
        self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', 'TEXTTABLE')
        COMPU_INTERNAL_TO_PHYS_Node = self.ODXG_AddNode(COMPU_METHOD_Node,  "COMPU-INTERNAL-TO-PHYS", doc, '', '')
        COMPU_SCALES_Node = self.ODXG_AddNode(COMPU_INTERNAL_TO_PHYS_Node,  "COMPU-SCALES", doc, '', '')
        COMPU_SCALE_Node = self.ODXG_AddNode(COMPU_SCALES_Node,  "COMPU-SCALE", doc, '', '')
        self.ODXG_AddNode(COMPU_SCALE_Node, "LOWER-LIMIT", doc, '', '1')
        self.ODXG_AddNode(COMPU_SCALE_Node, "UPPER-LIMIT", doc, '', '1')
        COMPU_CONST = self.ODXG_AddNode(COMPU_SCALE_Node, "COMPU-CONST", doc, '', '')
        self.ODXG_AddNode(COMPU_CONST, "VT", doc, '', 'Occurrence Counter')

        COMPU_SCALE_Node = self.ODXG_AddNode(COMPU_SCALES_Node,  "COMPU-SCALE", doc, '', '')
        self.ODXG_AddNode(COMPU_SCALE_Node, "LOWER-LIMIT", doc, '', '2')
        self.ODXG_AddNode(COMPU_SCALE_Node, "UPPER-LIMIT", doc, '', '2')
        COMPU_CONST = self.ODXG_AddNode(COMPU_SCALE_Node, "COMPU-CONST", doc, '', '')
        self.ODXG_AddNode(COMPU_CONST, "VT", doc, '', 'Healing Counter')
        
        COMPU_SCALE_Node = self.ODXG_AddNode(COMPU_SCALES_Node,  "COMPU-SCALE", doc, '', '')
        self.ODXG_AddNode(COMPU_SCALE_Node, "LOWER-LIMIT", doc, '', '3')
        self.ODXG_AddNode(COMPU_SCALE_Node, "UPPER-LIMIT", doc, '', '3')
        COMPU_CONST = self.ODXG_AddNode(COMPU_SCALE_Node, "COMPU-CONST", doc, '', '')
        self.ODXG_AddNode(COMPU_CONST, "VT", doc, '', 'Condition')
        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "DIAG-CODED-TYPE", doc, [('BASE-TYPE-ENCODING', "NONE"),('BASE-DATA-TYPE', 'A_UINT32'), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
        self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', '8')   
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UNICODE2STRING")], '') 
        
        DTCLocalLables = [{'0x800000': 'Body group'}, {'0xC00000': 'Network communication group'}, {'0xFFFFFF': 'All groups'}]
        DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROP' + 'LocalTable')], '')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', 'LocalTable')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', 'LocalTable')
        COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
        self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', 'TEXTTABLE')
        COMPU_INTERNAL_TO_PHYS_Node = self.ODXG_AddNode(COMPU_METHOD_Node,  "COMPU-INTERNAL-TO-PHYS", doc, '', '')
        COMPU_SCALES_Node = self.ODXG_AddNode(COMPU_INTERNAL_TO_PHYS_Node,  "COMPU-SCALES", doc, '', '')
        for DTCLocalLable in DTCLocalLables:
            COMPU_SCALE_Node = self.ODXG_AddNode(COMPU_SCALES_Node,  "COMPU-SCALE", doc, '', '')
            self.ODXG_AddNode(COMPU_SCALE_Node, "LOWER-LIMIT", doc, '', str(int(DTCLocalLable.keys()[0], 16)))
            self.ODXG_AddNode(COMPU_SCALE_Node, "UPPER-LIMIT", doc, '', str(int(DTCLocalLable.keys()[0], 16)))
            COMPU_CONST = self.ODXG_AddNode(COMPU_SCALE_Node, "COMPU-CONST", doc, '', '')
            self.ODXG_AddNode(COMPU_CONST, "VT", doc, '', DTCLocalLable.values()[0])
        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "DIAG-CODED-TYPE", doc, [('BASE-TYPE-ENCODING', "NONE"),('BASE-DATA-TYPE', 'A_UINT32'), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
        self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', '24')   
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UNICODE2STRING")], '') 
             
        INTERNAL_CONSTR_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "INTERNAL-CONSTR", doc, '', '')
        SCALE_CONSTRS_Node = self.ODXG_AddNode(INTERNAL_CONSTR_Node, "SCALE-CONSTRS", doc, '', '')
             
        DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROP' + 'DtcCount')], '')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', 'DtcCount')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', 'DtcCount')
        COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
        self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', 'IDENTICAL')
        attribute = [('BASE-DATA-TYPE', 'A_BYTEFIELD'), ('xsi:type', 'STANDARD-LENGTH-TYPE')]
        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "DIAG-CODED-TYPE", doc, attribute, '')
        self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', '16')
        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_BYTEFIELD")], '')
        SCALE_CONSTR_Node = self.ODXG_AddNode(SCALE_CONSTRS_Node, "SCALE-CONSTR", doc, [('VALIDITY', "NOT-DEFINED")], '')
        self.ODXG_AddNode(SCALE_CONSTR_Node, "LOWER-LIMIT", doc, '', '0') # LOWER-LIMIT
        self.ODXG_AddNode(SCALE_CONSTR_Node, "UPPER-LIMIT", doc, '', ' 8388607') # UPPER-LIMIT
        
        SCALE_CONSTR_Node = self.ODXG_AddNode(SCALE_CONSTRS_Node, "SCALE-CONSTR", doc, [('VALIDITY', "NOT-DEFINED")], '')
        self.ODXG_AddNode(SCALE_CONSTR_Node, "LOWER-LIMIT", doc, '', '8388609') # LOWER-LIMIT
        self.ODXG_AddNode(SCALE_CONSTR_Node, "UPPER-LIMIT", doc, '', ' 12582911') # UPPER-LIMIT
        
        SCALE_CONSTR_Node = self.ODXG_AddNode(SCALE_CONSTRS_Node, "SCALE-CONSTR", doc, [('VALIDITY', "NOT-DEFINED")], '')
        self.ODXG_AddNode(SCALE_CONSTR_Node, "LOWER-LIMIT", doc, '', '12582913') # LOWER-LIMIT
        self.ODXG_AddNode(SCALE_CONSTR_Node, "UPPER-LIMIT", doc, '', ' 16777214') # UPPER-LIMIT
        
        for dtcStatus in self.DTCStatuslists:
            DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROP' + dtcStatus)], '')
            self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', dtcStatus)
            self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', dtcStatus)
            COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
            self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', 'TEXTTABLE')
            COMPU_INTERNAL_TO_PHYS_Node = self.ODXG_AddNode(COMPU_METHOD_Node, "COMPU-INTERNAL-TO-PHYS", doc, '', '')
            COMPU_SCALES_Node = self.ODXG_AddNode(COMPU_INTERNAL_TO_PHYS_Node, "COMPU-SCALES", doc, '', '')
            COMPU_SCALE_Node = self.ODXG_AddNode(COMPU_SCALES_Node, "COMPU-SCALE", doc, '', '')
            self.ODXG_AddNode(COMPU_SCALE_Node, "LOWER-LIMIT", doc, '', '0')
            self.ODXG_AddNode(COMPU_SCALE_Node, "UPPER-LIMIT", doc, '', '0')
            COMPU_CONST = self.ODXG_AddNode(COMPU_SCALE_Node, "COMPU-CONST", doc, '', '')
            self.ODXG_AddNode(COMPU_CONST, "VT", doc, '', 'false')
            
            COMPU_SCALE_Node = self.ODXG_AddNode(COMPU_SCALES_Node, "COMPU-SCALE", doc, '', '')
            self.ODXG_AddNode(COMPU_SCALE_Node, "LOWER-LIMIT", doc, '', '1')
            self.ODXG_AddNode(COMPU_SCALE_Node, "UPPER-LIMIT", doc, '', '1')
            COMPU_CONST = self.ODXG_AddNode(COMPU_SCALE_Node, "COMPU-CONST", doc, '', '')
            self.ODXG_AddNode(COMPU_CONST, "VT", doc, '', 'true')
            
            attribute = [('BASE-TYPE-ENCODING', 'NONE'), ('BASE-DATA-TYPE', 'A_UINT32'), ('xsi:type', 'STANDARD-LENGTH-TYPE')]
            DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "DIAG-CODED-TYPE", doc, attribute, '')
            self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', '1')
            
            self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UNICODE2STRING")], '')
                      
        for signal in self.PIDSignallists:
            # Signal
            # 00-SignalName, 01-SignalStartbyte, 02-SignalBitSize, 
            # 03-SignalStartBit, 04-SignalUnit, 05-SignalDefaultValue, 
            # 06-SignalResolution, 07-SignalType, 08-SignalCategory, 09-PIDName
            # Attribute: ID = '__DATA_OBJECT_PROP' + SignalName
            # Attribute: ID = '__DATA_OBJECT_PROP' + SignalName
            
            DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROP' + signal[9] + signal[0])], '')
            self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', signal[0])
            self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', signal[0])

            COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
            
            attribute = [('BASE-TYPE-ENCODING', 'NONE'), ('BASE-DATA-TYPE', 'A_UINT32'), ('xsi:type', 'STANDARD-LENGTH-TYPE')]
            DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "DIAG-CODED-TYPE", doc, attribute, '')
            self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', str(signal[2])) # 02-SignalBitSize,  
            
            # If SignalCategory is Null, the default CATEGORY set to 'IDENTICAL' in COMPU_METHOD_Node
            if('' != signal[8]):
                self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', signal[8])
                COMPU_INTERNAL_TO_PHYS_Node = self.ODXG_AddNode(COMPU_METHOD_Node, "COMPU-INTERNAL-TO-PHYS", doc, '', '')
                COMPU_SCALES_Node = self.ODXG_AddNode(COMPU_INTERNAL_TO_PHYS_Node, "COMPU-SCALES", doc, '', '')
                if('LINEAR' == signal[8]):
                    COMPU_SCALE_Node = self.ODXG_AddNode(COMPU_SCALES_Node, "COMPU-SCALE", doc, '', '')
                    COMPU_RATIONAL_COEFFS = self.ODXG_AddNode(COMPU_SCALE_Node, "COMPU-RATIONAL-COEFFS", doc, '', '')
                    COMPU_NUMERATOR = self.ODXG_AddNode(COMPU_RATIONAL_COEFFS, "COMPU-NUMERATOR", doc, '', '')
                    self.ODXG_AddNode(COMPU_NUMERATOR, "V", doc, '', '0')
                    self.ODXG_AddNode(COMPU_NUMERATOR, "V", doc, '', str(signal[6]))
                    
                    COMPU_DENOMINATOR = self.ODXG_AddNode(COMPU_RATIONAL_COEFFS, "COMPU-DENOMINATOR", doc, '', '')
                    self.ODXG_AddNode(COMPU_DENOMINATOR, "V", doc, '', '1')
                    
                    self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_FLOAT64")], '') # Signal PHYSICAL-TYPE, 
                    if('' != signal[4]): # 04-SignalUnit
                        self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "UNIT-REF", doc, [('ID-REF', ('__UNIT_' + signal[0] + signal[9]))], '') # UNIT-REF,  09-PIDName
                    
                elif('TEXTTABLE' == signal[8]): # 05-SignalDefaultValue
                    valueList = signal[5].split('\n')
                    for value in valueList:
                        # value example: 0xA5: Normal Mode
                        valueDec = str(int(value.split(':')[0], 16)) # Translate to DEC
                        valueTxt = str(value.split(':')[1])
                        
                        COMPU_SCALE_Node = self.ODXG_AddNode(COMPU_SCALES_Node, "COMPU-SCALE", doc, '', '')
                        self.ODXG_AddNode(COMPU_SCALE_Node, "LOWER-LIMIT", doc, '', valueDec)
                        self.ODXG_AddNode(COMPU_SCALE_Node, "UPPER-LIMIT", doc, '', valueDec)
                        COMPU_CONST_Node = self.ODXG_AddNode(COMPU_SCALE_Node, "COMPU-CONST", doc, '', '')
                        self.ODXG_AddNode(COMPU_CONST_Node, "VT", doc, '', valueTxt)
                    self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UNICODE2STRING")], '') # Signal PHYSICAL-TYPE,    
                else:
                    pass
                
            else:
                self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', 'IDENTICAL')
                self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('DISPLAY-RADIX', "DEC")], '') # Signal PHYSICAL-TYPE,
         
        for uds in self.UDSlists:
            # self.UDSlists: 0-ServiceID, 1-ServiceName, 2-SubServiceList, 3-FunctClass, 4-NRCs
            DATA_OBJECT_PROP_Node = self.ODXG_AddNode(DATA_OBJECT_PROPS_Node, "DATA-OBJECT-PROP", doc, [('ID', '__DATA_OBJECT_PROP' + uds[1] + '_NR')], '')
            self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "SHORT-NAME", doc, '', (uds[1] + '_NR_DOP1')) # 1-ServiceName
            self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "LONG-NAME", doc, '', (uds[1] + '_NR_DOP')) # 1-ServiceName
            COMPU_METHOD_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node, "COMPU-METHOD", doc, '', '')
            self.ODXG_AddNode(COMPU_METHOD_Node,  "CATEGORY", doc, '', "TEXTTABLE")
            COMPU_INTERNAL_TO_PHYS_Node = self.ODXG_AddNode(COMPU_METHOD_Node, "COMPU-INTERNAL-TO-PHYS", doc, '', '')
            COMPU_SCALES_Node = self.ODXG_AddNode(COMPU_INTERNAL_TO_PHYS_Node, "COMPU-SCALES", doc, '', '')
            for nrc in uds[4]:
                nrc = nrc.strip()
                COMPU_SCALE_Node = self.ODXG_AddNode(COMPU_SCALES_Node, "COMPU-SCALE", doc, '', '')
                self.ODXG_AddNode(COMPU_SCALE_Node, "LOWER-LIMIT", doc, '', str(int(nrc, 16)))
                COMPU_CONST_Node = self.ODXG_AddNode(COMPU_SCALE_Node, "COMPU-CONST", doc, '', '')
                self.ODXG_AddNode(COMPU_CONST_Node, "VT", doc, '', self.NRCslists[nrc])
            
            DIAG_CODED_TYPE_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', 'A_UINT32'), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
            self.ODXG_AddNode(DIAG_CODED_TYPE_Node,  "BIT-LENGTH", doc, '', '8')
            
            self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "PHYSICAL-TYPE", doc, [('BASE-DATA-TYPE', "A_UNICODE2STRING")], '') 
             
            INTERNAL_CONSTR_Node = self.ODXG_AddNode(DATA_OBJECT_PROP_Node,  "INTERNAL-CONSTR", doc, '', '')
            SCALE_CONSTRS_Node = self.ODXG_AddNode(INTERNAL_CONSTR_Node, "SCALE-CONSTRS", doc, '', '')
            
            nrcLiners = []
            for nrc in uds[4]:
                nrcLiners.append(int(nrc.strip(),16))
            nrcLiners = sorted(nrcLiners)
            
            nrcSectionList = []
            nrcSectionList.append([0, nrcLiners[0]-1])
            for i in range(1, len(nrcLiners)):
                nrcSectionList.append([nrcLiners[i - 1]+1, nrcLiners[i]-1])
            nrcSectionList.append([nrcLiners[len(nrcLiners)-1]+1, '255'])
            
            for nrcSection in nrcSectionList:         
                SCALE_CONSTR_Node = self.ODXG_AddNode(SCALE_CONSTRS_Node, "SCALE-CONSTR", doc, [('VALIDITY', "NOT-DEFINED")], '')
                self.ODXG_AddNode(SCALE_CONSTR_Node, "LOWER-LIMIT", doc, '', str(nrcSection[0])) # LOWER-LIMIT
                self.ODXG_AddNode(SCALE_CONSTR_Node, "UPPER-LIMIT", doc, '', str(nrcSection[1])) # UPPER-LIMIT
             
    def odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_STRUCTURES(self, doc, parent):
        # For service 28 CommunicationControl
        STRUCTURES_Node = self.ODXG_AddNode(parent, "STRUCTURES", doc, '', '')
        STRUCTURE_Node = self.ODXG_AddNode(STRUCTURES_Node, "STRUCTURE", doc, [('ID', '__TRUCTURE_CommunicationControl')], '')
        self.ODXG_AddNode(STRUCTURE_Node, "SHORT-NAME", doc, '', 'CommunicationControl')
        self.ODXG_AddNode(STRUCTURE_Node, "LONG-NAME", doc, '', 'DTC CommunicationControl')
        self.ODXG_AddNode(STRUCTURE_Node, "BYTE-SIZE", doc, '', '1')
        PARAMS_Node = self.ODXG_AddNode(STRUCTURE_Node, "PARAMS", doc, '', '')
        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
        
        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'NormalCommunicationMessages')
        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'NormalCommunicationMessages')
        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
        self.ODXG_AddNode(PARAM_Node, "BIT-POSITION", doc, '', '0')
        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', ('__DATA_OBJECT_PROP' + 'RoutineStatusRecord'))], '') # Attribute: ID = '__DATA_OBJECT_PROP' + RoutineStatusRecord

        # For service 19
        # For DTC snapshot structure
        STRUCTURE_Node = self.ODXG_AddNode(STRUCTURES_Node, "STRUCTURE", doc, [('ID', '__TRUCTURE_DTCSnapshotRecord')], '')
        self.ODXG_AddNode(STRUCTURE_Node, "SHORT-NAME", doc, '', 'ListOfDTCSnapshotRecord')
        self.ODXG_AddNode(STRUCTURE_Node, "LONG-NAME", doc, '', 'ListOfDTCSnapshotRecord')
        PARAMS_Node = self.ODXG_AddNode(STRUCTURE_Node, "PARAMS", doc, '', '')
        
        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('xsi:type', "VALUE")], '')
        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DtcSnapshotRecordNumber')
        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DtcSnapshotRecordNumber')
        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', ('__DATA_OBJECT_PROP_DtcSnapshotRecordNumber'))], '')
        
        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('xsi:type', "VALUE")], '')
        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DTCSnapshotRecordNumberOfIdentifiers')
        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTCSnapshotRecordNumberOfIdentifiers')
        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', ('__DATA_OBJECT_PROP_DtcSnapshotRecordNumberOfIdentifiers'))], '') 
        
        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC',"DATA"),('xsi:type', "VALUE")], '')
        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SnapshotRecord')
        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SnapshotRecord')
        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', ('__DATA_OBJECT_PROP_DtcSnapshotRecord_dataIdentifier'))], '')

        # For DTC DTCExtendeddata structure
        STRUCTURE_Node = self.ODXG_AddNode(STRUCTURES_Node, "STRUCTURE", doc, [('ID', '__TRUCTURE_DTCExtendeddataRecord'),('IS-VISIBLE',"false")], '')
        self.ODXG_AddNode(STRUCTURE_Node, "SHORT-NAME", doc, '', 'STRUC')
        PARAMS_Node = self.ODXG_AddNode(STRUCTURE_Node, "PARAMS", doc, '', '')
        
        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('xsi:type', "VALUE")], '')
        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'ExtendedDataRecord')
        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'ExtendedDataRecord')
        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', ('__DATA_OBJECT_PROP_DtcSnapshotRecordNumber'))], '')

        # For DTC status structure
        # Attribute ID = '__TRUCTURE' + PIDName
        STRUCTURE_Node = self.ODXG_AddNode(STRUCTURES_Node, "STRUCTURE", doc, [('ID', '__TRUCTURE_DTCSTATUS')], '')
        self.ODXG_AddNode(STRUCTURE_Node, "SHORT-NAME", doc, '', 'DtcStatusbyte_1')
        self.ODXG_AddNode(STRUCTURE_Node, "LONG-NAME", doc, '', 'DTC Statusbyte')
        self.ODXG_AddNode(STRUCTURE_Node, "BYTE-SIZE", doc, '', '1')
        PARAMS_Node = self.ODXG_AddNode(STRUCTURE_Node, "PARAMS", doc, '', '')
        
        for i in range(0, len(self.DTCStatuslists)):
            PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
            
            self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', self.DTCStatuslists[i])
            self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', self.DTCStatuslists[i])
            self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
            self.ODXG_AddNode(PARAM_Node, "BIT-POSITION", doc, '', str(i))
            self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', ('__DATA_OBJECT_PROP' + self.DTCStatuslists[i]))], '') # 00-SignalName Attribute: ID = '__DATA_OBJECT_PROP' + dtcStatus
        
        STRUCTURE_Node = self.ODXG_AddNode(STRUCTURES_Node, "STRUCTURE", doc, [('ID', '__TRUCTURE_DTCLIST')], '')
        self.ODXG_AddNode(STRUCTURE_Node, "SHORT-NAME", doc, '', 'ListOfDTC')
        self.ODXG_AddNode(STRUCTURE_Node, "LONG-NAME", doc, '', 'ListOfDTC')
        PARAMS_Node = self.ODXG_AddNode(STRUCTURE_Node, "PARAMS", doc, '', '')
        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DTC')
        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTC')
        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__BASE_VARIANT_DTC_DOP_Node')], '') 
        
        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DtcStatusbyte_STRUCTURE')
        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTC Statusbyte')
        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '3')
        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__TRUCTURE_DTCSTATUS')], '')
        
    def odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_END_OF_PDU_FIELDS(self, doc, parent):
        END_OF_PDU_FIELDS_Node = self.ODXG_AddNode(parent, "END-OF-PDU-FIELDS", doc, '' , '')
        END_OF_PDU_FIELD_Node = self.ODXG_AddNode(END_OF_PDU_FIELDS_Node, "END-OF-PDU-FIELD", doc, [('ID', '_END_OF_PDU_FIELD_ListOfDTC')], '')
        self.ODXG_AddNode(END_OF_PDU_FIELD_Node, "SHORT-NAME", doc, '', 'ListOfDTC_1')
        self.ODXG_AddNode(END_OF_PDU_FIELD_Node, "LONG-NAME", doc, '', 'ListOfDTC')
        self.ODXG_AddNode(END_OF_PDU_FIELD_Node, "BASIC-STRUCTURE-REF", doc, [('ID-REF', "__TRUCTURE_DTCLIST")], '')
        
        END_OF_PDU_FIELD_Node = self.ODXG_AddNode(END_OF_PDU_FIELDS_Node, "END-OF-PDU-FIELD", doc, [('ID', '_END_OF_PDU_FIELD_ListOfDTCAndStatus')], '')
        self.ODXG_AddNode(END_OF_PDU_FIELD_Node, "SHORT-NAME", doc, '', 'ListOfDTCAndStatus_1')
        self.ODXG_AddNode(END_OF_PDU_FIELD_Node, "LONG-NAME", doc, '', 'ListOfDTCAndStatus')
        self.ODXG_AddNode(END_OF_PDU_FIELD_Node, "BASIC-STRUCTURE-REF", doc, [('ID-REF', "__TRUCTURE_DTCLIST")], '')
        
        END_OF_PDU_FIELD_Node = self.ODXG_AddNode(END_OF_PDU_FIELDS_Node, "END-OF-PDU-FIELD", doc, [('ID', '_END_OF_PDU_FIELD_DTCSnapshotRecord')], '')
        self.ODXG_AddNode(END_OF_PDU_FIELD_Node, "SHORT-NAME", doc, '', 'ListOfDTCSnapshotRecord_1')
        self.ODXG_AddNode(END_OF_PDU_FIELD_Node, "LONG-NAME", doc, '', 'ListOfDTCSnapshotRecord_1')
        self.ODXG_AddNode(END_OF_PDU_FIELD_Node, "BASIC-STRUCTURE-REF", doc, [('ID-REF', "__TRUCTURE_DTCSnapshotRecord")], '')

    def odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_MUXS(self, doc, parent):
        MUXS_Node = self.ODXG_AddNode(parent, "MUXS", doc, '', '')
        MUX_Node = self.ODXG_AddNode(MUXS_Node, "MUX", doc, [('ID',"_MUX_ExtendedDataRecord")], '')
        self.ODXG_AddNode(MUX_Node, "SHORT-NAME", doc, '', 'ExtendedDataRecord')
        self.ODXG_AddNode(MUX_Node, "LONG-NAME", doc, '', 'ExtendedDataRecord')
        self.ODXG_AddNode(MUX_Node, "BYTE-POSITION", doc, '', '1')
        
        SWITCH_KEY_Node = self.ODXG_AddNode(MUX_Node, "SWITCH-KEY", doc, '', '')
        self.ODXG_AddNode(SWITCH_KEY_Node, "BYTE-POSITION", doc, '', '0')
        self.ODXG_AddNode(SWITCH_KEY_Node, "DATA-OBJECT-PROP-REF", doc, [('ID-REF',"__DATA_OBJECT_PROP_ExtendedDataRecordNumber")], '')

        DEFAULT_CASE_Node = self.ODXG_AddNode(MUX_Node, "DEFAULT-CASE", doc, '', '')
        self.ODXG_AddNode(DEFAULT_CASE_Node, "SHORT-NAME", doc, '', 'Case_Default')
        self.ODXG_AddNode(DEFAULT_CASE_Node, "STRUCTURE-REF", doc, [('ID-REF',"__TRUCTURE_DTCExtendeddataRecord")], '')
              
    def odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_UNIT_SPEC(self, doc, parent):
        UNIT_SPEC_Node = self.ODXG_AddNode(parent, "UNIT-SPEC", doc, '', '')
        UNITS_Node = self.ODXG_AddNode(UNIT_SPEC_Node, "UNITS", doc, '', '')
        # SignalList incluede:
        # 00-SignalName, 01-SignalStartbyte, 02-SignalBitSize, 
        # 03-SignalStartBit, 04-SignalUnit, 05-SignalDefaultValue, 
        # 06-SignalResolution, 07-SignalType, 08-SignalCategory, 09-PIDName
        for signal in self.PIDSignallists:
            if('' != signal[4]):
                UNIT_Node = self.ODXG_AddNode(UNITS_Node, "UNIT", doc, [('ID', ('__UNIT_' + signal[0] + signal[9]))], '') # 09-PIDName
                self.ODXG_AddNode(UNIT_Node, "SHORT-NAME", doc, '', signal[4]) # 04-SignalUnit
                self.ODXG_AddNode(UNIT_Node, "DISPLAY-NAME", doc, '', signal[4]) # 04-SignalUnit
        
    def odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC(self, doc, parent):
        DIAG_DATA_DICTIONARY_SPEC_Node = self.ODXG_CreateElement("DIAG-DATA-DICTIONARY-SPEC", doc, '', '')
        
        # TABLES_Node = self.ODXG_CreateElement("TABLES", doc, '', '')
        
        self.odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_DTC_DOPS(doc, DIAG_DATA_DICTIONARY_SPEC_Node) # Add DTC-DOPS Node
        self.odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_ENV_DATA_DESCS(doc, DIAG_DATA_DICTIONARY_SPEC_Node) # Add ENV-DATA-DESCS Node
        self.odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_DATA_OBJECT_PROPS(doc, DIAG_DATA_DICTIONARY_SPEC_Node) # Add DATA-OBJECT-PROPS Node
        self.odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_STRUCTURES(doc, DIAG_DATA_DICTIONARY_SPEC_Node) # Add STRUCTURES Node
        self.odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_END_OF_PDU_FIELDS(doc, DIAG_DATA_DICTIONARY_SPEC_Node) # END-OF-PDU-FIELDS
        self.odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_MUXS(doc, DIAG_DATA_DICTIONARY_SPEC_Node) # MUXS
        self.odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC_UNIT_SPEC(doc, DIAG_DATA_DICTIONARY_SPEC_Node) # UNIT-SPEC
        
        parent.appendChild(DIAG_DATA_DICTIONARY_SPEC_Node)
    
    def odx_BASE_VARIANT_DIAG_COMMS(self, doc, parent):
        DIAG_COMMS_Node = self.ODXG_AddNode(parent, "DIAG-COMMS", doc, '', '')
        
        # self.UDSServicelists: 0-ServiceID, 1-ServiceName, 2-SubServiceID, 3-SubServiceName, 4-SubServiceLen, 5-FunctionClass
        for udsService in self.UDSServicelists:
            if('' != udsService[2] and '0x31' != udsService[0]):
                # DIAG_SERVICE_Node, Attribute: 'ID', ('__DIAG_SERVICE_' + SubServiceName)
                if('0x10' == udsService[0]):
                    semantic = 'SESSION'
                elif('0x27' == udsService[0]):
                    semantic = 'SECURITY'
                elif(('0x19' == udsService[0]) or ('0x14' == udsService[0])):
                    semantic = 'FAULTMEMORY'    
                elif('0x31' == udsService[0]):
                    semantic = 'CONTROL'
                elif(('0x34' == udsService[0]) or ('0x35' != udsService[0]) or ('0x36' != udsService[0]) or ('0x37' != udsService[0])):
                    semantic = 'UP-DOWNLOAD'
                else:
                    semantic = 'FUNCTION'
                if('NoResponse' in udsService[3]): 
                    attribute = [('ID', ('__DIAG_SERVICE_' + udsService[3])), ('SEMANTIC', semantic), ('ADDRESSING', "FUNCTIONAL-OR-PHYSICAL"), ('TRANSMISSION-MODE', "SEND-ONLY")]# 3-SubServiceName
                else:
                    attribute = [('ID', ('__DIAG_SERVICE_' + udsService[3])), ('SEMANTIC', semantic), ('ADDRESSING', "FUNCTIONAL-OR-PHYSICAL")]# 3-SubServiceName
                DIAG_SERVICE_Node = self.ODXG_AddNode(DIAG_COMMS_Node, "DIAG-SERVICE", doc, attribute, '') 
                self.ODXG_AddNode(DIAG_SERVICE_Node, "SHORT-NAME", doc, '', udsService[3])
                self.ODXG_AddNode(DIAG_SERVICE_Node, "LONG-NAME", doc, '', udsService[3])
                SDGS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "SDGS", doc, '', '')
                SDG_Node = self.ODXG_AddNode(SDGS_Node, "SDG", doc, '', '')
                SDG_CAPTION_Node = self.ODXG_AddNode(SDG_Node, "SDG-CAPTION", doc, [('ID', ('__SDG_CAPTION_' + udsService[3]))], '')
                self.ODXG_AddNode(SDG_CAPTION_Node, "SHORT-NAME", doc, '', 'CANdelaServiceInformation')
                
                self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'DiagInstanceQualifier')], udsService[3])
                self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'DiagInstanceName')], udsService[3])
                self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'ServiceQualifier')], udsService[3])
                self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'ServiceName')], udsService[3])
                if('NoResponse' in udsService[3]):
                    self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'PositiveResponseSuppressed')], 'yes')
                else:
                    self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'PositiveResponseSuppressed')], 'no')
                    
                FUNCT_CLASS_REFS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "FUNCT-CLASS-REFS", doc, '', '')
                self.ODXG_AddNode(FUNCT_CLASS_REFS_Node, "FUNCT-CLASS-REF", doc, [('ID-REF', ('__FUNCTCLASS' + udsService[5]))], '') # 5-FunctionClass

                REQUEST_REF_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "REQUEST-REF", doc, [('ID-REF', ('__REQUEST_Node_' + udsService[3]))], '') # 3-SubServiceName
                
                if('NoResponse' not in udsService[3]):
                    POS_RESPONSE_REFS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "POS-RESPONSE-REFS", doc, '', '')
                    self.ODXG_AddNode(POS_RESPONSE_REFS_Node, "POS-RESPONSE-REF", doc, [('ID-REF', ('__POS_RESPONSE_Node_' + udsService[3]))], '') # 3-SubServiceName
                
                if('NoResponse' in udsService[3]):
                    NegResponNodeID = ('__NEG_RESPONSE_Node_' + udsService[3][-11:]) # No response sub servicce remove suffix('_NoResponse') 
                else:
                    NegResponNodeID = ('__NEG_RESPONSE_Node_' + udsService[3])
                    
                NEG_RESPONSE_REFS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "NEG-RESPONSE-REFS", doc, '', '')
                self.ODXG_AddNode(NEG_RESPONSE_REFS_Node, "NEG-RESPONSE-REF", doc, [('ID-REF', NegResponNodeID)], '') # 3-SubServiceName

            if('0x31' == udsService[0]): # 0-ServiceID
                if('0x01' == udsService[2] or '0x02' == udsService[2]): # 2-SubServiceID
                    for UDSRoutine in self.UDSRoutineslists:
                        attribute = [('ID', ('__DIAG_SERVICE_' + udsService[3] + UDSRoutine[1])), ('SEMANTIC', 'CONTROL'), ('ADDRESSING', "FUNCTIONAL-OR-PHYSICAL")]# 3-SubServiceName
                        DIAG_SERVICE_Node = self.ODXG_AddNode(DIAG_COMMS_Node, "DIAG-SERVICE", doc, attribute, '') 
                        self.ODXG_AddNode(DIAG_SERVICE_Node, "SHORT-NAME", doc, '', udsService[3])
                        self.ODXG_AddNode(DIAG_SERVICE_Node, "LONG-NAME", doc, '', udsService[3])
                        SDGS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "SDGS", doc, '', '')
                        SDG_Node = self.ODXG_AddNode(SDGS_Node, "SDG", doc, '', '')
                        SDG_CAPTION_Node = self.ODXG_AddNode(SDG_Node, "SDG-CAPTION", doc, [('ID', ('__SDG_CAPTION_' + udsService[3] + UDSRoutine[1]))], '')
                        self.ODXG_AddNode(SDG_CAPTION_Node, "SHORT-NAME", doc, '', 'CANdelaServiceInformation')
                        
                        self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'DiagInstanceQualifier')], UDSRoutine[1])
                        self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'DiagInstanceName')], UDSRoutine[1])
                        self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'ServiceQualifier')], udsService[3])
                        self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'ServiceName')], udsService[3])
                        
                        self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'PositiveResponseSuppressed')], 'no')
                        
                        FUNCT_CLASS_REFS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "FUNCT-CLASS-REFS", doc, '', '')
                        self.ODXG_AddNode(FUNCT_CLASS_REFS_Node, "FUNCT-CLASS-REF", doc, [('ID-REF', ('__FUNCTCLASS' + udsService[5]))], '') # 5-FunctionClass

                        REQUEST_REF_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "REQUEST-REF", doc, [('ID-REF', ('__REQUEST_Node_' + udsService[3] + UDSRoutine[1]))], '') # 3-SubServiceName

                        POS_RESPONSE_REFS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "POS-RESPONSE-REFS", doc, '', '')
                        self.ODXG_AddNode(POS_RESPONSE_REFS_Node, "POS-RESPONSE-REF", doc, [('ID-REF', ('__POS_RESPONSE_Node_' + udsService[3] + UDSRoutine[1]))], '') # 3-SubServiceName
                        NegResponNodeID = ('__NEG_RESPONSE_Node_' + udsService[3])
                            
                        NEG_RESPONSE_REFS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "NEG-RESPONSE-REFS", doc, '', '')
                        self.ODXG_AddNode(NEG_RESPONSE_REFS_Node, "NEG-RESPONSE-REF", doc, [('ID-REF', NegResponNodeID)], '') # 3-SubServiceName

            if('0x22' == udsService[0]):
                # 0-PIDNumber, 1-PIDName, 2-ReadFlag
                # 3-WriteFlag, 4-ControlFlag, 5-byteSize, 6-SignalList
                #
                # SignalList incluede:
                # 00-SignalName, 01-SignalStartbyte, 02-SignalBitSize, 
                # 03-SignalStartBit, 04-SignalUnit, 05-SignalDefaultValue, 
                # 06-SignalResolution, 07-SignalType, 08-SignalCategory   
                for pid in self.PIDlists:
                    # self.UDSServicelists: 0-ServiceID, 1-ServiceName, 2-SubServiceID, 3-SubServiceName, 4-SubServiceLen, 5-FunctionClass
                    attribute = [('ID', ('__DIAG_SERVICE_' + udsService[3] + pid[1] + 'Read')), ('SEMANTIC', "STOREDDATA"), ('ADDRESSING', "FUNCTIONAL-OR-PHYSICAL")]# 3-SubServiceName
                    DIAG_SERVICE_Node = self.ODXG_AddNode(DIAG_COMMS_Node, "DIAG-SERVICE", doc, attribute, '') 
                    self.ODXG_AddNode(DIAG_SERVICE_Node, "SHORT-NAME", doc, '', (pid[1] + '_Read'))
                    self.ODXG_AddNode(DIAG_SERVICE_Node, "LONG-NAME", doc, '', (pid[1] + '_Read'))
                    SDGS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "SDGS", doc, '', '')
                    SDG_Node = self.ODXG_AddNode(SDGS_Node, "SDG", doc, '', '')
                    SDG_CAPTION_Node = self.ODXG_AddNode(SDG_Node, "SDG-CAPTION", doc, [('ID', ('__SDG_CAPTION_' + udsService[3] + pid[1] + 'Read'))], '')
                    self.ODXG_AddNode(SDG_CAPTION_Node, "SHORT-NAME", doc, '', 'CANdelaServiceInformation')
                    
                    self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'DiagInstanceQualifier')], pid[1])
                    self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'DiagInstanceName')], pid[1])
                    self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'ServiceQualifier')], 'read')
                    self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'ServiceName')], 'read')
                    self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'PositiveResponseSuppressed')], 'no')
      
                    FUNCT_CLASS_REFS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "FUNCT-CLASS-REFS", doc, '', '')
                    self.ODXG_AddNode(FUNCT_CLASS_REFS_Node, "FUNCT-CLASS-REF", doc, [('ID-REF', ('__FUNCTCLASS' + udsService[5]))], '') # 5-FunctionClass
                    
                    self.ODXG_AddNode(DIAG_SERVICE_Node, "AUDIENCE", doc, [('IS-SUPPLIER', 'false'), ('IS-AFTERMARKET', 'false')], '')
                    
                    REQUEST_REF_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "REQUEST-REF", doc, [('ID-REF', ('__REQUEST_Node_' + pid[1] + 'Read'))], '') # 3-SubServiceName

                    POS_RESPONSE_REFS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "POS-RESPONSE-REFS", doc, '', '')
                    self.ODXG_AddNode(POS_RESPONSE_REFS_Node, "POS-RESPONSE-REF", doc, [('ID-REF', ('__POS_RESPONSE_Node_' + pid[1] + 'Read'))], '') # 3-SubServiceName
                    
                    NEG_RESPONSE_REFS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "NEG-RESPONSE-REFS", doc, '', '')
                    self.ODXG_AddNode(NEG_RESPONSE_REFS_Node, "NEG-RESPONSE-REF", doc, [('ID-REF', ('__NEG_RESPONSE_Node_' + pid[1] + 'Read'))], '') # 3-SubServiceName
                    
                    # self.UDSServicelists: 0-ServiceID, 1-ServiceName, 2-SubServiceID, 3-SubServiceName, 4-SubServiceLen, 5-FunctionClass
                    attribute = [('ID', ('__DIAG_SERVICE_' + udsService[3] + pid[1] + 'Write')), ('SEMANTIC', "STOREDDATA"), ('ADDRESSING', "FUNCTIONAL-OR-PHYSICAL")]# 3-SubServiceName
                    DIAG_SERVICE_Node = self.ODXG_AddNode(DIAG_COMMS_Node, "DIAG-SERVICE", doc, attribute, '') 
                    self.ODXG_AddNode(DIAG_SERVICE_Node, "SHORT-NAME", doc, '', (pid[1] + '_Write'))
                    self.ODXG_AddNode(DIAG_SERVICE_Node, "LONG-NAME", doc, '', (pid[1] + '_Write'))
                    SDGS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "SDGS", doc, '', '')
                    SDG_Node = self.ODXG_AddNode(SDGS_Node, "SDG", doc, '', '')
                    SDG_CAPTION_Node = self.ODXG_AddNode(SDG_Node, "SDG-CAPTION", doc, [('ID', ('__SDG_CAPTION_' + udsService[3] + pid[1] + 'Write'))], '')
                    self.ODXG_AddNode(SDG_CAPTION_Node, "SHORT-NAME", doc, '', 'CANdelaServiceInformation')
                    
                    self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'DiagInstanceQualifier')], pid[1])
                    self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'DiagInstanceName')], pid[1])
                    self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'ServiceQualifier')], 'Write')
                    self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'ServiceName')], 'Write')
                    self.ODXG_AddNode(SDG_Node, "SD", doc, [('SI', 'PositiveResponseSuppressed')], 'no')
      
                    FUNCT_CLASS_REFS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "FUNCT-CLASS-REFS", doc, '', '')
                    self.ODXG_AddNode(FUNCT_CLASS_REFS_Node, "FUNCT-CLASS-REF", doc, [('ID-REF', ('__FUNCTCLASS' + udsService[5]))], '') # 5-FunctionClass
                    
                    self.ODXG_AddNode(DIAG_SERVICE_Node, "AUDIENCE", doc, [('IS-SUPPLIER', 'false'), ('IS-AFTERMARKET', 'false')], '')

                    REQUEST_REF_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "REQUEST-REF", doc, [('ID-REF', ('__REQUEST_Node_' + pid[1] + 'Write'))], '') # 3-SubServiceName

                    POS_RESPONSE_REFS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "POS-RESPONSE-REFS", doc, '', '')
                    self.ODXG_AddNode(POS_RESPONSE_REFS_Node, "POS-RESPONSE-REF", doc, [('ID-REF', ('__POS_RESPONSE_Node_' + pid[1] + 'Write'))], '') # 3-SubServiceName
                    
                    NEG_RESPONSE_REFS_Node = self.ODXG_AddNode(DIAG_SERVICE_Node, "NEG-RESPONSE-REFS", doc, '', '')
                    self.ODXG_AddNode(NEG_RESPONSE_REFS_Node, "NEG-RESPONSE-REF", doc, [('ID-REF', ('__NEG_RESPONSE_Node_' + pid[1] + 'Write'))], '') # 3-SubServiceName
            
    def odx_BASE_VARIANT_REQUESTS(self, doc, parent):
        # Add REQUESTS Node
        REQUESTS_Node = self.ODXG_AddNode(parent, "REQUESTS", doc, '', '')
        
        # self.UDSServicelists: 0-ServiceID, 1-ServiceName, 2-SubServiceID, 3-SubServiceName, 4-SubServiceLen
        for udsService in self.UDSServicelists:
            if('' != udsService[2] and '0x31' != udsService[0]):
                # REQUEST_Node, Attribute: 'ID', ('__REQUEST_Node_' + SubServiceName)
                REQUEST_Node = self.ODXG_AddNode(REQUESTS_Node, "REQUEST", doc, [('ID', ('__REQUEST_Node_' + udsService[3]))], '') # 3-SubServiceName
                self.ODXG_AddNode(REQUEST_Node, "SHORT-NAME", doc, '', ('RQ_' + udsService[3]))
                self.ODXG_AddNode(REQUEST_Node, "LONG-NAME", doc, '', ('RQ_' + udsService[3]))
                PARAMS_Node = self.ODXG_AddNode(REQUEST_Node, "PARAMS", doc, '', '')
                
                PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICE-ID"), ('xsi:type', "CODED-CONST")], '')
                self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SID_RQ')
                self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SID_RQ')
                self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
                ServiceID = str(int(udsService[0], 16)) # 0-ServiceID, change to Dec
                self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', ServiceID) # 0-ServiceID
                DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                
                if('Seed' in udsService[3]):
                    semantic = "ACCESSMODE"
                else:
                    semantic = "SUBFUNCTION"
                    
                if('0x14' == udsService[0]): # 0-ServiceID
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DtcStatusbyte_STRUCTURE')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTC Statusbyte')
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
                    self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__DATA_OBJECT_PROPLocalTable')], '')  
                else:
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', semantic), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', udsService[3]) # 3-SubServiceName
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', udsService[3]) # 3-SubServiceName
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
                    SubServiceID = str(int(udsService[2], 16)) # 2-SubServiceID, change to Dec
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', SubServiceID) # 2-SubServiceID
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', udsService[4]) # 4-SubServiceLen

                if('0x28' == udsService[0]): # 0-ServiceID
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'ControlType')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'type')
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                    self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__TRUCTURE_CommunicationControl')], '')
                
                if('0x27' == udsService[0]): # 0-ServiceID
                    if('0x02' == udsService[2] or '0x12' == udsService[2]): # 2-SubServiceID
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DtcStatusbyte_STRUCTURE')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTC Statusbyte')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__DATA_OBJECT_PROP' + 'SeedKey')], '') 

                if('0x19' == udsService[0]): # 0-ServiceID
                    if('0x01' == udsService[2] or '0x02' == udsService[2]): # 2-SubServiceID
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DtcStatusbyte_STRUCTURE')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTC Statusbyte')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__TRUCTURE_DTCSTATUS')], '')
                    if('0x04' == udsService[2] or '0x06' == udsService[2]): # 2-SubServiceID
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DTC')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTC')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__DTC_DOP_Node')], '')
                    if('0x04' == udsService[2]): # 2-SubServiceID
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DtcSnapshotRecordNumber')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DtcSnapshotRecordNumber')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '5')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__DATA_OBJECT_PROPSnapshot')], '')
                    if('0x06' == udsService[2]): # 2-SubServiceID
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'ExtendedDataRecordNumber')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'ExtendedDataRecordNumber')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '5')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__DATA_OBJECT_PROP_ExtendedDataRecordNumber')], '')                        

            if('0x31' == udsService[0]): # 0-ServiceID
                if('0x01' == udsService[2] or '0x02' == udsService[2]): # 2-SubServiceID
                    for UDSRoutine in self.UDSRoutineslists:
                        # self.UDSRoutineslists: 0-RoutineID, 1-RoutineName
                        # REQUEST_Node, Attribute: 'ID', ('__REQUEST_Node_' + SubServiceName)
                        REQUEST_Node = self.ODXG_AddNode(REQUESTS_Node, "REQUEST", doc, [('ID', ('__REQUEST_Node_' + udsService[3] + UDSRoutine[1]))], '') # 3-SubServiceName
                        self.ODXG_AddNode(REQUEST_Node, "SHORT-NAME", doc, '', ('RQ_' + udsService[3]))
                        self.ODXG_AddNode(REQUEST_Node, "LONG-NAME", doc, '', ('RQ_' + udsService[3]))
                        PARAMS_Node = self.ODXG_AddNode(REQUEST_Node, "PARAMS", doc, '', '')
                        
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICE-ID"), ('xsi:type', "CODED-CONST")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SID_RQ')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SID_RQ')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
                        ServiceID = str(int(udsService[0], 16)) # 0-ServiceID, change to Dec
                        self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', ServiceID) # 0-ServiceID
                        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                        self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                        
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', 'SUBFUNCTION'), ('xsi:type', "CODED-CONST")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', udsService[3]) # 3-SubServiceName
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', udsService[3]) # 3-SubServiceName
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
                        SubServiceID = str(int(udsService[2], 16)) # 2-SubServiceID, change to Dec
                        self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', SubServiceID) # 2-SubServiceID
                        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                        self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', udsService[4]) # 4-SubServiceLen
                        
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "ID"), ('xsi:type', "CODED-CONST")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'RoutineIdentifier')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'Identifier')               
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                        RoutineID = str(int(UDSRoutine[0], 16)) # 0-RoutineID, change to Dec
                        self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', RoutineID)
                        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                        self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '16')     
                        
            if('0x22' == udsService[0]):
                # 0-PIDNumber, 1-PIDName, 2-ReadFlag
                # 3-WriteFlag, 4-ControlFlag, 5-byteSize, 6-SignalList
                #
                # SignalList incluede:
                # 00-SignalName, 01-SignalStartbyte, 02-SignalBitSize, 
                # 03-SignalStartBit, 04-SignalUnit, 05-SignalDefaultValue, 
                # 06-SignalResolution, 07-SignalType, 08-SignalCategory   
                for pid in self.PIDlists:
                    # REQUEST_Node, Attribute: 'ID', ('__REQUEST_Node_' + PIDName + 'Read')
                    REQUEST_Node = self.ODXG_AddNode(REQUESTS_Node, "REQUEST", doc, [('ID', ('__REQUEST_Node_' + pid[1] + 'Read'))], '') # 1-PIDName
                    self.ODXG_AddNode(REQUEST_Node, "SHORT-NAME", doc, '', ('RQ_' + pid[1] + '_Read'))
                    self.ODXG_AddNode(REQUEST_Node, "LONG-NAME", doc, '', ('RQ_' + pid[1] + '_Read'))
                    PARAMS_Node = self.ODXG_AddNode(REQUEST_Node, "PARAMS", doc, '', '')
                    
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICE-ID"), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SID_RQ')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SID_RQ')
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', '34') # Read service 0x22
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "ID"), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'RecordDataIdentifier')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'Identifier')               
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
                    SubServiceID = str(int(pid[0], 16)) # 0-PIDNumber, change to Dec
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', SubServiceID) # 2-SubServiceID
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '16')  

                    # REQUEST_Node, Attribute: 'ID', ('__REQUEST_Node_' + PIDName + 'Write')
                    REQUEST_Node = self.ODXG_AddNode(REQUESTS_Node, "REQUEST", doc, [('ID', ('__REQUEST_Node_' + pid[1] + 'Write'))], '') # 1-PIDName
                    self.ODXG_AddNode(REQUEST_Node, "SHORT-NAME", doc, '', ('RQ_' + pid[1] + '_Write'))
                    self.ODXG_AddNode(REQUEST_Node, "LONG-NAME", doc, '', ('RQ_' + pid[1] + '_Write'))
                    PARAMS_Node = self.ODXG_AddNode(REQUEST_Node, "PARAMS", doc, '', '')
                    
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICE-ID"), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SID_RQ')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SID_RQ')
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', '46') # Write service 0x2E
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "ID"), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'RecordDataIdentifier')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'Identifier')               
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
                    SubServiceID = str(int(pid[0], 16)) # 0-PIDNumber, change to Dec
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', SubServiceID) # 2-SubServiceID
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '16')
                    '''
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', pid[1])
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', pid[1])
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '3') # 01-SignalStartbyte
                    self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', ('__TRUCTURE' + pid[1]))], '') # 01-PIDName
                    '''
                    for signal in pid[6]:
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', signal[0]) # 00-SignalName
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', signal[0]) # 00-SignalName 
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', str(2 + signal[1])) # 01-SignalStartbyte
                        
                        bitPos = signal[3] - signal[1] * 8 # 03-SignalStartBit 01-SignalStartbyte, bitPos = SignalStartBit - 8 * SignalStartbyte
                        self.ODXG_AddNode(PARAM_Node, "BIT-POSITION", doc, '', str(bitPos)) # 03-SignalStartBit                
                        
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', ('__DATA_OBJECT_PROP' + signal[9] + signal[0]))], '') # 00-SignalName Attribute: ID = '__DATA_OBJECT_PROP' + SignalName
                
    def odx_BASE_VARIANT_POS_RESPONSES(self, doc, parent):
        # Add POS-RESPONSES Node
        POS_RESPONSES_Node = self.ODXG_AddNode(parent, "POS-RESPONSES", doc, '', '')
         # self.UDSServicelists: 0-ServiceID, 1-ServiceName, 2-SubServiceID, 3-SubServiceName, 4-SubServiceLen
        for udsService in self.UDSServicelists:  
            if(('' != udsService[2]) and ('NoResponse' not in udsService[3]) and '0x31' != udsService[0]):
                # POS_RESPONSE_Node, Attribute: 'ID', ('__POS_RESPONSE_Node_' + SubServiceName)
                POS_RESPONSE_Node = self.ODXG_AddNode(POS_RESPONSES_Node, "POS-RESPONSE", doc, [('ID', ('__POS_RESPONSE_Node_' + udsService[3]))], '') # 3-SubServiceName
                self.ODXG_AddNode(POS_RESPONSE_Node, "SHORT-NAME", doc, '', ('PR_' + udsService[3]))
                self.ODXG_AddNode(POS_RESPONSE_Node, "LONG-NAME", doc, '', ('PR_' + udsService[3]))
                PARAMS_Node = self.ODXG_AddNode(POS_RESPONSE_Node, "PARAMS", doc, '', '')
                PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICE-ID"), ('xsi:type', "CODED-CONST")], '')
                self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SID_PR')
                self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SID_PR')
                self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
                ServiceID = str(int(udsService[0], 16) + 64) # 0-ServiceID, change to Dec +0x40 positive response
                self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', ServiceID) # 0-ServiceID
                DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                if('Seed' in udsService[3]):
                    semantic = "ACCESSMODE"
                else:
                    semantic = "SUBFUNCTION"
                    
                if('0x14' == udsService[0]): # 0-ServiceID
                    pass
                else:
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', semantic), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', udsService[3]) # 3-SubServiceName
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', udsService[3]) # 3-SubServiceName            
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
                    SubServiceID = str(int(udsService[2], 16)) # 2-SubServiceID, change to Dec
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', SubServiceID) # 2-SubServiceID
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', udsService[4]) # 4-SubServiceLen

                if('0x27' == udsService[0]): # 0-ServiceID
                    if('0x01' == udsService[2] or '0x11' == udsService[2]): # 2-SubServiceID
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DtcStatusbyte_STRUCTURE')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTC Statusbyte')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__DATA_OBJECT_PROP' + 'SeedKey')], '')
                
                
                if('0x19' == udsService[0]) : # 0-ServiceID, 
                    if('0x01' == udsService[2]): # 2-SubServiceID
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DtcStatusbyte_STRUCTURE')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTC Statusbyte')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__TRUCTURE_DTCSTATUS')], '')
                        
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('xsi:type', "RESERVED")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'reserved')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'reserved')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '3')
                        self.ODXG_AddNode(PARAM_Node, "BIT-LENGTH", doc, '', '8')
                        
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DtcCount')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DtcCount')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '4')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__DATA_OBJECT_PROPDtcCount')], '')
                        
                    if('0x02' == udsService[2]): # 2-SubServiceID
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DtcStatusbyte_STRUCTURE')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTC Statusbyte')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__TRUCTURE_DTCSTATUS')], '')
                        
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'ListOfDTC')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'ListOfDTC')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '3')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '_END_OF_PDU_FIELD_ListOfDTC')], '')
                        
                    if('0x0A' == udsService[2]): # 2-SubServiceID
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DtcStatusbyte_STRUCTURE')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTC Statusbyte')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__TRUCTURE_DTCSTATUS')], '')
                        
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'ListOfDTCAndStatus')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'ListOfDTCAndStatus')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '3')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '_END_OF_PDU_FIELD_ListOfDTCAndStatus')], '')
                        
                    if('0x04' == udsService[2] or '0x06' == udsService[2]): # 2-SubServiceID
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DTC')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTC')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__DTC_DOP_Node')], '')
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'DTC')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'DTC')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '5')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__TRUCTURE_DTCSTATUS')], '')
                    if('0x04' == udsService[2]): # 2-SubServiceID
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'ListOfDTCSnapshotRecord')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'ListOfDTCSnapshotRecord')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '6')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '_END_OF_PDU_FIELD_DTCSnapshotRecord')], '')
                    if('0x06' == udsService[2]): # 2-SubServiceID
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'ExtendedDataRecord')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'ExtendedDataRecord')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '6')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__DATA_OBJECT_PROP_ExtendedDataRecordNumber')], '')
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'ExtendedDataRecord')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'ExtendedDataRecord')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '6')
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '_MUX_ExtendedDataRecord')], '')
            
            if('0x31' == udsService[0]): # 0-ServiceID
                if('0x01' == udsService[2] or '0x02' == udsService[2]): # 2-SubServiceID
                    for UDSRoutine in self.UDSRoutineslists:
                        # POS_RESPONSE_Node, Attribute: 'ID', ('__POS_RESPONSE_Node_' + SubServiceName)
                        POS_RESPONSE_Node = self.ODXG_AddNode(POS_RESPONSES_Node, "POS-RESPONSE", doc, [('ID', ('__POS_RESPONSE_Node_' + udsService[3] + UDSRoutine[1]))], '') # 3-SubServiceName
                        self.ODXG_AddNode(POS_RESPONSE_Node, "SHORT-NAME", doc, '', ('PR_' + udsService[3] + UDSRoutine[1]))
                        self.ODXG_AddNode(POS_RESPONSE_Node, "LONG-NAME", doc, '', ('PR_' + udsService[3] + UDSRoutine[1]))
                        PARAMS_Node = self.ODXG_AddNode(POS_RESPONSE_Node, "PARAMS", doc, '', '')
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICE-ID"), ('xsi:type', "CODED-CONST")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SID_PR')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SID_PR')
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
                        ServiceID = str(int(udsService[0], 16) + 64) # 0-ServiceID, change to Dec +0x40 positive response
                        self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', ServiceID) # 0-ServiceID
                        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                        self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                        if('Seed' in udsService[3]):
                            semantic = "ACCESSMODE"
                        else:
                            semantic = "SUBFUNCTION"
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', semantic), ('xsi:type', "CODED-CONST")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', udsService[3]) # 3-SubServiceName
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', udsService[3]) # 3-SubServiceName            
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
                        SubServiceID = str(int(udsService[2], 16)) # 2-SubServiceID, change to Dec
                        self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', SubServiceID) # 2-SubServiceID
                        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                        self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', udsService[4]) # 4-SubServiceLen

                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "ID"), ('xsi:type', "CODED-CONST")], '')
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'RoutineIdentifier')
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'Identifier')               
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                        RoutineID = str(int(UDSRoutine[0], 16)) # 0-RoutineID, change to Dec
                        self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', RoutineID)
                        DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                        self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '16')                        
                    
            if('0x22' == udsService[0]):
                # 0-PIDNumber, 1-PIDName, 2-ReadFlag
                # 3-WriteFlag, 4-ControlFlag, 5-byteSize, 6-SignalList
                #
                # SignalList incluede:
                # 00-SignalName, 01-SignalStartbyte, 02-SignalBitSize, 
                # 03-SignalStartBit, 04-SignalUnit, 05-SignalDefaultValue, 
                # 06-SignalResolution, 07-SignalType, 08-SignalCategory   
                for pid in self.PIDlists:
                    # REQUEST_Node, Attribute: 'ID', ('__POS_RESPONSE_Node_' + PIDName + 'Read')
                    POS_RESPONSE_Node = self.ODXG_AddNode(POS_RESPONSES_Node, "POS-RESPONSE", doc, [('ID', ('__POS_RESPONSE_Node_' + pid[1] + 'Read'))], '') # 1-PIDName
                    self.ODXG_AddNode(POS_RESPONSE_Node, "SHORT-NAME", doc, '', ('PR_' + pid[1] + '_Read'))
                    self.ODXG_AddNode(POS_RESPONSE_Node, "LONG-NAME", doc, '', ('PR_' + pid[1] + '_Read'))
                    PARAMS_Node = self.ODXG_AddNode(POS_RESPONSE_Node, "PARAMS", doc, '', '')
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICE-ID"), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SID_PR')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SID_PR')
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', '98') # Read service 0x22
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "ID"), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'RecordDataIdentifier')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'Identifier')               
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
                    SubServiceID = str(int(pid[0], 16)) # 0-PIDNumber, change to Dec
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', SubServiceID) # 2-SubServiceID
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '16')
                    '''
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', pid[1])
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', pid[1])
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '3') # 01-SignalStartbyte
                    self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', ('__TRUCTURE' + pid[1]))], '') # 01-PIDName
                    '''
                    for signal in pid[6]:
                        PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')
                        
                        self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', signal[0]) # 00-SignalName
                        self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', signal[0]) # 00-SignalName 
                        self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', str(2 + signal[1])) # 01-SignalStartbyte
                        
                        bitPos = signal[3] - signal[1] * 8 # 03-SignalStartBit 01-SignalStartbyte, bitPos = SignalStartBit - 8 * SignalStartbyte
                        self.ODXG_AddNode(PARAM_Node, "BIT-POSITION", doc, '', str(bitPos)) # 03-SignalStartBit                
                        
                        self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', ('__DATA_OBJECT_PROP' + signal[9] + signal[0]))], '') # 00-SignalName Attribute: ID = '__DATA_OBJECT_PROP' + SignalName
                    
                    # REQUEST_Node, Attribute: 'ID', ('__POS_RESPONSE_Node_' + PIDName + 'Write')
                    POS_RESPONSE_Node = self.ODXG_AddNode(POS_RESPONSES_Node, "POS-RESPONSE", doc, [('ID', ('__POS_RESPONSE_Node_' + pid[1] + 'Write'))], '') # 1-PIDName
                    self.ODXG_AddNode(POS_RESPONSE_Node, "SHORT-NAME", doc, '', ('PR_' + pid[1] + '_Read'))
                    self.ODXG_AddNode(POS_RESPONSE_Node, "LONG-NAME", doc, '', ('PR_' + pid[1] + '_Read'))
                    PARAMS_Node = self.ODXG_AddNode(POS_RESPONSE_Node, "PARAMS", doc, '', '')
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICE-ID"), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SID_PR')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SID_PR')
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', '110') # Write service 0x2E
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "ID"), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'RecordDataIdentifier')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'Identifier')               
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
                    SubServiceID = str(int(pid[0], 16)) # 0-PIDNumber, change to Dec
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', SubServiceID) # 2-SubServiceID
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '16')                     
                        
    def odx_BASE_VARIANT_NEG_RESPONSES(self, doc, parent):
        # Add NEG-RESPONSES Node
        NEG_RESPONSES_Node = self.ODXG_AddNode(parent, "NEG-RESPONSES", doc, '', '')
         # self.UDSServicelists: 0-ServiceID, 1-ServiceName, 2-SubServiceID, 3-SubServiceName, 4-SubServiceLen, 5-FunctionClass, 6-NRCs
        for udsService in self.UDSServicelists:  
            if(('' != udsService[2]) and ('NoResponse' not in udsService[3])):
                # POS_RESPONSE_Node, Attribute: 'ID', ('__NEG_RESPONSE_Node_' + SubServiceName)
                NEG_RESPONSE_Node = self.ODXG_AddNode(NEG_RESPONSES_Node, "NEG-RESPONSE", doc, [('ID', ('__NEG_RESPONSE_Node_' + udsService[3]))], '') # 3-SubServiceName
                self.ODXG_AddNode(NEG_RESPONSE_Node, "SHORT-NAME", doc, '', ('NR_' + udsService[3]))
                self.ODXG_AddNode(NEG_RESPONSE_Node, "LONG-NAME", doc, '', ('NR_' + udsService[3]))
                PARAMS_Node = self.ODXG_AddNode(NEG_RESPONSE_Node, "PARAMS", doc, '', '')
                PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICE-ID"), ('xsi:type', "CODED-CONST")], '')
                self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SID_NR')
                self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SID_NR')
                self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
                self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', '127') # Negative response 0x7F
                DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICEIDRQ"), ('xsi:type', "CODED-CONST")], '')
                self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SIDRQ_NR')
                self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SIDRQ-NR')               
                self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
                SubServiceID = str(int(udsService[0], 16)) # 2-SubServiceID, change to Dec
                self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', SubServiceID) # 2-SubServiceID
                DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                if('0x14' == udsService[0]): # 0-ServiceID
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                else:
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', udsService[4]) # 4-SubServiceLen   

                PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')                
                self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', (udsService[3] + '_NR'))
                self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', (udsService[3] + '_NR'))
                self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__DATA_OBJECT_PROP' + udsService[1] + '_NR')], '')

                PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "NRC-CONST")], '')                
                self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', (udsService[3] + '_NR'))
                self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', (udsService[3] + '_NR'))
                self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                CODED_VALUES_Node = self.ODXG_AddNode(PARAM_Node, "CODED-VALUES", doc, '', '')
                for nrc in udsService[6]: # 6-NRCs
                    self.ODXG_AddNode(CODED_VALUES_Node, "CODED-VALUE", doc, '', str(int(nrc.strip(),16)))
                DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                
            if('0x22' == udsService[0]):
                # 0-PIDNumber, 1-PIDName, 2-ReadFlag
                # 3-WriteFlag, 4-ControlFlag, 5-byteSize, 6-SignalList
                #
                # SignalList incluede:
                # 00-SignalName, 01-SignalStartbyte, 02-SignalBitSize, 
                # 03-SignalStartBit, 04-SignalUnit, 05-SignalDefaultValue, 
                # 06-SignalResolution, 07-SignalType, 08-SignalCategory   
                for pid in self.PIDlists:
                    # NEG_RESPONSE_Node, Attribute: 'ID', ('__NEG_RESPONSE_Node_' + PIDName + 'Read')
                    NEG_RESPONSE_Node = self.ODXG_AddNode(NEG_RESPONSES_Node, "NEG-RESPONSE", doc, [('ID', ('__NEG_RESPONSE_Node_' + pid[1] + 'Read'))], '') # 1-PIDName
                    self.ODXG_AddNode(NEG_RESPONSE_Node, "SHORT-NAME", doc, '', ('NR_' + pid[1] + '_Read'))
                    self.ODXG_AddNode(NEG_RESPONSE_Node, "LONG-NAME", doc, '', ('NR_' + pid[1] + '_Read'))
                    PARAMS_Node = self.ODXG_AddNode(NEG_RESPONSE_Node, "PARAMS", doc, '', '')
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICE-ID"), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SID_NR')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SID_NR')
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', '127') # Negative response 0x7F
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICEIDRQ"), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SIDRQ_NR')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SIDRQ-NR')               
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', '34') 
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')

                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')                
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'Read_NR')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'Read_NR')
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                    self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__DATA_OBJECT_PROP' + udsService[1] + '_NR')], '')

                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "NRC-CONST")], '')                
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'NRCConst_Read_NR')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'Read NR')
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                    CODED_VALUES_Node = self.ODXG_AddNode(PARAM_Node, "CODED-VALUES", doc, '', '')
                    for nrc in udsService[6]: # 6-NRCs
                        self.ODXG_AddNode(CODED_VALUES_Node, "CODED-VALUE", doc, '', str(int(nrc.strip(),16)))
                    
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                    
                    
                    # NEG_RESPONSE_Node, Attribute: 'ID', ('__NEG_RESPONSE_Node_' + PIDName + 'Write')
                    NEG_RESPONSE_Node = self.ODXG_AddNode(NEG_RESPONSES_Node, "NEG-RESPONSE", doc, [('ID', ('__NEG_RESPONSE_Node_' + pid[1] + 'Write'))], '') # 1-PIDName
                    self.ODXG_AddNode(NEG_RESPONSE_Node, "SHORT-NAME", doc, '', ('NR_' + pid[1] + '_Write'))
                    self.ODXG_AddNode(NEG_RESPONSE_Node, "LONG-NAME", doc, '', ('NR_' + pid[1] + '_Write'))
                    PARAMS_Node = self.ODXG_AddNode(NEG_RESPONSE_Node, "PARAMS", doc, '', '')
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICE-ID"), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SID_NR')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SID_NR')
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '0')
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', '127') # Negative response 0x7F
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "SERVICEIDRQ"), ('xsi:type', "CODED-CONST")], '')
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'SIDRQ_NR')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'SIDRQ-NR')               
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '1')
                    SubServiceID = str(int(pid[0], 16)) # 0-PIDNumber, change to Dec
                    self.ODXG_AddNode(PARAM_Node, "CODED-VALUE", doc, '', '46')
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
                    
                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "VALUE")], '')                
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'Write_NR')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'Write_NR')
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                    self.ODXG_AddNode(PARAM_Node, "DOP-REF", doc, [('ID-REF', '__DATA_OBJECT_PROP' + udsService[1] + '_NR')], '')

                    PARAM_Node = self.ODXG_AddNode(PARAMS_Node, "PARAM", doc, [('SEMANTIC', "DATA"), ('xsi:type', "NRC-CONST")], '')                
                    self.ODXG_AddNode(PARAM_Node, "SHORT-NAME", doc, '', 'NRCConst_Write_NR')
                    self.ODXG_AddNode(PARAM_Node, "LONG-NAME", doc, '', 'Write NR')
                    self.ODXG_AddNode(PARAM_Node, "BYTE-POSITION", doc, '', '2')
                    CODED_VALUES_Node = self.ODXG_AddNode(PARAM_Node, "CODED-VALUES", doc, '', '')
                    for nrc in udsService[6]: # 6-NRCs
                        self.ODXG_AddNode(CODED_VALUES_Node, "CODED-VALUE", doc, '', str(int(nrc.strip(),16)))
                    
                    DIAG_CODED_TYPE_Node = self.ODXG_AddNode(PARAM_Node, "DIAG-CODED-TYPE", doc, [('BASE-DATA-TYPE', "A_UINT32"), ('xsi:type', "STANDARD-LENGTH-TYPE")], '')
                    self.ODXG_AddNode(DIAG_CODED_TYPE_Node, "BIT-LENGTH", doc, '', '8')
    
    def odx_BASE_VARIANT_GLOBAL_NEG_RESPONSES(self, doc, parent):
        # Add GLOBAL-NEG-RESPONSES Node
        GLOBAL_NEG_RESPONSES_Node = self.ODXG_AddNode(parent, "GLOBAL-NEG-RESPONSES", doc, '', '')
        pass
    
    def odx_BASE_VARIANT_IMPORT_REFS(self, doc, parent):
        # Add IMPORT-REFS Node
        IMPORT_REFS_Node = self.ODXG_AddNode(parent, "IMPORT-REFS", doc, '', '')
        self.ODXG_AddNode(IMPORT_REFS_Node, "IMPORT-REF", doc, [('ID-REF', '__ECU_SHARED_DATA_Node')], '')
    
    def odx_BASE_VARIANT_COMPARAM_REFS(self, doc, parent):
        COMPARAM_REFS_Node = self.ODXG_AddNode(parent, "COMPARAM-REFS", doc, '', '')
        
        # self.UDSParameterlists: 0-name, 1-value, 2-ISOtype, 3-comment
        for i in range(0, len(self.UDSParameterlists) - 2):
            Attribute = [('ID-REF', (self.UDSParameterlists[i][2] + '_' + self.UDSParameterlists[i][0])), ('DOCREF', self.UDSParameterlists[i][2]), ('DOCTYPE', "COMPARAM-SUBSET")]
            COMPARAM_REF_Node = self.ODXG_AddNode(COMPARAM_REFS_Node, "COMPARAM-REF", doc, Attribute, '')
            self.ODXG_AddNode(COMPARAM_REF_Node, "SIMPLE-VALUE", doc, '', self.UDSParameterlists[i][1])
            DESC_Node = self.ODXG_AddNode(COMPARAM_REF_Node, "DESC", doc, '', '')
            self.ODXG_AddNode(DESC_Node, "p", doc, '', self.UDSParameterlists[i][3])
            self.ODXG_AddNode(COMPARAM_REF_Node, "PROTOCOL-SNREF", doc, [('SHORT-NAME', "DC")], '')
            
        Attribute = [('ID-REF', 'ISO_15765_2.CP_UniqueRespIdTable'), ('DOCREF', 'ISO_15765_2'), ('DOCTYPE', "COMPARAM-SUBSET")]
        COMPARAM_REF_Node = self.ODXG_AddNode(COMPARAM_REFS_Node, "COMPARAM-REF", doc, Attribute, '')
        COMPLEX_VALUE_Node = self.ODXG_AddNode(COMPARAM_REF_Node, "COMPLEX-VALUE", doc, '', '')
        self.ODXG_AddNode(COMPLEX_VALUE_Node, "SIMPLE-VALUE", doc, '', '0')
        self.ODXG_AddNode(COMPLEX_VALUE_Node, "SIMPLE-VALUE", doc, '', 'normal segmented 11-bit transmit with FC')
        self.ODXG_AddNode(COMPLEX_VALUE_Node, "SIMPLE-VALUE", doc, '', self.UDSParameterlists[len(self.UDSParameterlists)-2][1])
        self.ODXG_AddNode(COMPLEX_VALUE_Node, "SIMPLE-VALUE", doc, '', '0')
        self.ODXG_AddNode(COMPLEX_VALUE_Node, "SIMPLE-VALUE", doc, '', 'normal segmented 11-bit receive with FC')
        self.ODXG_AddNode(COMPLEX_VALUE_Node, "SIMPLE-VALUE", doc, '', self.UDSParameterlists[len(self.UDSParameterlists)-1][1])
        self.ODXG_AddNode(COMPLEX_VALUE_Node, "SIMPLE-VALUE", doc, '', '0')
        self.ODXG_AddNode(COMPLEX_VALUE_Node, "SIMPLE-VALUE", doc, '', 'normal unsegmented 11-bit receive')
        self.ODXG_AddNode(COMPLEX_VALUE_Node, "SIMPLE-VALUE", doc, '', '4294967295')
        self.ODXG_AddNode(COMPLEX_VALUE_Node, "SIMPLE-VALUE", doc, '', self.ECUName)
           
    def odx_BASE_VARIANT_PARENT_REFS(self, doc, parent):
        PARENT_REFS_Node = self.ODXG_AddNode(parent, "PARENT-REFS", doc, '', '')
        self.ODXG_AddNode(PARENT_REFS_Node, "PARENT-REF", doc, [('ID-REF','__PROTOCOL_ISO_15765_3_on_ISO_15765_2'), ('xsi:type','PROTOCOL-REF')], '')
    
    def odx_BASE_VARIANT(self, doc, parent):
        BASE_VARIANT_Node = self.ODXG_AddNode(parent, "BASE-VARIANT", doc, [('ID', 'ACU')], '')
        
        DESC_Node = self.ODXG_CreateElement("DESC", doc, '', '')
        
        # STATE_CHARTS_Node = self.ODXG_CreateElement("STATE-CHARTS", doc, '', '')
        
        self.ODXG_AddNode(BASE_VARIANT_Node, 'SHORT-NAME', doc, '', self.ECUName)
        self.ODXG_AddNode(BASE_VARIANT_Node, 'LONG-NAME', doc, '', self.ECUName)
        
        BASE_VARIANT_Node.appendChild(DESC_Node)
        self.ODXG_AddNode(DESC_Node, 'p', doc, '', 'Base model which all variants of the ECU must support.')
        
        self.odx_BASE_VARIANT_FUNCT_CLASSS(doc, BASE_VARIANT_Node) # Add FUNCT-CLASSS Node
        self.odx_BASE_VARIANT_DIAG_DATA_DICTIONARY_SPEC(doc, BASE_VARIANT_Node) # Add DIAG-DATA-DICTIONARY-SPEC Node
        self.odx_BASE_VARIANT_DIAG_COMMS(doc, BASE_VARIANT_Node) # Add DIAG-COMMS Node
        self.odx_BASE_VARIANT_REQUESTS(doc, BASE_VARIANT_Node) # Add REQUESTS Node
        self.odx_BASE_VARIANT_POS_RESPONSES(doc, BASE_VARIANT_Node) # Add POS-RESPONSES Node
        self.odx_BASE_VARIANT_NEG_RESPONSES(doc, BASE_VARIANT_Node) # Add NEG-RESPONSES Node
        # self.odx_BASE_VARIANT_GLOBAL_NEG_RESPONSES(doc, BASE_VARIANT_Node) # Add GLOBAL-NEG-RESPONSES Node
        self.odx_BASE_VARIANT_IMPORT_REFS(doc, BASE_VARIANT_Node) # Add IMPORT-REFS Node
        self.odx_BASE_VARIANT_COMPARAM_REFS(doc, BASE_VARIANT_Node) # Add COMPARAM-REFS Node
        self.odx_BASE_VARIANT_PARENT_REFS(doc, BASE_VARIANT_Node) # Add PARENT-REFS Node
        
    def ODXG_CreateODX(self):
        doc = xml.dom.minidom.Document()
        
        attribute = [('xsi:noNamespaceSchemaLocation', 'odx.xsd'), ("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance"), ("MODEL-VERSION", "2.2.0")]
        ODX_Node = self.ODXG_AddNode(doc, "ODX", doc, attribute, '')
        
        DIAG_LAYER_CONTAINER_Node = self.ODXG_AddNode(ODX_Node, "DIAG-LAYER-CONTAINER", doc, [("ID", "_NEVS_DIAG_LAYER_CONTAINER_NODE")], '')
        self.ODXG_AddNode(DIAG_LAYER_CONTAINER_Node, "SHORT-NAME", doc, '', self.ECUName)
        self.ODXG_AddNode(DIAG_LAYER_CONTAINER_Node, "LONG-NAME", doc, '', self.ECUName)
        self.ODXG_DESC(doc, DIAG_LAYER_CONTAINER_Node)
        self.ODXG_ADMIN_DATA(doc, DIAG_LAYER_CONTAINER_Node)
        # self.ODXG_COMPANY_DATAS(doc, DIAG_LAYER_CONTAINER_Node)
        self.ODXG_PROTOCOLS(doc, DIAG_LAYER_CONTAINER_Node)
        
        ECU_SHARED_DATAS_Node = self.ODXG_AddNode(DIAG_LAYER_CONTAINER_Node, "ECU-SHARED-DATAS", doc, '', '')
        BASE_VARIANTS_Node = self.ODXG_AddNode(DIAG_LAYER_CONTAINER_Node, "BASE-VARIANTS", doc, '', '')
  
        # Node ECU-SHARED-DATAS
        self.odx_ECU_SHARED_DATAS(doc, ECU_SHARED_DATAS_Node)
        
        # Node BASE-VARIANTS
        self.odx_BASE_VARIANT(doc, BASE_VARIANTS_Node)
        
        file_object = open("NEVS_TS_ACU_ODX.odx", "w")  
        file_object.write(doc.toprettyxml(indent = "\t", newl = "\n"))  
        file_object.close()
    
    def ODXG_MAIN(self):
        self.ODXG_ReadPartII()
        self.ODXG_CreateODX()

def main():
    ben = ODXGENERATE()
    ben.ODXG_MAIN()
    raw_input('OVER')

if __name__ == '__main__':
    main()
