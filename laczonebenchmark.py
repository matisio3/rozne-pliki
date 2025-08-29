import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import urllib.request
import io

# --- OpenGL proc na poziomie modułu ---
def opengl_proc(q):
    import pygame
    import pygame.locals as pyloc
    from OpenGL import GL
    from OpenGL import GLU
    import time
    vertices = [[1,1,-1],[1,-1,-1],[-1,-1,-1],[-1,1,-1],
                [1,1,1],[1,-1,1],[-1,-1,1],[-1,1,1]]
    edges = [(0,1),(1,2),(2,3),(3,0),
             (4,5),(5,6),(6,7),(7,4),
             (0,4),(1,5),(2,6),(3,7)]
    def draw_cube():
        GL.glBegin(GL.GL_LINES)
        for edge in edges:
            for vertex in edge:
                GL.glVertex3fv(vertices[vertex])
        GL.glEnd()
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, pyloc.DOUBLEBUF | pyloc.OPENGL)
    GLU.gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    GL.glTranslatef(0.0, 0.0, -5)
    frame_count = 0
    total_frames = 0
    start_time = time.time()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pyloc.QUIT:
                running = False
        GL.glRotatef(1, 3, 1, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        draw_cube()
        pygame.display.flip()
        frame_count += 1
        total_frames += 1
        if time.time() - start_time >= 5.0:
            running = False
    avg_fps = total_frames / 5.0
    pygame.quit()
    q.put(f"Średni FPS z 5 sekund: {avg_fps:.2f}")

# --- Pozostałe testy ---
def run_speedtest():
    try:
        import speedtest
        st = speedtest.Speedtest()
        st.get_best_server()
        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        ping = st.results.ping
        return f"Ping: {ping:.2f} ms\nDownload: {download:.2f} Mbps\nUpload: {upload:.2f} Mbps"
    except Exception as e:
        return f"Error: {e}"

def run_video_benchmark():
    import cv2
    import requests
    import os
    import time

    VIDEO_URL = 'https://raw.githubusercontent.com/matisio3/rozne-pliki/refs/heads/main/video.mp4'
    VIDEO_PATH = 'downloaded_video.mp4'
    OUT_PATH = 'output.avi'
    FOURCC = cv2.VideoWriter_fourcc(*'XVID')

    try:
        if not os.path.exists(VIDEO_PATH):
            r = requests.get(VIDEO_URL, stream=True)
            with open(VIDEO_PATH, 'wb') as f:
                for data in r.iter_content(chunk_size=1024*1024):
                    f.write(data)
        cap = cv2.VideoCapture(VIDEO_PATH)
        if not cap.isOpened():
            return "Nie można otworzyć pliku wideo."
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps    = cap.get(cv2.CAP_PROP_FPS)
        out = cv2.VideoWriter(OUT_PATH, FOURCC, fps, (width, height))
        read_frames = 0
        start_time = time.time()
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            read_frames += 1
            out.write(frame)
        elapsed = time.time() - start_time
        cap.release()
        out.release()
        return f"Przetworzono {read_frames} klatek w {elapsed:.2f} s\nŚredni FPS: {read_frames/elapsed:.2f}\nVideo by Rain MeditateHub from Pixabay"
    except Exception as e:
        return f"Błąd: {e}"

def run_disk_benchmark():
    import os
    import time
    FILE_NAME = "benchmark_test_file.bin"
    FILE_SIZE_MB = 100
    def write_test(file_name, size_mb):
        data = os.urandom(1024 * 1024)
        start = time.perf_counter()
        with open(file_name, "wb") as f:
            for _ in range(size_mb):
                f.write(data)
        end = time.perf_counter()
        return end - start
    def read_test(file_name):
        start = time.perf_counter()
        with open(file_name, "rb") as f:
            while f.read(1024 * 1024):
                pass
        end = time.perf_counter()
        return end - start
    try:
        write_time = write_test(FILE_NAME, FILE_SIZE_MB)
        read_time = read_test(FILE_NAME)
        os.remove(FILE_NAME)
        res = (f"Test zapisu ({FILE_SIZE_MB} MB):\n"
               f"Czas zapisu: {write_time:.2f} s, prędkość: {FILE_SIZE_MB / write_time:.2f} MB/s\n"
               f"Test odczytu ({FILE_SIZE_MB} MB):\n"
               f"Czas odczytu: {read_time:.2f} s, prędkość: {FILE_SIZE_MB / read_time:.2f} MB/s")
        return res
    except Exception as e:
        return f"Błąd: {e}"

def run_opengl_benchmark():
    import multiprocessing
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=opengl_proc, args=(q,))
    p.start()
    p.join()
    return q.get()

# --- GUI ---
class BenchmarkGUI:
    def __init__(self, root, logo_url=None):
        self.root = root
        root.title("Benchmark Pack")
        root.geometry("470x470")
        root.resizable(False, False)

        # --- Styl Windowsa dla Progressbar! ---
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        else:
            style.theme_use("default")
        style.configure("TFrame", background="#faf8f4")
        style.configure("TLabel", background="#faf8f4", font=('Segoe UI', 13))
        style.configure("TButton", font=('Segoe UI Semibold', 12), padding=6,
                        background="#ff8c00", foreground="#fff")
        style.map("TButton",
                  background=[("active", "#ffa347"), ("!active", "#ff8c00")])
        # NIE ustawiaj customowego stylu dla Progressbar

        if logo_url:
            try:
                with urllib.request.urlopen(logo_url) as u:
                    raw_data = u.read()
                im = Image.open(io.BytesIO(raw_data))
                im = im.convert("RGBA")
                im = im.resize((110, 110))
                self.logo_img = ImageTk.PhotoImage(im)
                logo_lbl = tk.Label(root, image=self.logo_img, bg="#faf8f4")
                logo_lbl.pack(pady=(14, 8))
            except Exception as e:
                print("Nie udało się wczytać logo:", e)

        label = ttk.Label(root, text="Wybierz benchmark do uruchomienia:", font=('Segoe UI', 15, 'bold'))
        label.pack(pady=(18, 7))

        btn_frame = ttk.Frame(root, style="TFrame")
        btn_frame.pack(pady=8)

        button_style = {
            "font": ('Segoe UI', 12, 'bold'),
            "width": 18,
            "bg": "#ff8c00",
            "fg": "#fff",
            "activebackground": "#ffa347",
            "activeforeground": "#fff",
            "bd": 0,
            "relief": "flat",
            "highlightthickness": 0,
            "cursor": "hand2"
        }

        tk.Button(btn_frame, text="Speedtest", command=lambda: self.run_bench(run_speedtest, "Trwa speedtest... Czekaj "),
                  **button_style).grid(row=0, column=0, padx=12, pady=8)
        tk.Button(btn_frame, text="Benchmark Video", command=lambda: self.run_bench(run_video_benchmark, "Trwa testowanie wideo... Czekaj "),
                  **button_style).grid(row=0, column=1, padx=12, pady=8)
        tk.Button(btn_frame, text="Dysk (zapis/odczyt)", command=lambda: self.run_bench(run_disk_benchmark, "Trwa test dysku... Czekaj "),
                  **button_style).grid(row=1, column=0, padx=12, pady=8)
        tk.Button(btn_frame, text="OpenGL FPS", command=lambda: self.run_bench(run_opengl_benchmark, "Trwa test OpenGL... Czekaj "),
                  **button_style).grid(row=1, column=1, padx=12, pady=8)
        tk.Button(root, text="Wyjdź", command=root.quit,
                  font=('Segoe UI', 11, 'bold'), bg="#eee", fg="#555", bd=0, relief="flat", width=12,
                  activebackground="#f6bfa8", activeforeground="#222", cursor="hand2"
                  ).pack(pady=(10,2))

        self.result_box = tk.Text(root, height=9, width=54, font=("Fira Code", 11), bd=0, bg="#fff4e6",
                                 fg="#20232a", highlightthickness=0, wrap="word")
        self.result_box.pack(padx=20, pady=(16, 6))
        self.result_box.config(state=tk.DISABLED)

        # Teraz pasek determinate!
        self.progress = ttk.Progressbar(root, mode='determinate', length=260, style="Horizontal.TProgressbar", maximum=100)
        self.progress.pack(pady=(6,12))

    def run_bench(self, func, spinner_label):
        self.result_box.config(state=tk.NORMAL)
        self.result_box.delete(1.0, tk.END)
        self.result_box.config(state=tk.DISABLED)
        self.progress['value'] = 0
        spinner_running = [True]

        def spinner():
            spinner_chars = ['|', '/', '-', '\\']
            idx = 0
            value = 0
            while spinner_running[0]:
                msg = spinner_label + spinner_chars[idx % len(spinner_chars)]
                self.result_box.config(state=tk.NORMAL)
                self.result_box.delete(1.0, tk.END)
                self.result_box.insert(tk.END, msg)
                self.result_box.config(state=tk.DISABLED)
                # Wypełnianie progresu "płynnie"
                if value < 90:
                    value += 2
                self.progress['value'] = value
                idx += 1
                self.result_box.update()
                self.progress.update()
                self.result_box.after(100)
            self.progress['value'] = 100  # Po zakończeniu — na pełno

        def bench_thread():
            t_spin = threading.Thread(target=spinner)
            t_spin.start()
            try:
                result = func()
            except Exception as e:
                result = f"Błąd: {e}"
            finally:
                spinner_running[0] = False
            def show_result():
                self.result_box.config(state=tk.NORMAL)
                self.result_box.delete(1.0, tk.END)
                if "Błąd" in result or "Error" in result:
                    self.result_box.insert(tk.END, result)
                    self.result_box.tag_add("err", "1.0", "end")
                    self.result_box.tag_config("err", foreground="#c0392b")
                else:
                    self.result_box.insert(tk.END, result)
                    self.result_box.tag_add("ok", "1.0", "end")
                    self.result_box.tag_config("ok", foreground="#2c742f")
                self.result_box.config(state=tk.DISABLED)
                self.progress['value'] = 100  # Zawsze 100% na końcu
            self.result_box.after(0, show_result)
        threading.Thread(target=bench_thread, daemon=True).start()

if __name__ == "__main__":
    logo_url = None  # lub podaj link
    root = tk.Tk()
    app = BenchmarkGUI(root, logo_url=logo_url)
    root.mainloop()
