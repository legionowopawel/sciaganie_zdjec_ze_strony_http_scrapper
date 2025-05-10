#!/usr/bin/env python
import os
import sys
import shutil
import subprocess
import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Globalna referencja do procesu crawlera,
# dzięki której można anulować działanie w trakcie pobierania.
current_proc = None

def run_crawler(url, dest):
    """
    Funkcja tworzaca nowy projekt Scrapy, generująca plik spidera oraz uruchamiająca crawlera.
    Pobiera pliki multimedialne ze strony podanej przez użytkownika i zapisuje je w wskazanym katalogu.
    """
    global current_proc
    # Ustalanie ścieżki dla projektu Scrapy (katalog "scrapy_project")
    project_folder = os.path.join(os.getcwd(), "scrapy_project")
    
    # Jeśli istnieje stary projekt, usuń go.
    if os.path.exists(project_folder):
        try:
            shutil.rmtree(project_folder)
            print("Poprzedni projekt Scrapy został usunięty.")
        except Exception as e:
            print("Błąd przy usuwaniu starego projektu Scrapy:", e)
            return

    # Utwórz nowy projekt Scrapy
    try:
        result = subprocess.run(["scrapy", "startproject", "scrapy_project"], 
                                  capture_output=True, text=True, check=True)
        print("Projekt Scrapy został utworzony.")
    except subprocess.CalledProcessError as e:
        print("Błąd przy tworzeniu projektu Scrapy:", e.stderr)
        return

    # Ścieżka do katalogu ze spiderami znajduje się wewnątrz utworzonego projektu:
    # scrapy_project/scrapy_project/spiders/
    spider_dir = os.path.join(project_folder, "scrapy_project", "spiders")
    spider_file = os.path.join(spider_dir, "dynamic_spider.py")
    
    # Pobieramy domenę z URL (do allowed_domains)
    try:
        domain = url.split('/')[2]
    except IndexError:
        domain = ""

    # Kod spidera – pobiera obrazy i wideo z danej strony, zapisując pliki w folderze dest.
    spider_code = f'''import scrapy
from urllib.parse import urljoin
import os
import requests
from tqdm import tqdm

class DynamicSpider(scrapy.Spider):
    name = "dynamic_spider"
    allowed_domains = ["{domain}"]
    start_urls = ["{url}"]
    save_path = r"{dest}"

    def download_file(self, url, file_path):
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get("content-length", 0))
            with open(file_path, "wb") as f, tqdm(
                desc=os.path.basename(file_path),
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024
            ) as bar:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))
        except Exception as e:
            self.logger.error(f"Error downloading {{url}}: {{e}}")

    def parse(self, response):
        media_urls = response.css("img::attr(src), video::attr(src)").getall()
        for media in media_urls:
            media_url = urljoin(response.url, media)
            file_name = os.path.basename(media_url)
            file_path = os.path.join(self.save_path, file_name)
            self.logger.info(f"Pobieram: {{file_name}}")
            self.download_file(media_url, file_path)
            
        links = response.css("a::attr(href)").getall()
        for link in links:
            next_page = urljoin(response.url, link)
            yield scrapy.Request(next_page, callback=self.parse)
'''

    # Zapisz plik spidera
    try:
        with open(spider_file, "w", encoding="utf-8") as f:
            f.write(spider_code)
        print("Plik spidera został utworzony.")
    except Exception as e:
        print("Błąd przy tworzeniu pliku spidera:", e)
        return

    # Uruchom crawlera – wykonaj komendę "scrapy crawl dynamic_spider"
    try:
        # Uruchomienie odbywa się w katalogu projektu, gdzie znajduje się scrapy.cfg
        current_proc = subprocess.Popen(["scrapy", "crawl", "dynamic_spider"], cwd=project_folder)
        print("Uruchomiono crawlera. W terminalu wyświetlane są postępy pobierania...")
        current_proc.communicate()
        print(f"Skończone: Twoje pliki są w {dest}.")
    except Exception as e:
        print("Błąd podczas uruchamiania crawlera:", e)
    finally:
        current_proc = None

def start_crawl():
    """
    Funkcja wywoływana przy naciśnięciu przycisku START.
    Weryfikuje dane, ustala katalog zapisu (jeśli nie został podany przez użytkownika),
    a następnie uruchamia crawlera w osobnym wątku.
    """
    url = url_entry.get().strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        messagebox.showerror("Błąd", "Podaj poprawny URL zaczynający się od http:// lub https://")
        return

    dest = path_entry.get().strip()
    # Jeżeli użytkownik nie wpisał własnej ścieżki, wygeneruj domyślną na podstawie domeny i bieżącej daty
    if dest == "":
        try:
            domain = url.split('/')[2]
            prefix = domain[:3]
        except IndexError:
            prefix = "def"
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
        dest = os.path.join(os.getcwd(), f"{prefix}_{timestamp}")
        # Aktualizuj pole tekstowe na GUI
        path_entry.delete(0, tk.END)
        path_entry.insert(0, dest)

    os.makedirs(dest, exist_ok=True)
    # Wyłącz przycisk START (zmiana koloru)
    start_button.config(state=tk.DISABLED, bg="lightgreen")
    # Uruchom crawlera w wątku, aby GUI pozostało responsywne
    t = threading.Thread(target=run_crawler, args=(url, dest))
    t.daemon = True
    t.start()
    
def cancel_action():
    """
    Funkcja obsługująca przycisk Anuluj.
    Jeśli crawler jest w trakcie działania, zatrzymuje proces.
    W przeciwnym razie zamyka program.
    """
    global current_proc
    if current_proc is not None:
        try:
            current_proc.terminate()
            current_proc = None
            print("Proces crawlera został anulowany.")
            start_button.config(state=tk.NORMAL, bg="SystemButtonFace")
        except Exception as e:
            print("Błąd przy anulowaniu procesu:", e)
    else:
        print("Kończenie programu.")
        root.destroy()

# --- Budowanie interfejsu przy użyciu Tkinter ---

root = tk.Tk()
root.title("Scrapy Downloader")
root.geometry("500x300")

# Opis programu
desc = (
    "Program służy do pobierania obrazów (oraz innych multimediów) ze strony internetowej.\n"
    "Wpisz URL strony oraz wybierz, gdzie zapisać pobrane pliki.\n"
    "Domyślna lokalizacja zapisu zostanie utworzona w katalogu programu, \n"
    "w formacie: [3 pierwsze znaki domeny]_[yyyy_mm_dd_hh_mm]."
)
desc_label = tk.Label(root, text=desc, justify=tk.CENTER)
desc_label.pack(pady=10)

# Pole do wpisania URL
url_frame = tk.Frame(root)
url_frame.pack(pady=5, fill=tk.X, padx=20)
url_label = tk.Label(url_frame, text="Ścieżka strony internetowej:")
url_label.pack(side=tk.LEFT)
url_entry = tk.Entry(url_frame, width=40)
url_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)

# Pole do wpisania katalogu zapisu
path_frame = tk.Frame(root)
path_frame.pack(pady=5, fill=tk.X, padx=20)
path_label = tk.Label(path_frame, text="Gdzie zapisać obrazy:")
path_label.pack(side=tk.LEFT)
path_entry = tk.Entry(path_frame, width=40)
path_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)

# Przyciski START i Anuluj
btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)
start_button = tk.Button(btn_frame, text="START", width=10, bg="green", fg="white", command=start_crawl)
start_button.pack(side=tk.LEFT, padx=10)
cancel_button = tk.Button(btn_frame, text="Anuluj", width=10, command=cancel_action)
cancel_button.pack(side=tk.RIGHT, padx=10)

root.mainloop()
