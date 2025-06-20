#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanı işlemleri modülü.
FinanceManager sınıfını içerir.
"""

import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import os

class FinanceManager:
    """
    Uygulamanın tüm veritabanı mantığını yöneten sınıf.
    Bağlantılar güvenli (try...finally) blokları ile yönetilmektedir.
    """
    def __init__(self, db_name=os.path.join(os.getcwd(),"finans_yoneticisi.db")):
        self.db_name = db_name
        self.init_database()
        
    def init_database(self):
        """Veritabanını başlatır ve tabloların var olduğundan emin olur."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Gerekli sütunları ekle (varsa hata vermez)
            try:
                cursor.execute("ALTER TABLE user_settings ADD COLUMN updated_date TEXT DEFAULT CURRENT_TIMESTAMP")
                cursor.execute("ALTER TABLE extra_expenses ADD COLUMN updated_date TEXT DEFAULT CURRENT_TIMESTAMP")
            except sqlite3.OperationalError:
                pass # Sütunlar zaten var

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY,
                    monthly_income REAL NOT NULL DEFAULT 0,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS installments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    monthly_amount REAL NOT NULL,
                    total_months INTEGER NOT NULL,
                    remaining_months INTEGER NOT NULL,
                    start_date TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS extra_expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL,
                    category TEXT DEFAULT 'Diğer',
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monthly_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    income REAL NOT NULL,
                    subscriptions_total REAL NOT NULL,
                    installments_total REAL NOT NULL,
                    extra_expenses_total REAL NOT NULL,
                    total_expenses REAL NOT NULL,
                    savings REAL NOT NULL,
                    savings_rate REAL NOT NULL,
                    report_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(year, month)
                )
            ''')
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Veritabanı başlatma hatası: {e}")
            raise
        finally:
            if conn:
                conn.close()
            
        self.init_default_income()

    def init_default_income(self):
        """Kullanıcı ayarlarında gelir yoksa, başlangıç geliri olarak 0 ekler."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_settings")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO user_settings (id, monthly_income) VALUES (1, 0)")
                conn.commit()
        except sqlite3.Error as e:
            print(f"Default gelir ekleme hatası: {e}")
        finally:
            if conn:
                conn.close()

    # ... FinanceManager sınıfının TÜM diğer fonksiyonlarını buraya kopyalayın ...
    # (get_monthly_income, set_monthly_income, add_subscription, vb. hepsi dahil)
    # Örnek olarak birkaç fonksiyonu ekliyorum, tamamını siz eklemelisiniz.

    def get_monthly_income(self) -> float:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT monthly_income FROM user_settings WHERE id = 1")
            result = cursor.fetchone()
            return float(result[0]) if result else 0.0
        except sqlite3.Error as e:
            print(f"Gelir getirme hatası: {e}")
            return 0.0
        finally:
            if conn:
                conn.close()

    def set_monthly_income(self, income: float) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE user_settings SET monthly_income = ?, updated_date = datetime('now', 'localtime') WHERE id = 1", (income,))
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO user_settings (id, monthly_income) VALUES (1, ?)", (income,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Gelir güncelleme hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def add_subscription(self, name: str, amount: float, start_date: str, end_date: str = None) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO subscriptions (name, amount, start_date, end_date) VALUES (?, ?, ?, ?)", (name, amount, start_date, end_date))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Abonelik ekleme hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def add_installment(self, name: str, total_amount: float, monthly_amount: float, total_months: int, start_date: str) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO installments (name, total_amount, monthly_amount, total_months, remaining_months, start_date) VALUES (?, ?, ?, ?, ?, ?)", (name, total_amount, monthly_amount, total_months, total_months, start_date))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Taksit ekleme hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def add_extra_expense(self, name: str, amount: float, expense_date: str, category: str = "Diğer") -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO extra_expenses (name, amount, date, category) VALUES (?, ?, ?, ?)", (name, amount, expense_date, category))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Gider ekleme hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()

    # FinanceManager sınıfı içindeki bu fonksiyonu GÜNCELLE

    def get_active_subscriptions_for_month(self, year: int, month: int) -> list:
        """DEĞİŞTİRİLDİ: Bir aboneliğin ilgili ayla kesişip kesişmediğini doğru kontrol eder."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Ayın ilk ve son gününü hesapla
            first_day = f"{year}-{month:02d}-01"
            _, num_days = calendar.monthrange(year, month)
            last_day = f"{year}-{month:02d}-{num_days}"

            # Sorguyu, başlangıç tarihinin ayın sonundan önce, bitiş tarihinin ise ayın başından sonra olmasını kontrol edecek şekilde güncelle
            cursor.execute("""
                SELECT id, name, amount, start_date, end_date 
                FROM subscriptions 
                WHERE is_active = 1 
                AND date(start_date) <= date(?) 
                AND (end_date IS NULL OR date(end_date) >= date(?))
            """, (last_day, first_day))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Abonelik getirme hatası: {e}")
            return []
        finally:
            if conn:
                conn.close()
    # FinanceManager sınıfı içindeki bu fonksiyonu GÜNCELLE

    # FinanceManager sınıfındaki bu fonksiyonu GÜNCELLEYİN

    def get_active_installments_for_month(self, year: int, month: int) -> list:
        """
        Belirtilen ay için aktif taksitleri getirir.
        
        Args:
            year: Yıl
            month: Ay (1-12)
            
        Returns:
            list: Aktif taksit kayıtları
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, monthly_amount, remaining_months, total_months, start_date FROM installments WHERE is_active = 1 AND remaining_months > 0")
            results = cursor.fetchall()
            
            valid_installments = []
            first_day_of_month = datetime(year, month, 1)
            _, num_days = calendar.monthrange(year, month)
            last_day_of_month = datetime(year, month, num_days)

            for inst in results:
                inst_id, name, monthly_amount, rem_months, total_months, start_date = inst
                try:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    # DÜZELTİLDİ: Son ödeme ayını doğru hesapla
                    # Örnek: 12 aylık taksit Ocak'ta başlarsa, Aralık'ta biter (11 ay sonra)
                    end_date_obj = start_date_obj + relativedelta(months=total_months-1)
                    # Ay sonuna kadar uzat
                    _, last_day = calendar.monthrange(end_date_obj.year, end_date_obj.month)
                    end_date_obj = end_date_obj.replace(day=last_day)
                    
                    # Taksit dönemi, rapor ayıyla kesişiyor mu?
                    if start_date_obj <= last_day_of_month and end_date_obj >= first_day_of_month:
                        valid_installments.append(inst)
                except ValueError as e:
                    print(f"Tarih parse hatası (get_active_installments): {e}")
            return valid_installments
        except sqlite3.Error as e:
            print(f"Taksit getirme hatası: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_all_extra_expenses(self, year: int = None, month: int = None, category: str = None) -> list:
        """Filtrelenmiş veya tüm ekstra giderleri getirir."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            query = "SELECT id, name, amount, date, category FROM extra_expenses WHERE 1=1"
            params = []
            
            if year and month:
                query += " AND strftime('%Y', date) = ? AND strftime('%m', date) = ?"
                params.extend([str(year), f"{month:02d}"])
            
            if category and category != "Tümü":
                query += " AND category = ?"
                params.append(category)
                
            query += " ORDER BY date DESC, id DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Tüm giderleri getirme hatası: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def update_extra_expense(self, expense_id: int, name: str, amount: float, expense_date: str, category: str) -> bool:
        """Bir ekstra gideri ID'sine göre günceller."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE extra_expenses
                SET name = ?, amount = ?, date = ?, category = ?, updated_date = datetime('now', 'localtime')
                WHERE id = ?
            """, (name, amount, expense_date, category, expense_id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ekstra gider güncelleme hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def delete_extra_expense(self, expense_id: int) -> bool:
        """Bir ekstra gideri ID'sine göre siler."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM extra_expenses WHERE id = ?", (expense_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ekstra gider silme hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_monthly_extra_expenses(self, year: int, month: int) -> list:
        """Belirli ay için ekstra giderleri getirir."""
        return self.get_all_extra_expenses(year=year, month=month)

    def save_monthly_report(self, year: int, month: int, income: float, sub_total: float, inst_total: float, extra_total: float, total_expenses: float, savings: float, savings_rate: float) -> None:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO monthly_reports (year, month, income, subscriptions_total, installments_total, extra_expenses_total, total_expenses, savings, savings_rate, report_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))", (year, month, income, sub_total, inst_total, extra_total, total_expenses, savings, savings_rate))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Rapor kaydetme hatası: {e}")
        finally:
            if conn:
                conn.close()

    def get_historical_reports(self) -> list:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT year, month, income, total_expenses, savings, savings_rate FROM monthly_reports ORDER BY year DESC, month DESC LIMIT 12")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Geçmiş rapor getirme hatası: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def update_subscription_status(self) -> None:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            current_date = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("UPDATE subscriptions SET is_active = 0 WHERE end_date IS NOT NULL AND date(end_date) < date(?) AND is_active = 1", (current_date,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Abonelik durumu güncelleme hatası: {e}")
        finally:
            if conn:
                conn.close()

    def update_installment_status_for_month(self, year: int, month: int) -> None:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT id, start_date, total_months FROM installments WHERE is_active = 1")
            installments = cursor.fetchall()
            target_date = datetime(year, month, 1)

            for inst_id, start_date, total_months in installments:
                try:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    delta = relativedelta(target_date, start_date_obj)
                    months_passed = delta.years * 12 + delta.months
                    remaining = max(0, total_months - months_passed)
                    cursor.execute("UPDATE installments SET remaining_months = ? WHERE id = ?", (remaining, inst_id))
                    if remaining <= 0:
                        cursor.execute("UPDATE installments SET is_active = 0 WHERE id = ?", (inst_id,))
                except ValueError as e:
                    print(f"Tarih işleme hatası (update_installment_status): {e}")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Taksit durumu güncelleme hatası: {e}")
        finally:
            if conn:
                conn.close()

    def delete_subscription(self, sub_id: int) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM subscriptions WHERE id = ?", (sub_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Abonelik silme hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def delete_installment(self, inst_id: int) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM installments WHERE id = ?", (inst_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Taksit silme hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()
    # FinanceManager sınıfının içine bu 3 YENİ fonksiyonu ekle

    def update_subscription(self, sub_id: int, name: str, amount: float, end_date: str) -> bool:
        """Bir aboneliğin bilgilerini günceller."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            # Bitiş tarihi boş string ise NULL olarak kaydet
            db_end_date = end_date if end_date else None
            cursor.execute("""
                UPDATE subscriptions 
                SET name = ?, amount = ?, end_date = ?, is_active = 1
                WHERE id = ?
            """, (name, amount, db_end_date, sub_id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Abonelik güncelleme hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def update_installment_name(self, inst_id: int, new_name: str) -> bool:
        """Bir taksidin sadece adını günceller."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("UPDATE installments SET name = ? WHERE id = ?", (new_name, inst_id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Taksit adı güncelleme hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def close_installment_early(self, inst_id: int) -> bool:
        """Bir taksidi erken kapatır (kalan ayları sıfırlar ve pasif yapar)."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            # Kalan ayları 0 yap ve durumu pasif olarak güncelle
            cursor.execute("UPDATE installments SET remaining_months = 0, is_active = 0 WHERE id = ?", (inst_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Taksit erken kapatma hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()            

    def get_all_subscriptions(self) -> list:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, amount, start_date, end_date, is_active FROM subscriptions ORDER BY is_active DESC, name")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Abonelik listesi getirme hatası: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_all_installments(self) -> list:
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, total_amount, monthly_amount, total_months, remaining_months, is_active FROM installments ORDER BY is_active DESC, name")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Taksit listesi getirme hatası: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    # FinanceManager sınıfına bu yeni fonksiyonu ekleyin
    def calculate_monthly_totals(self, year: int, month: int) -> tuple[float, float, float]:
        """Aylık toplamları hesaplar. Kısmi ödeme yapılan taksitleri normal ödemeden düşer."""
        try:
            # O ay yapılan kısmi ödemeleri tespit etmek için tüm ekstra giderleri al
            extra_expenses = self.get_monthly_extra_expenses(year, month)
        
            # Bu ay içinde kısmi ödemesi yapılmış taksitlerin isimlerini bir sete kaydet
            partially_paid_installments = set()
            for exp in extra_expenses:
                # exp formatı: id, name, amount, date, category
                category = exp[4]
                if category == "💳 Taksit Ödemesi":
                    # Giderin adından taksitin adını çıkar
                    # Gider adı formatı: "'Araç Kredisi' için 2 aylık erken ödeme"
                    expense_name = exp[1]
                    if "için" in expense_name and "erken ödeme" in expense_name:
                        # Tırnak işaretleri arasındaki ismi al
                        try:
                            inst_name = expense_name.split("'")[1]
                            partially_paid_installments.add(inst_name)
                        except IndexError:
                            print(f"Hata: Taksit adı okunamadı: {expense_name}")


            # Abonelik toplamını hesapla (değişiklik yok)
            subscriptions = self.get_active_subscriptions_for_month(year, month)
            subscription_total = sum(sub[2] for sub in subscriptions)
            
            # Taksit toplamını hesaplarken, bu ay kısmi ödemesi yapılanları hariç tut
            installments = self.get_active_installments_for_month(year, month)
            installment_total = 0.0
            for inst in installments:
                # inst formatı: id, name, monthly_amount, ...
                inst_name = inst[1]
                if inst_name not in partially_paid_installments:
                    installment_total += inst[2] # Sadece kısmi ödemesi yapılmamışsa aylık tutarı ekle
            
            # Ekstra giderler toplamını hesapla (değişiklik yok)
            extra_total = sum(exp[2] for exp in extra_expenses)
            
            return subscription_total, installment_total, extra_total
            
        except Exception as e:
            print(f"Toplam hesaplama hatası: {e}")
            return 0.0, 0.0, 0.0
    
    def generate_monthly_report(self, year: int = None, month: int = None) -> dict:
        """Aylık raporu oluşturur ve döndürür."""
        if year is None: year = datetime.now().year
        if month is None: month = datetime.now().month
        
        self.update_subscription_status()
        # self.update_installment_status_for_month(year, month)
        
        income = self.get_monthly_income()
        sub_total, inst_total, extra_total = self.calculate_monthly_totals(year, month)
        
        total_expenses = sub_total + inst_total + extra_total
        savings = income - total_expenses
        savings_rate = (savings / income * 100) if income > 0 else 0
        
        self.save_monthly_report(year, month, income, sub_total, inst_total,
                                 extra_total, total_expenses, savings, savings_rate)
        
        return {
            'year': year, 'month': month, 'income': income,
            'subscriptions': sub_total, 'installments': inst_total,
            'extra_expenses': extra_total, 'total_expenses': total_expenses,
            'savings': savings, 'savings_rate': savings_rate
        }

    # FinanceManager sınıfına bu yeni fonksiyonu ekleyin
    def make_partial_payment(self, inst_id: int, months_to_pay: int) -> bool:
        """Bir taksidin belirli sayıda ayını erken öder ve bunu bir gider olarak kaydeder."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # 1. İlgili taksidin bilgilerini al (adı, aylık tutarı, kalan ay)
            cursor.execute("SELECT name, monthly_amount, remaining_months FROM installments WHERE id = ?", (inst_id,))
            result = cursor.fetchone()
            if result is None:
                return False # Taksit bulunamadı
            
            inst_name, monthly_amount, current_remaining = result
            
            # 2. Ödenecek ay sayısının geçerli olduğunu kontrol et
            if not (1 <= months_to_pay <= current_remaining):
                print(f"Hata: {months_to_pay} aylık ödeme yapılamaz. Kalan ay: {current_remaining}")
                return False
                
            # 3. İşlemleri hesapla
            payment_amount = months_to_pay * monthly_amount
            new_remaining = current_remaining - months_to_pay
            
            # --- Veritabanı İşlemi (Transaction) Başlıyor ---
            
            # 4. Ödemeyi 'extra_expenses' tablosuna bir gider olarak ekle
            expense_date = datetime.now().strftime("%Y-%m-%d")
            expense_name = f"'{inst_name}' için {months_to_pay} aylık erken ödeme"
            expense_category = "💳 Taksit Ödemesi" # Yeni kategori
            cursor.execute("INSERT INTO extra_expenses (name, amount, date, category) VALUES (?, ?, ?, ?)", 
                           (expense_name, payment_amount, expense_date, expense_category))
            
            # 5. Taksidin durumunu (kalan ay) güncelle
            if new_remaining == 0:
                # Eğer borç bittiyse, taksidi pasif yap
                cursor.execute("UPDATE installments SET remaining_months = 0, is_active = 0 WHERE id = ?", (inst_id,))
            else:
                cursor.execute("UPDATE installments SET remaining_months = ? WHERE id = ?", (new_remaining, inst_id))
            
            conn.commit() # Tüm işlemler başarılıysa onayla
            return True
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback() # Hata durumunda tüm işlemleri geri al
            print(f"Kısmi ödeme hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()
    # FinanceManager sınıfının içine, diğer fonksiyonlarla aynı hizada olacak şekilde ekleyin.

    def reset_all_data(self) -> bool:
        """
        Tüm işlem verilerini (raporlar, abonelikler, taksitler, giderler)
        veritabanından siler. Kullanıcı ayarlarını korur.
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Silinecek tablolar
            tables_to_clear = ["subscriptions", "installments", "extra_expenses", "monthly_reports"]
            
            for table in tables_to_clear:
                cursor.execute(f"DELETE FROM {table}")
                
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback() # Hata durumunda işlemi geri al
            print(f"Veritabanı sıfırlama hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()           
    