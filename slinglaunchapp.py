#!/usr/bin/env python3
"""
Launchpad/Slingshot Tarzı Uygulama Başlatıcısı
Ubuntu 22.04 - GTK 3 - PyGObject
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio
import os
import subprocess

class AppLauncher(Gtk.Window):
    def __init__(self):
        super().__init__(title="Uygulama Başlatıcısı")
        
        # Ekran boyutunu al
        screen = self.get_screen()
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Pencere özellikleri - ekran boyutuna göre ayarla
        self.set_default_size(int(screen_width * 0.8), int(screen_height * 0.8))
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_decorated(False)  # Pencere dekorasyonunu kaldır
        
        # Görev çubuğundan gizle
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        
        # Transparan arka plan için
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)
        
        # Focus kaybı olayını yakala
        self.connect("focus-out-event", self.on_focus_out)
        
        # Ana container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)
        
        # Üst bar - Arama ve kategori seçimi
        header_bar = self.create_header_bar()
        main_box.pack_start(header_bar, False, False, 0)
        
        # İçerik alanı
        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        main_box.pack_start(content_box, True, True, 0)
        
        # Sol taraf - Kategori listesi
        self.category_list = self.create_category_list()
        scrolled_categories = Gtk.ScrolledWindow()
        scrolled_categories.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_categories.add(self.category_list)
        scrolled_categories.set_size_request(int(screen_width * 0.12), -1)  # Ekran genişliğinin %12'si
        content_box.pack_start(scrolled_categories, False, False, 0)
        
        # Sağ taraf - Uygulama grid'i
        self.app_grid = Gtk.FlowBox()
        self.app_grid.set_valign(Gtk.Align.START)
        
        # Ekran boyutuna göre sütun sayısını dinamik olarak ayarla
        columns = self.calculate_columns(screen_width)
        self.app_grid.set_max_children_per_line(columns)
        self.app_grid.set_min_children_per_line(columns)
        
        self.app_grid.set_selection_mode(Gtk.SelectionMode.NONE)
        self.app_grid.set_homogeneous(True)
        
        # Boşlukları ekran boyutuna göre ayarla
        spacing = max(10, int(screen_height * 0.015))
        self.app_grid.set_row_spacing(spacing)
        self.app_grid.set_column_spacing(spacing)
        
        margin = max(10, int(screen_height * 0.015))
        self.app_grid.set_margin_top(margin)
        self.app_grid.set_margin_bottom(margin)
        self.app_grid.set_margin_start(margin)
        self.app_grid.set_margin_end(margin)
        
        scrolled_apps = Gtk.ScrolledWindow()
        scrolled_apps.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_apps.add(self.app_grid)
        content_box.pack_start(scrolled_apps, True, True, 0)
        
        # Uygulamaları yükle
        self.all_apps = self.load_applications()
        self.current_filter = "Tümü"
        
        # Kategori listesini doldur
        self.populate_categories()
        
        # İlk kategoriyi seç
        self.category_list.select_row(self.category_list.get_row_at_index(0))
        
        # CSS stil
        self.apply_css()
        
    def calculate_columns(self, screen_width):
        """Ekran genişliğine göre sütun sayısını hesapla"""
        if screen_width >= 3840:  # 4K ve üstü
            return 8
        elif screen_width >= 2560:  # 2K
            return 7
        elif screen_width >= 1920:  # Full HD
            return 6
        elif screen_width >= 1366:  # HD
            return 5
        else:  # Düşük çözünürlük
            return 4
    
    def create_header_bar(self):
        """Üst bar oluştur"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        # Ekran boyutuna göre margin ayarla
        screen = self.get_screen()
        margin = max(10, int(screen.get_height() * 0.015))
        header_box.set_margin_top(margin)
        header_box.set_margin_bottom(margin)
        header_box.set_margin_start(margin)
        header_box.set_margin_end(margin)
        
        # Normal Gtk.Entry kullanarak arama kutusu
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Uygulama ara...")
        self.search_entry.connect("changed", self.on_search_changed)
        
        # Arama ikonu ekle
        self.search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "system-search-symbolic")
        
        # Arama kutusu yüksekliğini ayarla
        self.search_entry.set_size_request(-1, max(35, int(screen.get_height() * 0.04)))
        
        header_box.pack_start(self.search_entry, True, True, 0)
        
        return header_box
    
    def create_category_list(self):
        """Kategori listesi oluştur"""
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        listbox.connect("row-selected", self.on_category_selected)
        return listbox
    
    def populate_categories(self):
        """Kategorileri listele"""
        # Kategorileri say
        category_counts = {}
        for app in self.all_apps:
            cat = app['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Sıralı kategori listesi
        categories = [
            ("Tümü", len(self.all_apps)),
            ("Aksesuar", category_counts.get("Aksesuar", 0)),
            ("Geliştirme", category_counts.get("Geliştirme", 0)),
            ("Grafik", category_counts.get("Grafik", 0)),
            ("İnternet", category_counts.get("İnternet", 0)),
            ("Multimedya", category_counts.get("Multimedya", 0)),
            ("Ofis", category_counts.get("Ofis", 0)),
            ("Oyun", category_counts.get("Oyun", 0)),
            ("Sistem", category_counts.get("Sistem", 0)),
            ("Ayarlar", category_counts.get("Ayarlar", 0)),
        ]
        
        for cat_name, count in categories:
            if count > 0 or cat_name == "Tümü":
                row = Gtk.ListBoxRow()
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                
                # Satır yüksekliğini ayarla
                screen = self.get_screen()
                row_height = max(35, int(screen.get_height() * 0.04))
                box.set_margin_top(8)
                box.set_margin_bottom(8)
                box.set_margin_start(15)
                box.set_margin_end(15)
                
                label = Gtk.Label(label=cat_name)
                label.set_xalign(0)
                box.pack_start(label, True, True, 0)
                
                count_label = Gtk.Label(label=str(count))
                count_label.get_style_context().add_class("dim-label")
                box.pack_start(count_label, False, False, 0)
                
                row.add(box)
                self.category_list.add(row)
    
    def load_applications(self):
        """Sistem uygulamalarını yükle"""
        apps = []
        app_dirs = [
            '/usr/share/applications',
            os.path.expanduser('~/.local/share/applications'),
            os.path.expanduser('~/.local/share/flatpak/exports/share/applications')
        ]
        
        for app_dir in app_dirs:
            if not os.path.exists(app_dir):
                continue
                
            for filename in os.listdir(app_dir):
                if not filename.endswith('.desktop'):
                    continue
                    
                filepath = os.path.join(app_dir, filename)
                app_info = self.parse_desktop_file(filepath)
                
                if app_info and not app_info.get('NoDisplay', False):
                    apps.append(app_info)
        
        # İsme göre sırala
        apps.sort(key=lambda x: x['name'].lower())
        return apps
    
    def parse_desktop_file(self, filepath):
        """Desktop dosyasını parse et"""
        try:
            desktop_entry = Gio.DesktopAppInfo.new_from_filename(filepath)
            if not desktop_entry:
                return None
            
            name = desktop_entry.get_display_name()
            if not name:
                return None
            
            # Kategori belirle
            categories = desktop_entry.get_categories()
            category = self.determine_category(categories)
            
            return {
                'name': name,
                'description': desktop_entry.get_description() or '',
                'icon': desktop_entry.get_icon(),
                'exec': desktop_entry.get_executable(),
                'desktop_entry': desktop_entry,
                'category': category,
                'NoDisplay': desktop_entry.get_nodisplay()
            }
        except Exception as e:
            return None
    
    def determine_category(self, categories_str):
        """Kategori belirle"""
        if not categories_str:
            return "Diğer"
        
        categories = categories_str.lower()
        
        category_map = {
            'utility': 'Aksesuar',
            'accessories': 'Aksesuar',
            'development': 'Geliştirme',
            'graphics': 'Grafik',
            'network': 'İnternet',
            'webbrowser': 'İnternet',
            'audiovideo': 'Multimedya',
            'audio': 'Multimedya',
            'video': 'Multimedya',
            'office': 'Ofis',
            'game': 'Oyun',
            'system': 'Sistem',
            'settings': 'Ayarlar',
        }
        
        for key, value in category_map.items():
            if key in categories:
                return value
        
        return "Diğer"
    
    def create_app_button(self, app):
        """Uygulama butonu oluştur"""
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.connect("clicked", self.on_app_clicked, app)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # Ekran boyutuna göre margin ve spacing ayarla
        screen = self.get_screen()
        margin = max(8, int(screen.get_height() * 0.01))
        box.set_margin_top(margin)
        box.set_margin_bottom(margin)
        box.set_margin_start(margin)
        box.set_margin_end(margin)
        
        # İkon boyutunu ekrana göre ayarla
        icon_size = max(48, int(screen.get_height() * 0.06))
        
        # İkon
        icon_widget = Gtk.Image()
        if app['icon']:
            try:
                if isinstance(app['icon'], Gio.ThemedIcon):
                    icon_widget.set_from_gicon(app['icon'], Gtk.IconSize.DIALOG)
                else:
                    icon_widget.set_from_icon_name(str(app['icon']), Gtk.IconSize.DIALOG)
                icon_widget.set_pixel_size(icon_size)
            except:
                icon_widget.set_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
                icon_widget.set_pixel_size(icon_size)
        else:
            icon_widget.set_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
            icon_widget.set_pixel_size(icon_size)
        
        box.pack_start(icon_widget, False, False, 0)
        
        # İsim - BASIT VE ÇALIŞAN VERSİYON
        label = Gtk.Label(label=app['name'])
        label.set_line_wrap(True)
        label.set_max_width_chars(15)
        label.set_justify(Gtk.Justification.CENTER)
        
        # Sadece normal label kullan, font boyutunu CSS'te genel olarak ayarla
        box.pack_start(label, False, False, 0)
        
        button.add(box)
        return button
    
    def filter_apps(self):
        """Uygulamaları filtrele ve göster"""
        # Grid'i temizle
        for child in self.app_grid.get_children():
            self.app_grid.remove(child)
        
        search_text = self.search_entry.get_text().lower()
        
        for app in self.all_apps:
            # Kategori filtresi
            if self.current_filter != "Tümü" and app['category'] != self.current_filter:
                continue
            
            # Arama filtresi
            if search_text and search_text not in app['name'].lower():
                if not app['description'] or search_text not in app['description'].lower():
                    continue
            
            app_button = self.create_app_button(app)
            self.app_grid.add(app_button)
        
        self.app_grid.show_all()
    
    def on_category_selected(self, listbox, row):
        """Kategori seçildiğinde"""
        if row:
            box = row.get_child()
            label = box.get_children()[0]
            self.current_filter = label.get_text()
            self.filter_apps()
    
    def on_search_changed(self, entry):
        """Arama değiştiğinde"""
        self.filter_apps()
    
    def on_app_clicked(self, button, app):
        """Uygulamaya tıklandığında"""
        try:
            app['desktop_entry'].launch([], None)
            # Pencereyi kapat
            self.destroy()
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Uygulama başlatılamadı"
            )
            dialog.format_secondary_text(str(e))
            dialog.run()
            dialog.destroy()
    
    def on_focus_out(self, widget, event):
        """Pencere focus kaybettiğinde kapat"""
        # Kısa bir gecikme ile kapat (dialog açılırsa problem olmasın diye)
        from gi.repository import GLib
        GLib.timeout_add(100, self.destroy)
        return False
    
    def apply_css(self):
        """CSS stilleri uygula"""
        css_provider = Gtk.CssProvider()
        css = """
        window {
            background-color: rgba(20, 20, 20, 0.95);
            color: #ffffff;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }

        list {
            background-color: rgba(30, 30, 30, 0.7);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            color: #ffffff;
        }

        list row {
            color: #ffffff;
        }

        list row:selected {
            background-color: rgba(74, 144, 217, 0.8);
            color: #ffffff;
        }

        list row:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }

        /* Entry (arama kutusu) icin stil */
        entry {
            background-color: #000000;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            padding: 8px;
            color: #ffffff;
            font-size: 14px;
        }

        entry:focus {
            border-color: rgba(74, 144, 217, 0.8);
        }

        flowbox {
            background-color: transparent;
        }

        flowboxchild {
            background-color: transparent;
        }

        button {
            background-color: rgba(40, 40, 40, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            transition: all 200ms ease;
            color: #ffffff;
        }

        button:hover {
            background-color: rgba(60, 60, 60, 0.7);
            border-color: rgba(74, 144, 217, 0.5);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        button label {
            color: #ffffff;
        }

        .dim-label {
            opacity: 0.6;
            color: #ffffff;
        }

        scrolledwindow {
            background-color: transparent;
        }
        """
        
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

def main():
    win = AppLauncher()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
