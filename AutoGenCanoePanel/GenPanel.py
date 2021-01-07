# Actor: Yueting Ben
import xml.dom.minidom
import os
import wx
import wx.grid
from copy import deepcopy
import time
import getpass


ThisFilePath = os.getcwd()

class GEN_PANEL(wx.Frame):
    def __init__(self, dbcFile, customerName, panelName, panelVersion, mainNode):   
        # **************** Main Frame statement **************** start{
        mainFrameName = "Ben"
        mainFrameSizeX = 800
        mainFrameSizeY = 500
        # **************** Main Frame statement **************** end}
        # **************** Grid statement **************** start{
        # DisPlay column number
        global VIEW_COL_NUM
        global CONTROL_COL_NUM
        global LOCK_TRIGGER_COL_NUM
        global UNLOCK_TRIGGER_COL_NUM

        VIEW_COL_NUM = 0
        CONTROL_COL_NUM = 1
        LOCK_TRIGGER_COL_NUM = 2
        UNLOCK_TRIGGER_COL_NUM = 3
        
        self.MainNode = mainNode
        self.PanelName = panelName
        self.PanelVersion = panelVersion
        self.CustomerName = customerName
        
        self.AttrNameList = ["View", "Control", "LockTrigger", "UnLockTrigger"]
        # Grid column attributes
        # key: DisplayName, ColNum
        self.AttrNameDicList = \
        [\
        {"DisplayName": self.AttrNameList[VIEW_COL_NUM],             "ColNum": VIEW_COL_NUM},
        {"DisplayName": self.AttrNameList[CONTROL_COL_NUM],          "ColNum": CONTROL_COL_NUM},
        {"DisplayName": self.AttrNameList[LOCK_TRIGGER_COL_NUM],     "ColNum": LOCK_TRIGGER_COL_NUM},
        {"DisplayName": self.AttrNameList[UNLOCK_TRIGGER_COL_NUM],   "ColNum": UNLOCK_TRIGGER_COL_NUM}\
        ]
        
        self.DbcFileName = dbcFile
        # **************** Grid statement **************** end}
        
        # **************** Panel statement **************** start{
        global PANEL_ELEMENT_ROW_SIZE
        global PANEL_ELEMENT_GAP_SIZE
        global TAB_HEIGTH_SIZE
        global CHECKBOX_SIZE_X
        global CHECKBOX_SIZE_Y
        global PANEL_SIZE_X
        global PANEL_SIZE_Y
        global PANELTAB_SIZE_X
        global PANELTAB_SIZE_Y
        global PANELTAB_POS_X
        global PANELTAB_POS_Y
        global PANELVECTORTAB_SIZE_X
        global PANELVECTORTAB_SIZE_Y
        global NODETAB_FULLSIZE_X
        global NODETAB_HALFSIZE_X
        global NODETAB_SIZE_Y

        PANEL_ELEMENT_ROW_SIZE = 20
        PANEL_ELEMENT_GAP_SIZE = 5
        
        TAB_HEIGTH_SIZE = 350
        
        CHECKBOX_SIZE_X = '120'
        CHECKBOX_SIZE_Y = '20'

        # Panel Tab position (15, 40)
        PANELTAB_POS_X = '15'
        PANELTAB_POS_Y = '40'
        
        # Node groupBox size
        NODETAB_FULLSIZE_X = '706'
        NODETAB_HALFSIZE_X = '350'
        NODETAB_SIZE_Y = str(TAB_HEIGTH_SIZE + 3 * PANEL_ELEMENT_ROW_SIZE)
        
        # Panel Vector Tab size 700 * 400
        PANELVECTORTAB_SIZE_X = '720'
        PANELVECTORTAB_SIZE_Y = str(int(NODETAB_SIZE_Y) + PANEL_ELEMENT_GAP_SIZE)
        
        # Panel Tab size 720 * 400
        PANELTAB_SIZE_X = '720'
        PANELTAB_SIZE_Y = str(int(PANELVECTORTAB_SIZE_Y) + 8 * PANEL_ELEMENT_GAP_SIZE)
        
        # Panel size 750 * 463
        PANEL_SIZE_X = '750'
        PANEL_SIZE_Y = str(int(PANELTAB_SIZE_Y) + 10 * PANEL_ELEMENT_GAP_SIZE)
        
        # **************** Panel statement **************** end}
        self.NodeInfoArrayDict = {}
        self.DbcFileInfoDict = {}
        
        self.read_Dbc(dbcFile)
        self.set_SignalDisplay()

        # **************** MainFrame **************** start{
        self.MainFrame = wx.Frame(None, -1, mainFrameName, size=(mainFrameSizeX,mainFrameSizeY))
        
        # swindow = wx.SplitterWindow(frame, id=-1, size=(500,400))
        left = wx.Panel(self.MainFrame, size=(200, 500), pos = (0, 0))
        self.right = wx.Panel(self.MainFrame, size=(600, 500), pos = (220, 0))
        left.SetBackgroundColour("Yellow")
        
        # **************** Tree **************** start{
        self.tree = wx.TreeCtrl(left, size=(200, 450))
        root = self.tree.AddRoot('Messages', image=0)

        for node in self.NodeInfoArrayDict.keys():
            nodeNode = self.tree.AppendItem(root, node, 0)
            for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                messageNode = self.tree.AppendItem(nodeNode, message, 1)
                for signal in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                    signalNode = self.tree.AppendItem(messageNode, signal, 1) 
        
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGING, self.on_Click)
        self.TreeItemName = "Messages"
        # **************** Tree **************** end}
        
        viewSelectAllbutton = wx.Button(self.right, -1, "ALL", pos=(10 + 200 + 10, 10), size=(80, 20))
        viewSelectNonebutton = wx.Button(self.right, -1, "NONE", pos=(10 + 200 + 10, 30), size=(80, 20))
        
        viewGenerationbutton = wx.Button(self.right, -1, "GENERATION", pos=(10 + 200 + 10, 410), size=(300, 40))
        viewGenerationbutton.Bind(wx.EVT_BUTTON, self.on_ClickGeneration)
        # **************** Creat Grid **************** start{
        self.WxGrid = wx.grid.Grid(self.right, -1, pos=(10, 50), size=(550, 350))
        self.RowNums = 1
        self.WxGrid.CreateGrid(self.RowNums, len(self.AttrNameDicList))
        self.WxGrid.SetRowLabelAlignment(wx.ALIGN_LEFT, 0)
        self.WxGrid.SetColLabelAlignment(wx.ALIGN_LEFT, 0)
        
        for i in range(0, len(self.AttrNameDicList)):
            self.WxGrid.SetColLabelValue(self.AttrNameDicList[i]["ColNum"], self.AttrNameDicList[i]["DisplayName"])

        self.WxGrid.SetLabelBackgroundColour("white")
        self.WxGrid.SetRowLabelSize(150)
        self.WxGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_CellChanged)
        # **************** Creat Grid **************** end}
        # **************** MainFrame **************** end}
        '''
        file = open("haha.txt", 'w')
        for node in self.NodeInfoArrayDict.keys():
            file.write(node + " " + str(self.NodeInfoArrayDict[node]["NODE_LAYOUT"]["TOTALROWSIZE"]) + "\n")
            for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                file.write('    ' + message + " " + str(self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"]) + "\n")
                for signal in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                    file.write('        ' + signal + "\n")
        file.close()
        '''
        
    def creat_NodeLibrary(self, node):
        # Creat information for Node
        node = node.strip()

        nodeInfoDir = {}
        # CAN_Node structure
        nodeInfoDir["NODE_ATTR"] = {}
        nodeInfoDir["NODE_LAYOUT"] = {}
        nodeInfoDir["NODE_TX_MSGS"] = {}
        nodeInfoDir["NODE_RX_MSGS"] = {}
        # Fill the information to CAN_Node
        nodeInfoDir["NODE_ATTR"]["NAME"] = node
        nodeInfoDir["NODE_ATTR"]["DISPLAY"] = '1'
        if('' != node):
            self.NodeInfoArrayDict[node] = nodeInfoDir
                      
    def creat_MessageLibrary(self, messageArray):
        # Creat information for Message
        # signalArray example:[  0,     1,      2,        3,    4    ]
        #                     ['BO_', '697', 'VCU_8_A:', '8', 'VCU\n']
        messageInfoDir = {}
        
        # CAN_Message structure
        messageInfoDir["MSG_ATTR"] = {}
        messageInfoDir["MSG_LAYOUT"] = {}
        messageInfoDir["MSG_SIGS"] = {}
        # Fill the information to CAN_Message
        messageInfoDir["MSG_ATTR"]["NAME"] = messageArray[2][:-1]
        messageInfoDir["MSG_ATTR"]["ID"] = messageArray[1]
        messageInfoDir["MSG_ATTR"]["DLC"] = messageArray[3]
        messageInfoDir["MSG_ATTR"]["MSGENABLE"] = True
        messageInfoDir["MSG_ATTR"]["ROLLCOUNTER"] = False
        messageInfoDir["MSG_ATTR"]["CHECKSUM"] = False
        messageInfoDir["MSG_ATTR"]["DLC"] = messageArray[3]
        messageInfoDir["MSG_ATTR"]["CYCLE"] = "0"
        messageInfoDir["MSG_ATTR"]["DISPLAY"] = '1'
        messageInfoDir["MSG_ATTR"]["NODENAME"] = messageArray[4].strip()
        # self.NodeInfoDirArray

        self.NodeInfoArrayDict[messageInfoDir["MSG_ATTR"]["NODENAME"]]["NODE_TX_MSGS"][messageInfoDir["MSG_ATTR"]["NAME"]] = messageInfoDir
        node = messageInfoDir["MSG_ATTR"]["NODENAME"]
        message = messageInfoDir["MSG_ATTR"]["NAME"]
        if('' != message):
            return((node, message))

            
    def creat_SignalLibrary(self, nodeName, messageName, signalArray):
        # Creat information for Signal
        # signalArray example: [ 0 ,   1,         2,              3,      4,       5,       6,      7,   8,     9]
        #                    : ['', 'SG_', 'VCU_8_A_MsgCounter', ':', '31|4@0+', '(1,0)', '[0|15]', '""', '', 'TEL,VCU,BCS,WCM,PCS,ESCL,EPS,BSDM,ICM,AVNT,GWM\n']]        
        
        # CAN_Signal structure
        signalInfoDir = {}
        signalInfoDir["SIG_ATTR"] = {}
        # Fill the information to CAN_Message
        signalInfoDir["SIG_ATTR"]["NAME"] = signalArray[2]
        signalInfoDir["SIG_ATTR"]["STARTBIT"] = signalArray[4].split('|')[0]
        signalInfoDir["SIG_ATTR"]["LEN"] = signalArray[4].split('|')[1].split('@')[0]
        signalInfoDir["SIG_ATTR"]["BYTEPOS"] = signalArray[4].split('|')[1].split('@')[1][0]
        signalInfoDir["SIG_ATTR"]["VALUETYPE"] = signalArray[4].split('|')[1].split('@')[1][1]
        signalInfoDir["SIG_ATTR"]["FACTOR"] = signalArray[5].split(',')[0][1:]
        signalInfoDir["SIG_ATTR"]["OFFSET"] = signalArray[5].split(',')[1][0:-1]
        signalInfoDir["SIG_ATTR"]["MIN"] = signalArray[6].split('|')[0][1:]
        signalInfoDir["SIG_ATTR"]["MAX"] = signalArray[6].split('|')[1][0:-1]
        signalInfoDir["SIG_ATTR"]["MESSAGENAME"] = messageName
        signalInfoDir["SIG_ATTR"]["NODENAME"] = nodeName

        signalInfoDir["SIG_ATTR"][self.AttrNameList[LOCK_TRIGGER_COL_NUM]] = '0'
        signalInfoDir["SIG_ATTR"][self.AttrNameList[UNLOCK_TRIGGER_COL_NUM]] = '0'
        signalInfoDir["SIG_ATTR"]["DISPLAY"] = {}

        signalInfoDir["SIG_ATTR"][self.AttrNameList[VIEW_COL_NUM]] = '0'
        signalInfoDir["SIG_ATTR"][self.AttrNameList[CONTROL_COL_NUM]] = '1'
        signalInfoDir["SIG_ATTR"]["DISPLAY"][self.AttrNameList[LOCK_TRIGGER_COL_NUM]] = True
        signalInfoDir["SIG_ATTR"]["DISPLAY"][self.AttrNameList[UNLOCK_TRIGGER_COL_NUM]] = True
        
        self.NodeInfoArrayDict[signalInfoDir["SIG_ATTR"]["NODENAME"]]["NODE_TX_MSGS"][signalInfoDir["SIG_ATTR"]["MESSAGENAME"]]["MSG_SIGS"][signalInfoDir["SIG_ATTR"]["NAME"]] = signalInfoDir
    
    def set_SignalDisplay(self):
        for node in self.NodeInfoArrayDict.keys():
            for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                # Network frame cycle is 500ms
                if((0x400 <= int(self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["ID"])) and (0x4FF >= int(self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["ID"]))):
                    self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CYCLE"] = "500"
                    
                for signal in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                    if(self.MainNode == node):
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[VIEW_COL_NUM]] = True
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[CONTROL_COL_NUM]] = False
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[VIEW_COL_NUM]] = '1'
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[CONTROL_COL_NUM]] = '0'
                    else:
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[VIEW_COL_NUM]] = False
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[CONTROL_COL_NUM]] = True
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[VIEW_COL_NUM]] = '0'
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[CONTROL_COL_NUM]] = '1'
                    
                    if(0 == int(self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CYCLE"])):
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[VIEW_COL_NUM]] = False
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[CONTROL_COL_NUM]] = False
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[VIEW_COL_NUM]] = '0'
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[CONTROL_COL_NUM]] = '0'
                        
                    if(0x700 <= int(self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["ID"])):
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CYCLE"] = "0"
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[VIEW_COL_NUM]] = False
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[CONTROL_COL_NUM]] = False
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[VIEW_COL_NUM]] = '0'
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[CONTROL_COL_NUM]] = '0'
                        
    def read_Dbc(self, filePath):
        # Open the dbc file
        dbc_file = open(filePath)
        # Read out all the lines
        dbc_file_lines = dbc_file.readlines()
        self.DbcFileInfoDict["DBC_ATTR"] = {}
        self.DbcFileInfoDict["DBC_ATTR"]["NAME"] = self.CustomerName
        # check information from each line

        for lineNum in range(0, len(dbc_file_lines)):
            # Split each line with the symbol ' '
            lineStrArray = dbc_file_lines[lineNum].split(' ')
            
            # Node information
            if('BU_:' == lineStrArray[0].strip()):
                # Node name start from the 1st 
                for i in range(1, len(lineStrArray)):
                    self.creat_NodeLibrary(lineStrArray[i])

            elif('BO_' == lineStrArray[0].strip()):
                # BO_ 570 Suspension_Data_HS2: 8 GWM
                try:
                    (nodeName, messageName) = self.creat_MessageLibrary(lineStrArray)
                    childLine = 1
                    lineStrArray = dbc_file_lines[lineNum + childLine].split(' ')
                
                    while('SG_' in lineStrArray[1]):
                        lineStrArray = dbc_file_lines[lineNum + childLine].split(' ')
                        self.creat_SignalLibrary(nodeName, messageName, lineStrArray)
                        childLine = childLine + 1
                except:
                    pass
            
            elif('CM_' == lineStrArray[0].strip()):
                # Example: 0    1   2    3           4
                #          CM_ SG_ 85 PEPS_WALReq "PEPS walk away lock request";
                try:
                    for node in self.NodeInfoArrayDict.keys():
                        for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                            if(lineStrArray[2].strip() == self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["ID"]):
                                self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][lineStrArray[3].strip()]["SIG_ATTR"]["COMMENT"] = (" ".join(lineStrArray[4:]))[1:-1]
                except:
                    pass
            elif('BA_' == lineStrArray[0].strip()):
                try:
                    if("GenMsgCycleTime\"" in lineStrArray[1].strip()):
                        # Example 0             1        2   3   4
                        #         BA_ "GenMsgCycleTime" BO_ 697 10;      
                        for node in self.NodeInfoArrayDict.keys():
                            for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                                if(lineStrArray[3].strip() == self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["ID"]):
                                    self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CYCLE"] = lineStrArray[4].strip()[:-1]
                    
                    if("GenMsgSendType" in lineStrArray[1].strip()):
                        # Example 0             1        2   3   4
                        #         BA_ "GenMsgSendType" BO_  867  0;         
                        for node in self.NodeInfoArrayDict.keys():
                            for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                                if(lineStrArray[3].strip() == self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["ID"]):
                                    self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["SENDTYPE"] = lineStrArray[4].strip()[:-1]
                    
                    if("DBName" in lineStrArray[1].strip()):
                        # Example 0          1             2
                        #         BA_        "DBName"     "SK83_BD";
                        self.DbcFileInfoDict["DBC_ATTR"]["NAME"] = lineStrArray[2].strip().split("\"")[1]

                except:
                    pass
            
            elif('VAL_' == lineStrArray[0].strip() and 1 < len(lineStrArray)):
                # Example   0   1           2                   3       4      5    6        7
                #          VAL_ 867 ESCL_PromptRotateSteerWheel 1 "Steering column is blocked" 0 "Steering column is not blocked " ;
                valuetableDir = {}
                valuetableString = ' '.join(lineStrArray[3:-1])
                valuetableStringArray = valuetableString.split("\"")
                for i in range(0, (len(valuetableStringArray)-1), 2):
                    valuetableDir[str(valuetableStringArray[i])] = str(valuetableStringArray[1 + i])
                
                for node in self.NodeInfoArrayDict.keys():
                    for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                        for signal in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                            if(lineStrArray[2].strip() == signal):
                                self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["VALUETABLE"] = valuetableDir
                        
            else:
                pass
        
        # Close the dbc file
        dbc_file.close()
        
        # Check message if need ROLLCOUNTER and CHECKSUM
        for node in self.NodeInfoArrayDict.keys():
            for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                for signal in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                    if("counter".upper() in signal.upper()):
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["ROLLCOUNTER"] = True
                    if("sum".upper() in signal.upper()):
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CHECKSUM"] = True    
                  
    def xml_ObjectCreateElement(self, name, attributeList, txt):
        # CreateElement node
        node = self.doc.createElement(name)
        
        # Set attribute
        if('' != attributeList):
            for attribute in attributeList:
                node.setAttribute(attribute[0], attribute[1])
                
        # Write txt
        if('' != txt):
            txtNode = self.doc.createTextNode(txt)
            node.appendChild(txtNode)
        
        return(node)
    
    def xlm_NodeAdd(self, parent, name, attributeList, txt):
        node = self.xml_ObjectCreateElement(name, attributeList, txt)
        parent.appendChild(node)
        return(node)
                  
    def creat_PanelFile(self):
        self.doc = xml.dom.minidom.Document()
        attributeList  =[("Type", "Vector.CANalyzer.Panels.PanelSerializer, Vector.CANalyzer.Panels.Serializer, Version=9.0.86.0, Culture=neutral, PublicKeyToken=null")]
        Node_Panel = self.xlm_NodeAdd(self.doc, "Panel", attributeList, '')
        attributeList  =[("Type", "Vector.CANalyzer.Panels.Runtime.Panel, Vector.CANalyzer.Panels.Common, Version=9.0.86.0, Culture=neutral, PublicKeyToken=null"), ("Name", self.PanelName), ("ControlName", self.PanelName)]
        Node_PanelObject = self.xlm_NodeAdd(Node_Panel, "Object", attributeList, '')
        self.xlm_NodeAdd(Node_PanelObject, "Property", [("Name", "Name")], 'Panel')
        # The panel size 750 * 463,  conform to golden ratio 
        self.xlm_NodeAdd(Node_PanelObject, "Property", [("Name", "Size")], (PANEL_SIZE_X + ',' + PANEL_SIZE_Y))
        self.xlm_NodeAdd(Node_PanelObject, "Property", [("Name", "BackColor")], 'Crimson')
        
        commonControlTypeTxt = "Vector.CANalyzer.Panels.Design.ReplaceXXX, Vector.CANalyzer.Panels.CommonControls, Version=9.0.86.0, Culture=neutral, PublicKeyToken=null"
        
        # StaticText: Project name and version number
        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'StaticTextControl')
        attributeList  =[("Type", typeTxt), ("Name", 'StaticTextControl1'), ("Children", "Controls"), ("ControlName", "")]
        xlmNode_StaticTextControl = self.xlm_NodeAdd(Node_PanelObject, "Object", attributeList, '')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Name")], 'StaticTextControl1')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Size")], "200, 25")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Location")], "15, 10")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","BackColor")], "Crimson")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Font")], "Arial Narrow, 12pt, style=Bold")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Text")],  self.CustomerName + " "+  self.PanelName + " " + self.PanelVersion)
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","ForeColor")], "HighlightText")
        # StaticText: BCS Suzhou
        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'StaticTextControl')
        attributeList  =[("Type", typeTxt), ("Name", 'StaticTextControl2'), ("Children", "Controls"), ("ControlName", "")]
        xlmNode_StaticTextControl = self.xlm_NodeAdd(Node_PanelObject, "Object", attributeList, '')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Name")], 'StaticTextControl2')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Size")], "100, 25")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Location")], "650, 10")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","BackColor")], "Crimson")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Font")], "Arial Narrow, 12pt, style=Bold")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Text")], "BCS SuZhou")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","ForeColor")], "HighlightText")

        
        # Add the VectorTabControl
        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'VectorTabControl')
        attributeList  =[("Type", typeTxt), ("Name", "VectorTabControl"), ("ControlName", "panelName")]
        Node_VectorTabControl = self.xlm_NodeAdd(Node_PanelObject, "Object", attributeList, '')
        self.xlm_NodeAdd(Node_VectorTabControl, "Property", [("Name","Name")], 'VectorTabControl')
        self.xlm_NodeAdd(Node_VectorTabControl, "Property", [("Name","Size")], (PANELTAB_SIZE_X + ',' + PANELTAB_SIZE_Y))
        self.xlm_NodeAdd(Node_VectorTabControl, "Property", [("Name","Location")], (PANELTAB_POS_X + ',' + PANELTAB_POS_Y))
        self.xlm_NodeAdd(Node_VectorTabControl, "Property", [("Name","SymbolConfiguration")], 'SymbolConfiguration')
        self.xlm_NodeAdd(Node_VectorTabControl, "Property", [("Name","TabIndex")], '0')

        self.creat_PanelLayout(Node_VectorTabControl)
        # self.test(Node_VectorTabControl)
        
        file_object = open(ThisFilePath + '/TestPanel/Panel/' + self.PanelName + ".xvp", "w")  
        file_object.write(self.doc.toprettyxml(indent = "\t", newl = "\n"))  
        file_object.close()
    
    def cal_PanelNodeUsedSize(self):
        '''
        # Desc: Calculate Panel layout used row size
        # Param: None
        # Return: None
        # Author: Yueting Ben
        '''
        for node in self.NodeInfoArrayDict.keys():
            self.NodeInfoArrayDict[node]["NODE_LAYOUT"]["ACTIVE"] = False
            self.NodeInfoArrayDict[node]["NODE_LAYOUT"]["TOTALROWSIZE"] = 0
            if(0 < len(self.NodeInfoArrayDict[node]["NODE_TX_MSGS"])):
                self.NodeInfoArrayDict[node]["NODE_LAYOUT"]["ACTIVE"] = True
                # Node EnableAllMsg or DisableAllMsg
                self.NodeInfoArrayDict[node]["NODE_LAYOUT"]["TOTALROWSIZE"] = 2* (PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE)
                
                for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                    self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["ACTIVE"] = True
                    self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] = 0
                    # Message MeesageEnable
                    self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["VIEWROWSIZE"] = 0
                    self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["CONTROLROWSIZE"] = 0

                    if(True == self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["MSGENABLE"]):
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    if(True == self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["ROLLCOUNTER"]):
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    if(True == self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CHECKSUM"]):
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE

                    for signal in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                        if("1" == self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[VIEW_COL_NUM]]):
                            self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["VIEWROWSIZE"] = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["VIEWROWSIZE"] + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                        if("1" == self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[CONTROL_COL_NUM]]):
                            self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["CONTROLROWSIZE"] = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["CONTROLROWSIZE"] + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    
                    # Calculate the total row size for one message
                    self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] + \
                                                                                                    self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["VIEWROWSIZE"] + \
                                                                                                    self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["CONTROLROWSIZE"]
                    # If there are View or Control signals, message total row size should include gap
                    if(0 < self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["VIEWROWSIZE"]):
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] + PANEL_ELEMENT_GAP_SIZE
                    if(0 < self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["CONTROLROWSIZE"]):
                        self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"] + PANEL_ELEMENT_GAP_SIZE
            
                    self.NodeInfoArrayDict[node]["NODE_LAYOUT"]["TOTALROWSIZE"] = self.NodeInfoArrayDict[node]["NODE_LAYOUT"]["TOTALROWSIZE"] + self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_LAYOUT"]["TOTALROWSIZE"]
                    self.NodeInfoArrayDict[node]["NODE_LAYOUT"]["TOTALROWSIZE"] = self.NodeInfoArrayDict[node]["NODE_LAYOUT"]["TOTALROWSIZE"] + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
            else:
                # This is a null Node
                pass
                
    def filter_UsedNodeInfoArrayDict(self):
        '''
        # Desc: Filter used node dictionary
        # Param: None
        # Return: nodeInfoArrayDictUsed
        # Author: Yueting Ben
        '''
        nodeInfoArrayDictUsed = {}
        for node in self.NodeInfoArrayDict.keys():
            nodeInfoDir = deepcopy(self.NodeInfoArrayDict[node])
            nodeInfoDir["NODE_TX_MSGS"] = {}
            
            for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                messageInfoDir = deepcopy(self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message])
                messageInfoDir["MSG_SIGS"] = {}
                for signal in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                    for i in range(0, len(self.AttrNameList)):
                        if("1" == self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[i]]):
                            if(signal not in list(messageInfoDir["MSG_SIGS"].keys())):
                                messageInfoDir["MSG_SIGS"][signal] = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]
                                # nodeInfoArrayDictUsed[node] = self.NodeInfoArrayDict[node]
                
                if((0 != len(messageInfoDir["MSG_SIGS"] )) or (0 != int(messageInfoDir["MSG_ATTR"]["CYCLE"]))):
                    if(message not in list(nodeInfoDir["NODE_TX_MSGS"].keys())):
                        print(node + "  " + message + "  " + str(len(messageInfoDir["MSG_SIGS"] )) + "  " + messageInfoDir["MSG_ATTR"]["CYCLE"])
                        nodeInfoDir["NODE_TX_MSGS"][message] = messageInfoDir
            
            if(0 != len(nodeInfoDir["NODE_TX_MSGS"])):
                nodeInfoArrayDictUsed[node] = nodeInfoDir

        return(nodeInfoArrayDictUsed)
        
    def get_needDisplaiedSignalArrayDict(self, messageInfoArrayDir, message, attr):
        signalInfoArrayDir = {}
        for signal in messageInfoArrayDir[message]["MSG_SIGS"].keys():
            if(True == messageInfoArrayDir[message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[attr]]):
                signalInfoArrayDir[signal] = messageInfoArrayDir[message]["MSG_SIGS"][signal]
                    
        return(signalInfoArrayDir)

    def get_ifAllSignalDisplaied(self, messageInfoArrayDir, message):
        result = True
        for signal in messageInfoArrayDir[message]["MSG_SIGS"].keys():
            if((True == messageInfoArrayDir[message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[CONTROL_COL_NUM]]) or (True == messageInfoArrayDir[message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[VIEW_COL_NUM]])):
                result = False
                return(result)
                    
        return(result)

    def creat_PanelLayout(self, parent):
        commonControlTypeTxt = "Vector.CANalyzer.Panels.Design.ReplaceXXX, Vector.CANalyzer.Panels.CommonControls, Version=9.0.86.0, Culture=neutral, PublicKeyToken=null"
        # Action Tab page
        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'VectorTabPage')
        attributeList  =[("Type", typeTxt), ("Name", 'VectorTabPage'), ("Children", "Controls"), ("ControlName", "")]
        xlmNode_VectorTabPage = self.xlm_NodeAdd(parent, "Object", attributeList, '')
        self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Name")], 'VectorTabPage')
        self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Size")], (PANELVECTORTAB_SIZE_X + ',' + PANELVECTORTAB_SIZE_Y))
        self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Location")], '4, 22')
        self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Text")], "Action")

        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'ButtonControl')
        attributeList  =[("Type", typeTxt), ("Name", 'ButtonControl1'), ("Children", "Controls"), ("ControlName", "")]
        symbolConfigurationValue = "4;16;ACTION;;;Commands;1;;;-1"
        xlmNode_ButtonControl = self.xlm_NodeAdd(xlmNode_VectorTabPage, "Object", attributeList, '')
        self.xlm_NodeAdd(xlmNode_ButtonControl, "Property", [("Name","Name")], 'ButtonControl1')
        self.xlm_NodeAdd(xlmNode_ButtonControl, "Property", [("Name","Size")], "100, 25")
        self.xlm_NodeAdd(xlmNode_ButtonControl, "Property", [("Name","Location")], "30, 50")
        self.xlm_NodeAdd(xlmNode_ButtonControl, "Property", [("Name","Text")], "Lock")
        self.xlm_NodeAdd(xlmNode_ButtonControl, "Property", [("Name","SymbolConfiguration")], symbolConfigurationValue)
        
        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'ButtonControl')
        attributeList  =[("Type", typeTxt), ("Name", 'ButtonControl2'), ("Children", "Controls"), ("ControlName", "")]
        symbolConfigurationValue = "4;16;ACTION;;;Commands;2;;;-1"
        xlmNode_ButtonControl = self.xlm_NodeAdd(xlmNode_VectorTabPage, "Object", attributeList, '')
        self.xlm_NodeAdd(xlmNode_ButtonControl, "Property", [("Name","Name")], 'ButtonControl2')
        self.xlm_NodeAdd(xlmNode_ButtonControl, "Property", [("Name","Size")], "100, 25")
        self.xlm_NodeAdd(xlmNode_ButtonControl, "Property", [("Name","Location")], "150, 50")
        self.xlm_NodeAdd(xlmNode_ButtonControl, "Property", [("Name","PressValue")], "2")
        self.xlm_NodeAdd(xlmNode_ButtonControl, "Property", [("Name","Text")], "Unlock")
        self.xlm_NodeAdd(xlmNode_ButtonControl, "Property", [("Name","SymbolConfiguration")], symbolConfigurationValue)


        self.cal_PanelNodeUsedSize()
        # Get  used NodeInfoArrayDict
        nodeInfoArrayDictCopy = deepcopy(self.filter_UsedNodeInfoArrayDict())

        allFilledFlag = False
        newTabPageFlag = False
        # Creat the first message Tab
        tabPageCnt = 1
        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'VectorTabPage')
        attributeList  =[("Type", typeTxt), ("Name", 'VectorTabPage' + str(tabPageCnt)), ("Children", "Controls"), ("ControlName", "")]
        xlmNode_VectorTabPage = self.xlm_NodeAdd(parent, "Object", attributeList, '')
        self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Name")], 'VectorTabPage' + str(tabPageCnt))
        self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Size")], (PANELVECTORTAB_SIZE_X + ',' + PANELVECTORTAB_SIZE_Y))
        self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Location")], '4, 22')
        self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Text")], 'Msg-' + str(tabPageCnt))
        tabPageCnt = tabPageCnt + 1
        tabUsedCnt = 0
        
        elementNumberNode = 0
        elementNumberMessage = 0
        elementNumberSignal = 0
        
        while({} != nodeInfoArrayDictCopy):
            nodeList = list(nodeInfoArrayDictCopy.keys())
            node = nodeList[0]
            
            heightUsedValue = 0
            heightLimitValue = TAB_HEIGTH_SIZE
            
            nodeGroupBoxPosX = 5
            nodeGroupBoxPosY = 25
            
            if(True == newTabPageFlag):
                # Creat new Tab
                newTabPageFlag = False
                commonControlTypeTxt = "Vector.CANalyzer.Panels.Design.ReplaceXXX, Vector.CANalyzer.Panels.CommonControls, Version=9.0.86.0, Culture=neutral, PublicKeyToken=null"
                typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'VectorTabPage')
                attributeList  =[("Type", typeTxt), ("Name", 'VectorTabPage' + str(tabPageCnt)), ("Children", "Controls"), ("ControlName", "")]
                xlmNode_VectorTabPage = self.xlm_NodeAdd(parent, "Object", attributeList, '')
                self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Name")], 'VectorTabPage' + str(tabPageCnt))
                self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Size")], (PANELVECTORTAB_SIZE_X + ',' + PANELVECTORTAB_SIZE_Y))
                self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Location")], '4, 22')
                self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Text")], 'Msg-' + str(tabPageCnt))
                tabPageCnt = tabPageCnt + 1
            
            typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'GroupBoxControl')
            attributeList  =[("Type", typeTxt), ("Name", 'GroupBoxControl' + node.replace('_','') + str(elementNumberNode)), ("Children", "Controls"), ("ControlName", "")]
            xlmNode_VectorTabPage_GroupBoxControl = self.xlm_NodeAdd(xlmNode_VectorTabPage, "Object", attributeList, '')
            self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Property", [("Name","Name")], 'GroupBoxControl' + node.replace('_','') + str(elementNumberNode))
            self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Property", [("Name","Font")], 'Arial, 12pt, style=Bold')
            self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Property", [("Name","ForeColor")], 'ControlDarkDark')                    
            self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Property", [("Name","Text")], node)
            elementNumberNode = elementNumberNode + 1
            
            if(0 == (tabUsedCnt % 2)): 
                # This is new Tab, start from left half tab
                if(TAB_HEIGTH_SIZE < nodeInfoArrayDictCopy[node]["NODE_LAYOUT"]["TOTALROWSIZE"]):
                    self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Property", [("Name","Size")], (NODETAB_FULLSIZE_X + ',' + NODETAB_SIZE_Y))
                    self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Property", [("Name","Location")], '2, 5')
                    heightLimitValue = TAB_HEIGTH_SIZE * 2
                    tabUsedCnt = tabUsedCnt + 2
                else:
                    self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Property", [("Name","Size")], (NODETAB_HALFSIZE_X + ',' + NODETAB_SIZE_Y))
                    self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Property", [("Name","Location")], '2, 5')
                    heightLimitValue = TAB_HEIGTH_SIZE
                    tabUsedCnt = tabUsedCnt + 1
            else:
                # This is old Tab, start from right half tab
                self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Property", [("Name","Size")], (NODETAB_HALFSIZE_X + ',' + NODETAB_SIZE_Y))
                self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Property", [("Name","Location")], '358, 5')
                heightLimitValue = TAB_HEIGTH_SIZE
                tabUsedCnt = tabUsedCnt + 1
            
            # Node_MsgEnableCheckBoxControl    
            typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'CheckBoxControl')
            attributeList  =[("Type", typeTxt), ("Name", 'EnableAllMsg' + node.replace('_','') + str(elementNumberNode)), ("Children", "Controls"), ("ControlName", "")]
            
            xlmNode_MsgEnableCheckBoxControl = self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Object", attributeList, '')
            symbolConfigurationValue = "4;16;NODE;;;" + node + "EnableAll_Msg;1;;;-1"
            self.xlm_NodeAdd(xlmNode_MsgEnableCheckBoxControl, "Property", [("Name","Name")], 'EnableAllMsg' + node.replace('_','') + str(elementNumberNode))
            self.xlm_NodeAdd(xlmNode_MsgEnableCheckBoxControl, "Property", [("Name","Size")], CHECKBOX_SIZE_X + ',' + CHECKBOX_SIZE_Y)
            self.xlm_NodeAdd(xlmNode_MsgEnableCheckBoxControl, "Property", [("Name","Location")], '8, ' + str(nodeGroupBoxPosY))
            self.xlm_NodeAdd(xlmNode_MsgEnableCheckBoxControl, "Property", [("Name","Text")], "EnableAll_Msg")
            self.xlm_NodeAdd(xlmNode_MsgEnableCheckBoxControl, "Property", [("Name","BackColor")], 'White') 
            self.xlm_NodeAdd(xlmNode_MsgEnableCheckBoxControl, "Property", [("Name","SymbolConfiguration")], symbolConfigurationValue)
            elementNumberNode = elementNumberNode + 1
            # Node_MsgDisEnableCheckBoxControl
            attributeList  =[("Type", typeTxt), ("Name", 'DisableAllMsg' + node.replace('_','') + str(elementNumberNode)), ("Children", "Controls"), ("ControlName", "")]
            xlmNode_MsgDisEnableCheckBoxControl = self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Object", attributeList, '')
            symbolConfigurationValue = "4;16;NODE;;;" + node + "DisableAll_Msg;1;;;-1"
            self.xlm_NodeAdd(xlmNode_MsgDisEnableCheckBoxControl, "Property", [("Name","Name")], 'DisableAllMsg' + node.replace('_','') + str(elementNumberNode))
            self.xlm_NodeAdd(xlmNode_MsgDisEnableCheckBoxControl, "Property", [("Name","Size")], CHECKBOX_SIZE_X + ',' + CHECKBOX_SIZE_Y)
            self.xlm_NodeAdd(xlmNode_MsgDisEnableCheckBoxControl, "Property", [("Name","Location")], '128, ' + str(nodeGroupBoxPosY))
            self.xlm_NodeAdd(xlmNode_MsgDisEnableCheckBoxControl, "Property", [("Name","Text")], "DisableAll_Msg")
            self.xlm_NodeAdd(xlmNode_MsgDisEnableCheckBoxControl, "Property", [("Name","BackColor")], 'White') 
            self.xlm_NodeAdd(xlmNode_MsgDisEnableCheckBoxControl, "Property", [("Name","SymbolConfiguration")], symbolConfigurationValue)
            elementNumberNode = elementNumberNode + 1
            heightUsedValue = heightUsedValue + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
            nodeGroupBoxPosY = nodeGroupBoxPosY + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
            
            messageInfoArrayDirCopy = deepcopy(nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"])
            while(heightUsedValue <= heightLimitValue and 0 < len(messageInfoArrayDirCopy)):
                messageList = list(messageInfoArrayDirCopy.keys())
                message = messageList[0]
                messageSize = 0
                
                messageGroupBoxPosX = 5
                messageGroupBoxPosY = 30
                messageSize = messageSize + messageGroupBoxPosY
                
                # If need to generate CheckBoxControl MessageEnable, MsgCounterEnable and ChecksumEnable
                messageAttrHeightTemp = 0
                if(True == messageInfoArrayDirCopy[message]["MSG_ATTR"]["MSGENABLE"]):
                    messageAttrHeightTemp = messageAttrHeightTemp + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                if(True == messageInfoArrayDirCopy[message]["MSG_ATTR"]["ROLLCOUNTER"]):
                    messageAttrHeightTemp = messageAttrHeightTemp + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                if(True == messageInfoArrayDirCopy[message]["MSG_ATTR"]["CHECKSUM"]):
                    messageAttrHeightTemp = messageAttrHeightTemp + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                
                # Change to right Tab page              
                if(nodeGroupBoxPosY + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE >= TAB_HEIGTH_SIZE - messageAttrHeightTemp and 5 == nodeGroupBoxPosX and TAB_HEIGTH_SIZE * 2 == heightLimitValue):
                    nodeGroupBoxPosX = 355
                    nodeGroupBoxPosY = 50
                    heightUsedValue = heightUsedValue + nodeGroupBoxPosY
                    nodeInfoArrayDictCopy[node]["NODE_LAYOUT"]["TOTALROWSIZE"] = nodeInfoArrayDictCopy[node]["NODE_LAYOUT"]["TOTALROWSIZE"] + 50
                    
                typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'GroupBoxControl')
                attributeList  =[("Type", typeTxt), ("Name", 'GroupBoxControl' + message.replace('_','') + str(elementNumberNode)), ("Children", "Controls"), ("ControlName", "")]
                xlmNode_MessageGroupBoxControl = self.xlm_NodeAdd(xlmNode_VectorTabPage_GroupBoxControl, "Object", attributeList, '') 
                self.xlm_NodeAdd(xlmNode_MessageGroupBoxControl, "Property", [("Name","Location")], str(nodeGroupBoxPosX) + ', ' + str(nodeGroupBoxPosY))

                if(True == messageInfoArrayDirCopy[message]["MSG_ATTR"]["MSGENABLE"]):
                    typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'CheckBoxControl')
                    attributeList  =[("Type", typeTxt), ("Name", 'MessageEnable' + message.replace('_','') + str(elementNumberMessage)), ("Children", "Controls"), ("ControlName", "")]
                    xlmNode_Message_CheckBoxControl = self.xlm_NodeAdd(xlmNode_MessageGroupBoxControl, "Object", attributeList, '')
                    symbolConfigurationValue = "4;16;MESSAGEFRAME;;;" + message + "MessageEnable;1;;;-1"
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","Name")], 'MessageEnable' + message.replace('_','') + str(elementNumberMessage))
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","Size")], CHECKBOX_SIZE_X + ',' + CHECKBOX_SIZE_Y)
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","Location")],  str(messageGroupBoxPosX) + ', ' + str(messageGroupBoxPosY)) 
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","Text")], 'MessageEnable')
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","SymbolConfiguration")], symbolConfigurationValue)
                    elementNumberMessage = elementNumberMessage + 1
                    # heightUsedValue = heightUsedValue + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    messageGroupBoxPosY = messageGroupBoxPosY + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    messageSize = messageSize + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    messageInfoArrayDirCopy[message]["MSG_ATTR"]["MSGENABLE"] = False

                if(True == messageInfoArrayDirCopy[message]["MSG_ATTR"]["ROLLCOUNTER"]):
                    typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'CheckBoxControl')
                    attributeList  =[("Type", typeTxt), ("Name", 'MsgCounterEnable' + message.replace('_','') + str(elementNumberMessage)), ("Children", "Controls"), ("ControlName", "")]
                    xlmNode_Message_CheckBoxControl = self.xlm_NodeAdd(xlmNode_MessageGroupBoxControl, "Object", attributeList, '')
                    symbolConfigurationValue = "4;16;MESSAGEFRAME;;;" + message + "MsgCounterEnable;1;;;-1"
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","Name")], 'MsgCounterEnable' + message.replace('_','') + str(elementNumberMessage))
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","Size")], CHECKBOX_SIZE_X + ',' + CHECKBOX_SIZE_Y)
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","Location")],  str(messageGroupBoxPosX) + ', ' + str(messageGroupBoxPosY)) 
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","Text")], 'MsgCounterEnable')
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","SymbolConfiguration")], symbolConfigurationValue)
                    elementNumberMessage = elementNumberMessage + 1
                    # heightUsedValue = heightUsedValue + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    messageGroupBoxPosY = messageGroupBoxPosY + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    messageSize = messageSize + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    messageInfoArrayDirCopy[message]["MSG_ATTR"]["ROLLCOUNTER"] = False
                    
                if(True == messageInfoArrayDirCopy[message]["MSG_ATTR"]["CHECKSUM"]):
                    typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'CheckBoxControl')
                    attributeList  =[("Type", typeTxt), ("Name", 'CheckSumEnable' + message.replace('_','') + str(elementNumberMessage)), ("Children", "Controls"), ("ControlName", "")]
                    xlmNode_Message_CheckBoxControl = self.xlm_NodeAdd(xlmNode_MessageGroupBoxControl, "Object", attributeList, '')
                    symbolConfigurationValue = "4;16;MESSAGEFRAME;;;" + message + "CheckSumEnable;1;;;-1"
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","Name")], 'CheckSumEnable' + message.replace('_','') + str(elementNumberMessage))
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","Size")], CHECKBOX_SIZE_X + ',' + CHECKBOX_SIZE_Y)
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","Location")],  str(messageGroupBoxPosX) + ', ' + str(messageGroupBoxPosY)) 
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","Text")], 'CheckSumEnable')
                    self.xlm_NodeAdd(xlmNode_Message_CheckBoxControl, "Property", [("Name","SymbolConfiguration")], symbolConfigurationValue)
                    elementNumberMessage = elementNumberMessage + 1
                    # heightUsedValue = heightUsedValue + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    messageGroupBoxPosY = messageGroupBoxPosY + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    messageSize = messageSize + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                    messageInfoArrayDirCopy[message]["MSG_ATTR"]["CHECKSUM"] = False
                
                signalGroupBoxControlX = 0
                signalGroupBoxControlY = 20
                signalGroupBoxViewY = 20
                # signalInfoArrayDirControlCopy = deepcopy(messageInfoArrayDirCopy[message]["MSG_SIGS"])
                signalInfoArrayDirControlCopy = deepcopy(self.get_needDisplaiedSignalArrayDict(messageInfoArrayDirCopy, message, CONTROL_COL_NUM))
                signalInfoArrayDirViewCopy = {}
                if(0 == len(signalInfoArrayDirControlCopy)):
                    signalInfoArrayDirViewCopy = deepcopy(self.get_needDisplaiedSignalArrayDict(messageInfoArrayDirCopy, message, VIEW_COL_NUM))

                if({} != signalInfoArrayDirControlCopy):
                    if(((nodeGroupBoxPosY + messageGroupBoxPosY + 2*(PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE)) < TAB_HEIGTH_SIZE) and 0 < len(signalInfoArrayDirControlCopy)):
                        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'GroupBoxControl')
                        attributeList  =[("Type", typeTxt), ("Name", 'MessageControl' + message.replace('_','') + str(elementNumberMessage)), ("Children", "Controls"), ("ControlName", "")]
                        xlmNode_MessageSubGroupBoxControl = self.xlm_NodeAdd(xlmNode_MessageGroupBoxControl, "Object", attributeList, '')
                        self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxControl, "Property", [("Name","Location")],  '0 , ' + str(messageGroupBoxPosY)) 
                        # print(signalInfoArrayDirControlCopy)
                        while((nodeGroupBoxPosY + messageGroupBoxPosY + signalGroupBoxControlY + PANEL_ELEMENT_ROW_SIZE) <= TAB_HEIGTH_SIZE and 0 < len(signalInfoArrayDirControlCopy)):
                            signalList = list(signalInfoArrayDirControlCopy.keys())
                            signal = signalList[0]

                            if('1' == messageInfoArrayDirCopy[message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[CONTROL_COL_NUM]]):
                                try:
                                    if('' != messageInfoArrayDirCopy[message]["MSG_SIGS"][signal]["SIG_ATTR"]["VALUETABLE"]):
                                        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'ComboBoxControl')
                                        attributeList  =[("Type", typeTxt), ("Name", 'ComboBoxControl' + str(elementNumberSignal)), ("Children", "Controls"), ("ControlName", "")]
                                        xlmNode_SignalComboBoxControl1 = self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxControl, "Object", attributeList, '')
                                        symbolConfigurationValue = "4;16;SIGNALINFO;;;" + signal + "Value;1;;;-1"   
                                        self.xlm_NodeAdd(xlmNode_SignalComboBoxControl1, "Property", [("Name","Size")], '300, 20')
                                        self.xlm_NodeAdd(xlmNode_SignalComboBoxControl1, "Property", [("Name","Location")],  '10 , ' + str(signalGroupBoxControlY))
                                        self.xlm_NodeAdd(xlmNode_SignalComboBoxControl1, "Property", [("Name","DropDownWidth")], '115')  
                                        self.xlm_NodeAdd(xlmNode_SignalComboBoxControl1, "Property", [("Name","BackColor")], 'Window') 
                                        self.xlm_NodeAdd(xlmNode_SignalComboBoxControl1, "Property", [("Name","ForeColor")], 'WindowText')
                                        self.xlm_NodeAdd(xlmNode_SignalComboBoxControl1, "Property", [("Name","TextBackColor")], 'White')
                                        self.xlm_NodeAdd(xlmNode_SignalComboBoxControl1, "Property", [("Name","DisplayLabel")], 'Left')
                                        self.xlm_NodeAdd(xlmNode_SignalComboBoxControl1, "Property", [("Name","DescriptionText")], signal)
                                        self.xlm_NodeAdd(xlmNode_SignalComboBoxControl1, "Property", [("Name","DescriptionSize")], '150, 20')
                                        self.xlm_NodeAdd(xlmNode_SignalComboBoxControl1, "Property", [("Name","SymbolConfiguration")], symbolConfigurationValue)
                                        self.xlm_NodeAdd(xlmNode_SignalComboBoxControl1, "Property", [("Name","TabIndex")], '4')
                                        elementNumberSignal = elementNumberSignal + 1
                                
                                except:
                                    # <Property Name="SymbolConfiguration">4;2;SK83_BD;ESCL;ESCL_5E5h;ESCL_Auth_BCM_Resp;1;CAN;;-1</Property>
                                    # symbolConfigurationValue = "4;2;" + self.DbcFileInfoDict["DBC_ATTR"]["NAME"] + ";" + node + ";" + message + ";" + signal + ";1;CAN;;-1"
                                    typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'TextBoxControl')
                                    attributeList  =[("Type", typeTxt), ("Name", 'TextBoxControl' + str(elementNumberSignal)), ("Children", "Controls"), ("ControlName", "")]
                                    xlmNode_SignalTextBoxControl = self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxControl, "Object", attributeList, '')
                                    symbolConfigurationValue = "4;16;SIGNALINFO;;;" + signal + "Value;1;;;-1"   
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","Name")], 'TextBoxControl')
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","Size")], '300, 20')
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","Location")],  '10 , ' + str(signalGroupBoxControlY)) 
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","AlarmUpperTextColor")], 'WindowText')
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","ValueDecimalPlaces")], '0')
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","AlarmLowerBkgColor")], 'Salmon')
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","TextBackColor")], 'White')
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","ValueDisplay")], 'Symbolic')
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","AlarmUpperBkgColor")], 'IndianRed')
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","AlarmLowerTextColor")], 'WindowText')
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","AlarmGeneralSettings")], '1;0;0;100')
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","DisplayLabel")], 'Left')             
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","DescriptionText")], signal)
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","DescriptionSize")], '150, 20')
                                    self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","SymbolConfiguration")], symbolConfigurationValue)
                                    elementNumberSignal = elementNumberSignal + 1
                                
                                signalGroupBoxControlY = signalGroupBoxControlY + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                                heightUsedValue = heightUsedValue + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                                
                            signalInfoArrayDirControlCopy[signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[CONTROL_COL_NUM]] = False
                            messageInfoArrayDirCopy[message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[CONTROL_COL_NUM]] = False

                            signalInfoArrayDirControlCopy = deepcopy(self.get_needDisplaiedSignalArrayDict(messageInfoArrayDirCopy, message, CONTROL_COL_NUM))
                            if(0 == len(signalInfoArrayDirControlCopy)):
                                signalInfoArrayDirViewCopy = deepcopy(self.get_needDisplaiedSignalArrayDict(messageInfoArrayDirCopy, message, VIEW_COL_NUM))
                                nodeInfoArrayDictCopy[node]["NODE_LAYOUT"]["TOTALROWSIZE"] = nodeInfoArrayDictCopy[node]["NODE_LAYOUT"]["TOTALROWSIZE"] + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE

                        signalGroupBoxControlY = signalGroupBoxControlY + PANEL_ELEMENT_GAP_SIZE        
                        self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxControl, "Property", [("Name","Name")], 'MessageControl' + message.replace('_','') + str(elementNumberMessage))
                        self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxControl, "Property", [("Name","Size")], '340, ' + str(signalGroupBoxControlY))
                        self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxControl, "Property", [("Name","Text")], 'Control')
                        self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxControl, "Property", [("Name","BackColor")], 'White')
                        elementNumberMessage = elementNumberMessage + 1
                
                if(signalGroupBoxControlY > 20):
                    messageSize = messageSize + signalGroupBoxControlY
                    messageGroupBoxPosY = messageGroupBoxPosY + signalGroupBoxControlY
                    
                if({} == signalInfoArrayDirControlCopy and {} != signalInfoArrayDirViewCopy):
                    if(((nodeGroupBoxPosY + messageGroupBoxPosY + 2*(PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE)) < TAB_HEIGTH_SIZE) and 0 < len(signalInfoArrayDirViewCopy)):
                        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'GroupBoxControl')
                        attributeList  =[("Type", typeTxt), ("Name", 'MessageView' + message.replace('_','') + str(elementNumberMessage)), ("Children", "Controls"), ("ControlName", "")]
                        xlmNode_MessageSubGroupBoxView = self.xlm_NodeAdd(xlmNode_MessageGroupBoxControl, "Object", attributeList, '')
                        self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxView, "Property", [("Name","Location")],  '0 , ' + str(messageGroupBoxPosY)) 
                        while((nodeGroupBoxPosY + messageGroupBoxPosY + signalGroupBoxViewY + PANEL_ELEMENT_ROW_SIZE) <= TAB_HEIGTH_SIZE and 0 < len(signalInfoArrayDirViewCopy)):
                            signalList = list(signalInfoArrayDirViewCopy.keys())
                            signal = signalList[0]
                            if('1' == messageInfoArrayDirCopy[message]["MSG_SIGS"][signal]["SIG_ATTR"][self.AttrNameList[VIEW_COL_NUM]]):
                                # <Property Name="SymbolConfiguration">4;2;SK83_BD;ESCL;ESCL_5E5h;ESCL_Auth_BCM_Resp;1;CAN;;-1</Property>
                                symbolConfigurationValue = "4;2;" + self.DbcFileInfoDict["DBC_ATTR"]["NAME"] + ";" + node + ";" + message + ";" + signal + ";1;CAN;;-1"
                                typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'TextBoxControl')
                                attributeList  =[("Type", typeTxt), ("Name", 'TextBoxControl' + str(elementNumberSignal)), ("Children", "Controls"), ("ControlName", "")]
                                xlmNode_SignalTextBoxControl = self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxView, "Object", attributeList, '')
                                # symbolConfigurationValue = "4;16;SIGNALINFO;;;" + signal + "Value;1;;;-1"   
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","Name")], 'TextBoxControl')
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","Size")], '300, 20')
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","Location")],  '10 , ' + str(signalGroupBoxViewY)) 
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","AlarmUpperTextColor")], 'WindowText')
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","ValueDecimalPlaces")], '0')
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","AlarmLowerBkgColor")], 'Salmon')
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","TextBackColor")], 'White')
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","ValueDisplay")], 'Symbolic')
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","AlarmUpperBkgColor")], 'IndianRed')
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","AlarmLowerTextColor")], 'WindowText')
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","AlarmGeneralSettings")], '1;0;0;100')
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","DisplayLabel")], 'Left')             
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","DescriptionText")], signal)
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","DescriptionSize")], '150, 20')
                                self.xlm_NodeAdd(xlmNode_SignalTextBoxControl, "Property", [("Name","SymbolConfiguration")], symbolConfigurationValue)
                                elementNumberSignal = elementNumberSignal + 1
                            
                                signalGroupBoxViewY = signalGroupBoxViewY + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                                heightUsedValue = heightUsedValue + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE

                            signalInfoArrayDirViewCopy[signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[VIEW_COL_NUM]] = False
                            messageInfoArrayDirCopy[message]["MSG_SIGS"][signal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[VIEW_COL_NUM]] = False
                            signalInfoArrayDirViewCopy = deepcopy(self.get_needDisplaiedSignalArrayDict(messageInfoArrayDirCopy, message, VIEW_COL_NUM))
                             
                        signalGroupBoxViewY = signalGroupBoxViewY + PANEL_ELEMENT_GAP_SIZE        
                        self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxView, "Property", [("Name","Name")], 'MessageView' + message.replace('_','') + str(elementNumberMessage))
                        self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxView, "Property", [("Name","Size")], '340, ' + str(signalGroupBoxViewY))
                        self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxView, "Property", [("Name","Text")], 'View')
                        self.xlm_NodeAdd(xlmNode_MessageSubGroupBoxView, "Property", [("Name","BackColor")], 'White')
                        elementNumberMessage = elementNumberMessage + 1
                
                if(signalGroupBoxViewY > 20):
                    messageSize = messageSize + signalGroupBoxViewY
                    messageGroupBoxPosY = messageGroupBoxPosY + signalGroupBoxViewY
                    
                self.xlm_NodeAdd(xlmNode_MessageGroupBoxControl, "Property", [("Name","Name")], message.replace('_','') + str(elementNumberNode))
                self.xlm_NodeAdd(xlmNode_MessageGroupBoxControl, "Property", [("Name","Size")], '340, ' + str(messageSize))
                self.xlm_NodeAdd(xlmNode_MessageGroupBoxControl, "Property", [("Name","BackColor")], 'White')    
                self.xlm_NodeAdd(xlmNode_MessageGroupBoxControl, "Property", [("Name","Font")], 'Arial Narrow, 9.75pt')                        
                self.xlm_NodeAdd(xlmNode_MessageGroupBoxControl, "Property", [("Name","Text")], message + '   0x' + str(hex(int(messageInfoArrayDirCopy[message]["MSG_ATTR"]["ID"])))[2:].upper())
                elementNumberNode = elementNumberNode + 1
                nodeGroupBoxPosY = nodeGroupBoxPosY + messageSize + PANEL_ELEMENT_GAP_SIZE
                heightUsedValue = heightUsedValue + messageSize + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                
                if(True == self.get_ifAllSignalDisplaied(messageInfoArrayDirCopy, message)):
                    messageInfoArrayDirCopy.pop(message)

                nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"] = deepcopy(messageInfoArrayDirCopy)  

            # Minus the alreay used row vale   
            nodeInfoArrayDictCopy[node]["NODE_LAYOUT"]["TOTALROWSIZE"] = nodeInfoArrayDictCopy[node]["NODE_LAYOUT"]["TOTALROWSIZE"] - heightUsedValue
            if(0 >= len(nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"])):
                nodeInfoArrayDictCopy.pop(node)
            else:
                # This node remain information should put in next Tab, should add the PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE for new header(EnableAllMsg and DisableAllMsg)
                nodeInfoArrayDictCopy[node]["NODE_LAYOUT"]["TOTALROWSIZE"] = nodeInfoArrayDictCopy[node]["NODE_LAYOUT"]["TOTALROWSIZE"] + PANEL_ELEMENT_ROW_SIZE + PANEL_ELEMENT_GAP_SIZE
                
            if(0 == (tabUsedCnt % 2)):
                newTabPageFlag = True
        
        # Help Tab page
        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'VectorTabPage')
        attributeList  =[("Type", typeTxt), ("Name", 'VectorTabPageHelp'), ("Children", "Controls"), ("ControlName", "")]
        xlmNode_VectorTabPage = self.xlm_NodeAdd(parent, "Object", attributeList, '')
        self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Name")], 'VectorTabPageHelp')
        self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Size")], (PANELVECTORTAB_SIZE_X + ',' + PANELVECTORTAB_SIZE_Y))
        self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Location")], '4, 22')
        self.xlm_NodeAdd(xlmNode_VectorTabPage, "Property", [("Name","Text")], "Help")
        # Project information
        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'StaticTextControl')
        attributeList  =[("Type", typeTxt), ("Name", 'StaticTextControlGeneral01'), ("Children", "Controls"), ("ControlName", "")]
        xlmNode_StaticTextControl = self.xlm_NodeAdd(xlmNode_VectorTabPage, "Object", attributeList, '')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Name")], 'StaticTextControlGeneral01')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Size")], "200, 20")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Location")], "15, 15")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","BackColor")], "White")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Font")], "Arial, 12pt, style=Bold")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Text")],  self.CustomerName + " " + self.PanelName + " " + self.PanelVersion)
        
        # General_Information
        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'StaticTextControl')
        attributeList  =[("Type", typeTxt), ("Name", 'StaticTextControlGeneral02'), ("Children", "Controls"), ("ControlName", "")]
        xlmNode_StaticTextControl = self.xlm_NodeAdd(xlmNode_VectorTabPage, "Object", attributeList, '')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Name")], 'StaticTextControlGeneral02')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Size")], "200, 20")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Location")], "15, 45")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","BackColor")], "White")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Font")], "Arial, 10pt, style=Bold")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Text")],  "General Information")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","ForeColor")], "Crimson")
        
        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'StaticTextControl')
        attributeList  =[("Type", typeTxt), ("Name", 'StaticTextControlGeneral03'), ("Children", "Controls"), ("ControlName", "")]
        xlmNode_StaticTextControl = self.xlm_NodeAdd(xlmNode_VectorTabPage, "Object", attributeList, '')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Name")], 'StaticTextControlGeneral03')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Size")], "200, 50")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Location")], "15, 65")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","BackColor")], "White")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Font")], "Arial Narrow, 9pt")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Text")],  "Generation time: " + time.strftime("%d/%m/%Y") + " " + time.strftime("%H:%M:%S") + '\n' \
                                                                                    + 'User: ' + getpass.getuser() + "\n"\
                                                                                    + 'Dbc: ' + self.DbcFileName + "\n")
        # Support
        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'StaticTextControl')
        attributeList  =[("Type", typeTxt), ("Name", 'StaticTextControlGeneral04'), ("Children", "Controls"), ("ControlName", "")]
        xlmNode_StaticTextControl = self.xlm_NodeAdd(xlmNode_VectorTabPage, "Object", attributeList, '')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Name")], 'StaticTextControlGeneral04')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Size")], "200, 20")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Location")], "15, 125")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","BackColor")], "White")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Font")], "Arial, 10pt, style=Bold")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Text")],  "Support")
        typeTxt = commonControlTypeTxt.replace('ReplaceXXX', 'StaticTextControl')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","ForeColor")], "Crimson")
        
        attributeList  =[("Type", typeTxt), ("Name", 'StaticTextControlGeneral05'), ("Children", "Controls"), ("ControlName", "")]
        xlmNode_StaticTextControl = self.xlm_NodeAdd(xlmNode_VectorTabPage, "Object", attributeList, '')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Name")], 'StaticTextControlGeneral05')
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Size")], "200, 50")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Location")], "15, 145")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","BackColor")], "White")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Font")], "Arial Narrow, 9pt")
        self.xlm_NodeAdd(xlmNode_StaticTextControl, "Property", [("Name","Text")],  "Author: Yueting Ben" + '\nEmail: Yueting.Ben@bcs-ais.com')
        
    def creat_VsysvarFile(self):
        '''
        # Desc: creat vsysvar file
        # Param: None
        # Return: None
        # Author: Yueting Ben
        '''
        self.doc = xml.dom.minidom.Document()
        
        attributeList  =[("systemvariables", "4")]
        Node_Panel = self.xlm_NodeAdd(self.doc, "systemvariables", attributeList, '')
        attributeList  =[("name", ""), ("comment", ""), ("interface", "")]
        namespace_PanelObject = self.xlm_NodeAdd(Node_Panel, "namespace", attributeList, '')
        
        # Action
        attributeList = [("name", "ACTION"), ("comment", ""), ("interface", "")]
        action_PanelObject = self.xlm_NodeAdd(namespace_PanelObject, "namespace", attributeList, '')
        # Action commands
        startValue = 1
        minValue = 0
        maxValue = 1
        attributeList = [("anlyzLocal", "0"), ("readOnly", "false"), ("valueSequence", "false"), ("unit", ""), ("name", 'Commands'), ("comment", ""), ("bitcount", "32"), ("isSigned", "true"), ("encoding", "65001"), ("type", "int"), ("startValue", str(startValue)), ("minValue", str(minValue)), ("minValuePhys", str(minValue)), ("maxValue", str(maxValue)), ("maxValuePhys", str(maxValue))]
        actionCommands_PanelObject = self.xlm_NodeAdd(action_PanelObject, "variable", attributeList, '')
        commandsTableNode = self.xlm_NodeAdd(actionCommands_PanelObject, "valuetable", [("definesMinMax", "true")], '')
        self.xlm_NodeAdd(commandsTableNode, "valuetableentry", [("value", "1"), ("description", "Lock")], '')
        self.xlm_NodeAdd(commandsTableNode, "valuetableentry", [("value", "2"), ("description", "Unlock")], '')
            
        # Node
        attributeList = [("name", "NODE"), ("comment", ""), ("interface", "")]
        nodes_PanelObject = self.xlm_NodeAdd(namespace_PanelObject, "namespace", attributeList, '')
        
        for node in self.NodeInfoArrayDict.keys():
            startValue = 1
            minValue = 0
            maxValue = 2
            attributeList = [("anlyzLocal", "0"), ("readOnly", "false"), ("valueSequence", "false"), ("unit", ""), ("name", node + 'EnableAll_Msg'), ("comment", ""), ("bitcount", "32"), ("isSigned", "true"), ("encoding", "65001"), ("type", "int"), ("startValue", str(startValue)), ("minValue", str(minValue)), ("minValuePhys", str(minValue)), ("maxValue", str(maxValue)), ("maxValuePhys", str(maxValue))]
            self.xlm_NodeAdd(nodes_PanelObject, "variable", attributeList, '')
            startValue = 0
            minValue = 0
            maxValue = 1
            attributeList = [("anlyzLocal", "0"), ("readOnly", "false"), ("valueSequence", "false"), ("unit", ""), ("name", node + 'DisableAll_Msg'), ("comment", ""), ("bitcount", "32"), ("isSigned", "true"), ("encoding", "65001"), ("type", "int"), ("startValue", str(startValue)), ("minValue", str(minValue)), ("minValuePhys", str(minValue)), ("maxValue", str(maxValue))]
            self.xlm_NodeAdd(nodes_PanelObject, "variable", attributeList, '')
        
        # Message
        attributeList = [("name", "MESSAGEFRAME"), ("comment", ""), ("interface", "")]
        messages_PanelObject = self.xlm_NodeAdd(namespace_PanelObject, "namespace", attributeList, '')
        # Signal
        attributeList = [("name", "SIGNALINFO"), ("comment", ""), ("interface", "")]
        signals_PanelObject = self.xlm_NodeAdd(namespace_PanelObject, "namespace", attributeList, '')
        
        for node in self.NodeInfoArrayDict.keys():
            for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                startValue = 1
                minValue = 0
                maxValue = 1
                attributeList = [("anlyzLocal", "0"), ("readOnly", "false"), ("valueSequence", "false"), ("unit", ""), ("name", message + "MessageEnable"), ("comment", ""), ("bitcount", "32"), ("isSigned", "true"), ("encoding", "65001"), ("type", "int"), ("startValue", str(startValue)), ("minValue", str(minValue)), ("minValuePhys", str(minValue)), ("maxValue", str(maxValue))]
                self.xlm_NodeAdd(messages_PanelObject, "variable", attributeList, '')
                startValue = 1
                minValue = 0
                maxValue = 1
                attributeList = [("anlyzLocal", "0"), ("readOnly", "false"), ("valueSequence", "false"), ("unit", ""), ("name", message + "MsgCounterEnable"), ("comment", ""), ("bitcount", "32"), ("isSigned", "true"), ("encoding", "65001"), ("type", "int"), ("startValue", str(startValue)), ("minValue", str(minValue)), ("minValuePhys", str(minValue)), ("maxValue", str(maxValue))]
                self.xlm_NodeAdd(messages_PanelObject, "variable", attributeList, '')    
                startValue = 1
                minValue = 0
                maxValue = 1
                attributeList = [("anlyzLocal", "0"), ("readOnly", "false"), ("valueSequence", "false"), ("unit", ""), ("name", message + "CheckSumEnable"), ("comment", ""), ("bitcount", "32"), ("isSigned", "true"), ("encoding", "65001"), ("type", "int"), ("startValue", str(startValue)), ("minValue", str(minValue)), ("minValuePhys", str(minValue)), ("maxValue", str(maxValue))]
                self.xlm_NodeAdd(messages_PanelObject, "variable", attributeList, '')
                try:
                    startValue = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CYCLE"]
                except:
                    startValue = 0
                minValue = 10
                maxValue = 100000
                attributeList = [("anlyzLocal", "0"), ("readOnly", "false"), ("valueSequence", "false"), ("unit", ""), ("name", message + "Period"), ("comment", ""), ("bitcount", "32"), ("isSigned", "true"), ("encoding", "65001"), ("type", "int"), ("startValue", str(startValue)), ("minValue", str(minValue)), ("minValuePhys", str(minValue)), ("maxValue", str(maxValue))]
                self.xlm_NodeAdd(messages_PanelObject, "variable", attributeList, '')    

                for signal in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                    startValue = 0
                    minValue = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["MIN"]
                    maxValue = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["MAX"]
                    typeValue = "int"
                    bitcount = 32
                    if('.' in minValue):
                        minValue = 0
                    if('.' in maxValue):
                        maxValue = 2 ** (int(self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["LEN"])) - 1
                    attributeList = [("anlyzLocal", "0"), ("readOnly", "false"), ("valueSequence", "false"), ("unit", ""), ("name", signal + 'Value'), ("comment", ""), ("bitcount", str(bitcount)), ("isSigned", "true"), ("encoding", "65001"), ("type", typeValue), ("startValue", str(startValue)), ("minValue", str(minValue)), ("minValuePhys", str(minValue)), ("maxValue", str(maxValue))]
                    if(int(self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["LEN"]) > 32):
                        typeValue = "longlong"
                        bitcount = 64
                        attributeList = [("anlyzLocal", "0"), ("readOnly", "false"), ("valueSequence", "false"), ("unit", ""), ("name", signal + 'Value'), ("comment", ""), ("bitcount", str(bitcount)), ("isSigned", "false"), ("encoding", "65001"), ("type", typeValue), ("startValue", str(startValue))]
                    
                    Signal_PanelObject = self.xlm_NodeAdd(signals_PanelObject, "variable", attributeList, '')
                    
                    # If the signal has ValueTable?
                    try:
                        if('' != self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["VALUETABLE"]):
                            valuetableNode = self.xlm_NodeAdd(Signal_PanelObject, "valuetable", [("definesMinMax", "true")], '')
                            valuetableDir = self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal]["SIG_ATTR"]["VALUETABLE"]
                            for key in valuetableDir:
                                self.xlm_NodeAdd(valuetableNode, "valuetableentry", [("value", key.strip()), ("description", valuetableDir[key])], '')
                    except:
                        pass
                    
        file_object = open(ThisFilePath + '/TestPanel/Sysvar/' + "vsysvar.vsysvar", "w")  
        file_object.write(self.doc.toprettyxml(indent = "\t", newl = "\n"))  
        file_object.close()
    
    def creat_CaplFile(self):
        '''
        # Desc: creat CAPL file
        # Param: None
        # Return: None
        # Author: Yueting Ben
        '''
        # Get  used NodeInfoArrayDict
        nodeInfoArrayDictCopy = deepcopy(self.filter_UsedNodeInfoArrayDict())
        # Creat folder
        # Folder struct
        # ..\CAPL
        # ....+NODE_A
        # ......+NODE_A.can
        # ....+NODE_B
        # ......+NODE_B.can
        # ....+NODE_C
        
        # Basic path for CAPL
        fileHeadInfoStr = \
'''/*MMMMMMMMMMMMNNNNNMMMMMMMMMMMMMMMMMMMMMMMMMMMNNNNNMMMMMMMMMMMMMMMMMMMMMMMMMMMNNNNNNMMMMMMMMMMMMM*/
/*M+NMMMNdyso+////++oyhmNMMMMMMMMMMMMMMMNmhso++////+oshmNMMMMMMMMMMMMMMMNmhyo++////+osydNNNNMNNNM*/
/*M+NMMd///+osyyyyss+///+smNMMMMMMMMMNds+///osyyyyyso////sdNMMMMMMMMMNmy+///+osyyyyso+///ohNNNNNM*/
/*M+NNMdohmNNMNNNNNNNNdy+//odNMMMMNNh+//+ymNNNNNNNNNNNmy+//+hNNNNNNNdo//+sdNNNNNNNNNNNmho//+yNNNM*/
/*M+NNNNNNNmhysooosydNNNNh+//yNNNNms//+dNNNNdysooosydNNNNdo//omNNNNy//+hNNNNdysooooyhmNNNms//+dNM*/
/*M+NNNNNdo//////////+ymNNmo//smmdo//sNNNms///////////sdmmdo//+dmms//omNNNy+//////////odmmms//+dM*/
/*M+mNNNy//////////////+mNNm+///////oNNNd+//////////////////////////+mNNm+/////////////////////oM*/
/*M+mNNd////////////////sNNNmdddhhhhmNNm+////////////////hhhhhhhhhhhdNNNmhhhhhhhhhhhhhhhhhhhh///M*/
/*M+mNNd////////////////oNNNNNNNNNNNNNNm+////////////////dNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNm+//M*/
/*M/hNNmo///////////////hNNNs///////yNNNy///////////////////////////////////////////////omNNh//+M*/
/*M/+dNNms////////////+hNNNy//+sss///hNNmy/////////////ssss+///sss+///ssss+////////////smNNd+//yM*/
/*M//+hmNNmyo+/////+shmNNms//+dNNNh+//ymNNmho+/////+ohmNNmy///hNNNd+//odNNmhs+//////oymNNmh+//ymM*/
/*Mh+//+ymNNNmmmdmmNNNmds///smNNNNNdo//+ydmNNNmmdmmmNNmdy+//odNNNNNms///sdmNNNmmdmmmNNNmy+//+hmNM*/
/*Mmmho///+syhdddddhyo+///sdmNNNNNNNmho///+syhdddddhys+///ohmNNNNNNNNds+//+oyhdddddhys+///ohmNNNM*/
/*Mmmmmdyo+///////////oshmmmNmmmmmmNNmmmhs+///////////+shmmNNNNNNNNNNNNmhso///////////+oydmNNmmmM*/
/*MmmmmmmmmmdhyyyyhddmmmmmmmmmmmmmmmmmmmmmmmddhyyyhddmmmmmmmmmmmmmmmmmmmmmmmddhyyyyhdmmmmmmmmmmmM*/
/*MMMMMMMMMMMMNNNNNMMMMMMMMMMMMMMMMMMMMMMMMMMMNNNNNMMMMMMMMMMMMMMMMMMMMMMMMMMMNNNNNNMMMMMMMMMMMMM*

  filename:     Filename_Replace
  
  description:  Brief: Brief_Replace
                Generation date: GenerationDate_Replace
                DBC File: DbcFile_Replace
                User Name: UserName_Replace
                
  ATTENTIONS:   This file code generated by Tool automatically, don't modify this 
                file manually.  
 ----------------------------------------------------------------------------- */
/* -----------------------------------------------------------------------------
  C O P Y R I G H T
 -------------------------------------------------------------------------------
  Copyright (c) 2019 by Yueting Ben. All rights reserved.
 -------------------------------------------------------------------------------
/**************************************************************************************************/
 '''
        onTimerCommentsStr = \
'''/**************************************************************************************************/
/*
  brief:        onTimerCommentsBrief_Replace
  
  author:       Generation tool
*/
/**************************************************************************************************/
 '''
 
        onSysvarCommentsStr = \
'''/**************************************************************************************************/
/*
  brief:        onSysvarCommentsBrief_Replace
  
  author:       Generation tool
*/
/**************************************************************************************************/
 '''
        basicPath = ThisFilePath + "\TestPanel\CAPL"
        for node in nodeInfoArrayDictCopy.keys():
            nodeFolderPath = basicPath + '\\' + node
            if (False == os.path.exists(nodeFolderPath)):
                os.makedirs(nodeFolderPath)

            # Creat CAPL file
            caplFilePath = nodeFolderPath + '\\' + node + '.can'
            caplFile = open(caplFilePath, 'w')
            # CAPL file head information
            fileHeadInfoStrTemp = fileHeadInfoStr.replace("Filename_Replace", node + '.can')
            fileHeadInfoStrTemp = fileHeadInfoStrTemp.replace("Brief_Replace", node)
            fileHeadInfoStrTemp = fileHeadInfoStrTemp.replace("GenerationDate_Replace", time.strftime("%d/%m/%Y") + " " + time.strftime("%H:%M:%S"))
            fileHeadInfoStrTemp = fileHeadInfoStrTemp.replace("DbcFile_Replace", self.DbcFileName)
            fileHeadInfoStrTemp = fileHeadInfoStrTemp.replace("UserName_Replace", getpass.getuser())
            caplFile.write(fileHeadInfoStrTemp)
            # CAPL variables
            caplFile.write("variables\n")
            # CAPL variables {
            caplFile.write("{\n")

            for message in nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"].keys():
                # Define message
                caplFile.write("  message " + message + ' ' + message + '_Frame;' + '\n')

            for message in nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"].keys():   
                # Define message timer
                caplFile.write("  msTimer " + message + '_Timer;' + '\n')

            for message in nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"].keys():
                # Define message enable flag
                caplFile.write("  byte " + message + '_EnableFlag;' + '\n')
                if(True == nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["ROLLCOUNTER"]):
                    caplFile.write("  byte " + message + '_MsgCounterEnable;' + '\n')
                if(True == nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CHECKSUM"]):
                    caplFile.write("  byte " + message + '_CheckSumEnable;' + '\n')
            # CAPL variables }
            caplFile.write("}\n")
            
            # CAPL on start
            caplFile.write("on start\n")
            # CAPL on start {
            caplFile.write("{\n")

            for message in nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"].keys():
                caplFile.write("  setTimer(" + message + "_Timer, " + str(0) + ");\n")

            for message in nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"].keys():
                caplFile.write("  " + message + "_EnableFlag = " + "@sysvar::MESSAGEFRAME::" + message + "MessageEnable & @sysvar::NODE::" + node + "EnableAll_Msg" + ";\n")
                if(True == nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["ROLLCOUNTER"]):
                    caplFile.write("  " + message + "_MsgCounterEnable = " + "@sysvar::MESSAGEFRAME::" + message + "MsgCounterEnable;\n")
                if(True == nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CHECKSUM"]):
                    caplFile.write("  " + message + "_CheckSumEnable = " + "@sysvar::MESSAGEFRAME::" + message + "CheckSumEnable;\n")
            # CAPL on start }
            caplFile.write("}\n\n")
            
            # CAPL on Timer
            for message in nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"].keys():
                onTimerCommentsStrTemp = onTimerCommentsStr.replace("onTimerCommentsBrief_Replace", "Send " + message + " in cycle")
                caplFile.write(onTimerCommentsStrTemp)
                caplFile.write("on Timer " + message + '_Timer' + '\n')
                # CAPL on Timer }
                caplFile.write("{\n")
                
                # Define messageName_MegCounter and messageName_CheckSum
                if(True == nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["ROLLCOUNTER"]):
                    caplFile.write("  byte " + message + '_MsgCounter;' + '\n')
                if(True == nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CHECKSUM"]):
                    caplFile.write("  byte " + message + '_CheckSum;' + '\n')
                
                # Send out message
                caplFile.write("  if(1 == " + message + "_EnableFlag)" + '\n')
                
                caplFile.write("  {\n")
                caplFile.write("    output(" + message + "_Frame);\n")
                caplFile.write("  }\n")
                    
                for signal in nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                    if("COUNTER" in signal.upper()):
                        caplFile.write("  if(1 == " + message + "_MsgCounterEnable)" + '\n')
                        caplFile.write("  {\n")
                    if("SUM" in signal.upper()):
                        # CheckSum
                        if(True == nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CHECKSUM"]):
                            caplFile.write("  /* Calculate checksum */ \n")
                            caplFile.write("  " + message + "_CheckSum = " + message + "_Frame.byte(0)\n" )
                            caplFile.write("                          ^ " + message + "_Frame.byte(1)\n" )
                            caplFile.write("                          ^ " + message + "_Frame.byte(2)\n" )
                            caplFile.write("                          ^ " + message + "_Frame.byte(3)\n" )
                            caplFile.write("                          ^ " + message + "_Frame.byte(4)\n" )
                            caplFile.write("                          ^ " + message + "_Frame.byte(5)\n" )
                            caplFile.write("                          ^ " + message + "_Frame.byte(6);\n" )
                            # caplFile.write("  " + message + "_CheckSum = 0xFF - " + message + "_CheckSum;\n")
                        
                        caplFile.write("  if(1 == " + message + "_CheckSumEnable)" + '\n')
                        caplFile.write("  {\n")
                        
                    if(("COUNTER" in signal.upper()) or ("SUM" in signal.upper())):
                        if("COUNTER" in signal.upper()):
                            caplFile.write("    @sysvar::SIGNALINFO::" + signal + "Value = " + message + "_MsgCounter;\n")
                        if("SUM" in signal.upper()):
                            caplFile.write("    @sysvar::SIGNALINFO::" + signal + "Value = " + message + "_CheckSum;\n")
                        caplFile.write("    " + message + '_Frame.' + signal + " = @sysvar::SIGNALINFO::" + signal + "Value;\n")
                        if("COUNTER" in signal.upper()):
                            caplFile.write("    " + message + "_MsgCounter = " + message + "_MsgCounter + 1;\n" )
                    else:
                        caplFile.write("  " + message + '_Frame.' + signal + " = @sysvar::SIGNALINFO::" + signal + "Value;\n")
                    
                    if("COUNTER" in signal.upper()):
                        caplFile.write("  }\n")
                    if("SUM" in signal.upper()):
                        caplFile.write("  }\n")
                try:
                    caplFile.write("  setTimer(" + message + "_Timer, " + str(nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CYCLE"]) + ");\n")
                except:
                    caplFile.write("  setTimer(" + message + "_Timer, " + str(0) + ");\n")
   
                # CAPL on Timer }
                caplFile.write("}\n\n")
            
            # CAPL on sysvar xxx_Node_EnableAll_Msg
            onSysvarCommentsStrTemp = onSysvarCommentsStr.replace("onSysvarCommentsBrief_Replace", "Check the CheckBox " + node + "_EnableAll_Msg")
            caplFile.write(onSysvarCommentsStrTemp)
            caplFile.write("on sysvar " + "NODE::" + node + "EnableAll_Msg" + '\n')
            # CAPL on sysvar {
            caplFile.write("{\n")
            caplFile.write("  if(1 == @sysvar::NODE::" + node + "EnableAll_Msg)" + "\n")
            # if {
            caplFile.write("  {\n")
            caplFile.write("    @sysvar::NODE::" + node + "EnableAll_Msg = 1" + ";\n")
            caplFile.write("    @sysvar::NODE::" + node + "DisableAll_Msg = 0" + ";\n")

            for message in nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"].keys():
                caplFile.write("    @sysvar::MESSAGEFRAME::" + message + "MessageEnable = 1" + ";\n")
                caplFile.write("    " + message + "_EnableFlag = " + "@sysvar::MESSAGEFRAME::" + message + "MessageEnable & @sysvar::NODE::" + node + "EnableAll_Msg" + ";\n")
            # end of if }
            caplFile.write("  }\n")
            caplFile.write("  else" + "\n")
            # if {
            caplFile.write("  {\n")
            caplFile.write("    @sysvar::NODE::" + node + "EnableAll_Msg = 0" + ";\n")
            caplFile.write("    @sysvar::NODE::" + node + "DisableAll_Msg = 1" + ";\n")

            for message in nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"].keys():
                caplFile.write("    @sysvar::MESSAGEFRAME::" + message + "MessageEnable = 0" + ";\n")
                caplFile.write("    " + message + "_EnableFlag = " + "@sysvar::MESSAGEFRAME::" + message + "MessageEnable & @sysvar::NODE::" + node + "EnableAll_Msg" + ";\n")
            # end of if }
            caplFile.write("  }\n")
            # CAPL on sysvar }
            caplFile.write("}\n\n")
            
            # CAPL on sysvar xxx_Node_DisableAll_Msg
            onSysvarCommentsStrTemp = onSysvarCommentsStr.replace("onSysvarCommentsBrief_Replace", "Check the CheckBox " + node + "_DisableAll_Msg")
            caplFile.write(onSysvarCommentsStrTemp)
            caplFile.write("on sysvar " + "NODE::" + node + "DisableAll_Msg" + '\n')
            # CAPL on sysvar {
            caplFile.write("{\n")
            caplFile.write("  if(1 == @sysvar::NODE::" + node + "DisableAll_Msg)" + "\n")
            # if {
            caplFile.write("  {\n")
            caplFile.write("    @sysvar::NODE::" + node + "EnableAll_Msg = 0" + ";\n")
            caplFile.write("    @sysvar::NODE::" + node + "DisableAll_Msg = 1" + ";\n")

            for message in nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"].keys():
                caplFile.write("    @sysvar::MESSAGEFRAME::" + message + "MessageEnable = 0" + ";\n")
                caplFile.write("    " + message + "_EnableFlag = " + "@sysvar::MESSAGEFRAME::" + message + "MessageEnable & @sysvar::NODE::" + node + "EnableAll_Msg" + ";\n")
            # end of if }
            caplFile.write("  }\n")
            caplFile.write("  else" + "\n")
            # if {
            caplFile.write("  {\n")
            caplFile.write("    @sysvar::NODE::" + node + "EnableAll_Msg = 1" + ";\n")
            caplFile.write("    @sysvar::NODE::" + node + "DisableAll_Msg = 0" + ";\n")

            for message in nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"].keys():
                caplFile.write("    @sysvar::MESSAGEFRAME::" + message + "MessageEnable = 1" + ";\n")
                caplFile.write("    " + message + "_EnableFlag = " + "@sysvar::MESSAGEFRAME::" + message + "MessageEnable & @sysvar::NODE::" + node + "EnableAll_Msg" + ";\n")
            # end of if }
            caplFile.write("  }\n")
            # CAPL on sysvar }
            caplFile.write("}\n\n")

            for message in nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"].keys():
                # CAPL on sysvar xxx_MessageEnable
                onSysvarCommentsStrTemp = onSysvarCommentsStr.replace("onSysvarCommentsBrief_Replace", "Check the CheckBox " + message + " MessageEnable")
                caplFile.write(onSysvarCommentsStrTemp)
                caplFile.write("on sysvar " + "MESSAGEFRAME::" + message + "MessageEnable" + '\n')
                # CAPL on sysvar {
                caplFile.write("{\n")
                caplFile.write("  " + message + "_EnableFlag = " + "@sysvar::MESSAGEFRAME::" + message + "MessageEnable & @sysvar::NODE::" + node + "EnableAll_Msg" + ";\n")  
                # CAPL on sysvar }
                caplFile.write("}\n\n")
                
                # CAPL on sysvar xxx_MessageCounterEnable
                if(True == nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["ROLLCOUNTER"]):
                    onSysvarCommentsStrTemp = onSysvarCommentsStr.replace("onSysvarCommentsBrief_Replace", "Check the CheckBox " + message + " MsgCounterEnable")
                    caplFile.write(onSysvarCommentsStrTemp)
                    caplFile.write("on sysvar " + "MESSAGEFRAME::" + message + "MsgCounterEnable" + '\n')
                    # CAPL on sysvar {
                    caplFile.write("{\n")
                    caplFile.write("  " + message + "_MsgCounterEnable = " + "@sysvar::MESSAGEFRAME::" + message + "MsgCounterEnable;\n")  
                    # CAPL on sysvar }
                    caplFile.write("}\n\n")
                    
                # CAPL on sysvar xxx_MessageCheckSumEnable
                if(True == nodeInfoArrayDictCopy[node]["NODE_TX_MSGS"][message]["MSG_ATTR"]["CHECKSUM"]):
                    onSysvarCommentsStrTemp = onSysvarCommentsStr.replace("onSysvarCommentsBrief_Replace", "Check the CheckBox " + message + " CheckSumEnable")
                    caplFile.write(onSysvarCommentsStrTemp)
                    caplFile.write("on sysvar " + "MESSAGEFRAME::" + message + "CheckSumEnable" + '\n')
                    # CAPL on sysvar {
                    caplFile.write("{\n")
                    caplFile.write("  " + message + "_CheckSumEnable = " + "@sysvar::MESSAGEFRAME::" + message + "CheckSumEnable;\n")  
                    # CAPL on sysvar }
                    caplFile.write("}\n\n")
                    
            caplFile.close()
        
    def set_SignalsAttrValue(self, treeName, row, attr, value):
        '''
        # Desc: set_SignalsAttrValue
        # Param: treeName, row, attr, value
        # Return: (nodeName, messageName)
        # Author: Yueting Ben
        '''    
        cnt = 0
        signalGroup = "Messages"
        startPositionNode = ""
        startPositionMessage = ""
        startPositionSignal = ""
        if("Messages" != treeName):
            for node in self.NodeInfoArrayDict.keys():
                if(node == treeName):
                    signalGroup = "NODE"
                    startPositionNode = node
                    break
                for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():  
                    if(message == treeName):
                        signalGroup = "MESSAGE"
                        startPositionNode = node
                        startPositionMessage = message
                        break
                        for signal in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                            if(signal == treeName):
                                signalGroup = "SIGNAL"
                                startPositionNode = node
                                startPositionMessage = message
                                startPositionSignal = signal
                                break      
        cnt = 0
        if("Messages" == signalGroup):
            for node in self.NodeInfoArrayDict.keys():
                for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():  
                    for signal in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                        if(row == cnt):
                            startPositionNode = node
                            startPositionMessage = message
                            startPositionSignal = signal
                        cnt = cnt + 1
                        
        elif("NODE" == signalGroup):
            for message in self.NodeInfoArrayDict[startPositionNode]["NODE_TX_MSGS"].keys():  
                for signal in self.NodeInfoArrayDict[startPositionNode]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                    if(row == cnt):
                        startPositionMessage = message
                        startPositionSignal = signal
                    cnt = cnt + 1
                    
        elif("MESSAGE" == signalGroup):
            for signal in self.NodeInfoArrayDict[startPositionNode]["NODE_TX_MSGS"][startPositionMessage]["MSG_SIGS"].keys():
                if(row == cnt):
                    startPositionSignal = signal
                cnt = cnt + 1          
        else:
            pass
            
        self.NodeInfoArrayDict[startPositionNode]["NODE_TX_MSGS"][startPositionMessage]["MSG_SIGS"][startPositionSignal]["SIG_ATTR"][self.AttrNameList[attr]] = value
        if("1" == value):
            self.NodeInfoArrayDict[startPositionNode]["NODE_TX_MSGS"][startPositionMessage]["MSG_SIGS"][startPositionSignal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[attr]] = True
        else:
            self.NodeInfoArrayDict[startPositionNode]["NODE_TX_MSGS"][startPositionMessage]["MSG_SIGS"][startPositionSignal]["SIG_ATTR"]["DISPLAY"][self.AttrNameList[attr]] = False
            
    def search_NodeName(self, name):
        '''
        # Desc: Seach the nodeName and messageName
        # Param: message name or signal name
        # Return: (nodeName, messageName)
        # Author: Yueting Ben
        '''
        nodeName = None
        messageName = None
        for node in self.NodeInfoArrayDict.keys():
            for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                if(message == name):
                    nodeName = node
                    messageName = message 
                for signal in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                    if(signal == name):
                        nodeName = node
                        messageName = message 
                        
        return((nodeName, messageName))                
    
    def get_SignalsList(self, treename):
        '''
        # Desc: Get the signal dictionary need to be display in Tree list
        # Return: Signal name list should be displayed in TreeList
        # Author: Yueting Ben
        '''
        signalsList = []
        collectFlagStart = False
        collectFlagEnd = True
        
        if("Messages" == treename):
            collectFlagStart = True
            
        for node in self.NodeInfoArrayDict.keys():
            if(node == treename):
                collectFlagStart = True
            for message in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"].keys():
                if(message == treename):
                    collectFlagStart = True     
                for signal in self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"].keys():
                    if(signal == treename):
                        collectFlagStart = True   
                    if(True == collectFlagStart and True == collectFlagEnd):
                        # signalsList.append(self.NodeInfoArrayDict[node]["NODE_TX_MSGS"][message]["MSG_SIGS"][signal])
                        signalsList.append(signal)
                    if(signal == treename):
                        collectFlagEnd = False
                if(message == treename):
                    collectFlagEnd = False 
            if(node == treename):
                collectFlagEnd = False 
        
        return(signalsList)        
                
    def on_Click(self, event):
        self.TreeItemNameOld = self.TreeItemName
        item = event.GetItem()
        self.TreeItemName = self.tree.GetItemText(item)

        signalsList = self.get_SignalsList(self.TreeItemName)

        if(self.RowNums > 0):
            try:
                self.WxGrid.DeleteRows(pos=0, numRows=self.RowNums, updateLabels = True)
            except:
                pass
        self.RowNums = len(signalsList)
        self.WxGrid.AppendRows(self.RowNums)
        
        # Grid attribute
        attr = wx.grid.GridCellAttr()
        attr.SetEditor(wx.grid.GridCellBoolEditor())
        attr.SetRenderer(wx.grid.GridCellBoolRenderer())
        
        for i in range(0, self.RowNums):
            self.WxGrid.SetRowLabelValue(i, signalsList[i])
            for colNum in range(0, len(self.AttrNameDicList)):
                self.WxGrid.SetAttr(i, self.AttrNameDicList[colNum]["ColNum"], attr)
                self.WxGrid.SetColSize(self.AttrNameDicList[colNum]["ColNum"], 100)
                signalName = signalsList[i]
                (nodeName, messageName) = self.search_NodeName(signalName)
                self.WxGrid.SetCellValue(i, self.AttrNameDicList[colNum]["ColNum"], self.NodeInfoArrayDict[nodeName]["NODE_TX_MSGS"][messageName]["MSG_SIGS"][signalName]["SIG_ATTR"][self.AttrNameList[colNum]])

    def on_ClickGeneration(self, event):
        self.creat_PanelFile()
        self.creat_VsysvarFile()
        self.creat_CaplFile()
        
    def frameShow(self):
        self.MainFrame.Show()
        
    def on_CellChanged(self, event):
        rowNum = event.GetRow()
        colNum = event.GetCol()
        self.set_SignalsAttrValue(self.TreeItemName, rowNum, colNum, str(self.WxGrid.GetCellValue(rowNum, colNum)))
          
def main():
    app = wx.PySimpleApp()
    # Test = GEN_PANEL(r"DBC_SAIC_SK83_V1.2.dbc", "SAIC", "SK83", "V1.0", "ESCL")
    Test = GEN_PANEL(r"GWM_B02_CSA.dbc", "GWM", "B02", "V1.0", "SCCM")
    # Test = GEN_PANEL(r"HS2_CAN_P703_U704_GASD_MY21_x GT WIP 200221.dbc", "SAIC", "SK83", "V1.0", "ESCL")
    Test.frameShow()
    app.MainLoop()
    
def Test():
    filePath = r"C:\OneDrive\OneDrive - BCS AIS\WorkSpace\MyProject\AutoGenCanoePanel\GWM_B02_CSA.dbc";
    dbc_file = open(filePath)
    # Read out all the lines
    dbc_file_lines = dbc_file.readlines()
    
if __name__ == '__main__':
    main()
    # Test()
    
    input('Ok')
