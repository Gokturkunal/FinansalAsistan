#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Kişisel Finans Yöneticisi
CustomTkinter ile otomatik abonelik ve taksit takibi
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import os
import sys

# Yerel modülden veritabanı yöneticisini içe aktar
from database_managment import FinanceManager

# Grafik kütüphanelerini kontrollü import et
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import pandas as pd
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("Grafik kütüphaneleri bulunamadı. Grafik özellikleri devre dışı.")

# CustomTkinter tema ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernFinanceGUI:
    def __init__(self):
        self.finance_manager = FinanceManager()
        self.setup_main_window()
        
    def setup_main_window(self):
        """Ana pencereyi oluştur"""
        self.root = ctk.CTk()
        self.root.title("💰 Kişisel Finans Yöneticisi")
        self.root.geometry("1400x800")
        
        # Pencereyi ekranın ortasına yerleştir
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1400x800+{x}+{y}")
        
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar()
        self.create_main_content()
        self.refresh_report()
    # ModernFinanceGUI sınıfının içine bu YENİ yardımcı fonksiyonu ekle

    def _perform_archive_and_reset(self, dialog_window):
        """Arşivleme ve sıfırlama işlemlerini yürüten ana mantık."""
    
        # 1. KULLANICIDAN ONAY AL
        onay = messagebox.askyesno(
            "⚠️ Tüm Verileri Sıfırla",
            "Bu işlem, mevcut raporları (Excel ve Grafik) kaydetme seçenekleri sunacak "
            "ve ardından programdaki BÜTÜN harcama, abonelik ve taksit verilerini SİLECEKTİR.\n\n"
            "Bu işlem geri alınamaz!\n\nDevam etmek istediğinize emin misiniz?",
            icon='warning',
            parent=dialog_window # Mesajın bu pencerenin üstünde çıkmasını sağlar
        )
    
        if not onay:
            messagebox.showinfo("İptal Edildi", "Sıfırlama işlemi iptal edildi.", parent=dialog_window)
            return

    # 2. RAPORLARI DIŞA AKTAR
        try:
            self.export_report()
            if len(self.finance_manager.get_historical_reports()) >= 2:
                self.show_trend_chart()
                messagebox.showinfo("Grafik Kaydetme", "Trend grafiği yeni bir pencerede açıldı. Lütfen 'Grafiği Kaydet' butonuyla onu da kaydedip pencereyi kapatın.", parent=dialog_window)
        except Exception as e:
            messagebox.showerror("Arşivleme Hatası", f"Raporlar kaydedilirken hata oluştu: {e}", parent=dialog_window)
            return

    # 3. VERİTABANINI SIFIRLA (SON ONAY)
        son_onay = messagebox.askyesno(
            "✅ Son Onay",
            "Raporlarınızı kaydettiğinizi varsayıyoruz. Şimdi tüm veriler kalıcı olarak silinecektir. Devam edilsin mi?",
            icon='question',
            parent=dialog_window
     )

        if son_onay:
            if self.finance_manager.reset_all_data():
                # Başarılı olursa, önce yönetim penceresini kapat, sonra ana raporu yenile
                dialog_window.destroy()
                self.refresh_report()
                messagebox.showinfo("Başarılı!", "Tüm veriler başarıyla sıfırlandı. Temiz bir başlangıç yapabilirsiniz!")
            else:
                messagebox.showerror("Hata!", "Veritabanı sıfırlanırken bir hata oluştu.", parent=dialog_window)    
    # ModernFinanceGUI sınıfındaki bu fonksiyonu GÜNCELLE

    def data_management_dialog(self):
        """Veri Yönetimi seçeneklerini içeren yeni bir pencere açar."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("🗄️ Veri Yönetimi")
        dialog.geometry("500x300")
        dialog.resizable(False, False)

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"500x300+{x}+{y}")
    
        dialog.focus()
        dialog.grab_set()

        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
        title_label = ctk.CTkLabel(main_frame, text="Veri Yönetimi Seçenekleri", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(10, 20))
    
        info_label = ctk.CTkLabel(main_frame, text="Tüm verilerinizi (Excel ve Grafik) bir dosya olarak arşivlemek ve ardından programı sıfırlamak için aşağıdaki butonu kullanın.", wraplength=450)
        info_label.pack(pady=10)

        # Buton artık gerçek işlevi çağırıyor
        archive_button = ctk.CTkButton(
            main_frame, 
            text="🗄️ Arşivle ve Sıfırla", 
            # lambda kullanarak dialog penceresini fonksiyona parametre olarak gönderiyoruz
            command=lambda: self._perform_archive_and_reset(dialog),
            height=40,
            fg_color=("#C82333", "#DC3545"),
            hover_color=("#AE202D", "#C82333")
        )
        archive_button.pack(pady=20, padx=20, fill="x", side="bottom")
        
    def create_sidebar(self):
        """Sol kenar çubuğunu oluştur"""
        self.sidebar_frame = ctk.CTkFrame(self.root, width=280, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(11, weight=1)
        
        # Logo
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="💰 Finans Yöneticisi",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Gelir göstergesi
        current_income = self.finance_manager.get_monthly_income()
        self.income_label = ctk.CTkLabel(
            self.sidebar_frame,
            text=f"Aylık Gelir: {current_income:,.2f} TL",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.income_label.grid(row=1, column=0, padx=20, pady=10)
        
        # Butonlar
        self.income_button = ctk.CTkButton(
            self.sidebar_frame,
            text="💰 Gelir Ayarla",
            command=self.set_income_dialog,
            height=40
        )
        self.income_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.subscription_button = ctk.CTkButton(
            self.sidebar_frame,
            text="📺 Abonelik Ekle",
            command=self.add_subscription_dialog,
            height=40,
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#36719F", "#144870")
        )
        self.subscription_button.grid(row=3, column=0, padx=20, pady=10)
        
        self.installment_button = ctk.CTkButton(
            self.sidebar_frame,
            text="💳 Taksit Ekle",
            command=self.add_installment_dialog,
            height=40,
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#36719F", "#144870")
        )
        self.installment_button.grid(row=4, column=0, padx=20, pady=10)
        
        self.expense_button = ctk.CTkButton(
            self.sidebar_frame,
            text="💸 Gider Ekle",
            command=self.add_expense_dialog,
            height=40,
            fg_color=("#3B8ED0", "#1F6AA5"),
            hover_color=("#36719F", "#144870")
        )
        self.expense_button.grid(row=5, column=0, padx=20, pady=10)
        
        self.report_button = ctk.CTkButton(
            self.sidebar_frame,
            text="📊 Rapor Yenile",
            command=self.refresh_report,
            height=40,
            fg_color=("#28A745", "#1E7E34"),
            hover_color=("#1E7E34", "#155724")
        )
        self.report_button.grid(row=6, column=0, padx=20, pady=10)
        
        self.list_subscriptions_button = ctk.CTkButton(
            self.sidebar_frame,
            text="📋 Abonelikleri Listele",
            command=self.list_subscriptions_dialog,
            height=40,
            fg_color=("#6C757D", "#5A6268"),
            hover_color=("#5A6268", "#495057")
        )
        self.list_subscriptions_button.grid(row=7, column=0, padx=20, pady=10)
        
        self.list_installments_button = ctk.CTkButton(
            self.sidebar_frame,
            text="📋 Taksitleri Listele",
            command=self.list_installments_dialog,
            height=40,
            fg_color=("#6C757D", "#5A6268"),
            hover_color=("#5A6268", "#495057")
        )
        self.list_installments_button.grid(row=8, column=0, padx=20, pady=10)
        
        self.list_expenses_button = ctk.CTkButton(
            self.sidebar_frame,
            text="📋 Giderleri Listele",
            command=self.list_expenses_dialog,
            height=40,
            fg_color=("#6C757D", "#5A6268"),
            hover_color=("#5A6268", "#495057")
        )
        self.list_expenses_button.grid(row=9, column=0, padx=20, pady=10)
        
        if PLOTTING_AVAILABLE:
            self.chart_button = ctk.CTkButton(
                self.sidebar_frame,
                text="📈 Trend Grafiği",
                command=self.show_trend_chart,
                height=40,
                fg_color=("#FF6B6B", "#E55454"),
                hover_color=("#E55454", "#CC4B4B")
            )
            self.chart_button.grid(row=10, column=0, padx=20, pady=10)
            
            self.export_button = ctk.CTkButton(
                self.sidebar_frame,
                text="📄 Excel'e Aktar",
                command=self.export_report,
                height=40,
                fg_color=("#6C757D", "#5A6268"),
                hover_color=("#5A6268", "#495057")
            )
            self.export_button.grid(row=11, column=0, padx=20, pady=(10, 20)) 
            
            self.data_management_button = ctk.CTkButton(
            self.sidebar_frame,
            text="🗄️ Veri Yönetimi",
            command=self.data_management_dialog,
            height=40,
            fg_color=("#17A2B8", "#138496"),
            hover_color=("#138496", "#117A8B")
            )
            self.data_management_button.grid(row=12, column=0, padx=20, pady=(10, 20))







    
    def create_main_content(self):
        """Ana içerik alanını oluştur"""
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(20, 20), pady=(20, 20))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="📊 Aylık Finansal Rapor",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.report_textbox = ctk.CTkTextbox(
            self.main_frame,
            width=600,
            height=500,
            font=ctk.CTkFont(family="Courier New", size=13)
        )
        self.report_textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def set_income_dialog(self):
        """Gelir ayarlama diyalogu"""
        current_income = self.finance_manager.get_monthly_income()
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("💰 Aylık Gelir Ayarla")
        dialog.geometry("450x300")
        dialog.resizable(False, False)
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"450x300+{x}+{y}")
        
        dialog.focus()
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="💰 Aylık Gelirinizi Girin",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        current_label = ctk.CTkLabel(
            main_frame,
            text=f"Mevcut Gelir: {current_income:,.2f} TL",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray70")
        )
        current_label.pack(pady=5)
        
        income_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Örn: 15000",
            width=250,
            height=45,
            font=ctk.CTkFont(size=16),
            justify="center"
        )
        income_entry.pack(pady=20)
        income_entry.insert(0, str(current_income))
        income_entry.focus()
        income_entry.select_range(0, 'end')
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=15)
        
        def save_income():
            try:
                income_text = income_entry.get().strip()
                if not income_text:
                    messagebox.showerror("Hata", "Lütfen bir gelir miktarı girin!")
                    return
                    
                income = float(income_text)
                if income < 0:
                    messagebox.showerror("Hata", "Gelir negatif olamaz!")
                    return
                
                if self.finance_manager.set_monthly_income(income):
                    self.income_label.configure(text=f"Aylık Gelir: {income:,.2f} TL")
                    messagebox.showinfo("Başarılı", f"✅ Aylık gelir {income:,.2f} TL olarak güncellendi!")
                    dialog.destroy()
                    self.refresh_report()
                else:
                    messagebox.showerror("Hata", "Gelir güncellenirken bir hata oluştu!")
                    
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin!")
        
        def on_enter(event):
            save_income()
        
        income_entry.bind('<Return>', on_enter)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 Kaydet",
            command=save_income,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#28A745", "#1E7E34")
        )
        save_button.pack(side="left", padx=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="❌ İptal",
            command=dialog.destroy,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#DC3545", "#C82333")
        )
        cancel_button.pack(side="left", padx=10)

    def add_subscription_dialog(self):
        """Abonelik ekleme diyalogu"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("📺 Yeni Abonelik Ekle")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")
        
        dialog.focus()
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="📺 Yeni Abonelik Ekle",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        name_label = ctk.CTkLabel(main_frame, text="Abonelik Adı:", font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(pady=(10, 5))
        
        name_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Örn: Netflix, Spotify, YouTube Premium...",
            width=350,
            height=45,
            font=ctk.CTkFont(size=14)
        )
        name_entry.pack(pady=5)
        name_entry.focus()
        
        amount_label = ctk.CTkLabel(main_frame, text="Aylık Tutar (TL):", font=ctk.CTkFont(size=16, weight="bold"))
        amount_label.pack(pady=(20, 5))
        
        amount_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Örn: 39.99",
            width=350,
            height=45,
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        amount_entry.pack(pady=5)
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=15)
        
       # add_subscription_dialog içindeki bu fonksiyonu GÜNCELLE
        
        def save_subscription():
            try:
                name = name_entry.get()
                amount_text = amount_entry.get().strip()
                
                # --- YENİ EKLENEN DOĞRULAMA ---
                if not self.is_valid_name(name, "Abonelik"):
                    name_entry.focus()
                    return
                # --- BİTTİ ---
                
                if not amount_text:
                    messagebox.showerror("Hata", "❌ Lütfen bir tutar girin!")
                    amount_entry.focus()
                    return
                
                amount = float(amount_text)
                
                if amount <= 0:
                    messagebox.showerror("Hata", "❌ Tutar sıfırdan büyük olmalıdır!")
                    amount_entry.focus()
                    return
                
                start_date = datetime.now().strftime("%Y-%m-%d")
                
                # İsmi, başındaki/sonundaki boşlukları temizleyerek kaydet
                if self.finance_manager.add_subscription(name.strip(), amount, start_date):
                    messagebox.showinfo("Başarılı", f"✅ {name.strip()} aboneliği başarıyla eklendi!\n💰 Aylık: {amount:,.2f} TL")
                    dialog.destroy()
                    self.refresh_report()
                else:
                    messagebox.showerror("Hata", "❌ Abonelik eklenirken bir hata oluştu!")
                    
            except ValueError:
                messagebox.showerror("Hata", "❌ Geçerli bir tutar girin!")
                amount_entry.focus()
            except Exception as e:
                messagebox.showerror("Hata", f"❌ Bir hata oluştu: {str(e)}")

        def on_enter(event):
            if event.widget == name_entry:
                amount_entry.focus()
            elif event.widget == amount_entry:
                save_subscription()
        
        name_entry.bind('<Return>', on_enter)
        amount_entry.bind('<Return>', on_enter)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 Kaydet",
            command=save_subscription,
            width=140,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#28A745", "#1E7E34")
        )
        save_button.pack(side="left", padx=15)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="❌ İptal",
            command=dialog.destroy,
            width=140,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#DC3545", "#C82333")
        )
        cancel_button.pack(side="left", padx=15)

    def add_installment_dialog(self):
        """Taksit ekleme diyalogu"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("💳 Yeni Taksit Ekle")
        dialog.geometry("550x600")
        dialog.resizable(False, False)
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"550x600+{x}+{y}")
        
        dialog.focus()
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="💳 Yeni Taksit Ekle",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        name_label = ctk.CTkLabel(main_frame, text="Taksit Adı:", font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(pady=(10, 5))
        
        name_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Örn: Kredi Kartı, Araç Kredisi, Telefon Taksit...",
            width=400,
            height=45,
            font=ctk.CTkFont(size=14)
        )
        name_entry.pack(pady=5)
        name_entry.focus()
        
        total_label = ctk.CTkLabel(main_frame, text="Toplam Tutar (TL):", font=ctk.CTkFont(size=16, weight="bold"))
        total_label.pack(pady=(20, 5))
        
        total_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Örn: 12000",
            width=400,
            height=45,
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        total_entry.pack(pady=5)
        
        months_label = ctk.CTkLabel(main_frame, text="Taksit Sayısı (Ay):", font=ctk.CTkFont(size=16, weight="bold"))
        months_label.pack(pady=(20, 5))
        
        months_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Örn: 12",
            width=400,
            height=45,
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        months_entry.pack(pady=5)
        
        monthly_frame = ctk.CTkFrame(main_frame, fg_color=("#E8F5E8", "#2D5A2D"))
        monthly_frame.pack(pady=20, padx=20, fill="x")
        
        monthly_label = ctk.CTkLabel(
            monthly_frame,
            text="💰 Aylık Tutar: 0.00 TL",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#1E7E34", "#4CAF50")
        )
        monthly_label.pack(pady=15)
        
        def calculate_monthly(*args):
            """Aylık taksit tutarını hesaplar ve görüntüler."""
            try:
                total_text = total_entry.get().strip()
                months_text = months_entry.get().strip()
                
                if total_text and months_text:
                    total = float(total_text)
                    months = int(months_text)
                    if total > 0 and months > 0:
                        monthly = total / months
                        monthly_label.configure(text=f"💰 Aylık Tutar: {monthly:,.2f} TL")
                        return
                
                monthly_label.configure(text="💰 Aylık Tutar: 0.00 TL")
            except ValueError:
                monthly_label.configure(text="💰 Aylık Tutar: ⚠️ Geçersiz değer")
            except Exception as e:
                print(f"Hesaplama hatası: {e}")
                monthly_label.configure(text="💰 Aylık Tutar: ❌ Hata")
        
        total_entry.bind("<KeyRelease>", calculate_monthly)
        months_entry.bind("<KeyRelease>", calculate_monthly)
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=15)
        
        # add_installment_dialog içindeki bu fonksiyonu GÜNCELLE
        
        def save_installment():
            try:
                name = name_entry.get()
                total_text = total_entry.get().strip()
                months_text = months_entry.get().strip()
                
                # --- YENİ EKLENEN DOĞRULAMA ---
                if not self.is_valid_name(name, "Taksit"):
                    name_entry.focus()
                    return
                # --- BİTTİ ---

                if not total_text:
                    messagebox.showerror("Hata", "❌ Lütfen toplam tutarı girin!")
                    total_entry.focus()
                    return
                
                if not months_text:
                    messagebox.showerror("Hata", "❌ Lütfen taksit sayısını girin!")
                    months_entry.focus()
                    return
                
                total_amount = float(total_text)
                total_months = int(months_text)
                
                if total_amount <= 0:
                    messagebox.showerror("Hata", "❌ Toplam tutar sıfırdan büyük olmalıdır!")
                    total_entry.focus()
                    return
                
                if total_months <= 0:
                    messagebox.showerror("Hata", "❌ Taksit sayısı sıfırdan büyük olmalıdır!")
                    months_entry.focus()
                    return
                
                monthly_amount = total_amount / total_months
                start_date = datetime.now().strftime("%Y-%m-%d")
                
                if self.finance_manager.add_installment(name.strip(), total_amount, monthly_amount, 
                                                        total_months, start_date):
                    messagebox.showinfo("Başarılı", 
                        f"✅ {name.strip()} taksiti başarıyla eklendi!\n" +
                        f"💰 Toplam: {total_amount:,.2f} TL\n" +
                        f"📅 {total_months} ay\n" +
                        f"💳 Aylık: {monthly_amount:,.2f} TL")
                    dialog.destroy()
                    self.refresh_report()
                else:
                    messagebox.showerror("Hata", "❌ Taksit eklenirken bir hata oluştu!")
                    
            except ValueError:
                messagebox.showerror("Hata", "❌ Lütfen geçerli sayısal değerler girin!")
            except Exception as e:
                messagebox.showerror("Hata", f"❌ Bir hata oluştu: {str(e)}")
        
        def on_enter(event):
            if event.widget == name_entry:
                total_entry.focus()
            elif event.widget == total_entry:
                months_entry.focus()
            elif event.widget == months_entry:
                save_installment()
        
        name_entry.bind('<Return>', on_enter)
        total_entry.bind('<Return>', on_enter)
        months_entry.bind('<Return>', on_enter)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 Kaydet",
            command=save_installment,
            width=150,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#28A745", "#1E7E34")
        )
        save_button.pack(side="left", padx=15)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="❌ İptal",
            command=dialog.destroy,
            width=150,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#DC3545", "#C82333")
        )
        cancel_button.pack(side="left", padx=15)

    def add_expense_dialog(self):
        """Gider ekleme diyalogu"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("💸 Ekstra Gider Ekle")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"500x600+{x}+{y}")
        
        dialog.focus()
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="💸 Ekstra Gider Ekle",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        name_label = ctk.CTkLabel(main_frame, text="Gider Açıklaması:", font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(pady=(10, 5))
        
        name_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Örn: Market alışverişi, Benzin, Yemek...",
            width=400,
            height=45,
            font=ctk.CTkFont(size=14)
        )
        name_entry.pack(pady=5)
        name_entry.focus()
        
        amount_label = ctk.CTkLabel(main_frame, text="Tutar (TL):", font=ctk.CTkFont(size=16, weight="bold"))
        amount_label.pack(pady=(20, 5))
        
        amount_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Örn: 150.50",
            width=400,
            height=45,
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        amount_entry.pack(pady=5)
        
        category_label = ctk.CTkLabel(main_frame, text="Kategori:", font=ctk.CTkFont(size=16, weight="bold"))
        category_label.pack(pady=(20, 5))
        
        category_combo = ctk.CTkComboBox(
            main_frame,
            values=["Diğer", "🛒 Market", "🚗 Ulaşım", "🍽️ Yemek", "🎬 Eğlence", 
                    "💊 Sağlık", "👕 Kıyafet", "💻 Teknoloji", "📚 Eğitim", "🏠 Ev"],
            width=400,
            height=45,
            font=ctk.CTkFont(size=14),
            state="readonly"
        )
        category_combo.pack(pady=5)
        category_combo.set("Diğer")
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=15)
        
        # add_expense_dialog içindeki bu fonksiyonu GÜNCELLE

        def save_expense():
            try:
                name = name_entry.get()
                amount_text = amount_entry.get().strip()
                category = category_combo.get()
                
                # --- YENİ EKLENEN DOĞRULAMA ---
                if not self.is_valid_name(name, "Gider"):
                    name_entry.focus()
                    return
                # --- BİTTİ ---
                
                if not amount_text:
                    messagebox.showerror("Hata", "❌ Lütfen bir tutar girin!")
                    amount_entry.focus()
                    return
                
                amount = float(amount_text)
                
                if amount <= 0:
                    messagebox.showerror("Hata", "❌ Tutar sıfırdan büyük olmalıdır!")
                    amount_entry.focus()
                    return
                
                expense_date = datetime.now().strftime("%Y-%m-%d")
                
                if self.finance_manager.add_extra_expense(name.strip(), amount, expense_date, category):
                    messagebox.showinfo("Başarılı", 
                        f"✅ Gider başarıyla eklendi!\n" +
                        f"📝 {name.strip()}\n" +
                        f"💰 {amount:,.2f} TL\n" +
                        f"📂 {category}")
                    dialog.destroy()
                    self.refresh_report()
                else:
                    messagebox.showerror("Hata", "❌ Gider eklenirken bir hata oluştu!")
                    
            except ValueError:
                messagebox.showerror("Hata", "❌ Geçerli bir tutar girin!")
                amount_entry.focus()
            except Exception as e:
                messagebox.showerror("Hata", f"❌ Bir hata oluştu: {str(e)}")
        
        def on_enter(event):
            if event.widget == name_entry:
                amount_entry.focus()
            elif event.widget == amount_entry:
                save_expense()
        
        name_entry.bind('<Return>', on_enter)
        amount_entry.bind('<Return>', on_enter)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 Kaydet",
            command=save_expense,
            width=150,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#28A745", "#1E7E34")
        )
        save_button.pack(side="left", padx=15)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="❌ İptal",
            command=dialog.destroy,
            width=150,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#DC3545", "#C82333")
        )
        cancel_button.pack(side="left", padx=15)
        
    # ModernFinanceGUI sınıfındaki bu fonksiyonu GÜNCELLE

    def list_subscriptions_dialog(self):
        """Abonelikleri listele diyalogu (Düzenle butonu eklendi)"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("📋 Abonelik Listesi")
        dialog.geometry("800x600")
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"800x600+{x}+{y}")
        
        dialog.focus()
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(main_frame, text="📋 Tüm Abonelikler", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(pady=(20, 20))
        
        list_frame = ctk.CTkScrollableFrame(main_frame, height=400)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        def refresh_list():
            """Diyalog içindeki listeyi yeniden yükler."""
            # Önceki widgetları temizle
            for widget in list_frame.winfo_children():
                widget.destroy()
            
            subscriptions = self.finance_manager.get_all_subscriptions()
            
            if not subscriptions:
                no_data_label = ctk.CTkLabel(list_frame, text="📭 Henüz abonelik eklenmemiş.", font=ctk.CTkFont(size=16), text_color=("gray50", "gray70"))
                no_data_label.pack(pady=50)
            else:
                for sub in subscriptions:
                    sub_id, name, amount, start_date, end_date, is_active = sub
                    card_frame = ctk.CTkFrame(list_frame)
                    card_frame.pack(fill="x", padx=10, pady=5)
                    
                    info_text = f"📺 {name} - 💰 {amount:,.2f} TL/ay"
                    status_text = "✅ Aktif" if is_active else "❌ Pasif"
                    status_color = ("#28A745", "#1E7E34") if is_active else ("#DC3545", "#C82333")
                    
                    status_label = ctk.CTkLabel(card_frame, text=status_text, font=ctk.CTkFont(size=14, weight="bold"), text_color=status_color)
                    status_label.pack(side="left", padx=10, pady=10)

                    info_label = ctk.CTkLabel(card_frame, text=info_text, font=ctk.CTkFont(size=14), anchor="w")
                    info_label.pack(side="left", padx=10, pady=10, expand=True, fill="x")
                    
                    def create_delete_command(s_id, s_name):
                        def delete():
                            if messagebox.askyesno("Onay", f"'{s_name}' aboneliğini silmek istediğinize emin misiniz?"):
                                if self.finance_manager.delete_subscription(s_id):
                                    messagebox.showinfo("Başarılı", "✅ Abonelik silindi!")
                                    refresh_list()
                                    self.refresh_report()
                                else:
                                    messagebox.showerror("Hata", "❌ Abonelik silinirken hata oluştu!")
                        return delete

                    delete_button = ctk.CTkButton(card_frame, text="🗑️ Sil", command=create_delete_command(sub_id, name), width=80, height=30, fg_color=("#DC3545", "#C82333"))
                    delete_button.pack(side="right", padx=5, pady=10)

                    # --- YENİ DÜZENLE BUTONU ---
                    def create_edit_command(s_id, s_name, s_amount, s_end_date):
                        def edit():
                            self.edit_subscription_dialog(s_id, s_name, s_amount, s_end_date, refresh_list)
                        return edit

                    edit_button = ctk.CTkButton(card_frame, text="✏️ Düzenle", command=create_edit_command(sub_id, name, amount, end_date), width=90, height=30, fg_color=("#FF9800", "#F57C00"))
                    edit_button.pack(side="right", padx=5, pady=10)
        
        refresh_list() # Listeyi ilk kez yükle

        close_button = ctk.CTkButton(main_frame, text="❌ Kapat", command=dialog.destroy, height=40, font=ctk.CTkFont(size=15, weight="bold"))
        close_button.pack(side="bottom", pady=(15,0), fill="x", padx=20)
    # ModernFinanceGUI sınıfının içine bu YENİ fonksiyonu ekle

    def edit_subscription_dialog(self, sub_id, name, amount, end_date, refresh_callback):
        """Abonelik düzenleme diyalogu"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("✏️ Abonelik Düzenle")
        dialog.geometry("500x500")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(main_frame, text="✏️ Abonelik Düzenle", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(pady=(10, 20))
        
        ctk.CTkLabel(main_frame, text="Abonelik Adı:", font=ctk.CTkFont(size=16)).pack(pady=(10, 5), anchor="w")
        name_entry = ctk.CTkEntry(main_frame, width=400, height=45)
        name_entry.pack(fill="x")
        name_entry.insert(0, name)
        
        ctk.CTkLabel(main_frame, text="Aylık Tutar (TL):", font=ctk.CTkFont(size=16)).pack(pady=(10, 5), anchor="w")
        amount_entry = ctk.CTkEntry(main_frame, width=400, height=45)
        amount_entry.pack(fill="x")
        amount_entry.insert(0, str(amount))
        
        ctk.CTkLabel(main_frame, text="Bitiş Tarihi (YYYY-AA-GG, süresiz ise boş bırakın):", font=ctk.CTkFont(size=16)).pack(pady=(10, 5), anchor="w")
        end_date_entry = ctk.CTkEntry(main_frame, width=400, height=45)
        end_date_entry.pack(fill="x")
        if end_date:
            end_date_entry.insert(0, end_date)

        def save_changes():
            new_name = name_entry.get()
            new_amount_str = amount_entry.get().strip()
            new_end_date = end_date_entry.get().strip()

            if not self.is_valid_name(new_name, "Abonelik"):
                return
            
            try:
                new_amount = float(new_amount_str)
                if new_amount <= 0:
                    messagebox.showerror("Hata", "Tutar sıfırdan büyük olmalıdır!", parent=dialog)
                    return
            except ValueError:
                messagebox.showerror("Hata", "Geçerli bir tutar girin!", parent=dialog)
                return

            if new_end_date:
                try:
                    datetime.strptime(new_end_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Hata", "Geçerli tarih formatı YYYY-AA-GG olmalıdır!", parent=dialog)
                    return
            
            if self.finance_manager.update_subscription(sub_id, new_name.strip(), new_amount, new_end_date):
                messagebox.showinfo("Başarılı", "✅ Abonelik güncellendi!", parent=dialog)
                dialog.destroy()
                refresh_callback()
                self.refresh_report()
            else:
                messagebox.showerror("Hata", "❌ Güncelleme sırasında bir hata oluştu!", parent=dialog)

        save_button = ctk.CTkButton(main_frame, text="💾 Değişiklikleri Kaydet", command=save_changes, height=45)
        save_button.pack(pady=(30, 10), fill="x")    
        
    # ModernFinanceGUI sınıfındaki bu fonksiyonu GÜNCELLE

    def list_installments_dialog(self):
        """Taksitleri listele diyalogu (Tek, güçlü Düzenle butonu ile güncellendi)"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("📋 Taksit Listesi")
        dialog.geometry("900x600")
        dialog.grab_set()

        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(main_frame, text="📋 Tüm Taksitler", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(pady=(20, 20))
        
        list_frame = ctk.CTkScrollableFrame(main_frame, height=400)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        def refresh_list():
            for widget in list_frame.winfo_children():
                widget.destroy()

            installments = self.finance_manager.get_all_installments()
            
            if not installments:
                ctk.CTkLabel(list_frame, text="📭 Henüz taksit eklenmemiş.", font=ctk.CTkFont(size=16), text_color=("gray50", "gray70")).pack(pady=50)
            else:
                for inst in installments:
                    inst_id, name, total, monthly, total_m, remain_m, is_active = inst
                    card_frame = ctk.CTkFrame(list_frame)
                    card_frame.pack(fill="x", padx=10, pady=5)

                    status_text = f"✅ Aktif ({remain_m} ay kaldı)" if is_active else " Bitti"
                    info_text = f"💳 {name} - 💵 Aylık: {monthly:,.2f} TL"

                    status_label = ctk.CTkLabel(card_frame, text=status_text, font=ctk.CTkFont(size=12, weight="bold"))
                    status_label.pack(side="left", padx=10, pady=10)

                    info_label = ctk.CTkLabel(card_frame, text=info_text, font=ctk.CTkFont(size=14), anchor="w")
                    info_label.pack(side="left", padx=10, pady=10, expand=True, fill="x")

                    def create_delete_command(i_id, i_name):
                        def delete():
                            if messagebox.askyesno("Onay", f"'{i_name}' taksidini tamamen silmek istediğinize emin misiniz? Bu işlem geri alınamaz.", parent=dialog):
                                if self.finance_manager.delete_installment(i_id):
                                    messagebox.showinfo("Başarılı", "✅ Taksit silindi!", parent=dialog)
                                    refresh_list()
                                    self.refresh_report()
                        return delete

                    delete_button = ctk.CTkButton(card_frame, text="🗑️ Sil", command=create_delete_command(inst_id, name), width=60, height=30, fg_color=("#DC3545", "#C82333"))
                    delete_button.pack(side="right", padx=5, pady=10)

                    if is_active:
                        def create_edit_command(inst_data):
                            def edit():
                                self.edit_installment_dialog(inst_data, refresh_list)
                            return edit
                            
                        edit_button = ctk.CTkButton(card_frame, text="✏️ Düzenle", command=create_edit_command(inst), width=120, height=30, fg_color=("#FF9800", "#F57C00"))
                        edit_button.pack(side="right", padx=5, pady=10)

        refresh_list()

        close_button = ctk.CTkButton(main_frame, text="❌ Kapat", command=dialog.destroy, height=40)
        close_button.pack(side="bottom", pady=(15,0), fill="x", padx=20)
    # ModernFinanceGUI sınıfının içine bu YENİ fonksiyonu ekle

    # ModernFinanceGUI sınıfına bu YENİ ve KAPSAMLI fonksiyonu ekle
# (Eski edit_installment_name_dialog fonksiyonunu silebilirsin)

    def edit_installment_dialog(self, inst_data, refresh_callback):
        """Gelişmiş taksit düzenleme diyalogu"""
        inst_id, name, _, _, _, remaining_months, _ = inst_data
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"✏️ Taksit Düzenle: {name}")
        dialog.geometry("550x550")
        dialog.resizable(False, False)
        dialog.grab_set()

        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- BÖLÜM 1: İsim Düzenleme ---
        name_frame = ctk.CTkFrame(main_frame)
        name_frame.pack(fill="x", pady=(10, 20))
        
        ctk.CTkLabel(name_frame, text="Taksit Adı", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10,5))
        name_entry = ctk.CTkEntry(name_frame, placeholder_text="Yeni taksit adı", height=40)
        name_entry.pack(fill="x", padx=15)
        name_entry.insert(0, name)

        def save_name_change():
            new_name = name_entry.get()
            if new_name != name and self.is_valid_name(new_name, "Taksit"):
                if self.finance_manager.update_installment_name(inst_id, new_name.strip()):
                    messagebox.showinfo("Başarılı", "✅ Taksit adı güncellendi!", parent=dialog)
                    dialog.destroy()
                    refresh_callback()
                    self.refresh_report()
                else:
                    messagebox.showerror("Hata", "Ad güncellenirken bir hata oluştu.", parent=dialog)

        save_name_button = ctk.CTkButton(name_frame, text="Adı Değiştir", command=save_name_change)
        save_name_button.pack(pady=(10,15), padx=15, fill="x")

        # --- BÖLÜM 2: Erken Ödeme ---
        payment_frame = ctk.CTkFrame(main_frame, fg_color=("#2E2E2E", "#343A40"))
        payment_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(payment_frame, text="Erken Ödeme Seçenekleri", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10,5))
        ctk.CTkLabel(payment_frame, text=f"Kalan Ay: {remaining_months}", font=ctk.CTkFont(size=14)).pack()

        # Kısmi Ödeme
        partial_frame = ctk.CTkFrame(payment_frame, fg_color="transparent")
        partial_frame.pack(pady=10, padx=15, fill="x")
        
        ctk.CTkLabel(partial_frame, text="Ödenecek Ay Sayısı:").pack(side="left")
        months_entry = ctk.CTkEntry(partial_frame, width=80)
        months_entry.pack(side="left", padx=10, expand=True, fill="x")

        def perform_partial_payment():
            try:
                months_to_pay = int(months_entry.get())
                if not (1 <= months_to_pay <= remaining_months):
                    messagebox.showerror("Hata", f"Lütfen 1 ile {remaining_months} arasında geçerli bir ay sayısı girin.", parent=dialog)
                    return
                
                if messagebox.askyesno("Onay", f"{months_to_pay} aylık erken ödeme yapmak istediğinize emin misiniz?", parent=dialog):
                    if self.finance_manager.make_partial_payment(inst_id, months_to_pay):
                        messagebox.showinfo("Başarılı", f"✅ {months_to_pay} aylık ödeme yapıldı!", parent=dialog)
                        dialog.destroy()
                        refresh_callback()
                        self.refresh_report()
            except (ValueError, TypeError):
                messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin.", parent=dialog)
        
        partial_button = ctk.CTkButton(partial_frame, text="Kısmi Öde", command=perform_partial_payment)
        partial_button.pack(side="left", padx=10)
        
        # Tamamını Kapatma
        def perform_full_payoff():
            if messagebox.askyesno("Onay", f"'{name}' taksidinin tamamını kapatmak istediğinize emin misiniz?", parent=dialog):
                if self.finance_manager.close_installment_early(inst_id):
                    messagebox.showinfo("Başarılı", "✅ Taksit tamamen kapatıldı!", parent=dialog)
                    dialog.destroy()
                    refresh_callback()
                    self.refresh_report()

        full_payoff_button = ctk.CTkButton(payment_frame, text="Taksidin Tamamını Kapat", command=perform_full_payoff, height=45, fg_color=("#28A745", "#1E7E34"))
        full_payoff_button.pack(pady=15, padx=15, fill="x")

    def list_expenses_dialog(self):
        """DEĞİŞTİRİLDİ: Ekstra giderleri listele diyalogu (Sadece mevcut yılı gösterir)"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("📋 Ekstra Gider Listesi")
        dialog.geometry("1000x700")
        
        # Pencereyi ortala
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (1000 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"1000x700+{x}+{y}")
        
        dialog.focus()
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(main_frame, text="📋 Ekstra Giderler", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(pady=(20, 10))
        
        # Filtre çerçevesi
        filter_frame = ctk.CTkFrame(main_frame)
        filter_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # --- YENİ AY FİLTRESİ MANTIĞI ---
        month_label = ctk.CTkLabel(filter_frame, text="Ay:", font=ctk.CTkFont(size=14, weight="bold"))
        month_label.pack(side="left", padx=(20, 5), pady=15)
        
        months_list = ["Tümü"]
        today = date.today()
        # Mevcut ayın numarasını al (Örn: Haziran için 6)
        # Sadece bu yılın başından bugüne kadar olan ayları listele
        for i in range(today.month):
            current_month = today - relativedelta(months=i)
            months_list.append(current_month.strftime("%Y-%m"))
        # --- BİTTİ ---

        month_combo = ctk.CTkComboBox(filter_frame, values=months_list, width=200, state="readonly")
        month_combo.pack(side="left", padx=5, pady=15)
        month_combo.set("Tümü")
        
        # Kategori seçici
        category_label = ctk.CTkLabel(filter_frame, text="Kategori:", font=ctk.CTkFont(size=14, weight="bold"))
        category_label.pack(side="left", padx=(20, 5), pady=15)
        
        category_combo = ctk.CTkComboBox(
            filter_frame,
            values=["Tümü", "💳 Taksit Ödemesi", "🛒 Market", "🚗 Ulaşım", "🍽️ Yemek", "🎬 Eğlence", "💊 Sağlık", "👕 Kıyafet", "💻 Teknoloji", "📚 Eğitim", "🏠 Ev", "Diğer"],
            width=150,
            state="readonly"
        )
        category_combo.pack(side="left", padx=5, pady=15)
        category_combo.set("Tümü")
        
        # Özet bilgi çerçevesi
        summary_frame = ctk.CTkFrame(main_frame, fg_color=("#E3F2FD", "#1E3A8A"))
        summary_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        summary_label = ctk.CTkLabel(
            summary_frame,
            text="💰 Toplam: 0.00 TL | 📊 Kayıt: 0 adet",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        summary_label.pack(pady=15)
        
        # Liste çerçevesi
        list_frame = ctk.CTkScrollableFrame(main_frame, height=350)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        def load_expenses():
            """Giderleri yükle ve listele (Bu kısımda değişiklik yok)"""
            for widget in list_frame.winfo_children():
                widget.destroy()
            
            selected_month_str = month_combo.get()
            selected_category = category_combo.get()
            
            year, month = None, None
            if selected_month_str != "Tümü":
                year, month = map(int, selected_month_str.split('-'))

            expenses = self.finance_manager.get_all_extra_expenses(year, month, selected_category)
            
            if not expenses:
                no_data_label = ctk.CTkLabel(list_frame, text="📭 Seçilen kriterlere uygun gider bulunamadı.", font=ctk.CTkFont(size=16), text_color=("gray50", "gray70"))
                no_data_label.pack(pady=50)
                summary_label.configure(text="💰 Toplam: 0.00 TL | 📊 Kayıt: 0 adet")
                return
            
            total_amount = sum(exp[2] for exp in expenses)
            count = len(expenses)
            summary_label.configure(text=f"💰 Toplam: {total_amount:,.2f} TL | 📊 Kayıt: {count} adet")
            
            for exp in expenses:
                exp_id, name, amount, expense_date_str, category_name = exp
                
                card_frame = ctk.CTkFrame(list_frame)
                card_frame.pack(fill="x", padx=10, pady=5)
                
                try:
                    date_obj = datetime.strptime(expense_date_str, "%Y-%m-%d")
                    date_text = date_obj.strftime("%d.%m.%Y")
                except:
                    date_text = expense_date_str
                
                date_label = ctk.CTkLabel(card_frame, text=f"📅 {date_text}", font=ctk.CTkFont(size=12, weight="bold"), text_color=("#2196F3", "#64B5F6"))
                date_label.pack(side="left", padx=10, pady=10)
                
                category_label_widget = ctk.CTkLabel(card_frame, text=f"📂 {category_name}", font=ctk.CTkFont(size=12), text_color=("#FF9800", "#FFB74D"))
                category_label_widget.pack(side="left", padx=10, pady=10)
                
                info_text = f"💸 {name} - 💰 {amount:,.2f} TL"
                info_label = ctk.CTkLabel(card_frame, text=info_text, font=ctk.CTkFont(size=14))
                info_label.pack(side="left", padx=10, pady=10, expand=True, fill="x")
                
                def create_edit_command(exp_id_to_edit, exp_data):
                    def edit():
                        self.edit_expense_dialog(exp_id_to_edit, exp_data, load_expenses)
                    return edit
                
                edit_button = ctk.CTkButton(card_frame, text="✏️ Düzenle", command=create_edit_command(exp_id, (name, amount, expense_date_str, category_name)), width=90, height=30, fg_color=("#FF9800", "#F57C00"))
                edit_button.pack(side="right", padx=5, pady=10)
                
                def create_delete_command(exp_id_to_delete, exp_name):
                    def delete():
                        if messagebox.askyesno("Onay", f"'{exp_name}' giderini silmek istediğinize emin misiniz?"):
                            if self.finance_manager.delete_extra_expense(exp_id_to_delete):
                                messagebox.showinfo("Başarılı", "✅ Gider silindi!")
                                load_expenses()
                                self.refresh_report()
                            else:
                                messagebox.showerror("Hata", "❌ Gider silinirken hata oluştu!")
                    return delete
                
                delete_button = ctk.CTkButton(card_frame, text="🗑️ Sil", command=create_delete_command(exp_id, name), width=80, height=30, fg_color=("#DC3545", "#C82333"))
                delete_button.pack(side="right", padx=5, pady=10)
        
        # Filtrele butonu
        filter_button = ctk.CTkButton(filter_frame, text="🔍 Filtrele", width=100, height=35, fg_color=("#2196F3", "#1976D2"), command=load_expenses)
        filter_button.pack(side="left", padx=20, pady=15)
        
        # İlk yükleme
        load_expenses()

    def edit_expense_dialog(self, expense_id, expense_data, refresh_callback):
        """Gider düzenleme diyalogu"""
        name, amount, expense_date, category = expense_data
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("✏️ Gider Düzenle")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"500x600+{x}+{y}")
        
        dialog.focus()
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(main_frame, text="✏️ Gider Düzenle", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(pady=(20, 30))
        
        current_label = ctk.CTkLabel(main_frame, text=f"Düzenlenen: {name} - {amount:,.2f} TL", font=ctk.CTkFont(size=14), text_color=("gray50", "gray70"))
        current_label.pack(pady=10)
        
        name_label = ctk.CTkLabel(main_frame, text="Gider Açıklaması:", font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(pady=(10, 5))
        
        name_entry = ctk.CTkEntry(main_frame, placeholder_text="Gider açıklaması...", width=400, height=45, font=ctk.CTkFont(size=14))
        name_entry.pack(pady=5)
        name_entry.insert(0, name)
        name_entry.focus()
        
        amount_label = ctk.CTkLabel(main_frame, text="Tutar (TL):", font=ctk.CTkFont(size=16, weight="bold"))
        amount_label.pack(pady=(20, 5))
        
        amount_entry = ctk.CTkEntry(main_frame, placeholder_text="Tutar...", width=400, height=45, font=ctk.CTkFont(size=14), justify="center")
        amount_entry.pack(pady=5)
        amount_entry.insert(0, str(amount))
        
        date_label = ctk.CTkLabel(main_frame, text="Tarih (YYYY-MM-DD):", font=ctk.CTkFont(size=16, weight="bold"))
        date_label.pack(pady=(20, 5))
        
        date_entry = ctk.CTkEntry(main_frame, placeholder_text="YYYY-AA-GG", width=400, height=45, font=ctk.CTkFont(size=14), justify="center")
        date_entry.pack(pady=5)
        date_entry.insert(0, expense_date)
        
        category_label = ctk.CTkLabel(main_frame, text="Kategori:", font=ctk.CTkFont(size=16, weight="bold"))
        category_label.pack(pady=(20, 5))
        
        category_combo = ctk.CTkComboBox(
            main_frame,
            values=["Diğer", "🛒 Market", "🚗 Ulaşım", "🍽️ Yemek", "🎬 Eğlence", "💊 Sağlık", "👕 Kıyafet", "💻 Teknoloji", "📚 Eğitim", "🏠 Ev"],
            width=400,
            height=45,
            font=ctk.CTkFont(size=14),
            state="readonly"
        )
        category_combo.pack(pady=5)
        category_combo.set(category)
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=15)
        
        def save_changes():
            try:
                new_name = name_entry.get().strip()
                new_amount_text = amount_entry.get().strip()
                new_date = date_entry.get().strip()
                new_category = category_combo.get()
                
                if not new_name or not new_amount_text or not new_date:
                    messagebox.showerror("Hata", "❌ Tüm alanlar doldurulmalıdır!")
                    return
                
                new_amount = float(new_amount_text)
                
                if new_amount <= 0:
                    messagebox.showerror("Hata", "❌ Tutar sıfırdan büyük olmalıdır!")
                    return
                
                try:
                    datetime.strptime(new_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Hata", "❌ Geçerli bir tarih formatı girin! (YYYY-MM-DD)")
                    return
                
                if self.finance_manager.update_extra_expense(expense_id, new_name, new_amount, new_date, new_category):
                    messagebox.showinfo("Başarılı", "✅ Gider başarıyla güncellendi!")
                    dialog.destroy()
                    refresh_callback()
                    self.refresh_report()
                else:
                    messagebox.showerror("Hata", "❌ Gider güncellenirken hata oluştu!")
                    
            except ValueError:
                messagebox.showerror("Hata", "❌ Geçerli bir tutar girin!")
            except Exception as e:
                messagebox.showerror("Hata", f"❌ Bir hata oluştu: {str(e)}")

        save_button = ctk.CTkButton(button_frame, text="💾 Kaydet", command=save_changes, width=150, height=45, font=ctk.CTkFont(size=16, weight="bold"), fg_color=("#28A745", "#1E7E34"))
        save_button.pack(side="left", padx=15)
        
        cancel_button = ctk.CTkButton(button_frame, text="❌ İptal", command=dialog.destroy, width=150, height=45, font=ctk.CTkFont(size=16, weight="bold"), fg_color=("#DC3545", "#C82333"))
        cancel_button.pack(side="left", padx=15)


    def refresh_report(self):
        """Raporu yenile ve güncelle. Metin kutusunu kullanıcıya karşı kilitler."""
        try:
            report = self.finance_manager.generate_monthly_report()
            
            turkish_months = {
                1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
                7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
            }
            current_month_name = turkish_months.get(report['month'], str(report['month']))
            
            # Hizalama için standart bir genişlik belirliyoruz, örn: 25
            ALIGN_WIDTH = 25
            
            report_text = f"""
    🏦 KİŞİSEL FİNANS RAPORU
    {'═' * 60}
    📅 Rapor Dönemi: {current_month_name} {report['year']}

    💰 GELİRLER
    {'─' * 40}
    Aylık Gelir: {report['income']:>{ALIGN_WIDTH},.2f} TL

    💸 GİDERLER
    {'─' * 40}
    📺 Abonelikler: {report['subscriptions']:>{ALIGN_WIDTH - 2},.2f} TL
    💳 Taksitler: {report['installments']:>{ALIGN_WIDTH - 3},.2f} TL
    🛒 Ekstra Giderler: {report['extra_expenses']:>{ALIGN_WIDTH - 5},.2f} TL
    {'─' * 40}
    💰 Toplam Gider: {report['total_expenses']:>{ALIGN_WIDTH - 2},.2f} TL

    📊 ÖZET
    {'─' * 40}
    """
            
            if report['savings'] >= 0:
                report_text += f"✅ Bu Ay Tasarrufunuz: {report['savings']:>{ALIGN_WIDTH - 8},.2f} TL\n"
                report_text += f"📈 Tasarruf Oranı: {report['savings_rate']:>{ALIGN_WIDTH - 5},.1f}%\n\n"
                if report['savings_rate'] >= 20:
                    report_text += "🎉 Mükemmel! Çok iyi tasarruf ediyorsunuz!\n"
                elif report['savings_rate'] >= 10:
                    report_text += "👍 İyi! Tasarruf hedefinize yaklaşıyorsunuz.\n"
                else:
                    report_text += "⚠️ Tasarruf oranınızı artırmaya çalışın.\n"
            else:
                report_text += f"❗ Bu Ay Açığınız: {abs(report['savings']):>{ALIGN_WIDTH - 5},.2f} TL\n"
                report_text += "❗ Giderlerinizi gözden geçirmeniz önerilir.\n"
            
            if report['savings'] > 0:
                report_text += f"\n💡 YATIRIM ÖNERİSİ\n{'─' * 40}\n"
                conservative = report['savings'] * 0.6
                moderate = report['savings'] * 0.3
                aggressive = report['savings'] * 0.1
                report_text += f"🟢 Muhafazakar (%60): {conservative:>{ALIGN_WIDTH - 9},.2f} TL\n"
                report_text += f"🟡 Orta Risk (%30): {moderate:>{ALIGN_WIDTH - 7},.2f} TL\n"
                report_text += f"🔴 Yüksek Risk (%10): {aggressive:>{ALIGN_WIDTH - 8},.2f} TL\n"
            
            report_year = report['year']
            report_month = report['month']
            
            subscriptions = self.finance_manager.get_active_subscriptions_for_month(report_year, report_month)
            if subscriptions:
                report_text += f"\n📋 AKTİF ABONELİKLER ({current_month_name} {report_year})\n{'─' * 50}\n"
                for sub in subscriptions:
                    end_date_text = f" (🔚 {sub[4]})" if sub[4] else " (♾️ Süresiz)"
                    report_text += f"📺 {sub[1]:<25} {sub[2]:>10,.2f} TL{end_date_text}\n"
            
            installments = self.finance_manager.get_active_installments_for_month(report_year, report_month)
            if installments:
                report_text += f"\n📋 AKTİF TAKSİTLER ({current_month_name} {report_year})\n{'─' * 50}\n"
                for inst in installments:
                    try:
                        remaining, total_months = inst[3], inst[4]
                        report_text += f"💳 {inst[1]:<25} {inst[2]:>10,.2f} TL ({remaining}/{total_months} ay kaldı)\n"
                    except Exception as e:
                        print(f"Taksit gösterme hatası: {e}")
            
            extra_expenses = self.finance_manager.get_monthly_extra_expenses(report_year, report_month)
            if extra_expenses:
                report_text += f"\n📋 EKSTRA GİDERLER ({current_month_name} {report_year})\n{'─' * 50}\n"
                for exp in extra_expenses[:10]:
                    report_text += f"💸 {exp[1]:<25} {exp[2]:>10,.2f} TL - {exp[3]}\n"
                if len(extra_expenses) > 10:
                    report_text += f"\n... ve {len(extra_expenses) - 10} gider daha\n"
            
            self.report_textbox.configure(state="normal")
            self.report_textbox.delete("1.0", "end")
            self.report_textbox.insert("1.0", report_text)
            self.report_textbox.configure(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor yenilenirken hata oluştu: {str(e)}")
            print(f"Rapor yenileme hatası: {e}")  
    
    def show_trend_chart(self):
        """Trend grafiği göster"""
        if not PLOTTING_AVAILABLE:
            messagebox.showerror("Hata", "Grafik kütüphaneleri bulunamadı!")
            return
            
        reports = self.finance_manager.get_historical_reports()
        
        if len(reports) < 2:
            messagebox.showinfo("Bilgi", "📊 Trend grafiği için en az 2 aylık veri gereklidir.")
            return
        
        reports = list(reversed(reports))
        
        chart_window = ctk.CTkToplevel(self.root)
        chart_window.title("📈 Finansal Trend Analizi")
        chart_window.geometry("900x700")
        
        chart_window.update_idletasks()
        x = (chart_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (chart_window.winfo_screenheight() // 2) - (700 // 2)
        chart_window.geometry(f"900x700+{x}+{y}")
        
        chart_window.focus()
        chart_window.grab_set()
        
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        plt.style.use('dark_background')
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle('📈 Finansal Trend Analizi', fontsize=18, fontweight='bold', color='white')
        fig.patch.set_facecolor('#212121')
        
        months, incomes, expenses, savings, savings_rates = [], [], [], [], []
        
        turkish_months_short = {1: "Oca", 2: "Şub", 3: "Mar", 4: "Nis", 5: "May", 6: "Haz", 7: "Tem", 8: "Ağu", 9: "Eyl", 10: "Eki", 11: "Kas", 12: "Ara"}
        
        for report in reports:
            year, month, income, total_exp, saving, saving_rate = report
            month_name = f"{turkish_months_short[month]}\n{year}"
            months.append(month_name)
            incomes.append(income)
            expenses.append(total_exp)
            savings.append(saving)
            savings_rates.append(saving_rate)
        
        ax1.plot(months, incomes, marker='o', linewidth=3, label='💰 Gelir', color='#4CAF50', markersize=8)
        ax1.plot(months, expenses, marker='s', linewidth=3, label='💸 Gider', color='#F44336', markersize=8)
        ax1.plot(months, savings, marker='^', linewidth=3, label='📈 Tasarruf', color='#2196F3', markersize=8)
        
        ax1.set_title('💰 Aylık Gelir, Gider ve Tasarruf Trendi', fontsize=16, fontweight='bold', pad=20)
        ax1.set_ylabel('Tutar (TL)', fontsize=14)
        ax1.legend(fontsize=12, loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45, labelsize=10)
        ax1.set_facecolor('#2b2b2b')
        
        bars = ax2.bar(months, savings_rates, color='#03DAC6', alpha=0.8, edgecolor='white', linewidth=1)
        ax2.axhline(y=20, color='#4CAF50', linestyle='--', alpha=0.8, linewidth=2, label='🎯 Hedef: %20')
        ax2.axhline(y=10, color='#FF9800', linestyle='--', alpha=0.8, linewidth=2, label='⚠️ Minimum: %10')
        
        for bar, rate in zip(bars, savings_rates):
            if rate != 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        ax2.set_title('📊 Tasarruf Oranı Trendi', fontsize=16, fontweight='bold', pad=20)
        ax2.set_ylabel('Tasarruf Oranı (%)', fontsize=14)
        ax2.legend(fontsize=12, loc='upper left')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45, labelsize=10)
        ax2.set_facecolor('#2b2b2b')
        
        plt.tight_layout()
        
        main_frame = ctk.CTkFrame(chart_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        canvas = FigureCanvasTkAgg(fig, main_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=15)
        
        def save_chart():
            try:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG dosyaları", "*.png"), ("Tüm Dosyalar", "*.*")],
                    title="Grafiği Kaydet"
                )
                if filename:
                    fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#212121')
                    messagebox.showinfo("Başarılı", f"📊 Grafik '{os.path.basename(filename)}' olarak kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Grafik kaydedilirken hata oluştu: {str(e)}")
        
        save_button = ctk.CTkButton(button_frame, text="💾 Grafiği Kaydet", command=save_chart, height=40, font=ctk.CTkFont(size=14, weight="bold"), fg_color=("#28A745", "#1E7E34"))
        save_button.pack(side="left", padx=10, expand=True, fill="x")
        
        close_button = ctk.CTkButton(button_frame, text="❌ Kapat", command=chart_window.destroy, height=40, font=ctk.CTkFont(size=15, weight="bold"), fg_color=("#DC3545", "#C82333"))
        close_button.pack(side="right", padx=10, expand=True, fill="x")
    
    # ModernFinanceGUI sınıfı içindeki export_report fonksiyonunu bununla değiştirin.

    # ModernFinanceGUI sınıfı içinde...

    # ModernFinanceGUI sınıfındaki export_report fonksiyonunu bununla değiştirin.

    # ModernFinanceGUI sınıfındaki export_report fonksiyonunu bununla değiştirin.

    def export_report(self):
        """Excel raporu dışa aktarır. (Daha güvenli hale getirildi)"""
        if not PLOTTING_AVAILABLE:
            messagebox.showerror("Hata", "❌ Excel dışa aktarımı için pandas kütüphanesi gereklidir.")
            return
            
        try:
            reports = self.finance_manager.get_historical_reports()
            
            if not reports:
                messagebox.showinfo("Bilgi", "📄 Dışa aktarılacak rapor bulunamadı.")
                return
            
            import pandas as pd
            
            turkish_months = {1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"}
            
            df_data = []
            for report in reversed(reports):
                year, month, income, total_exp, saving, saving_rate = report
                df_data.append({
                    'Yıl': year,
                    'Ay': turkish_months.get(month, month),
                    'Gelir (TL)': income,
                    'Gider (TL)': total_exp,
                    'Tasarruf (TL)': saving,
                    'Tasarruf Oranı (%)': round(saving_rate, 2)
                })
            
            df = pd.DataFrame(df_data)
            
            filename_from_dialog = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Dosyaları", "*.xlsx")],
                title="Finans Raporunu Dışa Aktar"
            )

            # =========================================================
            # YENİ SAVUNMA VE HATA AYIKLAMA KODU
            # =========================================================
            print(f">>> DEBUG: Dosya diyalogundan gelen değer: '{filename_from_dialog}'")
            print(f">>> DEBUG: Gelen değerin tipi: {type(filename_from_dialog)}")

            # Gelen değerin bir string (metin) ve geçerli bir dosya yolu olduğundan emin oluyoruz.
            if not isinstance(filename_from_dialog, str) or not filename_from_dialog:
                messagebox.showinfo("İptal Edildi", "Dosya seçme işlemi iptal edildi veya geçersiz bir dosya adı döndü.")
                return
                
            # Değişkeni yeni ve güvenli bir isme atayarak devam edelim.
            safe_filename = filename_from_dialog
            print(f">>> DEBUG: Güvenli dosya adı: '{safe_filename}'")
            # =========================================================

            with pd.ExcelWriter(safe_filename) as writer:
                df.to_excel(writer, index=False, sheet_name='Finansal Rapor')
                
                worksheet = writer.sheets['Finansal Rapor']
                for idx, col in enumerate(df.columns):
                    max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.column_dimensions[chr(65 + idx)].width = max_length
            
            messagebox.showinfo("Başarılı", f"📊 Rapor '{os.path.basename(safe_filename)}' olarak dışa aktarıldı!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Rapor dışa aktarılırken hata oluştu: {str(e)}")
        
    def run(self):
        """Uygulamayı çalıştır"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Uygulama çalışırken kritik hata: {e}")
            messagebox.showerror("Kritik Hata", f"Uygulama beklenmedik bir hatayla karşılaştı: {str(e)}")
            # ModernFinanceGUI sınıfının içine bu yeni fonksiyonu ekle

    def is_valid_name(self, name: str, item_type: str) -> bool:
        """
        Girilen ismin geçerli olup olmadığını kontrol eden yardımcı fonksiyon.
        - Boş olamaz.
        - Sadece sayılardan oluşamaz.
        - En az bir harf içermelidir.
        """
        stripped_name = name.strip()
        
        # 1. Kontrol: İsim boş veya sadece boşluklardan mı oluşuyor?
        if not stripped_name:
            messagebox.showerror("Geçersiz İsim", f"❌ {item_type} adı boş bırakılamaz!")
            return False
            
        # 2. Kontrol: İsim sadece sayılardan mı oluşuyor? (Kullanıcının isteği)
        if stripped_name.isdigit():
            messagebox.showerror("Geçersiz İsim", f"❌ {item_type} adı sadece sayılardan oluşamaz!")
            return False
            
        # 3. Kontrol: İsimde en az bir harf var mı? (Daha sağlam bir kontrol)
        if not any(char.isalpha() for char in stripped_name):
            messagebox.showerror("Geçersiz İsim", f"❌ {item_type} adı en az bir harf içermelidir!")
            return False
            
        # Tüm kontrollerden geçtiyse isim geçerlidir.
        return True
if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        os.chdir(application_path)

    app = ModernFinanceGUI()
    app.run()