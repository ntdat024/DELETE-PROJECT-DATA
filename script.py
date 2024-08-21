# -*- coding: utf-8 -*-
#region library
import clr 
import os
import sys

clr.AddReference("System")
clr.AddReference("System.Data")
clr.AddReference("RevitServices")
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference('PresentationCore')
clr.AddReference('PresentationFramework')
clr.AddReference("System.Windows.Forms")

import math
import System
import RevitServices
import Autodesk
import Autodesk.Revit
import Autodesk.Revit.DB

from Autodesk.Revit.UI import *
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB.Mechanical import *

from System.Collections.Generic import *
from System.Windows import MessageBox
from System.IO import FileStream, FileMode, FileAccess
from System.Windows.Markup import XamlReader
from Helper import Utils, Action

#endregion

#region revit infor
# Get the directory path of the script.py & the Window.xaml
dir_path = os.path.dirname(os.path.realpath(__file__))
xaml_file_path = os.path.join(dir_path, "Window.xaml")

#Get UIDocument, Document, UIApplication, Application
uidoc = __revit__.ActiveUIDocument
uiapp = UIApplication(uidoc.Document.Application)
app = uiapp.Application
doc = uidoc.Document
activeView = doc.ActiveView
#endregion


#defind wpf window
class WPFWindow:

    #region load and bindind data
    def load_window(self):

        #import window from .xaml file path
        file_stream = FileStream(xaml_file_path, FileMode.Open, FileAccess.Read)
        window = XamlReader.Load(file_stream)

        #Groupbox Data
        self.rb_view_not_placed = window.FindName("rb_sheet")
        self.rb_project_params = window.FindName("rb_param")
        self.rb_view_template = window.FindName("rb_view")
        self.rb_view_filter = window.FindName("rb_filter")

        #Groupbox Filter
        self.rb_all = window.FindName("rb_All")
        self.rb_used = window.FindName("rb_Using")
        self.rb_unuse = window.FindName("rb_Donotuse")

        #listbox
        self.lbx_data = window.FindName("lbx_Data")
        self.tb_filter = window.FindName("tb_Filter")

        #button
        self.bt_OK = window.FindName("bt_OK")
        self.bt_Cancel = window.FindName("bt_Cancel")

        # #bindingdata
        self.bindind_data()
        self.window = window
        

        return window

    def bindind_data(self):

        self.rb_view_not_placed.IsChecked = True
        self.rb_all.IsChecked = True
        self.rb_used.IsEnabled = False
        self.rb_unuse.IsEnabled = False
        self.data_default()

        #event
        self.rb_view_not_placed.Checked += self.rb_view_not_placed_Checked
        self.rb_project_params.Checked += self.rb_project_parameter_Checked
        self.rb_view_template.Checked += self.rb_viewtemplate_Checked
        self.rb_view_filter.Checked += self.rb_viewfilter_Checked
        self.rb_all.Checked += self.rb_all_Checked
        self.rb_used.Checked += self.rb_used_Checked
        self.rb_unuse.Checked += self.rb_unused_Checked
        self.tb_filter.TextChanged += self.tb_filter_Changed
        self.bt_Cancel.Click += self.cancel_Click
        self.bt_OK.Click += self.ok_Click
    
    def data_default (self):
        views_not_placed = Utils().get_view_not_placed()
        view_names = []
        for view in views_not_placed:
            full_name = Utils().get_view_full_name(view)
            view_names.append(full_name)
        
        view_names.sort()
        self.all_items = view_names
        self.lbx_data.ItemsSource = view_names

    #endregion


    #region Checked Event
    def rb_project_parameter_Checked (self, sender, e):
        self.rb_used.IsEnabled = False
        self.rb_unuse.IsEnabled = False
        self.rb_all.IsEnabled = True
        self.rb_all.IsChecked = True
        self.all_items = Utils().get_all_parameter_names()
        self.lbx_data.ItemsSource = self.all_items
        self.tb_filter.Text = ""

        
    
    def rb_view_not_placed_Checked (self, sender, e):
        self.rb_used.IsEnabled = False
        self.rb_unuse.IsEnabled = False
        self.rb_all.IsChecked = True
        self.data_default()
        self.tb_filter.Text = ""


    def rb_viewtemplate_Checked (self, sender, e):
        self.rb_used.IsEnabled = True
        self.rb_unuse.IsEnabled = True

        if self.rb_all.IsChecked:
            self.all_items = Utils().get_all_viewtemplate_names()
        elif self.rb_used.IsChecked:
            self.all_items = Utils().get_viewtemplate_used_names()
        elif self.rb_unuse.IsChecked:
            self.all_items = Utils().get_viewtemplate_unuse_names()
            
        self.lbx_data.ItemsSource = self.all_items
        self.tb_filter.Text = ""

    
    def rb_viewfilter_Checked (self, sender, e):
        self.rb_used.IsEnabled = True
        self.rb_unuse.IsEnabled = True

        if self.rb_all.IsChecked:
            self.all_items = Utils().get_all_fiter_names()
        elif self.rb_used.IsChecked:
            self.all_items = Utils().get_all_filter_used_names()
        elif self.rb_unuse.IsChecked:
            self.all_items = Utils().get_all_filter_unused_names()

        self.lbx_data.ItemsSource = self.all_items
        self.tb_filter.Text = ""

    
    def tb_filter_Changed (self, sender, e):
        filter_name = str(self.tb_filter.Text)
        new_list = []
        if filter_name is not None or filter_name != "":
            name = filter_name.lower()
            for item_Name in self.all_items:
                if str(item_Name).lower().__contains__(name):
                    new_list.append(item_Name)
            self.lbx_data.ItemsSource = new_list
        else: self.lbx_data.ItemsSource = self.all_items

    #endregion
    
    #region Filter Status
    def rb_all_Checked (self, sender, e):
        if self.rb_view_template.IsChecked:
            self.all_items = Utils().get_all_viewtemplate_names()
        elif self.rb_view_filter.IsChecked:
            self.all_items = Utils().get_all_fiter_names()

        self.lbx_data.ItemsSource = self.all_items
        self.tb_filter.Text = ""

    def rb_used_Checked (self, sender, e):
        if self.rb_view_template.IsChecked:
            self.all_items = Utils().get_viewtemplate_used_names()
        elif self.rb_view_filter.IsChecked:
            self.all_items = Utils().get_all_filter_used_names()
            
        self.lbx_data.ItemsSource = self.all_items
        self.tb_filter.Text = ""

    def rb_unused_Checked (self, sender, e):
        if self.rb_view_template.IsChecked:
            self.all_items = Utils().get_viewtemplate_unuse_names()
        elif self.rb_view_filter.IsChecked:
            self.all_items = Utils().get_all_filter_unused_names()

        self.lbx_data.ItemsSource = self.all_items
        self.tb_filter.Text = ""

    #endregion

    #region button event
    def ok_Click(self, sender, e):
        list_names = self.lbx_data.SelectedItems
        if len(list_names) == 0: MessageBox.Show("0 items selected!","Message")
        else:
            try:
                if self.rb_view_not_placed.IsChecked:
                    Action().remove_view(list_names)
                if self.rb_project_params.IsChecked:
                    Action().remove_parameter(list_names)
                if self.rb_view_template.IsChecked:
                    Action().remove_view_template(list_names)
                if self.rb_view_filter.IsChecked:
                    Action().remove_view_filter(list_names)

                #reset listbox
                all_items = list(self.lbx_data.Items)
                for name in list_names:
                    all_items.Remove(name)
                self.lbx_data.ItemsSource = all_items

            except Exception as e:
                MessageBox.Show(str(e),"Message")


    def cancel_Click(self, sender, e):
        self.window.Close()
    
    #endregion


def main_task ():
    try:
        window = WPFWindow().load_window()
        window.ShowDialog()
    except Exception as e:
        MessageBox.Show(str(e), "Message")
    

if __name__ == "__main__":
    main_task()
        
