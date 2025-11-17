# slinglaunchapp
launchpad application launcher
# App Launcher

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![GTK](https://img.shields.io/badge/GTK-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A modern and practical application launcher for Ubuntu. Provides an interface similar to macOS Launchpad or elementary OS Slingshot.

## ✨ Features

- 🎯 **Modern Interface**: Elegant and user-friendly GTK3 interface
- 🔍 **Quick Search**: Instant search in application names and descriptions
- 📂 **Category System**: Filter applications by categories
- 🖼️ **Application Icons**: Automatically loads system application icons
- 📱 **Responsive Design**: Adapts to different screen resolutions
- 🎨 **Customizable**: Appearance customization with CSS
- 📦 **Flatpak Support**: Automatically detects Flatpak applications

## 🚀 Installation

### Requirements

- Ubuntu 22.04 or higher
- Python 3.6+
- GTK 3.0
- PyGObject

### Required Packages

```bash
sudo apt update
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 flatpak
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/username/app-launcher.git
cd app-launcher
```

2. Make executable:
```bash
chmod +x slinglaunchapp.py
```

3. Run the application:
```bash
./slinglaunchapp
```

Or with Python:
```bash
python3 slinglaunchapp.py
```

## ⌨️ Usage

- **Search**: Type application name in the search box at the top
- **Category Selection**: Select a category from the left side
- **Launch Application**: Click on the application icon
- **Exit**: Click outside the window or press ESC key

## 🎯 Creating Shortcut

To launch the application with a keyboard shortcut:

1. Example shortcut for `Super` (Windows) key:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias launcher="/path/to/slinglaunchapp.py"
```

2. To create a system shortcut, create `~/.local/share/applications/launcher.desktop` file:
```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=App Launcher
Comment=Modern application launcher
Exec=/path/to/slinglaunchapp.py
Icon=application-x-executable
Categories=Utility;
Terminal=false
StartupNotify=false
```

## 🔧 Customization

### Changing Appearance with CSS

You can customize the appearance by editing the `apply_css` method:

```python
css = """
window {
    background-color: rgba(25, 25, 25, 0.95);
    border-radius: 15px;
}

/* To change color theme */
button {
    background-color: your_color_here;
}
"""
```

### Adding Categories

To add new categories, edit the `populate_categories` method:

```python
categories = [
    ("All", len(self.all_apps)),
    ("New Category", category_counts.get("New Category", 0)),
    # ... other categories
]
```

## 🐛 Troubleshooting

### Applications Not Showing
- If Flatpak applications are not showing: `Make sure flatpak --user is installed`

### Icons Not Showing
- Make sure icon packages are installed:
```bash
sudo apt install gnome-icon-theme-full
```

### Dependency Error
- Install required packages:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

## 🤝 Contributing

We welcome your contributions! Please:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- GTK+ and PyGObject developers
- Ubuntu community
- All contributors

---

Bu README dosyasını proje dizinine `README.md` olarak kaydedebilirsiniz. GitHub'da projenizin ana sayfasında otomatik olarak görüntülenecektir.
