import sys
import os
import json
import webbrowser
import requests
import threading
import subprocess
from io import BytesIO
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QGridLayout, QFileDialog, QCheckBox, 
                             QLineEdit, QMessageBox, QProgressBar, QScrollArea, QSpacerItem, 
                             QSizePolicy, QComboBox, QToolBar, QAction, QMenu)
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon
from PyQt5.QtCore import Qt, QUrl, QSize, pyqtSignal, QObject, QThread, QSettings, QTranslator, QLocale
from PyQt5.QtWidgets import QProgressDialog

# Dictionary of supported languages
LANGUAGES = {
    "ar": "العربية",
    "en": "English",
    "zh": "中文",
    "pt": "Português",
    "de": "Deutsch",
    "es": "Spanish",
    "fr": "Français",
    "it": "Italiano",
    "ru": "Русский",
    "ja": "日本語",
    "ko": "한국어"
}

# Dictionary of UI translations
TRANSLATIONS = {
    "ar": {
        "appTitle": "EmuHub",
        "back": "العودة",
        "loading": "جاري تحميل البيانات...",
        "loadSuccess": "تم تحميل البيانات بنجاح.",
        "loadError": "حدث خطأ أثناء تحميل البيانات: ",
        "connectionError": "حدث خطأ أثناء الاتصال: ",
        "noData": "لا توجد بيانات متاحة. تأكد من اتصالك بالإنترنت.",
        "noImage": "لا توجد صورة",
        "untitled": "بدون عنوان",
        "visitWebsite": "زيارة الموقع الرسمي",
        "downloadPath": "مسار التنزيل:",
        "browse": "تصفح",
        "downloadReqs": "تنزيل المتطلبات مع المحاكي",
        "downloadEmulator": "تنزيل المحاكي",
        "requirements": "المتطلبات",
        "downloadingTitle": "جاري التنزيل",
        "downloading": "جاري تنزيل: ",
        "downloadComplete": "اكتمل التنزيل",
        "downloadSuccess": "تم تنزيل {0} بنجاح",
        "error": "خطأ",
        "invalidUrl": "رابط التنزيل غير صالح",
        "cantCreateFolder": "لا يمكن إنشاء مجلد التنزيل: ",
        "downloadError": "حدث خطأ أثناء التنزيل: ",
        "language": "اللغة"
    },
    "en": {
        "appTitle": "EmuHub",
        "back": "Back",
        "loading": "Loading data...",
        "loadSuccess": "Data loaded successfully.",
        "loadError": "Error loading data: ",
        "connectionError": "Connection error: ",
        "noData": "No data available. Check your internet connection.",
        "noImage": "No image",
        "untitled": "Untitled",
        "visitWebsite": "Visit Official Website",
        "downloadPath": "Download path:",
        "browse": "Browse",
        "downloadReqs": "Download requirements with emulator",
        "downloadEmulator": "Download Emulator",
        "requirements": "Requirements",
        "downloadingTitle": "Downloading",
        "downloading": "Downloading: ",
        "downloadComplete": "Download Complete",
        "downloadSuccess": "{0} downloaded successfully",
        "error": "Error",
        "invalidUrl": "Invalid download URL",
        "cantCreateFolder": "Cannot create download folder: ",
        "downloadError": "Error during download: ",
        "language": "Language"
    },
    "zh": {
        "appTitle": "EmuHub",
        "back": "返回",
        "loading": "正在加载数据...",
        "loadSuccess": "数据加载成功。",
        "loadError": "加载数据时出错: ",
        "connectionError": "连接错误: ",
        "noData": "没有可用数据。请检查您的互联网连接。",
        "noImage": "没有图片",
        "untitled": "无标题",
        "visitWebsite": "访问官方网站",
        "downloadPath": "下载路径:",
        "browse": "浏览",
        "downloadReqs": "下载模拟器及其依赖",
        "downloadEmulator": "下载模拟器",
        "requirements": "依赖项",
        "downloadingTitle": "正在下载",
        "downloading": "正在下载: ",
        "downloadComplete": "下载完成",
        "downloadSuccess": "{0} 下载成功",
        "error": "错误",
        "invalidUrl": "无效的下载URL",
        "cantCreateFolder": "无法创建下载文件夹: ",
        "downloadError": "下载时出错: ",
        "language": "语言"
    },
    "pt": {
        "appTitle": "EmuHub",
        "back": "Voltar",
        "loading": "Carregando dados...",
        "loadSuccess": "Dados carregados com sucesso.",
        "loadError": "Erro ao carregar dados: ",
        "connectionError": "Erro de conexão: ",
        "noData": "Nenhum dado disponível. Verifique sua conexão com a internet.",
        "noImage": "Sem imagem",
        "untitled": "Sem título",
        "visitWebsite": "Visitar Site Oficial",
        "downloadPath": "Caminho de download:",
        "browse": "Procurar",
        "downloadReqs": "Baixar requisitos com o emulador",
        "downloadEmulator": "Baixar Emulador",
        "requirements": "Requisitos",
        "downloadingTitle": "Baixando",
        "downloading": "Baixando: ",
        "downloadComplete": "Download Completo",
        "downloadSuccess": "{0} baixado com sucesso",
        "error": "Erro",
        "invalidUrl": "URL de download inválido",
        "cantCreateFolder": "Não é possível criar pasta de download: ",
        "downloadError": "Erro durante o download: ",
        "language": "Idioma"},
            "fr": {
        "appTitle": "EmuHub",
        "back": "Retour",
        "loading": "Chargement des données...",
        "loadSuccess": "Données chargées avec succès.",
        "loadError": "Erreur lors du chargement des données: ",
        "connectionError": "Erreur de connexion: ",
        "noData": "Aucune donnée disponible. Vérifiez votre connexion internet.",
        "noImage": "Aucune image",
        "untitled": "Sans titre",
        "visitWebsite": "Visiter le site officiel",
        "downloadPath": "Chemin de téléchargement:",
        "browse": "Parcourir",
        "downloadReqs": "Télécharger les exigences avec l'émulateur",
        "downloadEmulator": "Télécharger l'émulateur",
        "requirements": "Exigences",
        "downloadingTitle": "Téléchargement",
        "downloading": "Téléchargement: ",
        "downloadComplete": "Téléchargement terminé",
        "downloadSuccess": "{0} téléchargé avec succès",
        "error": "Erreur",
        "invalidUrl": "URL de téléchargement invalide",
        "cantCreateFolder": "Impossible de créer le dossier de téléchargement: ",
        "downloadError": "Erreur lors du téléchargement: ",
        "language": "Langue"
    },
    "de": {
        "appTitle": "EmuHub",
        "back": "Zurück",
        "loading": "Lade Daten...",
        "loadSuccess": "Daten erfolgreich geladen.",
        "loadError": "Fehler beim Laden der Daten: ",
        "connectionError": "Verbindungsfehler: ",
        "noData": "Keine Daten verfügbar. Überprüfen Sie Ihre Internetverbindung.",
        "noImage": "Kein Bild",
        "untitled": "Ohne Titel",
        "visitWebsite": "Offizielle Website besuchen",
        "downloadPath": "Download-Pfad:",
        "browse": "Durchsuchen",
        "downloadReqs": "Anforderungen mit Emulator herunterladen",
        "downloadEmulator": "Emulator herunterladen",
        "requirements": "Anforderungen",
        "downloadingTitle": "Herunterladen",
        "downloading": "Herunterladen: ",
        "downloadComplete": "Download abgeschlossen",
        "downloadSuccess": "{0} erfolgreich heruntergeladen",
        "error": "Fehler",
        "invalidUrl": "Ungültige Download-URL",
        "cantCreateFolder": "Download-Ordner kann nicht erstellt werden: ",
        "downloadError": "Fehler beim Herunterladen: ",
        "language": "Sprache"
    },
        "fr": {
        "appTitle": "EmuHub",
        "back": "Retour",
        "loading": "Chargement des données...",
        "loadSuccess": "Données chargées avec succès.",
        "loadError": "Erreur lors du chargement des données : ",
        "connectionError": "Erreur de connexion : ",
        "noData": "Aucune donnée disponible. Vérifiez votre connexion Internet.",
        "noImage": "Aucune image",
        "untitled": "Sans titre",
        "visitWebsite": "Visiter le site officiel",
        "downloadPath": "Chemin de téléchargement :",
        "browse": "Parcourir",
        "downloadReqs": "Télécharger les prérequis avec l'émulateur",
        "downloadEmulator": "Télécharger l'émulateur",
        "requirements": "Prérequis",
        "downloadingTitle": "Téléchargement",
        "downloading": "Téléchargement : ",
        "downloadComplete": "Téléchargement terminé",
        "downloadSuccess": "{0} téléchargé avec succès",
        "error": "Erreur",
        "invalidUrl": "URL de téléchargement invalide",
        "cantCreateFolder": "Impossible de créer le dossier de téléchargement : ",
        "downloadError": "Erreur lors du téléchargement : ",
        "language": "Langue"
    },
    "it": {
        "appTitle": "EmuHub",
        "back": "Indietro",
        "loading": "Caricamento dati...",
        "loadSuccess": "Dati caricati con successo.",
        "loadError": "Errore durante il caricamento dei dati: ",
        "connectionError": "Errore di connessione: ",
        "noData": "Nessun dato disponibile. Controlla la tua connessione Internet.",
        "noImage": "Nessuna immagine",
        "untitled": "Senza titolo",
        "visitWebsite": "Visita il sito ufficiale",
        "downloadPath": "Percorso di download:",
        "browse": "Sfoglia",
        "downloadReqs": "Scarica i requisiti con l'emulatore",
        "downloadEmulator": "Scarica l'emulatore",
        "requirements": "Requisiti",
        "downloadingTitle": "Download",
        "downloading": "Scaricamento: ",
        "downloadComplete": "Download completato",
        "downloadSuccess": "{0} scaricato con successo",
        "error": "Errore",
        "invalidUrl": "URL di download non valido",
        "cantCreateFolder": "Impossibile creare la cartella di download: ",
        "downloadError": "Errore durante il download: ",
        "language": "Lingua"
    },
    "ru": {
        "appTitle": "EmuHub",
        "back": "Назад",
        "loading": "Загрузка данных...",
        "loadSuccess": "Данные успешно загружены.",
        "loadError": "Ошибка загрузки данных: ",
        "connectionError": "Ошибка соединения: ",
        "noData": "Нет доступных данных. Проверьте подключение к Интернету.",
        "noImage": "Нет изображения",
        "untitled": "Без названия",
        "visitWebsite": "Посетить официальный сайт",
        "downloadPath": "Путь загрузки:",
        "browse": "Обзор",
        "downloadReqs": "Загрузить зависимости вместе с эмулятором",
        "downloadEmulator": "Скачать эмулятор",
        "requirements": "Требования",
        "downloadingTitle": "Загрузка",
        "downloading": "Загрузка: ",
        "downloadComplete": "Загрузка завершена",
        "downloadSuccess": "{0} успешно загружен",
        "error": "Ошибка",
        "invalidUrl": "Недействительный URL загрузки",
        "cantCreateFolder": "Невозможно создать папку загрузки: ",
        "downloadError": "Ошибка при загрузке: ",
        "language": "Язык"
    },
    "ja": {
        "appTitle": "EmuHub",
        "back": "戻る",
        "loading": "データを読み込み中...",
        "loadSuccess": "データの読み込みに成功しました。",
        "loadError": "データの読み込みエラー: ",
        "connectionError": "接続エラー: ",
        "noData": "利用可能なデータがありません。インターネット接続を確認してください。",
        "noImage": "画像なし",
        "untitled": "無題",
        "visitWebsite": "公式ウェブサイトを訪れる",
        "downloadPath": "ダウンロードパス:",
        "browse": "参照",
        "downloadReqs": "エミュレーターと必要ファイルをダウンロード",
        "downloadEmulator": "エミュレーターをダウンロード",
        "requirements": "要件",
        "downloadingTitle": "ダウンロード中",
        "downloading": "ダウンロード中: ",
        "downloadComplete": "ダウンロード完了",
        "downloadSuccess": "{0} のダウンロードが成功しました",
        "error": "エラー",
        "invalidUrl": "無効なダウンロードURL",
        "cantCreateFolder": "ダウンロードフォルダを作成できません: ",
        "downloadError": "ダウンロード中にエラーが発生しました: ",
        "language": "言語"
    },
    "ko": {
        "appTitle": "EmuHub",
        "back": "뒤로",
        "loading": "데이터 로드 중...",
        "loadSuccess": "데이터가 성공적으로 로드되었습니다.",
        "loadError": "데이터 로드 중 오류 발생: ",
        "connectionError": "연결 오류: ",
        "noData": "사용 가능한 데이터가 없습니다. 인터넷 연결을 확인하세요.",
        "noImage": "이미지 없음",
        "untitled": "제목 없음",
        "visitWebsite": "공식 웹사이트 방문",
        "downloadPath": "다운로드 경로:",
        "browse": "찾아보기",
        "downloadReqs": "에뮬레이터와 함께 필수 항목 다운로드",
        "downloadEmulator": "에뮬레이터 다운로드",
        "requirements": "요구 사항",
        "downloadingTitle": "다운로드 중",
        "downloading": "다운로드 중: ",
        "downloadComplete": "다운로드 완료",
        "downloadSuccess": "{0} 다운로드 성공",
        "error": "오류",
        "invalidUrl": "잘못된 다운로드 URL",
        "cantCreateFolder": "다운로드 폴더를 만들 수 없습니다: ",
        "downloadError": "다운로드 중 오류 발생: ",
        "language": "언어"
    },
    "es": {
        "appTitle": "EmuHub",
        "back": "Volver",
        "loading": "Cargando datos...",
        "loadSuccess": "Datos cargados con éxito.",
        "loadError": "Error al cargar datos: ",
        "connectionError": "Error de conexión: ",
        "noData": "No hay datos disponibles. Verifique su conexión a internet.",
        "noImage": "Sin imagen",
        "untitled": "Sin título",
        "visitWebsite": "Visitar el sitio oficial",
        "downloadPath": "Ruta de descarga:",
        "browse": "Explorar",
        "downloadReqs": "Descargar requisitos con el emulador",
        "downloadEmulator": "Descargar emulador",
        "requirements": "Requisitos",
        "downloadingTitle": "Descargando",
        "downloading": "Descargando: ",
        "downloadComplete": "Descarga completa",
        "downloadSuccess": "{0} descargado con éxito",
        "error": "Error",
        "invalidUrl": "URL de descarga no válida",
        "cantCreateFolder": "No se puede crear la carpeta de descarga: ",
        "downloadError": "Error durante la descarga: ",
        "language": "Idioma"
    }

}

class DownloaderWorker(QObject):
    progress_updated = pyqtSignal(int, int, str)
    download_finished = pyqtSignal(str)
    download_error = pyqtSignal(str)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        try:
            filename = os.path.basename(self.url)
            file_path = os.path.join(self.save_path, filename)
            
            response = requests.get(self.url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(file_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.progress_updated.emit(downloaded, total_size, filename)
            
            self.download_finished.emit(filename)
        except Exception as e:
            self.download_error.emit(str(e))

class DataLoader(QObject):
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            # Try to load data from the internet
            response = requests.get(self.url)

            # Parse data
            data = json.loads(response.text)
            self.data_loaded.emit(data)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class EmulatorLoaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize settings
        self.settings = QSettings("MasterHunterr", "EmuHub")
        
        # Set default language if not set
        if not self.settings.contains("language"):
            self.settings.setValue("language", "en")
        
        # Load current language
        self.current_language = self.settings.value("language", "en")
        
        self.setWindowTitle("EmuHub")
        self.setMinimumSize(900, 700)
        self.setStyleSheet("background-color: #2C2F33; color: white; ")
        
        self.init_ui()
        self.setup_language_menu()
        
        self.load_data_from_online()
        
    def tr(self, key):
        """Translate key to current language"""
        return TRANSLATIONS.get(self.current_language, TRANSLATIONS["en"]).get(key, key)
        
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_view = QWidget()
        self.detail_view = QWidget()
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.main_view)
        self.main_layout.addWidget(self.detail_view)
        
        self.detail_view.hide()
        
        self.setup_main_view()
        self.setup_detail_view()
        
    def setup_language_menu(self):
        # Create toolbar for language selection
        self.toolbar = QToolBar("Language")
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #23272A;
                border: none;
                spacing: 5px;
                padding: 2px;
            }
        """)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        # Create language menu
        self.lang_menu = QMenu(self.tr("language"), self)
        self.lang_menu.setStyleSheet("""
            QMenu {
                background-color: #23272A;
                color: white;
                border: 1px solid #444;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #7289DA;
            }
        """)
        
        # Add language options
        lang_button = QPushButton(self.tr("language"))
        lang_button.setStyleSheet("""
            QPushButton {
                background-color: #4A5A70;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3A4A60;
            }
        """)
        
        for lang_code, lang_name in LANGUAGES.items():
            action = QAction(lang_name, self)
            action.setData(lang_code)
            action.triggered.connect(self.change_language)
            self.lang_menu.addAction(action)
        
        lang_button.setMenu(self.lang_menu)
        self.toolbar.addWidget(lang_button)
        
    def change_language(self):
        action = self.sender()
        if action:
            # Save selected language
            lang_code = action.data()
            self.current_language = lang_code
            self.settings.setValue("language", lang_code)
            
            # Set text direction based on language
            if lang_code == "ar":
                QApplication.setLayoutDirection(Qt.RightToLeft)
            else:
                QApplication.setLayoutDirection(Qt.LeftToRight)
            
            # Update UI text
            self.update_ui_texts()
            
    def update_ui_texts(self):
        # Update window title
        self.setWindowTitle(self.tr("appTitle"))
        
        # Update toolbar
        for action in self.toolbar.actions():
            if action.text() == self.tr("language"):
                action.setText(self.tr("language"))
        
        # Refresh view
        self.display_emulators()
        
        # If detail view is visible, refresh it
        if not self.detail_view.isHidden() and hasattr(self, 'selected_emulator'):
            self.show_detail_view(self.emulators_data.index(self.selected_emulator))
            
    def setup_main_view(self):
        main_layout = QVBoxLayout(self.main_view)
        
        title_label = QLabel(self.tr("appTitle"))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF; margin: 20px;")
        main_layout.addWidget(title_label)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #2C2F33;
                border: none;
                color: white;
            }
        """)
        
        self.scroll_content = QWidget()
        self.emulators_grid = QGridLayout(self.scroll_content)
        self.emulators_grid.setSpacing(20)
        self.emulators_grid.setContentsMargins(20, 10, 20, 10)
        
        scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(scroll_area)
    
    def setup_detail_view(self):
        detail_layout = QVBoxLayout(self.detail_view)
        
        back_button = QPushButton(self.tr("back"))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #4A5A70;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3A4A60;
            }
        """)

        back_button.clicked.connect(self.show_main_view)
        
        back_layout = QHBoxLayout()
        back_layout.addWidget(back_button)
        back_layout.addStretch()
        detail_layout.addLayout(back_layout)
        
        self.detail_content = QWidget()
        self.detail_content_layout = QVBoxLayout(self.detail_content)
        self.detail_content_layout.setAlignment(Qt.AlignCenter)
        self.detail_content_layout.setSpacing(15)
        
        detail_layout.addWidget(self.detail_content)
    
    def load_data_from_online(self):
        try:
            json_url = "https://raw.githubusercontent.com/MasterHunterr/xsimulators/refs/heads/main/EmuHub.json"
            self.status_message(self.tr("loading"))
            thread = QThread()
            worker = DataLoader(json_url)
            worker.moveToThread(thread)
            worker.data_loaded.connect(self.on_data_loaded)
            worker.error_occurred.connect(self.on_data_error)
            thread.started.connect(worker.run)
            thread.start()
            self.data_thread = thread
            self.data_worker = worker
        except Exception as e:
            QMessageBox.critical(self, self.tr("error"), f"{self.tr('connectionError')}{str(e)}")
            self.emulators_data = []
            self.display_emulators()
    
    def on_data_loaded(self, data):
        self.emulators_data = data
        self.data_thread.quit()
        self.data_thread.wait()
        self.status_message(self.tr("loadSuccess"))
        self.display_emulators()
    
    def on_data_error(self, error_msg):
        self.data_thread.quit()
        self.data_thread.wait()
        QMessageBox.critical(self, self.tr("error"), f"{self.tr('loadError')}{error_msg}")
        self.emulators_data = []
        self.display_emulators()
    
    def status_message(self, message):
        self.statusBar().showMessage(message, 3000)
    
    def display_emulators(self):
        while self.emulators_grid.count():
            item = self.emulators_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # If no data is available
        if not hasattr(self, 'emulators_data') or not self.emulators_data:
            no_data_label = QLabel(self.tr("noData"))
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("font-size: 16px; color: #555; padding: 40px;")
            self.emulators_grid.addWidget(no_data_label, 0, 0, 1, 3)
            return
        
        # Store image references
        self.pixmap_refs = []
        
        # Add emulators to grid (3 per row)
        row, col = 0, 0
        for idx, emulator in enumerate(self.emulators_data):
            # Create emulator card
            card = self.create_emulator_card(emulator, idx)
            self.emulators_grid.addWidget(card, row, col)
            
            # Move to next column or row
            col += 1
            if col > 2:  # 3 emulators per row
                col = 0
                row += 1
        
        # Add space at the end
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.emulators_grid.addItem(spacer, row + 1, 0, 1, 3)
    
    def create_emulator_card(self, emulator, idx):
        # Create emulator card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #23272A;
                border-radius: 8px;
                border: 1px solid #444;
                color: white;
            }
            QFrame:hover {
                border: 1px solid #7289DA;
                background-color: #2E3338;
            }
        """)

        card.setFixedSize(250, 250)
        
        # Layout
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        
        # Image
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setFixedHeight(120)
        image_label.setStyleSheet("border: none;")
        
        # Load image
        image_url = emulator.get("image_url", "")
        if image_url and not image_url.startswith("رابط_الصورة"):
            try:
                response = requests.get(image_url)
                image_data = BytesIO(response.content)
                image = QImage.fromData(image_data.getvalue())
                pixmap = QPixmap.fromImage(image)
                pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
                self.pixmap_refs.append(pixmap)  # Store reference
            except Exception as e:
                image_label.setText(self.tr("noImage"))
        else:
            image_label.setText(self.tr("noImage"))
        
        # Title
        title = emulator.get("title", self.tr("untitled"))
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        
        # Description
        description = emulator.get("description", "")
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 13px; color: #BBBBBB;")
        
        # Add elements to layout
        card_layout.addWidget(image_label)
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        card_layout.addStretch()
        
        # Make card clickable
        card.mousePressEvent = lambda event, idx=idx: self.show_detail_view(idx)
        
        return card
    
    def show_detail_view(self, emulator_idx):
        # Get selected emulator
        self.selected_emulator = self.emulators_data[emulator_idx]
        
        # Clear detail view content
        while self.detail_content_layout.count():
            item = self.detail_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Show detail content
        
        # Image
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        
        # Load image
        image_url = self.selected_emulator.get("image_url", "")
        if image_url and not image_url.startswith("رابط_الصورة"):
            try:
                response = requests.get(image_url)
                image_data = BytesIO(response.content)
                image = QImage.fromData(image_data.getvalue())
                pixmap = QPixmap.fromImage(image)
                pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
                self.detail_pixmap = pixmap  # Store reference
            except Exception as e:
                image_label.setText(self.tr("noImage"))
                image_label.setStyleSheet("font-size: 14px; color: #777; padding: 40px;")
        else:
            image_label.setText(self.tr("noImage"))
            image_label.setStyleSheet("font-size: 14px; color: #777; padding: 40px;")
        
        # Title
        title = self.selected_emulator.get("title", self.tr("untitled"))
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color:rgb(255, 255, 255); margin-top: 10px;")
        
        # Description
        description = self.selected_emulator.get("description", "")
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("font-size: 16px; color:rgb(252, 252, 252); margin: 5px 0;")
        
        # URL
        url = self.selected_emulator.get("url", "")
        url_button = None

        if url and not url.startswith("رابط_تفاصيل"):
            url_button = QPushButton(self.tr("visitWebsite"))
            url_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 8px 15px;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            url_button.clicked.connect(lambda: webbrowser.open(url))
        
        # Download frame
        download_frame = QFrame()
        download_frame.setStyleSheet("""
            QFrame {
                background-color:#777;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }
        """)
        
        download_layout = QVBoxLayout(download_frame)
        
        # Download path
        path_layout = QHBoxLayout()
        path_label = QLabel(self.tr("downloadPath"))
        path_label.setStyleSheet("font-size: 14px;")
        
        self.path_input = QLineEdit(os.path.join(os.path.expanduser("~"), "Downloads"))
        
        browse_button = QPushButton(self.tr("browse"))
        browse_button.setStyleSheet("""
            QPushButton {
                background-color:rgba(2, 92, 92, 0.62);
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color:rgba(0, 64, 64, 0.25);
            }
        """)
        browse_button.clicked.connect(self.browse_folder)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_button)
        
        # Download requirements
        self.req_checkbox = QCheckBox(self.tr("downloadReqs"))
        self.req_checkbox.setChecked(True)
        self.req_checkbox.setStyleSheet("font-size: 14px; margin: 10px 0;")
        
        # Download button
        download_button = QPushButton(self.tr("downloadEmulator"))
        download_button.setStyleSheet("""
            QPushButton {
                background-color:rgba(0, 123, 255, 0.38);
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color:rgba(0, 87, 179, 0.33);
            }
        """)

        download_button.clicked.connect(self.start_download)
        
        # Add elements to download frame
        download_layout.addLayout(path_layout)
        download_layout.addWidget(self.req_checkbox)
        download_layout.addWidget(download_button, 0, Qt.AlignCenter)
        
        # Requirements list
        requirements = self.selected_emulator.get("requirements_urls", [])
        requirements_frame = None
        
        if requirements and not all(url.startswith("رابط_المتطلب") for url in requirements):
            requirements_frame = QFrame()
            requirements_layout = QVBoxLayout(requirements_frame)
            
            req_title = QLabel(f"{self.tr('requirements')} ({len(requirements)}):")
            req_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 15px;")
            requirements_layout.addWidget(req_title)
            
            for i, req_url in enumerate(requirements):
                if not req_url.startswith("رابط_المتطلب"):
                    req_name = os.path.basename(req_url)
                    req_item = QLabel(f"{i+1}. {req_name}")
                    req_item.setStyleSheet("font-size: 13px; color: #fff; margin-left: 20px;")
                    requirements_layout.addWidget(req_item)
        
        # Add all elements to detail layout
        self.detail_content_layout.addWidget(image_label)
        self.detail_content_layout.addWidget(title_label)
        self.detail_content_layout.addWidget(desc_label)
        if url_button:
            self.detail_content_layout.addWidget(url_button, 0, Qt.AlignCenter)
        self.detail_content_layout.addWidget(download_frame)
        if requirements_frame:
            self.detail_content_layout.addWidget(requirements_frame)
        
        # Add space at the end
        self.detail_content_layout.addStretch()
        
        # Show detail view and hide main view
        self.main_view.hide()
        self.detail_view.show()
    
    def show_main_view(self):
        # Hide detail view and show main view
        self.detail_view.hide()
        self.main_view.show()
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.tr("browse"), self.path_input.text())
        if folder:
            self.path_input.setText(folder)
    
    def start_download(self):
        # Get download URL
        download_url = self.selected_emulator.get("download_url", "")
        if not download_url or download_url.startswith("رابط_تنزيل"):
            QMessageBox.critical(self, self.tr("error"), self.tr("invalidUrl"))
            return
            
        # Make sure download directory exists
        download_path = self.path_input.text()
        if not os.path.exists(download_path):
            try:
                os.makedirs(download_path)
            except Exception as e:
                QMessageBox.critical(self, self.tr("error"), f"{self.tr('cantCreateFolder')}{str(e)}")
                return
        
        # Start emulator download
        self.download_file(download_url, download_path)
        
        # Download requirements if checked
        if self.req_checkbox.isChecked():
            requirements = self.selected_emulator.get("requirements_urls", [])
            if requirements and not all(url.startswith("رابط_المتطلب") for url in requirements):
                for req_url in requirements:
                    if not req_url.startswith("رابط_المتطلب"):
                        self.download_file(req_url, download_path)
    
    def download_file(self, url, download_path):
        # Create progress dialog
        progress_dialog = QProgressDialog(self)
        progress_dialog.setWindowTitle(self.tr("downloadingTitle"))
        progress_dialog.setLabelText(f"{self.tr('downloading')}{os.path.basename(url)}")
        progress_dialog.setCancelButton(None)
        progress_dialog.setRange(0, 100)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setMinimumWidth(300)
        
        # Create worker and thread
        thread = QThread()
        worker = DownloaderWorker(url, download_path)
        worker.moveToThread(thread)
        
        # Connect signals
        # ربط الإشارات
        worker.progress_updated.connect(lambda current, total, name: self.update_progress(progress_dialog, current, total, name))
        worker.download_finished.connect(lambda name: self.on_download_finished(name, download_path, progress_dialog, thread))
        worker.download_error.connect(lambda err: self.on_download_error(err, progress_dialog, thread))
        
        thread.started.connect(worker.run)
        thread.start()
        
        # تخزين مراجع الخيط
        self.download_threads = getattr(self, "download_threads", []) + [(thread, worker)]
        
        progress_dialog.exec_()
    
    def update_progress(self, dialog, current, total, name):
        if total > 0:
            percent = int((current / total) * 100)
            dialog.setValue(percent)
            dialog.setLabelText(f"جاري تنزيل: {name}\n{percent}% - {current/(1024*1024):.1f} MB / {total/(1024*1024):.1f} MB")
    
    def on_download_finished(self, filename, download_path, dialog, thread):
        dialog.close()
        QMessageBox.information(self, "اكتمل التنزيل", f"تم تنزيل {filename} بنجاح")
        thread.quit()
        thread.wait()
        
        # فتح مجلد التنزيلات
        self.open_folder(download_path)
    
    def on_download_error(self, error, dialog, thread):
        dialog.close()
        QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء التنزيل: {error}")
        thread.quit()
        thread.wait()
    
    def open_folder(self, folder_path):
        # فتح مجلد في مستكشف الملفات
        if os.path.exists(folder_path):
            url = QUrl.fromLocalFile(folder_path)

class DataLoader(QObject):
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            # محاولة تحميل البيانات من الإنترنت
            response = requests.get(self.url)

            # تحليل البيانات
            data = json.loads(response.text)
            self.data_loaded.emit(data)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setLayoutDirection(Qt.RightToLeft)
    
    window = EmulatorLoaderApp()
    window.show()
    sys.exit(app.exec_())
