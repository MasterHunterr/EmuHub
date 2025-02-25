# بكل شغف من محمد بن حسين

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
                             QSizePolicy)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QUrl, QSize, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QProgressDialog

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

class EmulatorLoaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EmuHub")
        self.setMinimumSize(900, 700)
        self.setStyleSheet("background-color: #2C2F33; color: white; ")
        
        self.init_ui()
        
        self.load_data_from_online()
        
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
        
    def setup_main_view(self):
        main_layout = QVBoxLayout(self.main_view)
        
        title_label = QLabel("EmuHub")
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
        
        back_button = QPushButton("العودة")
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
            self.status_message("جاري تحميل البيانات...")
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
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الاتصال: {str(e)}")
            self.emulators_data = []
            self.display_emulators()
    
    def on_data_loaded(self, data):
        self.emulators_data = data
        self.data_thread.quit()
        self.data_thread.wait()
        self.status_message("تم تحميل البيانات بنجاح.")
        self.display_emulators()
    
    def on_data_error(self, error_msg):
        self.data_thread.quit()
        self.data_thread.wait()
        QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل البيانات: {error_msg}")
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
        
        # إذا لم تكن هناك بيانات
        if not self.emulators_data:
            no_data_label = QLabel("لا توجد بيانات متاحة. تأكد من اتصالك بالإنترنت.")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("font-size: 16px; color: #555; padding: 40px;")
            self.emulators_grid.addWidget(no_data_label, 0, 0, 1, 3)
            return
        
        # تخزين مراجع الصور
        self.pixmap_refs = []
        
        # إضافة المحاكيات إلى الشبكة (3 في كل صف)
        row, col = 0, 0
        for idx, emulator in enumerate(self.emulators_data):
            # إنشاء بطاقة المحاكي
            card = self.create_emulator_card(emulator, idx)
            self.emulators_grid.addWidget(card, row, col)
            
            # الانتقال إلى العمود التالي أو الصف التالي
            col += 1
            if col > 2:  # 3 محاكيات في كل صف
                col = 0
                row += 1
        
        # إضافة عنصر مساحة في النهاية
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.emulators_grid.addItem(spacer, row + 1, 0, 1, 3)
    
    def create_emulator_card(self, emulator, idx):
        # إنشاء بطاقة المحاكي
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
        
        # التخطيط
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        
        # الصورة
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setFixedHeight(120)
        image_label.setStyleSheet("border: none;")
        
        # تحميل الصورة
        image_url = emulator.get("image_url", "")
        if image_url and not image_url.startswith("رابط_الصورة"):
            try:
                response = requests.get(image_url)
                image_data = BytesIO(response.content)
                image = QImage.fromData(image_data.getvalue())
                pixmap = QPixmap.fromImage(image)
                pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
                self.pixmap_refs.append(pixmap)  # تخزين المرجع
            except Exception as e:
                image_label.setText("لا توجد صورة")
        else:
            image_label.setText("لا توجد صورة")
        
        # العنوان
        title = emulator.get("title", "بدون عنوان")
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")  # تعديل اللون من #333 إلى #FFFFFF
        
        # الوصف
        description = emulator.get("description", "")
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 13px; color: #BBBBBB;")  # تعديل اللون من #555 إلى #BBBBBB ليصبح أوضح
        
        # إضافة العناصر إلى التخطيط
        card_layout.addWidget(image_label)
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        card_layout.addStretch()
        
        # جعل البطاقة قابلة للنقر
        card.mousePressEvent = lambda event, idx=idx: self.show_detail_view(idx)
        
        return card
    
    def show_detail_view(self, emulator_idx):
        # الحصول على المحاكي المحدد
        self.selected_emulator = self.emulators_data[emulator_idx]
        
        # مسح محتوى الـشاشة التفصيلية
        while self.detail_content_layout.count():
            item = self.detail_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # عرض محتوى التفاصيل
        
        # الصورة
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        
        # تحميل الصورة
        image_url = self.selected_emulator.get("image_url", "")
        if image_url and not image_url.startswith("رابط_الصورة"):
            try:
                response = requests.get(image_url)
                image_data = BytesIO(response.content)
                image = QImage.fromData(image_data.getvalue())
                pixmap = QPixmap.fromImage(image)
                pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
                self.detail_pixmap = pixmap  # تخزين المرجع
            except Exception as e:
                image_label.setText("لا توجد صورة")
                image_label.setStyleSheet("font-size: 14px; color: #777; padding: 40px;")
        else:
            image_label.setText("لا توجد صورة")
            image_label.setStyleSheet("font-size: 14px; color: #777; padding: 40px;")
        
        # العنوان
        title = self.selected_emulator.get("title", "بدون عنوان")
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color:rgb(255, 255, 255); margin-top: 10px;")
        
        # الوصف
        description = self.selected_emulator.get("description", "")
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("font-size: 16px; color:rgb(252, 252, 252); margin: 5px 0;")
        
        # الرابط
        url = self.selected_emulator.get("url", "")
        url_button = None

        if url and not url.startswith("رابط_تفاصيل"):
            url_button = QPushButton("زيارة الموقع الرسمي")
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
        
        # إطار التنزيل
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
        
        # مسار التنزيل
        path_layout = QHBoxLayout()
        path_label = QLabel("مسار التنزيل:")
        path_label.setStyleSheet("font-size: 14px;")
        
        self.path_input = QLineEdit(os.path.join(os.path.expanduser("~"), "Downloads"))
        
        browse_button = QPushButton("تصفح")
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
        
        # تحميل المتطلبات
        self.req_checkbox = QCheckBox("تنزيل المتطلبات مع المحاكي")
        self.req_checkbox.setChecked(True)
        self.req_checkbox.setStyleSheet("font-size: 14px; margin: 10px 0;")
        
        # زر التنزيل
        download_button = QPushButton("تنزيل المحاكي")
        download_button.setStyleSheet("""
            QPushButton {
                background-color:rgba(0, 123, 255, 0.38); /* لون أزرق */
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color:rgba(0, 87, 179, 0.33); /* لون أزرق غامق عند التحويم */
            }
        """)

        download_button.clicked.connect(self.start_download)
        
        # إضافة العناصر إلى إطار التنزيل
        download_layout.addLayout(path_layout)
        download_layout.addWidget(self.req_checkbox)
        download_layout.addWidget(download_button, 0, Qt.AlignCenter)
        
        # قائمة المتطلبات
        requirements = self.selected_emulator.get("requirements_urls", [])
        requirements_frame = None
        
        if requirements and not all(url.startswith("رابط_المتطلب") for url in requirements):
            requirements_frame = QFrame()
            requirements_layout = QVBoxLayout(requirements_frame)
            
            req_title = QLabel(f"المتطلبات ({len(requirements)}):")
            req_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 15px;")
            requirements_layout.addWidget(req_title)
            
            for i, req_url in enumerate(requirements):
                if not req_url.startswith("رابط_المتطلب"):
                    req_name = os.path.basename(req_url)
                    req_item = QLabel(f"{i+1}. {req_name}")
                    req_item.setStyleSheet("font-size: 13px; color: #fff; margin-left: 20px;")
                    requirements_layout.addWidget(req_item)
        
        # إضافة كل العناصر إلى التخطيط التفصيلي
        self.detail_content_layout.addWidget(image_label)
        self.detail_content_layout.addWidget(title_label)
        self.detail_content_layout.addWidget(desc_label)
        if url_button:
            self.detail_content_layout.addWidget(url_button, 0, Qt.AlignCenter)
        self.detail_content_layout.addWidget(download_frame)
        if requirements_frame:
            self.detail_content_layout.addWidget(requirements_frame)
        
        # إضافة مساحة في النهاية
        self.detail_content_layout.addStretch()
        
        # إظهار عرض التفاصيل وإخفاء العرض الرئيسي
        self.main_view.hide()
        self.detail_view.show()
    
    def show_main_view(self):
        # إخفاء عرض التفاصيل وإظهار العرض الرئيسي
        self.detail_view.hide()
        self.main_view.show()
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "اختر مجلد التنزيل", self.path_input.text())
        if folder:
            self.path_input.setText(folder)
    
    def start_download(self):
        # الحصول على رابط التنزيل
        download_url = self.selected_emulator.get("download_url", "")
        if not download_url or download_url.startswith("رابط_تنزيل"):
            QMessageBox.critical(self, "خطأ", "رابط التنزيل غير صالح")
            return
        # التأكد من وجود مجلد التنزيل
        download_path = self.path_input.text()
        if not os.path.exists(download_path):
            try:
                os.makedirs(download_path)
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"لا يمكن إنشاء مجلد التنزيل: {str(e)}")
                return
        
        # بدء تنزيل المحاكي
        self.download_file(download_url, download_path)
        
        # تنزيل المتطلبات إذا تم تحديد ذلك
        if self.req_checkbox.isChecked():
            requirements = self.selected_emulator.get("requirements_urls", [])
            if requirements and not all(url.startswith("رابط_المتطلب") for url in requirements):
                for req_url in requirements:
                    if not req_url.startswith("رابط_المتطلب"):
                        self.download_file(req_url, download_path)
    
    def download_file(self, url, download_path):
        # إنشاء نافذة التقدم
        progress_dialog = QProgressDialog(self)
        progress_dialog.setWindowTitle("جاري التنزيل")
        progress_dialog.setLabelText(f"جاري تنزيل: {os.path.basename(url)}")
        progress_dialog.setCancelButton(None)
        progress_dialog.setRange(0, 100)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setMinimumWidth(300)
        
        # إنشاء العامل والخيط
        thread = QThread()
        worker = DownloaderWorker(url, download_path)
        worker.moveToThread(thread)
        
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
