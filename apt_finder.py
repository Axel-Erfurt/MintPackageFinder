#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from subprocess import check_output, run
import encodings
import mypackage_lister
import distro, platform


class TreeViewWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Package Finder & Installer")
        self.set_name("mywindow")
        self.set_icon_name("package_system")
        self.set_border_width(2)
        self.column_count = 3
        self.connect("delete-event", self.on_close)
        self.myheader = ["Status", "Name", "Description"]
        self.founded_packages = ""
        self.value_list = []
        distro_info = f"{distro.id()} {distro.name()}{distro.version()} Kernel {platform.release()}"
        
        self.theme_settings = Gtk.Settings.get_default()
        self.use_dark = self.theme_settings.get_property("gtk-application-prefer-dark-theme")
        print(f'Theme: {self.theme_settings.get_property("gtk-theme-name")}')
        print(f"dark theme used: {self.use_dark}")
        
        # vbox
        self.vbox = Gtk.Box(orientation=1, vexpand=True, margin_left=10, 
                            margin_right=10)
        self.add(self.vbox)
        
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.set_title("Package Finder & Installer")
        headerbar.set_subtitle(distro_info)
        self.set_titlebar(headerbar)

        # install button
        self.btn_install = Gtk.Button.new_from_icon_name("emblem-downloads", 3)
        self.btn_install.set_name("btn_save")
        self.btn_install.set_tooltip_text("install selected package")
        self.btn_install.set_hexpand(False)
        self.btn_install.set_relief(2)
        self.btn_install.connect("clicked", self.on_install_package)
        
        # information button
        self.btn_information = Gtk.Button.new_from_icon_name("dialog-information", 3)
        self.btn_information.set_name("btn_information")
        self.btn_information.set_tooltip_text("package description")
        self.btn_information.set_hexpand(False)
        self.btn_information.set_relief(2)
        self.btn_information.connect("clicked", self.get_package_info)
        
        # mypackages button
        self.btn_mypackages = Gtk.Button.new_from_icon_name("emblem-generic", 3)
        self.btn_mypackages.set_name("btn_mypackages")
        self.btn_mypackages.set_tooltip_text("show installed packages")
        self.btn_mypackages.set_hexpand(False)
        self.btn_mypackages.set_relief(2)
        self.btn_mypackages.connect("clicked", self.show_mypackages)
        
        # mintupdate button
        self.btn_mintupdate = Gtk.Button.new_from_icon_name("system-software-update", 3)
        self.btn_mintupdate.set_name("btn_mintupdate")
        self.btn_mintupdate.set_tooltip_text("run mintupdate")
        self.btn_mintupdate.set_hexpand(False)
        self.btn_mintupdate.set_relief(2)
        self.btn_mintupdate.connect("clicked", self.show_mintupdate)
        
        # dark_theme button
        self.btn_dark_theme = Gtk.Button.new_from_icon_name("preferences-desktop-theme", 3)
        self.btn_dark_theme.set_name("btn_dark_theme")
        self.btn_dark_theme.set_tooltip_text("toggle light / dark theme")
        self.btn_dark_theme.set_hexpand(False)
        self.btn_dark_theme.set_relief(2)
        self.btn_dark_theme.connect("clicked", self.use_dark_theme)
        
        headerbar.pack_start(self.btn_install)
        headerbar.pack_start(self.btn_information)
        sep = Gtk.Separator()
        headerbar.pack_start(sep)
        headerbar.pack_start(self.btn_mypackages)
        headerbar.pack_start(self.btn_mintupdate)
        sep = Gtk.Separator()
        headerbar.pack_start(sep)
        headerbar.pack_start(self.btn_dark_theme)
        
        # search field
        self.search_field = Gtk.SearchEntry()
        self.search_field.set_placeholder_text("search ...")
        self.search_field.set_tooltip_text("enter search term and press Return")
        self.search_field.connect("activate", self.on_search_changed)
        self.search_field.set_vexpand(False)

        headerbar.pack_end(self.search_field)
                
        self.my_liststore = Gtk.ListStore(*[str]* self.column_count)

        # treeview
        self.treeview = Gtk.TreeView()
        self.treeview.set_name("csv-view")
        self.treeview.set_grid_lines(3)
        self.treeview.set_reorderable(True)
        self.treeview.set_activate_on_single_click(True)
        self.treeview.connect("row-activated", self.on_selection_changed)
        self.treeview.set_search_column(1)
        self.treeview.set_model(self.my_liststore)
        
        for i, column_title in enumerate(self.myheader):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.colnr = i
            self.treeview.append_column(column)
        
        # status_label
        self.status_label = Gtk.Label(label="installed packages")
        self.status_label.set_name("sublabel")
        self.status_label.set_justify(2) 
        self.vbox.pack_end(self.status_label, False, True, 1)

        self.my_treelist = Gtk.ScrolledWindow()
        self.my_treelist.add(self.treeview)
        self.vbox.pack_end(self.my_treelist, True, True, 1)
        
        self.search_field.grab_focus()
        
    def use_dark_theme(self, *args):
        if self.use_dark:
            self.theme_settings.set_property("gtk-application-prefer-dark-theme", False)
            self.use_dark = False
        else:
            self.theme_settings.set_property("gtk-application-prefer-dark-theme", True)
            self.use_dark = True
        
    def show_mintupdate(self, *args):
        run("mintupdate")
        
    def show_mypackages(self, *args):
        win = mypackage_lister.TreeViewFilterWindow()
        win.set_size_request(800, 600)
        win.move(0, 0)
        win.show_all()
        win.resize(1000, 700)        
        
    def get_packages(self, *args):
        self.founded_packages = ""
        search_term = self.search_field.get_text()
        ### aptitude gives a better result than apt
        cmd = f"aptitude search '{search_term}'"
        founded_packages = check_output(cmd, shell = True).decode().splitlines()

        for lines in founded_packages:
            status_i = lines.split(" ", 2)[:2][0]
            status_a = lines.split(" ", 2)[:2][1]
            name = (lines.split(" ", )[2])
            description = lines.split(' - ')[1]
            self.founded_packages += (f"{status_i}{status_a}\t{name}\t{description}\n")
        self.load_into_table()
        
    def on_close(self, *args):
        print("closing, goodbye ...")
        Gtk.main_quit()
        
    def on_selection_changed(self, treeview, path, column):
        model, pathlist = treeview.get_selection().get_selected()
        if pathlist:
            self.value_list = []
            for x in range(self.column_count):
                self.value_list.append(model[pathlist][x])
            self.status_label.set_markup(f"<b>{self.value_list[1]}</b>\n{self.value_list[2]}")

    def load_into_table(self, *args):
        my_list = []
        my_csv = self.founded_packages.splitlines() #[7:]
        packages_len = len(my_csv)

        for line in my_csv:
            row = line.split('\t')
            my_list.append(tuple(row))
            
        for line_value in my_list:
            self.my_liststore.append(list(line_value))

        self.treeview.set_model(self.my_liststore)
        self.status_label.set_text(f"found {packages_len} packages")
        #self.treeview.set_cursor(0)
        #self.treeview.grab_focus()
        
    def on_search_changed(self, *args):
        self.clear_table()
        self.get_packages()
        
    def on_install_package(self, *args):
        if len(self.value_list) > 0:
            pkgname = self.value_list[1]
            print(f"installing {pkgname} ...")
            self.status_label.set_text(f"installing {pkgname} ...")
            run(["xdg-open", f"apt://{pkgname}"])
        else:
            self.status_label.set_text("Install: no package selected!")
        
    def get_package_info(self, *args):
        if len(self.value_list) > 0:
            ### apt show -a "$PKGNAME"|grep Description: -A99
            pkgname = self.value_list[1]
            package_info = check_output(f"aptitude show {pkgname}", shell = True, universal_newlines=True)
            description = package_info.split("Homepage: ")[0]
            homepage = package_info.split("Homepage: ")[1].lstrip().split("\n")[0]
            version = package_info.split("Version: ")[1].lstrip().split("\n")[0]
            
            dialog = Gtk.AboutDialog(title = "Information")
            dialog.set_title("Information")
            dialog.set_authors([f"{pkgname} Developers"])
            dialog.set_version(version)
            dialog.set_program_name(pkgname.title())
            dialog.set_website(homepage)
            dialog.set_website_label(pkgname.title())
            dialog.set_logo_icon_name("help-about")
            dialog.set_comments(description)
            dialog.set_size_request(800, 600)
            dialog.connect('response', lambda dialog, data: dialog.destroy())
            dialog.show_all()
        else:
            self.status_label.set_text("Information: no package selected!")
            
    def clear_table(self, *args):
        self.my_liststore.clear()
        for i in range(len(self.my_liststore)):
            self.treeview.set_cursor(i)
            selection = self.treeview.get_selection()
            model = self.my_liststore
            model, treeiter = selection.get_selected()
            if treeiter:
                model.remove(treeiter)

            
win = TreeViewWindow()
win.connect("destroy", Gtk.main_quit)
win.set_size_request(800, 600)
win.move(0, 0)
win.show_all()
win.resize(1000, 700)
Gtk.main()
