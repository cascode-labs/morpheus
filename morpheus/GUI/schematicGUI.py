
import sys
import wx
class schematicGUIPanel():
    def __init__(self,viewer,panel):
        self.panel_main = panel
        self.viewer =viewer
        pass
    def build(self):
        rows = 2
        cols = 2
        self.body = wx.FlexGridSizer(rows, cols, 0, 0)

    # ROW 1) Testbench LIBRARY SELECTION
        #text
        lib_txt = wx.StaticText(self.panel_main, wx.ID_ANY, "Select Testbench Library")
        self.header.Add(lib_txt, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 50)
        #dropdown
        self.lib_sel = wx.ComboBox(self.panel_main, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.header.Add(self.lib_sel, 0, wx.ALL | wx.EXPAND, 2)
    # ROW 2) RUN BUTTON
        self.run_btn = wx.Button(self.panel_main, wx.ID_ANY, "Make Test\n")
        self.run_btn.SetMinSize((170, 30))
        self.run_btn.SetMaxSize((170, 30))
        self.header.Add(self.run_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE | wx.LEFT, 10)

        self.refresh_btn = wx.Button(self.panel_main, wx.ID_ANY, "Refresh Options\n")
        self.refresh_btn.SetMinSize((170, 30))
        self.refresh_btn.SetMaxSize((170, 30))
        self.header.Add(self.refresh_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.FIXED_MINSIZE | wx.LEFT, 10)
        #self.panel_main.SetSizer(self.header)

        for i in range(rows): #make rows growable
            self.header.AddGrowableRow(i)
