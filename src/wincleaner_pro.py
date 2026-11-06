# -*- coding: utf-8 -*-
"""
WinCleaner Pro v2.0 — تنظيف وتسريع وإصلاح Windows
تشغيل:   python app.py
EXE:     pyinstaller --onefile --windowed --uac-admin --name WinCleanerPro ^
         --collect-all customtkinter --collect-all matplotlib app.py
"""

import os, sys, json, shutil, ctypes, platform, subprocess, threading, winreg, tempfile
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ================= المسارات =================
APP_DIR      = os.path.join(os.environ.get("LOCALAPPDATA", tempfile.gettempdir()), "WinCleanerPro")
BACKUP_ROOT  = os.path.join(APP_DIR, "Backup")
HISTORY_FILE = os.path.join(APP_DIR, "usage.json")
PREFS_FILE   = os.path.join(APP_DIR, "prefs.json")
AUTO_LOG     = os.path.join(APP_DIR, "auto_clean.log")
os.makedirs(BACKUP_ROOT, exist_ok=True)

VERSION = "2.0"

# ================= الترجمة =================
STR = {
"ar": {
  "app":"WinCleaner Pro","home":"🏠 الرئيسية","clean":"🧹 التنظيف","fix":"🔧 الإصلاح",
  "startup":"🚀 بدء التشغيل","charts":"📊 الإحصاءات","settings":"⚙️ الإعدادات","about":"ℹ️ حول البرنامج",
  "welcome":"👋 مرحباً بك في WinCleaner Pro","subtitle":"أداة تنظيف وتسريع وإصلاح نظام Windows",
  "refresh":"🔄 تحديث المعلومات","quickscan":"⚡ فحص وتنظيف سريع",
  "ram_label":"استخدام الذاكرة RAM:","disk_label":"مساحة القرص C:",
  "admin_ok":"✅ يعمل بصلاحيات المسؤول","admin_no":"⚠️ شغّل كمسؤول لبعض العمليات",
  "stat_win":"🪟 Windows","stat_cpu":"🧠 المعالج:","stat_ram":"💾 RAM:","stat_disk":"💽 القرص C:","stat_uptime":"⏱ مدة التشغيل:",
  "clean_title":"🧹 التنظيف","t_temp":"🗑️ الملفات المؤقتة (TEMP)","t_prefetch":"📦 مجلد Prefetch",
  "t_bin":"♻️ إفراغ سلة المحذوفات","t_dns":"🌐 مسح ذاكرة DNS","t_wucache":"🧹 كاش تحديثات Windows",
  "t_all":"🚀 تنظيف شامل (الكل فوراً)","backup_chk":"🗄️ نسخ احتياطي قبل الحذف (موصى به)",
  "open_backup":"📂 فتح مجلد النسخ الاحتياطية","restore":"♻️ استعادة آخر نسخة احتياطية",
  "fix_title":"🔧 إصلاح النظام","f_sfc":"🛡️ فحص ملفات النظام (sfc /scannow)","f_dism":"🔧 إصلاح صورة Windows (DISM)",
  "f_chkdsk":"💽 فحص وإصلاح القرص (chkdsk /F)","f_winsock":"🌐 إعادة ضبط Winsock","f_ip":"🔄 إعادة ضبط IP","f_net":"📡 إعادة ضبط الشبكة بالكامل",
  "startup_title":"🚀 برامج بدء التشغيل التلقائي","startup_hint":"احذف برنامجاً من التشغيل التلقائي لتسريع إقلاع الجهاز:",
  "s_refresh":"🔄 تحديث القائمة","s_empty":"لا توجد برامج في بدء التشغيل","s_del":"🗑 حذف",
  "charts_title":"📊 سجل استخدام الموارد","c_update":"🔄 تحديث الرسم","c_hint":"agram يُسجَّل استخدام الذاكرة والقرص عند كل تحديث — آخر 200 قراءة",
  "settings_title":"⚙️ الإعدادات","lang_lbl":"🌐 اللغة / Language:","lang_btn":"English",
  "auto_lbl":"⏰ تنظيف تلقائي عند بدء Windows","auto_desc":"يشغّل البرنامج نفسه صامتاً عند كل إقلاع وينظّف الملفات المؤقتة",
  "backup_lbl":"🗄️ النسخ الاحتياطي الافتراضي","backup_desc":"عند تفعيلها، تُنسخ الملفات إلى مجلد احتياطي قبل حذفها (يمكن استعادتها لاحقاً)",
  "clear_backups":"🗑 مسح جميع النسخ الاحتياطية","saved":"✅ تم حفظ الإعدادات",
  "about_title":"حول البرنامج",
  "about_text":"برنامج مجاني لتنظيف وتسريع وإصلاح Windows:\n\n🧹 حذف الملفات المؤقتة وPrefetch وكاش التحديثات\n♻️ إفراغ سلة المحذوفات مع نسخ احتياطي\n🔧 SFC و DISM و CHKDSK\n🌐 إعادة ضبط الشبكة ومسح DNS\n🚀 إدارة برامج بدء التشغيل\n📊 رسم بياني لاستخدام الموارد\n⏰ تنظيف تلقائي عند الإقلاع\n\n⚠️ شغّل الملف كمسؤول. بعض الإصلاحات تحتاج إعادة تشغيل.",
  # السجلات
  "l_start":"بدء العملية...","l_temp":"🗑️ تنظيف الملفات المؤقتة...","l_prefetch":"📦 تنظيف Prefetch...",
  "l_bin":"♻️ إفراغ سلة المحذوفات...","l_bin_ok":"تم الإفراغ بنجاح ✅","l_bin_fail":"فشل — شغّل كمسؤول ❌",
  "l_dns":"🌐 مسح ذاكرة DNS...","l_dns_ok":"تم ✅","l_dns_fail":"فشل ❌",
  "l_wu":"🧹 تنظيف كاش تحديثات Windows...","l_all":"🚀 بدء التنظيف الشامل...",
  "l_freed":"🎉 تم تحرير","l_skip":"ملف مشغول تم تخطيه:","l_done":"✅ اكتمل!",
  "l_sfc":"🛡️ sfc /scannow (قد يستغرق دقائق)...","l_dism":"🔧 DISM RestoreHealth (يتطلب إنترنت)...",
  "l_chkdsk":"💽 chkdsk C: /F — قد يُجدول عند إعادة التشغيل...","l_winsock":"🌐 netsh winsock reset...",
  "l_ip":"🔄 netsh int ip reset...","l_net":"📡 إعادة ضبط الشبكة بالكامل...","l_net_done":"✅ اكتملت — يُنصح بإعادة التشغيل",
  "l_restore":"♻️กำลัง استعادة النسخة الاحتياطية...","l_restore_ok":"✅ تمت الاستعادة","l_no_backup":"لا توجد نسخة احتياطية",
  "l_cleared":"🗑 تم مسح النسخ الاحتياطية","l_auto":"⏰ وضع التنظيف التلقائي — سيُغلق البرنامج بعد الانتهاء...",
},
"en": {
  "app":"WinCleaner Pro","home":"🏠 Home","clean":"🧹 Cleaner","fix":"🔧 Repair",
  "startup":"🚀 Startup","charts":"📊 Statistics","settings":"⚙️ Settings","about":"ℹ️ About",
  "welcome":"👋 Welcome to WinCleaner Pro","subtitle":"Clean, speed up & repair Windows",
  "refresh":"🔄 Refresh Info","quickscan":"⚡ Quick Scan & Clean",
  "ram_label":"RAM usage:","disk_label":"Drive C: space:",
  "admin_ok":"✅ Running as Administrator","admin_no":"⚠️ Run as admin for some tasks",
  "stat_win":"🪟 Windows","stat_cpu":"🧠 CPU:","stat_ram":"💾 RAM:","stat_disk":"💽 Drive C:","stat_uptime":"⏱ Uptime:",
  "clean_title":"🧹 Cleaning","t_temp":"🗑️ Temp Files","t_prefetch":"📦 Prefetch Folder",
  "t_bin":"♻️ Empty Recycle Bin","t_dns":"🌐 Flush DNS","t_wucache":"🧹 Windows Update Cache",
  "t_all":"🚀 Clean Everything Now","backup_chk":"🗄️ Backup before deleting (recommended)",
  "open_backup":"📂 Open Backup Folder","restore":"♻️ Restore Last Backup",
  "fix_title":"🔧 System Repair","f_sfc":"🛡️ System File Check (sfc /scannow)","f_dism":"🔧 Repair Windows Image (DISM)",
  "f_chkdsk":"💽 Check Disk (chkdsk /F)","f_winsock":"🌐 Reset Winsock","f_ip":"🔄 Reset IP","f_net":"📡 Full Network Reset",
  "startup_title":"🚀 Startup Programs","startup_hint":"Remove a program from startup to speed up boot:",
  "s_refresh":"🔄 Refresh List","s_empty":"No startup programs found","s_del":"🗑 Remove",
  "charts_title":"📊 Resource Usage History","c_update":"🔄 Update Chart","c_hint":"RAM & disk usage are logged on every refresh — last 200 readings",
  "settings_title":"⚙️ Settings","lang_lbl":"🌐 اللغة / Language:","lang_btn":"العربية",
  "auto_lbl":"⏰ Auto-clean on Windows startup","auto_desc":"Runs silently at every boot and cleans temp files",
  "backup_lbl":"🗄️ Default Backup","backup_desc":"When enabled, files are copied to a backup folder before deletion (restorable later)",
  "clear_backups":"🗑 Delete All Backups","saved":"✅ Settings saved",
  "about_title":"About",
  "about_text":"Free tool to clean, speed up & repair Windows:\n\n🧹 Delete temp files, Prefetch & update cache\n♻️ Empty Recycle Bin with backup\n🔧 SFC, DISM & CHKDSK\n🌐 Network reset & DNS flush\n🚀 Manage startup programs\n📊 Resource usage charts\n⏰ Auto-clean at boot\n\n⚠️ Run as administrator. Some repairs need a reboot.",
  "l_start":"Starting...","l_temp":"🗑️ Cleaning temp files...","l_prefetch":"📦 Cleaning Prefetch...",
  "l_bin":"♻️ Emptying Recycle Bin...","l_bin_ok":"Emptied ✅","l_bin_fail":"Failed — run as admin ❌",
  "l_dns":"🌐 Flushing DNS...","l_dns_ok":"Done ✅","l_dns_fail":"Failed ❌",
  "l_wu":"🧹 Cleaning Windows Update cache...","l_all":"🚀 Starting full clean...",
  "l_freed":"🎉 Freed","l_skip":"Skipped (in use):","l_done":"✅ Done!",
  "l_sfc":"🛡️ sfc /scannow (may take minutes)...","l_dism":"🔧 DISM RestoreHealth (needs internet)...",
  "l_chkdsk":"💽 chkdsk C: /F — may run at next reboot...","l_winsock":"🌐 netsh winsock reset...",
  "l_ip":"🔄 netsh int ip reset...","l_net":"📡 Full network reset...","l_net_done":"✅ Done — reboot recommended",
  "l_restore":"♻️ Restoring backup...","l_restore_ok":"✅ Restored","l_no_backup":"No backup found",
  "l_cleared":"🗑 Backups deleted","l_auto":"⏰ Auto-clean mode — app will close when finished...",
}}

# ================= أدوات =================
def load_prefs():
    try:
        with open(PREFS_FILE, encoding="utf-8") as f: return json.load(f)
    except Exception: return {"lang":"ar","backup":True}

def save_prefs(p):
    with open(PREFS_FILE,"w",encoding="utf-8") as f: json.dump(p,f,ensure_ascii=False)

def is_admin():
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception: return False

def human_size(n):
    for u in ["B","KB","MB","GB","TB"]:
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"

def mem_info():
    class M(ctypes.Structure):
        _fields_=[("dwLength",ctypes.c_ulong),("dwMemoryLoad",ctypes.c_ulong),
                  ("ullTotalPhys",ctypes.c_ulonglong),("ullAvailPhys",ctypes.c_ulonglong),
                  ("ullTotalPageFile",ctypes.c_ulonglong),("ullAvailPageFile",ctypes.c_ulonglong),
                  ("ullTotalVirtual",ctypes.c_ulonglong),("ullAvailVirtual",ctypes.c_ulonglong),
                  ("ullAvailExtendedVirtual",ctypes.c_ulonglong)]
    s=M(); s.dwLength=ctypes.sizeof(M)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
    return s.ullTotalPhys-s.ullAvailPhys, s.ullTotalPhys

def disk_info(drive="C:\\"):
    try: u=shutil.disk_usage(drive); return u.used,u.total
    except Exception: return 0,0

def uptime_str():
    try: secs=ctypes.windll.kernel32.GetTickCount64()/1000
    except Exception: return "?"
    d,r=divmod(int(secs),86400); h,r=divmod(r,3600); m=r//60
    return f"{d}d {h}h {m}m"

def run_cmd(cmd):
    try:
        p=subprocess.run(cmd,shell=True,capture_output=True,text=True,encoding="utf-8",errors="ignore")
        return p.returncode==0, ((p.stdout or "")+(p.stderr or "")).strip()
    except Exception as e: return False,str(e)

def empty_bin():
    try: return ctypes.windll.shell32.SHEmptyRecycleBinW(None,None,0x07)==0
    except Exception: return False

def list_startup():
    out=[]; paths=[(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run","HKCU"),
                  (winreg.HKEY_LOCAL_MACHINE,r"Software\Microsoft\Windows\CurrentVersion\Run","HKLM"),
                  (winreg.HKEY_LOCAL_MACHINE,r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run","HKLM32")]
    for root,sub,tag in paths:
        try:
            k=winreg.OpenKey(root,sub,0,winreg.KEY_READ); i=0
            while True:
                try:
                    n,v,_=winreg.EnumValue(k,i); out.append((tag,root,sub,n,v)); i+=1
                except OSError: break
            winreg.CloseKey(k)
        except Exception: pass
    return out

def del_startup(root,sub,name):
    try:
        k=winreg.OpenKey(root,sub,0,winreg.KEY_SET_VALUE); winreg.DeleteValue(k,name); winreg.CloseKey(k); return True
    except Exception: return False

# ---------- السجل التاريخي ----------
def load_history():
    try:
        with open(HISTORY_FILE,encoding="utf-8") as f: return json.load(f)
    except Exception: return []

def append_history(ram_pct,disk_pct):
    h=load_history()
    h.append({"t":datetime.now().strftime("%H:%M"),"ram":round(ram_pct*100,1),"disk":round(disk_pct*100,1)})
    h=h[-200:]
    with open(HISTORY_FILE,"w",encoding="utf-8") as f: json.dump(h,f,ensure_ascii=False)

# ---------- النسخ الاحتياطي ----------
def clean_folder(path, backup=True):
    """يمسح/ينقل ملفات مجلد. إذا backup=True تُنقل إلى مجلد احتياطي مع manifest."""
    session=datetime.now().strftime("%Y%m%d_%H%M%S")
    b=c=s=0; manifest=[]
    if not os.path.isdir(path): return 0,0,0
    for root,dirs,files in os.walk(path):
        for name in files:
            fp=os.path.join(root,name)
            try:
                sz=os.path.getsize(fp)
                if backup:
                    rel=os.path.relpath(fp,path)
                    dest=os.path.join(BACKUP_ROOT,session,rel)
                    os.makedirs(os.path.dirname(dest),exist_ok=True)
                    shutil.move(fp,dest); manifest.append([fp,dest])
                else:
                    os.remove(fp)
                b+=sz; c+=1
            except Exception: s+=1
    if backup and manifest:
        with open(os.path.join(BACKUP_ROOT,session,"_manifest.json"),"w",encoding="utf-8") as f:
            json.dump(manifest,f,ensure_ascii=False)
    return b,c,s

def latest_backup():
    try:
        sessions=sorted([d for d in os.listdir(BACKUP_ROOT) if os.path.isdir(os.path.join(BACKUP_ROOT,d))])
        return sessions[-1] if sessions else None
    except Exception: return None

def restore_latest():
    s=latest_backup()
    if not s: return 0
    mf=os.path.join(BACKUP_ROOT,s,"_manifest.json")
    if not os.path.exists(mf): return 0
    with open(mf,encoding="utf-8") as f: manifest=json.load(f)
    n=0
    for orig,dest in manifest:
        try:
            if os.path.exists(dest):
                os.makedirs(os.path.dirname(orig),exist_ok=True)
                if not os.path.exists(orig): shutil.move(dest,orig); n+=1
        except Exception: pass
    shutil.rmtree(os.path.join(BACKUP_ROOT,s),ignore_errors=True)
    return n

# ---------- التشغيل التلقائي ----------
def get_autostart_cmd():
    if getattr(sys,"frozen",False):
        return f'"{sys.executable}" --auto'
    pyw=os.path.join(os.path.dirname(sys.executable),"pythonw.exe")
    py=pyw if os.path.exists(pyw) else sys.executable
    return f'"{py}" "{os.path.abspath(__file__)}" --auto'

def set_autostart(enable):
    k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run",0,winreg.KEY_SET_VALUE)
    if enable: winreg.SetValueEx(k,"WinCleanerPro",0,winreg.REG_SZ,get_autostart_cmd())
    else:
        try: winreg.DeleteValue(k,"WinCleanerPro")
        except FileNotFoundError: pass
    winreg.CloseKey(k)

def is_autostart():
    try:
        k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run",0,winreg.KEY_READ)
        v,_=winreg.QueryValueEx(k,"WinCleanerPro"); winreg.CloseKey(k); return True
    except Exception: return False

# ================= الواجهة =================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.prefs=load_prefs()
        self.lang=self.prefs.get("lang","ar")
        self.backup_enabled=bool(self.prefs.get("backup",True))
        self.title(f"{self.t('app')} v{VERSION}")
        self.geometry("980x640"); self.minsize(880,580)
        self.current_page="home"
        self.build_ui()
        self.show_page("home")
        self.refresh_stats()

    def t(self,k): return STR[self.lang].get(k,k)

    # ---------- بناء الواجهة (تُعاد عند تغيير اللغة) ----------
    def build_ui(self):
        for w in self.winfo_children(): w.destroy()
        self.sidebar=ctk.CTkFrame(self,width=200,corner_radius=0)
        self.sidebar.pack(side="right",fill="y"); self.sidebar.pack_propagate(False)
        ctk.CTkLabel(self.sidebar,text=f"🧹 {self.t('app')}",font=ctk.CTkFont(size=19,weight="bold")).pack(pady=(22,4))
        ctk.CTkLabel(self.sidebar,text=f"v{VERSION}",font=ctk.CTkFont(size=11),text_color="gray").pack(pady=(0,15))
        self.nav={}
        for txt,key in [(self.t("home"),"home"),(self.t("clean"),"clean"),(self.t("fix"),"fix"),
                        (self.t("startup"),"startup"),(self.t("charts"),"charts"),
                        (self.t("settings"),"settings"),(self.t("about"),"about")]:
            b=ctk.CTkButton(self.sidebar,text=txt,anchor="e",fg_color="transparent",hover_color="#3a3a3a",
                            font=ctk.CTkFont(size=14),command=lambda k=key:self.show_page(k))
            b.pack(fill="x",padx=12,pady=4); self.nav[key]=b
        self.admin_lbl=ctk.CTkLabel(self.sidebar,text="",font=ctk.CTkFont(size=11))
        self.admin_lbl.pack(side="bottom",pady=12)
        self.admin_lbl.configure(text=self.t("admin_ok") if is_admin() else self.t("admin_no"),
                                 text_color="#2ecc71" if is_admin() else "#e67e22")

        self.container=ctk.CTkFrame(self,fg_color="transparent")
        self.container.pack(side="left",expand=True,fill="both",padx=12,pady=12)
        self.frames={k:ctk.CTkFrame(self.container,fg_color="transparent") for k in self.nav}
        self.build_home(); self.build_clean(); self.build_fix(); self.build_startup()
        self.build_charts(); self.build_settings(); self.build_about()

    def show_page(self,key):
        self.current_page=key
        for k,f in self.frames.items():
            f.pack(fill="both",expand=True) if k==key else f.pack_forget()
        for k,b in self.nav.items():
            b.configure(fg_color=("#1f6aa5" if k==key else "transparent"))
        if key=="startup": self.refresh_startup()
        if key=="charts": self.update_chart()

    def switch_lang(self):
        self.lang="en" if self.lang=="ar" else "ar"
        self.prefs["lang"]=self.lang; save_prefs(self.prefs)
        cur=self.current_page; self.build_ui(); self.show_page(cur); self.refresh_stats()

    def log(self,box,msg):
        def a():
            box.insert("end",f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n"); box.see("end")
        self.after(0,a)

    def set_bar(self,bar,active):
        def a(): bar.start() if active else (bar.stop(),bar.set(0))
        self.after(0,a)

    # ---------- الرئيسية ----------
    def build_home(self):
        f=self.frames["home"]
        ctk.CTkLabel(f,text=self.t("welcome"),font=ctk.CTkFont(size=24,weight="bold")).pack(pady=(8,2))
        ctk.CTkLabel(f,text=self.t("subtitle"),font=ctk.CTkFont(size=13),text_color="gray").pack(pady=(0,12))
        info=ctk.CTkFrame(f); info.pack(fill="x",padx=8,pady=5)
        self.stat_lbl={}
        for i,k in enumerate(["win","cpu","ram","disk","uptime"]):
            l=ctk.CTkLabel(info,text="...",font=ctk.CTkFont(size=12))
            l.grid(row=0,column=i,padx=6,pady=10); self.stat_lbl[k]=l
        bars=ctk.CTkFrame(f,fg_color="transparent"); bars.pack(fill="x",padx=20,pady=5)
        ctk.CTkLabel(bars,text=self.t("ram_label")).pack(fill="x")
        self.ram_bar=ctk.CTkProgressBar(bars); self.ram_bar.pack(fill="x",pady=(2,8))
        ctk.CTkLabel(bars,text=self.t("disk_label")).pack(fill="x")
        self.disk_bar=ctk.CTkProgressBar(bars); self.disk_bar.pack(fill="x",pady=(2,8))
        btns=ctk.CTkFrame(f,fg_color="transparent"); btns.pack(pady=8)
        ctk.CTkButton(btns,text=self.t("quickscan"),width=190,height=38,font=ctk.CTkFont(size=14,weight="bold"),
                      command=self.quick_scan).pack(side="right",padx=5)
        ctk.CTkButton(btns,text=self.t("refresh"),width=150,height=38,fg_color="#555",
                      command=self.refresh_stats).pack(side="right",padx=5)
        self.home_bar=ctk.CTkProgressBar(f); self.home_bar.pack(fill="x",padx=20,pady=5); self.home_bar.set(0)
        self.home_log=ctk.CTkTextbox(f,height=160,font=ctk.CTkFont(size=12))
        self.home_log.pack(fill="both",expand=True,padx=20,pady=(5,10))

    def refresh_stats(self):
        used,total=mem_info(); du,dt=disk_info()
        self.stat_lbl["win"].configure(text=f"{self.t('stat_win')} {platform.release()}")
        self.stat_lbl["cpu"].configure(text=f"{self.t('stat_cpu')} {os.cpu_count()}")
        self.stat_lbl["ram"].configure(text=f"{self.t('stat_ram')} {human_size(used)} / {human_size(total)}")
        self.stat_lbl["disk"].configure(text=f"{self.t('stat_disk')} {human_size(du)} / {human_size(dt)}")
        self.stat_lbl["uptime"].configure(text=f"{self.t('stat_uptime')} {uptime_str()}")
        self.ram_bar.set(used/total if total else 0); self.disk_bar.set(du/dt if dt else 0)
        append_history(used/total if total else 0, du/dt if dt else 0)

    def quick_scan(self):
        def work():
            self.set_bar(self.home_bar,True); self.log(self.home_log,self.t("l_all"))
            b,c,s=clean_folder(tempfile.gettempdir(),self.backup_enabled)
            self.log(self.home_log,f"{self.t('l_temp')} {c} ({human_size(b)})")
            pf=os.path.join(os.environ.get("SystemRoot",r"C:\Windows"),"Prefetch")
            b,c,s=clean_folder(pf,self.backup_enabled)
            self.log(self.home_log,f"{self.t('l_prefetch')} {c} ({human_size(b)})")
            self.log(self.home_log,self.t("l_bin_ok") if empty_bin() else self.t("l_bin_fail"))
            ok,_=run_cmd("ipconfig /flushdns"); self.log(self.home_log,f"{self.t('l_dns')} "+(self.t("l_dns_ok") if ok else self.t("l_dns_fail")))
            self.after(0,self.refresh_stats); self.log(self.home_log,self.t("l_done")); self.set_bar(self.home_bar,False)
        threading.Thread(target=work,daemon=True).start()

    # ---------- التنظيف ----------
    def build_clean(self):
        f=self.frames["clean"]
        ctk.CTkLabel(f,text=self.t("clean_title"),font=ctk.CTkFont(size=22,weight="bold")).pack(pady=(8,10))
        grid=ctk.CTkFrame(f,fg_color="transparent"); grid.pack(padx=10)
        acts=[(self.t("t_temp"),self.act_temp),(self.t("t_prefetch"),self.act_prefetch),
              (self.t("t_bin"),self.act_bin),(self.t("t_dns"),self.act_dns),(self.t("t_wucache"),self.act_update)]
        for i,(txt,fn) in enumerate(acts):
            ctk.CTkButton(grid,text=txt,width=235,height=40,font=ctk.CTkFont(size=13),command=fn
                          ).grid(row=i//2,column=i%2,padx=6,pady=6)
        ctk.CTkButton(grid,text=self.t("t_all"),width=486,height=44,fg_color="#1f6aa5",
                      font=ctk.CTkFont(size=15,weight="bold"),command=self.act_all
                      ).grid(row=3,column=0,columnspan=2,pady=10)
        self.backup_var=ctk.CTkCheckBox(f,text=self.t("backup_chk"),variable=None)
        self.backup_var=ctk.CTkCheckBox(f,text=self.t("backup_chk"))
        self.backup_var.select() if self.backup_enabled else self.backup_var.deselect()
        self.backup_var.pack(pady=4)
        row=ctk.CTkFrame(f,fg_color="transparent"); row.pack(pady=4)
        ctk.CTkButton(row,text=self.t("open_backup"),width=220,fg_color="#555",command=self.open_backup).pack(side="right",padx=4)
        ctk.CTkButton(row,text=self.t("restore"),width=220,fg_color="#2e7d32",hover_color="#388e3c",command=self.restore_backup).pack(side="right",padx=4)
        self.clean_bar=ctk.CTkProgressBar(f); self.clean_bar.pack(fill="x",padx=20,pady=5); self.clean_bar.set(0)
        self.clean_log=ctk.CTkTextbox(f,font=ctk.CTkFont(size=12))
        self.clean_log.pack(fill="both",expand=True,padx=20,pady=(5,10))

    def _bk(self): return bool(self.backup_var.get())

    def act_temp(self):
        def work():
            self.set_bar(self.clean_bar,True); self.log(self.clean_log,self.t("l_temp"))
            tb=tf=ts=0
            for p in [tempfile.gettempdir(),os.path.join(os.environ.get("SystemRoot",r"C:\Windows"),"Temp")]:
                b,c,s=clean_folder(p,self._bk()); tb+=b; tf+=c; ts+=s
            self.log(self.clean_log,f"✅ {self.t('l_freed')} {human_size(tb)} — {tf} files, {ts} {self.t('l_skip')}")
            self.set_bar(self.clean_bar,False)
        threading.Thread(target=work,daemon=True).start()

    def act_prefetch(self):
        def work():
            self.set_bar(self.clean_bar,True)
            pf=os.path.join(os.environ.get("SystemRoot",r"C:\Windows"),"Prefetch")
            self.log(self.clean_log,self.t("l_prefetch"))
            b,c,s=clean_folder(pf,self._bk()); self.log(self.clean_log,f"✅ {c} ({human_size(b)})")
            self.set_bar(self.clean_bar,False)
        threading.Thread(target=work,daemon=True).start()

    def act_bin(self):
        def work():
            self.set_bar(self.clean_bar,True); self.log(self.clean_log,self.t("l_bin"))
            self.log(self.clean_log,self.t("l_bin_ok") if empty_bin() else self.t("l_bin_fail"))
            self.set_bar(self.clean_bar,False)
        threading.Thread(target=work,daemon=True).start()

    def act_dns(self):
        def work():
            self.set_bar(self.clean_bar,True); self.log(self.clean_log,self.t("l_dns"))
            ok,_=run_cmd("ipconfig /flushdns")
            self.log(self.clean_log,self.t("l_dns_ok") if ok else self.t("l_dns_fail"))
            self.set_bar(self.clean_bar,False)
        threading.Thread(target=work,daemon=True).start()

    def act_update(self):
        def work():
            self.set_bar(self.clean_bar,True); self.log(self.clean_log,self.t("l_wu"))
            run_cmd("net stop wuauserv"); run_cmd("net stop bits")
            folder=os.path.join(os.environ.get("SystemRoot",r"C:\Windows"),"SoftwareDistribution","Download")
            b,c,s=clean_folder(folder,self._bk())
            self.log(self.clean_log,f"✅ {c} ({human_size(b)})")
            run_cmd("net start wuauserv"); run_cmd("net start bits")
            self.log(self.clean_log,self.t("l_done")); self.set_bar(self.clean_bar,False)
        threading.Thread(target=work,daemon=True).start()

    def act_all(self):
        def work():
            self.set_bar(self.clean_bar,True); self.log(self.clean_log,self.t("l_all"))
            tb=tf=0
            for p in [tempfile.gettempdir(),os.path.join(os.environ.get("SystemRoot",r"C:\Windows"),"Temp"),
                      os.path.join(os.environ.get("SystemRoot",r"C:\Windows"),"Prefetch")]:
                b,c,s=clean_folder(p,self._bk()); tb+=b; tf+=c
            self.log(self.clean_log,f"{self.t('l_temp')} {human_size(tb)} ({tf})")
            self.log(self.clean_log,self.t("l_bin_ok") if empty_bin() else self.t("l_bin_fail"))
            ok,_=run_cmd("ipconfig /flushdns"); self.log(self.clean_log,self.t("l_dns_ok") if ok else self.t("l_dns_fail"))
            self.after(0,self.refresh_stats)
            self.log(self.clean_log,f"{self.t('l_freed')} {human_size(tb)} — {self.t('l_done')}")
            self.set_bar(self.clean_bar,False)
        threading.Thread(target=work,daemon=True).start()

    def open_backup(self):
        os.startfile(BACKUP_ROOT)

    def restore_backup(self):
        def work():
            n=restore_latest()
            self.log(self.clean_log,self.t("l_restore_ok")+f" ({n})" if n else self.t("l_no_backup"))
        threading.Thread(target=work,daemon=True).start()

    # ---------- الإصلاح ----------
    def build_fix(self):
        f=self.frames["fix"]
        ctk.CTkLabel(f,text=self.t("fix_title"),font=ctk.CTkFont(size=22,weight="bold")).pack(pady=(8,10))
        grid=ctk.CTkFrame(f,fg_color="transparent"); grid.pack(padx=10)
        fixes=[(self.t("f_sfc"),"sfc /scannow",self.t("l_sfc")),
               (self.t("f_dism"),"DISM /Online /Cleanup-Image /RestoreHealth",self.t("l_dism")),
               (self.t("f_chkdsk"),"echo y | chkdsk C: /F",self.t("l_chkdsk")),
               (self.t("f_winsock"),"netsh winsock reset",self.t("l_winsock")),
               (self.t("f_ip"),"netsh int ip reset",self.t("l_ip")),
               (self.t("f_net"),None,self.t("l_net"))]
        for i,(txt,cmd,note) in enumerate(fixes):
            ctk.CTkButton(grid,text=txt,width=300,height=42,font=ctk.CTkFont(size=13),
                          command=lambda c=cmd,n=note:(self.fix_net() if c is None else self.fix_cmd(c,n))
                          ).grid(row=i//2,column=i%2,padx=6,pady=6)
        self.fix_bar=ctk.CTkProgressBar(f); self.fix_bar.pack(fill="x",padx=20,pady=5); self.fix_bar.set(0)
        self.fix_log=ctk.CTkTextbox(f,font=ctk.CTkFont(size=12))
        self.fix_log.pack(fill="both",expand=True,padx=20,pady=(5,10))

    def fix_cmd(self,cmd,note):
        def work():
            self.set_bar(self.fix_bar,True); self.log(self.fix_log,note)
            ok,out=run_cmd(cmd)
            tail="\n".join((out or "").splitlines()[-6:])
            for line in tail.splitlines(): self.log(self.fix_log,"   "+line)
            self.log(self.fix_log,"✅" if ok else "⚠️"); self.set_bar(self.fix_bar,False)
        threading.Thread(target=work,daemon=True).start()

    def fix_net(self):
        def work():
            self.set_bar(self.fix_bar,True); self.log(self.fix_log,self.t("l_net"))
            run_cmd("netsh winsock reset"); run_cmd("netsh int ip reset")
            ok,_=run_cmd("ipconfig /flushdns"); self.log(self.fix_log,self.t("l_dns_ok") if ok else self.t("l_dns_fail"))
            self.log(self.fix_log,self.t("l_net_done")); self.set_bar(self.fix_bar,False)
        threading.Thread(target=work,daemon=True).start()

    # ---------- بدء التشغيل ----------
    def build_startup(self):
        f=self.frames["startup"]
        ctk.CTkLabel(f,text=self.t("startup_title"),font=ctk.CTkFont(size=22,weight="bold")).pack(pady=(8,5))
        top=ctk.CTkFrame(f,fg_color="transparent"); top.pack(fill="x",padx=10)
        ctk.CTkLabel(top,text=self.t("startup_hint"),font=ctk.CTkFont(size=12),text_color="gray").pack(side="right")
        ctk.CTkButton(top,text=self.t("s_refresh"),width=120,command=self.refresh_startup).pack(side="left",padx=5)
        self.startup_scroll=ctk.CTkScrollableFrame(f)
        self.startup_scroll.pack(fill="both",expand=True,padx=10,pady=10)

    def refresh_startup(self):
        if not hasattr(self,"startup_scroll"): return
        for w in self.startup_scroll.winfo_children(): w.destroy()
        entries=list_startup()
        if not entries:
            ctk.CTkLabel(self.startup_scroll,text=self.t("s_empty")).pack(pady=10); return
        for tag,root,sub,name,value in entries:
            row=ctk.CTkFrame(self.startup_scroll); row.pack(fill="x",pady=2)
            ctk.CTkLabel(row,text=f"{name} [{tag}]",width=190,anchor="e",font=ctk.CTkFont(size=12,weight="bold")).pack(side="right",padx=5)
            ctk.CTkLabel(row,text=str(value)[:80],anchor="e",font=ctk.CTkFont(size=11)).pack(side="right",padx=5,fill="x",expand=True)
            ctk.CTkButton(row,text=self.t("s_del"),width=80,fg_color="#c0392b",hover_color="#e74c3c",
                          command=lambda r=root,s=sub,n=name:(del_startup(r,s,n),self.refresh_startup())
                          ).pack(side="left",padx=5)

    # ---------- الإحصاءات (الرسم البياني) ----------
    def build_charts(self):
        f=self.frames["charts"]
        ctk.CTkLabel(f,text=self.t("charts_title"),font=ctk.CTkFont(size=22,weight="bold")).pack(pady=(8,2))
        ctk.CTkLabel(f,text=self.t("c_hint"),font=ctk.CTkFont(size=11),text_color="gray").pack()
        ctk.CTkButton(f,text=self.t("c_update"),width=140,command=self.update_chart).pack(pady=6)
        self.chart_frame=ctk.CTkFrame(f); self.chart_frame.pack(fill="both",expand=True,padx=10,pady=10)
        self.update_chart()

    def update_chart(self):
        if not hasattr(self,"chart_frame"): return
        for w in self.chart_frame.winfo_children(): w.destroy()
        h=load_history()
        fig=Figure(figsize=(7,4),dpi=90,facecolor="#2b2b2b")
        ax=fig.add_subplot(111); ax.set_facecolor("#2b2b2b")
        if h:
            x=list(range(len(h)))
            ax.plot(x,[p["ram"] for p in h],color="#4fc3f7",label="RAM %",linewidth=2)
            ax.plot(x,[p["disk"] for p in h],color="#ffb74d",label="Disk C: %",linewidth=2)
            ax.set_ylim(0,100); ax.set_ylabel("%",color="white")
            ticks=list(range(0,len(h),max(1,len(h)//8)))
            ax.set_xticks(ticks); ax.set_xticklabels([h[i]["t"] for i in ticks],color="white",rotation=45,fontsize=7)
            ax.tick_params(colors="white"); ax.legend(facecolor="#2b2b2b",labelcolor="white")
            for sp in ax.spines.values(): sp.set_color("#555")
        else:
            ax.text(0.5,0.5,"No data yet — refresh the Home page",color="white",ha="center",transform=ax.transAxes)
        canvas=FigureCanvasTkAgg(fig,master=self.chart_frame)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both",expand=True)

    # ---------- الإعدادات ----------
    def build_settings(self):
        f=self.frames["settings"]
        ctk.CTkLabel(f,text=self.t("settings_title"),font=ctk.CTkFont(size=22,weight="bold")).pack(pady=(10,15))
        box=ctk.CTkFrame(f,width=520); box.pack(padx=20,pady=5); box.pack_propagate(False)
        ctk.CTkLabel(box,text=self.t("lang_lbl"),font=ctk.CTkFont(size=14)).pack(anchor="e",padx=15,pady=(15,5))
        ctk.CTkButton(box,text=self.t("lang_btn"),width=200,height=38,command=self.switch_lang).pack(padx=15,pady=5)
        ctk.CTkLabel(box,text=self.t("auto_lbl"),font=ctk.CTkFont(size=14,weight="bold")).pack(anchor="e",padx=15,pady=(15,2))
        ctk.CTkLabel(box,text=self.t("auto_desc"),font=ctk.CTkFont(size=11),text_color="gray").pack(anchor="e",padx=15)
        self.auto_var=ctk.CTkCheckBox(box,text="")
        self.auto_var.pack(anchor="e",padx=15,pady=5)
        if is_autostart(): self.auto_var.select()
        self.auto_var.configure(command=self.on_auto_toggle)
        ctk.CTkLabel(box,text=self.t("backup_lbl"),font=ctk.CTkFont(size=14,weight="bold")).pack(anchor="e",padx=15,pady=(15,2))
        ctk.CTkLabel(box,text=self.t("backup_desc"),font=ctk.CTkFont(size=11),text_color="gray").pack(anchor="e",padx=15)
        self.bk_var=ctk.CTkCheckBox(box,text="")
        self.bk_var.pack(anchor="e",padx=15,pady=5)
        if self.backup_enabled: self.bk_var.select()
        self.bk_var.configure(command=self.on_backup_toggle)
        ctk.CTkButton(box,text=self.t("clear_backups"),width=250,height=38,fg_color="#c0392b",hover_color="#e74c3c",
                      command=self.clear_backups).pack(padx=15,pady=(15,10))
        self.settings_msg=ctk.CTkLabel(f,text="",text_color="#2ecc71",font=ctk.CTkFont(size=12))
        self.settings_msg.pack(pady=5)

    def on_auto_toggle(self):
        try:
            set_autostart(bool(self.auto_var.get()))
            self.settings_msg.configure(text=self.t("saved"))
        except Exception as e:
            messagebox.showerror("Error",str(e))

    def on_backup_toggle(self):
        self.backup_enabled=bool(self.bk_var.get())
        self.prefs["backup"]=self.backup_enabled; save_prefs(self.prefs)
        self.settings_msg.configure(text=self.t("saved"))

    def clear_backups(self):
        if messagebox.askyesno("?",self.t("clear_backups")):
            shutil.rmtree(BACKUP_ROOT,ignore_errors=True); os.makedirs(BACKUP_ROOT,exist_ok=True)
            self.settings_msg.configure(text=self.t("l_cleared"))

    # ---------- حول ----------
    def build_about(self):
        f=self.frames["about"]
        ctk.CTkLabel(f,text=f"🧹 {self.t('app')}",font=ctk.CTkFont(size=26,weight="bold")).pack(pady=(30,5))
        ctk.CTkLabel(f,text=f"v{VERSION}",font=ctk.CTkFont(size=14),text_color="gray").pack()
        ctk.CTkLabel(f,text=self.t("about_text"),font=ctk.CTkFont(size=13),justify="right").pack(padx=40,pady=20)

    # ---------- الوضع التلقائي (--auto) ----------
    def auto_clean_and_exit(self):
        self.withdraw()
        def work():
            with open(AUTO_LOG,"a",encoding="utf-8") as lf:
                lf.write(f"\n=== {datetime.now()} ===\n")
                for p in [tempfile.gettempdir(),os.path.join(os.environ.get("SystemRoot",r"C:\Windows"),"Prefetch")]:
                    b,c,s=clean_folder(p,True); lf.write(f"{p}: {c} files, {human_size(b)}\n")
                lf.write(f"bin: {empty_bin()}\n")
                ok,_=run_cmd("ipconfig /flushdns"); lf.write(f"dns: {ok}\n")
            self.after(0,self.destroy)
        threading.Thread(target=work,daemon=True).start()

# ================= التشغيل =================
if __name__=="__main__":
    app=App()
    if "--auto" in sys.argv:
        app.after(1200,app.auto_clean_and_exit)
    app.mainloop()
