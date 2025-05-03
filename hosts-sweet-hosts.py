import os
import platform
import ctypes
import requests
import shutil
import configparser
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading

CONFIG_FILE = "config.ini"
CONFIG_SECTION = "Settings"
CONFIG_SECTION_PARAM = "Settings_Param"
APPNAME = "Hosts Sweet Hosts"
APPVERSION = "0.2"
MENTION = ""

class RepeatedTimer:
    def __init__(self, interval, function, args=None, kwargs=None, timer_var=None):
        self.interval = interval
        self.function = function
        self.args = args if args else []
        self.kwargs = kwargs if kwargs else {}
        self.timer_var = timer_var
        self.thread = None
        self.is_running = False

    def _run(self):
        self.is_running = False
        self.start()
        if self.timer_var is not None:
            self.timer_var.set(self.interval)
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self.thread = threading.Timer(self.interval, self._run)
            self.thread.daemon = True
            self.thread.start()
            self.is_running = True

    def stop(self):
        if self.thread:
            self.thread.cancel()
        self.is_running = False

def is_admin():
    if os.name == 'nt':
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0

def get_os():
    os_name = platform.system()
    if os_name == "Windows":
        return "Windows"
    elif os_name == "Darwin":
        return "Mac"
    else:
        return None

def get_hosts_path(os_type):
    if os_type == "Windows":
        return r"C:\Windows\System32\drivers\etc\hosts"
    elif os_type == "Mac":
        return "/etc/hosts"
    else:
        raise Exception("Système d'exploitation non supporté.")

def download_hosts_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def backup_file(file_path):
    backup_path = file_path + ".bak"
    shutil.copy(file_path, backup_path)

def replace_hosts_file(file_path, content):
    backup_file(file_path)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def flush_dns(os_type):
    if os_type == "Windows":
        os.system("ipconfig /flushdns")
    elif os_type == "Mac":
        os.system("sudo killall -HUP mDNSResponder")

def load_config():
    config = configparser.RawConfigParser()
    if not os.path.exists(CONFIG_FILE):
        config[CONFIG_SECTION] = {
            "hosts_url": "https://example.com/hosts",
            "window_geometry": "550x400+100+100",
            "refresh_time": "1",  # minutes par défaut
            "auto_refresh": "False"  # --- AJOUT AUTO REFRESH ---
        }
        config[CONFIG_SECTION_PARAM] = {
            "param_geometry": "420x265+300+300"
        }
        with open(CONFIG_FILE, "w") as f:
            config.write(f)
    else:
        config.read(CONFIG_FILE)
        if CONFIG_SECTION not in config:
            config[CONFIG_SECTION] = {
                "hosts_url": "https://example.com/hosts",
                "window_geometry": "550x400+100+100",
                "refresh_time": "1",
                "auto_refresh": "False"  # --- AJOUT AUTO REFRESH ---
            }
        if CONFIG_SECTION_PARAM not in config:
            config[CONFIG_SECTION_PARAM] = {
                "param_geometry": "420x265+300+300"
            }
        # --- AJOUT AUTO REFRESH : ajout si absent ---
        if "auto_refresh" not in config[CONFIG_SECTION]:
            config[CONFIG_SECTION]["auto_refresh"] = "False"
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

def open_settings_window(parent, url_var, refresh_time_var, config, update_labels_callback, auto_refresh_var):
    def save_and_close():
        url = url_entry.get().strip()
        refresh = refresh_entry.get().strip()
        if not url.startswith("https://"):
            messagebox.showerror("Erreur", "Veuillez entrer une URL HTTPS valide.")
            return
        try:
            val = int(refresh)
            if val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre entier positif pour le temps de rafraîchissement.")
            return
        config[CONFIG_SECTION]["hosts_url"] = url
        config[CONFIG_SECTION]["refresh_time"] = refresh
        config[CONFIG_SECTION]["auto_refresh"] = str(auto_refresh_var.get())  # --- AJOUT AUTO REFRESH ---
        config[CONFIG_SECTION_PARAM]["param_geometry"] = settings_win.winfo_geometry()
        save_config(config)
        url_var.set(url)
        refresh_time_var.set(refresh)
        update_labels_callback()
        settings_win.destroy()

    settings_win = tk.Toplevel(parent)
    settings_win.title("Paramètres")
    param_geometry = config[CONFIG_SECTION_PARAM].get("param_geometry", "420x265+250+250")
    settings_win.geometry(param_geometry)
    settings_win.resizable(False, True)
    settings_win.configure(bg="#222831")

    # URL
    tk.Label(settings_win, text="URL du fichier hosts :", bg="#222831", fg="#eeeeee", font=("Segoe UI", 11)).pack(pady=(14, 4))
    url_entry = tk.Entry(settings_win, width=55, font=('Segoe UI', 11), bg="#393e46", fg="#eeeeee", insertbackground="#eeeeee", borderwidth=2, relief="groove")
    url_entry.pack(pady=(0, 8), ipadx=2, ipady=4)
    url_entry.insert(0, url_var.get())

    # Temps de rafraîchissement en minutes
    tk.Label(settings_win, text="Temps de rafraîchissement (minutes) :", bg="#222831", fg="#eeeeee", font=("Segoe UI", 11)).pack(pady=(0, 2))
    refresh_entry = tk.Entry(settings_win, width=15, font=("Segoe UI", 12), bg="#393e46", fg="#eeeeee", insertbackground="#eeeeee", borderwidth=2, relief="groove")
    refresh_entry.pack(pady=(0, 8), ipadx=8, ipady=6)
    refresh_entry.insert(0, refresh_time_var.get())

    # --- AJOUT AUTO REFRESH : case à cocher ---
    auto_refresh_check = tk.Checkbutton(
        settings_win,
        text="Auto Refresh (lancer automatiquement la mise à jour)",
        variable=auto_refresh_var,
        onvalue=True,
        offvalue=False,
        bg="#222831",
        fg="#eeeeee",
        selectcolor="#393e46",
        font=("Segoe UI", 11)
    )
    auto_refresh_check.pack(pady=(0, 16))
    # --- FIN AJOUT ---

    save_btn = tk.Button(settings_win, text="Enregistrer", width=16, bg="#00adb5", fg="#222831", font=("Segoe UI", 12, "bold"),
                         activebackground="#007c80", activeforeground="#eeeeee", command=save_and_close)
    save_btn.pack(pady=(0, 16))

    def on_param_close():
        config[CONFIG_SECTION_PARAM]["param_geometry"] = settings_win.winfo_geometry()
        save_config(config)
        settings_win.destroy()

    settings_win.protocol("WM_DELETE_WINDOW", on_param_close)
    settings_win.transient(parent)
    settings_win.grab_set()
    settings_win.focus_set()

def main_process(url, output_widget):
    try:
        os_type = get_os()
        if not os_type:
            output_widget.insert(tk.END, "Erreur : Système d'exploitation non supporté.\n")
            output_widget.see(tk.END)
            return
        output_widget.insert(tk.END, f"Système détecté : {os_type}\n")
        output_widget.see(tk.END)
        if not is_admin():
            output_widget.insert(tk.END, "Erreur : droits administrateur nécessaires.\n")
            output_widget.see(tk.END)
            return
        output_widget.insert(tk.END, "Téléchargement du fichier hosts...\n")
        output_widget.see(tk.END)
        hosts_content = download_hosts_file(url)
        output_widget.insert(tk.END, "Fichier hosts téléchargé.\n")
        output_widget.see(tk.END)
        hosts_path = get_hosts_path(os_type)
        replace_hosts_file(hosts_path, hosts_content)
        output_widget.insert(tk.END, f"Fichier hosts remplacé ({hosts_path}).\n")
        output_widget.see(tk.END)
        flush_dns(os_type)
        output_widget.insert(tk.END, "Cache DNS vidé. Opération terminée.\n")
        output_widget.see(tk.END)
    except Exception as e:
        output_widget.insert(tk.END, f"Erreur : {e}\n")
        output_widget.see(tk.END)

def wipe_hosts_file(output_widget):
    # Ajout du popup de confirmation
    if not messagebox.askyesno("Confirmation", "Etes-vous sûr de vouloir supprimer tous les hosts locaux ?"):
        return
    
    try:
        os_type = get_os()
        if not os_type:
            output_widget.insert(tk.END, "Erreur : Système d'exploitation non supporté.\n")
            output_widget.see(tk.END)
            return
        if not is_admin():
            output_widget.insert(tk.END, "Erreur : droits administrateur nécessaires.\n")
            output_widget.see(tk.END)
            return
        hosts_path = get_hosts_path(os_type)
        backup_file(hosts_path)
        with open(hosts_path, 'w', encoding='utf-8') as f:
            f.write("")
        output_widget.insert(tk.END, f"Fichier hosts vidé ({hosts_path}).\n")
        flush_dns(os_type)
        output_widget.insert(tk.END, "Cache DNS vidé.\n")
        output_widget.see(tk.END)
    except Exception as e:
        output_widget.insert(tk.END, f"Erreur lors du wipe : {e}\n")
        output_widget.see(tk.END)

rt = None  # Timer global

def get_refresh_time(refresh_time_var):
    try:
        val = int(refresh_time_var.get())
        if val <= 0:
            raise ValueError
        return val * 60  # Conversion minutes -> secondes
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer un nombre entier positif pour le temps de rafraîchissement.")
        return None

# Fonction pour créer un tooltip
def create_tooltip(widget, text):
    tooltip = None
    timer_id = None
    alpha = 0.0
    fade_in_progress = False
    fade_out_progress = False
    
    def enter(event):
        nonlocal tooltip, timer_id
        if timer_id:
            widget.after_cancel(timer_id)
        # Délai de 1.5 secondes avant d'afficher le tooltip
        timer_id = widget.after(750, show_tooltip)
    
    def show_tooltip():
        nonlocal tooltip, alpha, fade_in_progress
        if tooltip:
            return
            
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 20
        
        # Création du tooltip
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        tooltip.attributes("-alpha", 0.0)  # Commence complètement transparent
        
        label = tk.Label(tooltip, text=text, justify='left',
                         background="#ffffcc", relief="solid", borderwidth=1,
                         font=("Segoe UI", 10))
        label.pack(ipadx=5, ipady=3)
        
        # Démarrer l'animation de fondu
        alpha = 0.0
        fade_in_progress = True
        fade_in()
    
    def fade_in():
        nonlocal alpha, fade_in_progress
        if tooltip and fade_in_progress:
            alpha += 0.1
            if alpha >= 1.0:
                alpha = 1.0
                fade_in_progress = False
            else:
                tooltip.attributes("-alpha", alpha)
                widget.after(30, fade_in)  # Continuer l'animation
            tooltip.attributes("-alpha", alpha)
    
    def leave(event):
        nonlocal timer_id, fade_out_progress
        if timer_id:
            widget.after_cancel(timer_id)
            timer_id = None
        
        if tooltip:
            fade_out_progress = True
            fade_out()
    
    def fade_out():
        nonlocal alpha, tooltip, fade_out_progress
        if tooltip and fade_out_progress:
            alpha -= 0.1
            if alpha <= 0:
                tooltip.destroy()
                tooltip = None
                fade_out_progress = False
            else:
                tooltip.attributes("-alpha", alpha)
                widget.after(30, fade_out)  # Continuer l'animation
    
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

def main():
    config = load_config()
    root = tk.Tk()
    #root.title("Gestionnaire de hosts")
    root.title(f"{APPNAME} {APPVERSION} {MENTION}")
    saved_geometry = config[CONFIG_SECTION].get("window_geometry", "580x370+100+100")
    root.geometry(saved_geometry)
    root.configure(bg="#222831")
    fg_color = "#eeeeee"
    accent_color = "#00adb5"
    btn_bg = "#393e46"

    url_var = tk.StringVar()
    url_var.set(config[CONFIG_SECTION].get("hosts_url", "https://example.com/hosts"))

    refresh_time_var = tk.StringVar()
    refresh_time_var.set(config[CONFIG_SECTION].get("refresh_time", "1"))

    # --- AJOUT AUTO REFRESH : variable tkinter ---
    auto_refresh_var = tk.BooleanVar()
    auto_refresh_var.set(config[CONFIG_SECTION].get("auto_refresh", "False") == "True")
    # --- FIN AJOUT ---

    time_left_var = tk.IntVar(value=0)
    timer_active = tk.BooleanVar(value=False)

    def update_config_labels():
        url_label_val.config(text=url_var.get())
        refresh_label_val.config(text=f"{refresh_time_var.get()} min")
        admin_label_val.config(text="Oui" if is_admin() else "Non")

    frame_config = tk.Frame(root, bg="#222831")
    frame_config.pack(pady=(20, 10))

    tk.Label(frame_config, text="URL du fichier hosts :", bg="#222831", fg=fg_color, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=2)
    url_label_val = tk.Label(frame_config, text=url_var.get(), bg="#222831", fg=accent_color, font=("Segoe UI", 11))
    url_label_val.grid(row=0, column=1, sticky="w", padx=5, pady=2)

    tk.Label(frame_config, text="Temps de rafraîchissement :", bg="#222831", fg=fg_color, font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=2)
    refresh_label_val = tk.Label(frame_config, text=f"{refresh_time_var.get()} min", bg="#222831", fg=accent_color, font=("Segoe UI", 11))
    refresh_label_val.grid(row=1, column=1, sticky="w", padx=5, pady=2)

    tk.Label(frame_config, text="Droits administrateur :", bg="#222831", fg=fg_color, font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=2)
    admin_label_val = tk.Label(frame_config, text="Oui" if is_admin() else "Non", bg="#222831", fg=accent_color, font=("Segoe UI", 11))
    admin_label_val.grid(row=2, column=1, sticky="w", padx=5, pady=2)

    output_widget = scrolledtext.ScrolledText(root, width=65, height=10, font=("Consolas", 10), bg="#393e46", fg=fg_color, borderwidth=2, relief="groove")
    output_widget.pack(pady=(0, 8))

    timer_label = tk.Label(root, text="", font=("Segoe UI", 12, "bold"), bg="#222831", fg="#00adb5")
    timer_label.pack(pady=(0, 10))

    def update_timer_label():
        seconds = time_left_var.get()
        if timer_active.get() and seconds > 0:
            min_left = seconds // 60
            sec_left = seconds % 60
            timer_label.config(text=f"Prochaine mise à jour dans {min_left:02d}:{sec_left:02d}")
            time_left_var.set(seconds - 1)
        elif timer_active.get():
            timer_label.config(text="Prochaine mise à jour imminente…")
        else:
            timer_label.config(text="Pas de mise à jour en cours…")
        root.after(1000, update_timer_label)

    btn_frame = tk.Frame(root, bg="#222831")
    btn_frame.pack()

    def start_timer():
        global rt
        url = url_var.get().strip()
        if not url.startswith("https://"):
            messagebox.showerror("Erreur", "Veuillez entrer une URL HTTPS valide.")
            return
        output_widget.delete(1.0, tk.END)
        if rt is not None:
            rt.stop()
        threading.Thread(target=main_process, args=(url, output_widget), daemon=True).start()
        interval = get_refresh_time(refresh_time_var)
        if interval is None:
            return
        time_left_var.set(interval)
        rt = RepeatedTimer(interval, main_process, args=(url, output_widget), timer_var=time_left_var)
        rt.start()
        timer_active.set(True)
        va_btn.config(text="Stop")
        update_wipe_btn_state()

    def stop_timer():
        global rt
        if rt is not None:
            rt.stop()
        timer_active.set(False)
        va_btn.config(text="GO")
        time_left_var.set(0)
        update_wipe_btn_state()

    def toggle_timer():
        if not timer_active.get():
            start_timer()
        else:
            stop_timer()

    va_btn = tk.Button(btn_frame, text="GO", width=12, bg=accent_color, fg="#222831", font=("Segoe UI", 11, "bold"),
                       activebackground="#007c80", activeforeground=fg_color,
                       command=toggle_timer)
    va_btn.grid(row=0, column=0, padx=10)

    params_btn = tk.Button(btn_frame, text="Paramètres", width=12, bg=btn_bg, fg=fg_color, font=("Segoe UI", 11),
                           activebackground="#222831", activeforeground=accent_color,
                           command=lambda: open_settings_window(root, url_var, refresh_time_var, config, update_config_labels, auto_refresh_var))
    params_btn.grid(row=0, column=1, padx=10)
    # Ajout du tooltip pour le bouton Paramètres
    create_tooltip(params_btn, "Vos configurations...")

    # Interversion des boutons Quitter et Wipe Hosts (colonnes 2 et 3)
    wipe_btn = tk.Button(
        btn_frame,
        text="Wipe Hosts",
        width=12,
        bg=btn_bg,
        fg=fg_color,
        font=("Segoe UI", 11),
        activebackground="#222831",
        activeforeground=accent_color,
        command=lambda: wipe_hosts_file(output_widget),
        state=tk.NORMAL if not timer_active.get() else tk.DISABLED
    )
    wipe_btn.grid(row=0, column=2, padx=10)  # Maintenant en colonne 2 (avant en colonne 3)
    # Ajout du tooltip pour le bouton Wipe Hosts
    create_tooltip(wipe_btn, "Effacer les Hosts locaux")

    quit_btn = tk.Button(btn_frame, text="Quitter", width=12, bg=btn_bg, fg=fg_color, font=("Segoe UI", 11),
                         activebackground="#222831", activeforeground=accent_color,
                         command=root.destroy)
    quit_btn.grid(row=0, column=3, padx=10)  # Maintenant en colonne 3 (avant en colonne 2)

    def update_wipe_btn_state():
        if timer_active.get():
            wipe_btn.config(state=tk.DISABLED)
        else:
            wipe_btn.config(state=tk.NORMAL)
    update_wipe_btn_state()

    def on_closing():
        config[CONFIG_SECTION]["window_geometry"] = root.winfo_geometry()
        config[CONFIG_SECTION]["hosts_url"] = url_var.get()
        config[CONFIG_SECTION]["refresh_time"] = refresh_time_var.get()
        config[CONFIG_SECTION]["auto_refresh"] = str(auto_refresh_var.get())  # --- AJOUT AUTO REFRESH ---
        save_config(config)
        global rt
        if rt is not None:
            rt.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    update_config_labels()
    update_timer_label()

    # --- AJOUT AUTO REFRESH : lancement auto si activé ---
    if auto_refresh_var.get():
        start_timer()
    # --- FIN AJOUT ---

    root.mainloop()

if __name__ == "__main__":
    main()
