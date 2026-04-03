import customtkinter as ctk
import subprocess
import os

# Ruta al motor ADB en tu disco:
adb_path = r"E:\platform-tools-latest-windows\platform-tools\adb.exe"

class EstacionMando(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ESTACIÓN DE MANDO PRO - REDMI 9C")
        self.geometry("1000x650")
        ctk.set_appearance_mode("dark")

        # Configuración de columnas (Sidebar + Contenido)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL LATERAL (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="MENÚ DE MISIONES", font=("Roboto", 22, "bold"))
        self.logo.pack(pady=30)

        # Grupo 1: Mantenimiento y Velocidad
        self.label_g1 = ctk.CTkLabel(self.sidebar, text="MANTENIMIENTO", font=("Roboto", 12, "bold"), text_color="gray")
        self.label_g1.pack(pady=(10, 5))
        
        ctk.CTkButton(self.sidebar, text="3. Limpiar RAM/Caché", command=self.mision_limpieza).pack(pady=5, padx=20)
        ctk.CTkButton(self.sidebar, text="11. Activar Escudo", fg_color="#27ae60", command=self.mision_escudo).pack(pady=5, padx=20)
        ctk.CTkButton(self.sidebar, text="12. Desactivar Escudo", fg_color="#c0392b", command=lambda: self.gestionar_escudo(False)).pack(pady=5, padx=20)

        # Grupo 2: Gestión de Archivos y Apps
        self.label_g2 = ctk.CTkLabel(self.sidebar, text="ARCHIVOS Y APPS", font=("Roboto", 12, "bold"), text_color="gray")
        self.label_g2.pack(pady=(20, 5))
        
        ctk.CTkButton(self.sidebar, text="1. Listar Apps", command=lambda: self.correr_mision("pm list packages -3")).pack(pady=5, padx=20)
        ctk.CTkButton(self.sidebar, text="2. Borrar App", fg_color="#d35400", command=self.ventana_borrar_app).pack(pady=5, padx=20)
        ctk.CTkButton(self.sidebar, text="8. Buscar Pesados", command=lambda: self.correr_mision("find /sdcard/ -type f -size +100M")).pack(pady=5, padx=20)
        ctk.CTkButton(self.sidebar, text="9. Borrar Carpeta/Ruta", fg_color="#d35400", command=self.ventana_borrar_ruta).pack(pady=5, padx=20)
        ctk.CTkButton(self.sidebar, text="7. Inyectar Música", fg_color="#2980b9", command=self.mision_musica).pack(pady=5, padx=20)

        # Grupo 3: Sistema
        self.label_g3 = ctk.CTkLabel(self.sidebar, text="SISTEMA", font=("Roboto", 12, "bold"), text_color="gray")
        self.label_g3.pack(pady=(20, 5))
        
        ctk.CTkButton(self.sidebar, text="5. Reiniciar Celular", command=lambda: subprocess.run([adb_path, "reboot"])).pack(pady=5, padx=20)

        # --- CONTENIDO PRINCIPAL (DERECHA) ---
        self.main_content = ctk.CTkFrame(self, corner_radius=15)
        self.main_content.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.label_status = ctk.CTkLabel(self.main_content, text="SISTEMA LISTO", font=("Roboto", 20, "bold"), text_color="#2ecc71")
        self.label_status.pack(pady=15)

        self.textbox = ctk.CTkTextbox(self.main_content, font=("Consolas", 14))
        self.textbox.pack(padx=20, pady=10, fill="both", expand=True)

        self.btn_taskmgr = ctk.CTkButton(self.main_content, text="VER ESTADO (Admin de Tareas)", 
                                        height=50, font=("Roboto", 16, "bold"), command=self.actualizar_admin_tareas)
        self.btn_taskmgr.pack(pady=20, padx=20, fill="x")

    # --- LÓGICA DE FUNCIONES ---

    def ejecutar_adb(self, comando):
        try:
            res = subprocess.check_output(f'"{adb_path}" shell {comando}', shell=True, stderr=subprocess.STDOUT)
            return res.decode("utf-8")
        except Exception as e:
            return f"Error: No se pudo contactar con el Redmi Note 9.\n{str(e)}"

    def correr_mision(self, comando):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", f"Ejecutando misión...\n\n{self.ejecutar_adb(comando)}")

    def actualizar_admin_tareas(self):
        self.textbox.delete("1.0", "end")
        ram = self.ejecutar_adb("free -m")
        temp = self.ejecutar_adb("dumpsys battery | grep temperature")
        storage = self.ejecutar_adb("df -h /data")
        informe = f"--- MEMORIA RAM ---\n{ram}\n\n--- CALOR ---\n{temp}\n--- DISCO ---\n{storage}"
        self.textbox.insert("end", informe)

    def ventana_borrar_app(self):
        dialog = ctk.CTkInputDialog(text="Pega el nombre del paquete (ej: com.facebook.katana):", title="Borrar App")
        pkg = dialog.get_input()
        if pkg: self.correr_mision(f"pm uninstall --user 0 {pkg}")

    def ventana_borrar_ruta(self):
        dialog = ctk.CTkInputDialog(text="Pega la ruta completa de la carpeta:", title="Borrar Carpeta")
        ruta = dialog.get_input()
        if ruta and "WhatsApp" not in ruta:
            self.correr_mision(f"rm -rf '{ruta}'")
        else:
            self.textbox.insert("end", "\n[ALERTA] Operación cancelada: Ruta protegida o vacía.")

    def mision_limpieza(self):
        self.textbox.delete("1.0", "end")
        self.ejecutar_adb("pm trim-caches 999G")
        self.ejecutar_adb("rm -rf /sdcard/DCIM/.thumbnails")
        self.textbox.insert("end", "✔ Limpieza profunda terminada.\nRAM refrescada y miniaturas eliminadas.")

    def mision_musica(self):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", "Iniciando transferencia de música desde E:\Mi_música...")
        subprocess.run([adb_path, "push", r"E:\Mi_música", "/sdcard/Music/"], shell=True)
        self.textbox.insert("end", "\n\n✔ ¡Música inyectada con éxito!")

    def mision_escudo(self):
        servicios = ["com.miui.analytics", "com.miui.msa.global", "com.xiaomi.joyose", "com.miui.daemon"]
        self.textbox.delete("1.0", "end")
        for s in servicios:
            self.ejecutar_adb(f"pm disable-user --user 0 {s}")
        self.textbox.insert("end", "✔ ESCUDO ACTIVADO: El celular ya no enviará datos de rastreo.")

if __name__ == "__main__":
    app = EstacionMando()
    app.mainloop()
