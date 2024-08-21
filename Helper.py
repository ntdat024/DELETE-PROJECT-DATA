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


#endregion

#region revit infor
uidoc = __revit__.ActiveUIDocument
uiapp = UIApplication(uidoc.Document.Application)
app = uiapp.Application
doc = uidoc.Document
activeView = doc.ActiveView
#endregion

class Utils:
    def __init__(self):
        pass

#region filter
    def get_all_fiter_names(self):
        filters = FilteredElementCollector(doc).OfClass(ParameterFilterElement).WhereElementIsNotElementType().ToElements()
        names = [filter_elem.Name for filter_elem in filters]
        names.sort()
        return names
    
    def get_all_filter_used_names(self):
        view_names =[]
        for view in self.get_view_inModel():
            for id in view.GetFilters():
                ele = doc.GetElement(id)
                view_names.append(ele.Name)
                
        
        view_names = list(set(view_names))
        view_names.sort()
        return view_names
    
    def get_all_filter_unused_names(self):
        all = self.get_all_fiter_names()
        used = self.get_all_filter_used_names()
        unUse = [item for item in all if item not in used]

        unUse.sort()
        return unUse


#endregion


#region viewtemplate

    def get_view_template(self):
            views_all = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
            views = []
            for view in views_all:
                if view.IsTemplate:
                    views.append(view)
            return views
    
    def get_view_inModel (self):
        views_all = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType().ToElements()
        views = []
        for view in views_all:
            if view.IsTemplate == False:
                views.append(view)
        return views

    def get_all_viewtemplate_names (self):
        names = []
        for view in self.get_view_template():
            names.append(view.Name)
            
        names.sort()
        return names

    def get_viewtemplate_used_names (self):
        names = []
        for view in self.get_view_inModel():
            ele = doc.GetElement(view.ViewTemplateId)
            if (ele is not None):
                names.append(ele.Name)

        names = list(set(names))
        names.sort()
        return names

    def get_viewtemplate_unuse_names (self):
        all = self.get_all_viewtemplate_names()
        used = self.get_viewtemplate_used_names()
        unUse = [item for item in all if item not in used]

        unUse.sort()
        return unUse
    

    def get_view_not_placed (self):
        views = []
        for view in self.get_view_inModel():
            p_map = view.ParametersMap
            is_not_placed = True
            for p in p_map:
                if p.Definition.Name == "Sheet Number":
                    is_not_placed = False
                    break
            
            if is_not_placed: views.append(view)
        
        return views
        
    def get_view_full_name(self, view):
        view_type = str(view.ViewType)
        view_name = view.Name
        full_name = "<" + view_type + ">: " + view_name
        return full_name
    

#endregion

#region parameter
    def get_all_parameter_names (self):
        param_binding = doc.ParameterBindings
        it = param_binding.ForwardIterator()
        it.Reset()

        names = []
        while it.MoveNext():
            names.append(it.Key.Name)
        
        return names
    

#endregion

    

class Action:
    def __init__(self):
        pass

    def remove_view(self, list_names):
        views_all = Utils().get_view_inModel()
        
        #find a view placed on sheet
        view_other = None
        for view in views_all:
            full_name = Utils().get_view_full_name(view)
            if full_name not in Utils().get_view_not_placed():
                view_other = view
                break
                
        
        #if list view not placed on sheet contain active view -> change active view
        if(view_other is not None):
            actiview_fullName = Utils().get_view_full_name(activeView)
            if list(list_names).__contains__(actiview_fullName):
                uidoc.ActiveView = view_other

        #remove view
        t = Transaction(doc, "remove")
        t.Start()
        for view in views_all:
            if view.IsTemplate == False:
                full_name = Utils().get_view_full_name(view)
                if list(list_names).__contains__(full_name):
                    try:
                        doc.Delete(view.Id)
                    except:
                        pass
        t.Commit()
        
        
    def remove_parameter (self, list_names):

        param_Elements = FilteredElementCollector(doc)\
            .WhereElementIsNotElementType()\
            .OfClass(ParameterElement)
        
        t = Transaction(doc, "remove")
        t.Start()
        for name in list_names:
            for p in param_Elements:
                if p.GetDefinition().Name == name:
                    doc.Delete(p.Id)
                    break
        t.Commit()

    def remove_view_template (self, list_names):
        t = Transaction(doc, "remove")
        t.Start()
        for view in Utils().get_view_template():
            if list(list_names).__contains__(view.Name):
                try:
                    doc.Delete(view.Id)
                except:
                    pass
                
        t.Commit()
    
    def remove_view_filter (self, list_names):
        filters = FilteredElementCollector(doc).OfClass(ParameterFilterElement).ToElements()
        t = Transaction(doc, "remove")
        t.Start()
        for filter in filters:
            if list(list_names).__contains__(filter.Name):
                doc.Delete(filter.Id)
        t.Commit()
        
                

        
        
            



    
        
    
        

