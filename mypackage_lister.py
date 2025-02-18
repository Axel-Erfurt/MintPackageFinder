#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from subprocess import check_output

class TreeViewFilterWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Package List")
        self.set_name("mywindow")
        self.set_icon_name("package_system")
        self.set_border_width(4)
        self.column_count = 4
        self.connect("delete-event", self.on_close)
        self.myheader = ["Name", "Version", "Architecture", "Description"]
        self.installed_packages = ""
        
        # vbox
        self.vbox = Gtk.Box(orientation=1, vexpand=True, margin_left=10, margin_right=10)
        self.add(self.vbox)
        
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.set_title("Package Lister")
        headerbar.set_subtitle("installed packages")
        self.set_titlebar(headerbar)
        
        # save as button
        self.btn_save_as = Gtk.Button.new_from_icon_name("document-save-as-symbolic", 2)
        self.btn_save_as.set_name("btn_save")
        self.btn_save_as.set_tooltip_text("Save As ...\ntab delimited csv file")
        self.btn_save_as.set_hexpand(False)
        self.btn_save_as.set_relief(2)
        self.btn_save_as.connect("clicked", self.on_save_file_as)
        
        headerbar.pack_start(self.btn_save_as)
        
        # search field
        self.search_field = Gtk.SearchEntry()
        self.search_field.set_placeholder_text("filter")
        self.search_field.connect("activate", self.on_selection_button_clicked)
        self.search_field.connect("search-changed", self.on_search_changed)
        self.search_field.set_vexpand(False)
        headerbar.pack_end(self.search_field)
        
        # treeview
        self.treeview = Gtk.TreeView()
        self.treeview.set_name("csv-view")
        self.treeview.set_grid_lines(3)
        self.treeview.set_reorderable(True)
        self.treeview.set_activate_on_single_click(True)
        self.treeview.connect("row-activated", self.on_selection_changed)
        self.treeview.set_search_column(1)
        
        # label
        self.status_label = Gtk.Label(label="installed packages")
        self.status_label.set_name("sublabel")
        self.status_label.set_justify(2) 
        self.vbox.pack_end(self.status_label, False, True, 1)

        self.my_treelist = Gtk.ScrolledWindow()
        self.my_treelist.add(self.treeview)
        self.vbox.pack_end(self.my_treelist, True, True, 5)
        
        self.load_into_table()
        
    def get_packages(self, *args):
        cmd = ["dpkg -l", " | ", "grep ii"]
        installed_packages = check_output(cmd, shell = True).decode().splitlines()

        for lines in installed_packages[7:]:
            line = lines.split()
            status = line[0]
            name = line[1]
            version = line[2]
            arch = line[3]
            description = " ".join(line[4:])
            self.installed_packages += (f"{status}\t{name}\t{version}\t{arch}\t{description}\n")
        
    def on_close(self, *args):
        print("closing mypackage_lister ...")
        self.close()
        
    def on_selection_changed(self, treeview, path, column):
        model, pathlist = treeview.get_selection().get_selected()
        if pathlist:
            self.value_list = []
            for x in range(self.column_count):
                self.value_list.append(model[pathlist][x])
            self.status_label.set_markup(f"<b>{self.value_list[0]}</b>\n{self.value_list[3]}")

       
    def load_into_table(self, *args):
        self.search_field.set_text("")
        self.current_filter_text = ""
        for column in self.treeview.get_columns():
            self.treeview.remove_column(column)
        my_list = []
        self.get_packages()
        my_csv = self.installed_packages.splitlines() #[7:]
        packages_len = len(my_csv)
        self.my_liststore = Gtk.ListStore(*[str]* self.column_count)
            
        for i, column_title in enumerate(self.myheader):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.colnr = i
            self.treeview.append_column(column)

        for line in my_csv:
            row = line.split('\t')[1:]
            my_list.append(tuple(row))
            
        for line_value in my_list:
            self.my_liststore.append(list(line_value))
                 
        self.my_filter = self.my_liststore.filter_new()
        self.my_filter.set_visible_func(self.visible_cb)
        self.treeview.set_model(self.my_filter)
        self.status_label.set_text(f"{packages_len} installed packages")
        self.treeview.grab_focus()

    def my_filter_func(self, model, iter, data):
        if (
            self.current_filter_text is None
            or self.current_filter_text == "None"
        ):
            return True
        else:
            return model[iter][0] == self.current_filter_text

    def on_selection_button_clicked(self, widget):
        self.current_filter_text = widget.get_text()
        self.my_filter.refilter()

    def visible_cb(self, model, iter, data=None):
        search_query = self.search_field.get_text().lower()
        active_category = 0
        search_in_all_columns = True

        if search_query == "":
            return True

        if search_in_all_columns:
            for col in range(0,self.treeview.get_n_columns()):
                value = model.get_value(iter, col)
                if (search_query.lower() in  value
                    or search_query.upper() in  value
                    or search_query.title() in  value):
                    return True

            return False

        value = model.get_value(iter, active_category).lower()
        return True if value.startswith(search_query) else False
        
    def on_search_changed(self, *args):
        self.on_selection_button_clicked(self.search_field)
        
    def on_save_file_as(self, *args):
       dlg = Gtk.FileChooserDialog(title="Please choose a filename", parent=None, action = 1)
       dlg.set_do_overwrite_confirmation(True)
       dlg.add_buttons("Cancel", Gtk.ResponseType.CANCEL,
                 "Save", Gtk.ResponseType.OK)
                 
       filter = Gtk.FileFilter()
       filter.set_name("CSV Files")
       filter.add_pattern("*.csv")
       dlg.add_filter(filter)
       
       dlg.set_current_name("installed_packages.csv")
       response = dlg.run()

       if response == Gtk.ResponseType.OK:
            infile = (dlg.get_filename())
            print(infile)
            # model to csv_file
            list_string = []        
            for node in self.my_liststore:
                d = []
                for column in range(self.column_count):
                    the_node = node[column]
                    if the_node == None:
                        the_node = ""
                    d.append(the_node)
                list_string.append(d)
            with open(infile, 'w') as f:
                f.write("\t".join(self.myheader))
                f.write('\n')
                for line in list_string:
                    value = "\t".join(line)
                    f.write(f'{value}\n')
                self.status_label.set_text(f"{infile} saved!")
                self.current_file = infile
       else:
           print("cancelled")
       dlg.destroy()  
    
            
#win = TreeViewFilterWindow()
#win.connect("destroy", Gtk.main_quit)
#win.set_size_request(800, 600)
#win.move(0, 0)
#win.show_all()
#win.resize(1000, 700)
#Gtk.main()