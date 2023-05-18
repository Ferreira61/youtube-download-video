# Importando os módulos necessários

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

import threading

import urllib.request
from io import BytesIO

import yt_dlp as youtube_dl
import re
import os



class YoutubeDownloadWindow(tk.Tk):


    def get_unique_resolutions(self, inf_dict):
        resolutions = {}
        for format in inf_dict['formats']:
            if re.match(r'^\d+p', format['format_note']) :
                resolution_id = format['format_id']
                resolution = format['format_note']
                if 'HDR' in resolution:
                    resolution = re.search(r'\d+p\d* HDR', resolution)[0]
                resolutions[resolution ] =resolution_id

        resolutions = [(v, k) for k, v in resolutions.items()]
        return sorted(resolutions, key=lambda k: [int(k[1].split('p')[0]), k[1].split('p')[-1]])


    def download_info_dict(self):
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio/best',
            'forcejson': True,
            'dump_single_json': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.video_url.get(), download=False)
        return info_dict

    def download_thumbnail(self, url):
        with urllib.request.urlopen(url) as url:
            img_data = url.read()
        return img_data

    def create_pil_image(self, img_data):
        img = Image.open(BytesIO(img_data))
        img.thumbnail((120, 120))
        return img

    def create_photo_image(self, img):
        return ImageTk.PhotoImage(img)

    def display_image_and_title(self, info_dict, photo2):
        label = tk.Label(self.image_frame, image=photo2)
        label.grid(row = 0 , padx = 5, pady = 5)
        label.configure(image=photo2)
        label.image = photo2

        text_label = tk.Label(
            self.image_frame,
            text=info_dict['title'],
            font=("Arial", 8, "bold"),
            bg="#FFFFFF",
            fg="#000000"
        )
        text_label.grid(row=1, padx=5, pady=5)

    def create_resolutions_label(self):
        resolutions_label = tk.Label(
            self.entry_frame,
            text="Resolutions:",
            font=("verdana", "10"),
            bg="#4F4F4F",
            fg="#000000",
            anchor=tk.SE
        )
        resolutions_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)

    def create_resolutions_dropdown(self, info_dict):
        resolutions = self.get_unique_resolutions(info_dict)
        self.resolutions_fields['values'] = [res[1] for res in resolutions]
        self.ids = {res[1]: res[0] for res in resolutions}
        self.resolutions_fields.current(0)
        self.resolutions_fields.grid(row=2, column=1, pady=5)

    def set_image(self):
        info_dict = self.download_info_dict()
        img_data = self.download_thumbnail(info_dict['thumbnail'])
        img = self.create_pil_image(img_data)
        photo2 = self.create_photo_image(img)
        self.display_image_and_title(info_dict, photo2)
        self.create_resolutions_label()
        self.create_resolutions_dropdown(info_dict)

    def progress_hook(self , data):
        if data['status'] == 'downloading':
            downloaded = data['downloaded_bytes']

            total = data['total_bytes']  if data.get('total_bytes' ,None) else data['total_bytes_estimate']
            percentage = downloaded / total * 100
            percentage = round(percentage, 2)

            self.progress_bar["value"] =  percentage
            self.progress_bar.update()

            self.style.configure('text.Horizontal.TProgressbar', text='{:g} %'.format(percentage))



    def setup_ydl_opts(self):
        # Recuperação das string dos campos de entrada
        format = self.ids[self.resolutions_fields.get()]
        download_folder = self.download_dir.get()

        return {
            'format': f"{format}+bestaudio",
            'merge_output_format': 'mkv' ,
            'progress_hooks': [self.progress_hook],
            'outtmpl': os.path.join(
                download_folder, '%(title)s-%(format)s.%(ext)s'
            ),
        }

    def download_video(self):
        # Verificar se os campos estão vazios
        youtube_url = self.video_url.get()
        download_folder = self.download_dir.get()

        if youtube_url and download_folder:
            # Barra de progresso
            self.progress_bar.grid(column=0, row=0, columnspan=2, padx=10, pady=20)

            ydl_opts = self.setup_ydl_opts()

            # Download do video
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])

            # Ocultar barra de mensagem e mostrar a mensagem de sucesso
            self.progress_bar.grid_remove()
            messagebox.showinfo(title='Sucesso', message='O vídeo foi baixado com sucesso.')
        else:
            # Mensagem de erro de campo vazio
            messagebox.showerror("Algum campo está vazio", "Preencha todos os campos!")




    def browse_folder(self):
        
        download_path = filedialog.askdirectory(initialdir = "D:\Downloads", title = "Selecione a pasta que deseja salvar o video")
        self.download_dir.set(download_path)

        if self.video_url.get()=="" :
            return

        download_thread = threading.Thread(target=self.set_image)
        download_thread.start()

    def download_video_thread(self):
        download_thread = threading.Thread(target=self.download_video)
        download_thread.start()


    def reset(self):
        self.video_url.set("")
        self.download_dir.set("")
        self.url_field.focus_set()

    def exit(self):
        self.destroy()

    def __init__(self):
        super().__init__()



        
        self.title("YouTube Video Downloader #Ferreira")

        
        self.geometry("580x380+700+250")

        
        self.resizable(0, 0)

        
        self.config(bg = "#4F4F4F")


        
        header_frame = tk.Frame(self, bg = "#4F4F4F")
        self.image_frame = tk.Frame(self, bg = "#4F4F4F")
        self.entry_frame = tk.Frame(self, bg = "#4F4F4F")
        button_frame = tk.Frame(self, bg = "#4F4F4F")
        progress_frame = tk.Frame(self, bg = "#4F4F4F")

        
        header_frame.pack()
        self.image_frame.pack()
        self.entry_frame.pack()
        button_frame.pack()
        progress_frame.pack()


        header_label = tk.Label(
            header_frame,
            text = "Download de videos Youtube",
            font = ("verdana", "12", "bold"),
            bg = "#4F4F4F",
            anchor = tk.SE
            )

        header_label.grid(row = 0, column = 1, padx = 10, pady = 10)

        
        url_label = tk.Label(
            self.entry_frame,
            text = "Video URL:",
            font = ("verdana", "10"),
            bg = "#4F4F4F",
            fg = "#000000",
            anchor = tk.SE
            )
        des_label = tk.Label(
            self.entry_frame,
            text = "Destino:",
            font = ("verdana", "10"),
            bg = "#4F4F4F",
            fg = "#000000",
            anchor = tk.SE
            )




       
        url_label.grid(row = 0, column = 0, padx = 5, pady = 5, sticky = tk.E)
        des_label.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = tk.E)


        self.video_url = tk.StringVar()
        self.download_dir = tk.StringVar()

        
        self.url_field = tk.Entry(
            self.entry_frame,
            textvariable = self.video_url,
            width = 35,
            font = ("verdana", "10"),
            bg = "#FFFFFF",
            fg = "#000000",
            relief = tk.GROOVE
            )
        des_field = tk.Entry(
            self.entry_frame,
            textvariable = self.download_dir,
            width = 26,
            font = ("verdana", "10"),
            bg = "#FFFFFF",
            fg = "#000000",
            relief = tk.GROOVE
            )


        self.url_field.grid(row = 0, column = 1, padx = 5, pady = 5, columnspan = 2)
        des_field.grid(row = 1, column = 1, padx = 5, pady = 5)

        resolution = tk.StringVar()



        self.resolutions_fields = ttk.Combobox(self.entry_frame, state= "readonly", width = 20, font = ("verdana", "8"))

        browse_button = tk.Button(
            self.entry_frame,
            text = "Browser",
            width = 7,
            font = ("verdana", "10"),
            bg = "#FF9200",
            fg = "#FFFFFF",
            activebackground = "#FFE0B7",
            activeforeground = "#000000",
            relief = tk.GROOVE,
            command = self.browse_folder,
            highlightthickness = 0
            )


        browse_button.grid(row = 1, column = 2, padx = 5, pady = 5)


        self.style = ttk.Style(self)
        self.style.layout('text.Horizontal.TProgressbar',
                    [('Horizontal.Progressbar.trough',
                    {'children': [('Horizontal.Progressbar.pbar',
                                    {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'}),
                    ('Horizontal.Progressbar.label', {'sticky': ''})])
        self.style.configure('text.Horizontal.TProgressbar', text='0 %')

        self.progress_bar = ttk.Progressbar(progress_frame,   orient = tk.HORIZONTAL, style='text.Horizontal.TProgressbar',
                length = 250, mode = 'determinate')

        self.progress_bar.grid(column=0, row=0, columnspan=2, padx=10, pady=20)

        self.progress_bar.grid_remove()


        download_button = tk.Button(
            button_frame,
            text="Download",
            width=12,
            font=("verdana", "10"),
            bg="#15EF5F",
            fg="#FFFFFF",
            activebackground="#97F9B8",
            activeforeground="#000000",
            relief=tk.GROOVE,
            command=self.download_video_thread,
            highlightthickness=0  
        )
        limpar_button = tk.Button(
            button_frame,
            text="Limpar",
            width=12,
            font=("verdana", "10"),
            bg="#23B1E6",
            fg="#FFFFFF",
            activebackground="#C3E6EF",
            activeforeground="#000000",
            relief=tk.GROOVE,
            command=self.reset,
            highlightthickness=0  
        )
        fechar_button = tk.Button(
            button_frame,
            text="Fechar",
            width=12,
            font=("verdana", "10"),
            bg="#F64247",
            fg="#FFFFFF",
            activebackground="#F7A2A5",
            activeforeground="#000000",
            relief=tk.GROOVE,
            command=self.exit,
            highlightthickness=0  
        )

        download_button.grid(row=10, column=0, padx=10, pady=10)
        limpar_button.grid(row=10, column=1, padx=10, pady=10)
        fechar_button.grid(row=10, column=2, padx=10, pady=10)


if __name__ == "__main__":
    app = YoutubeDownloadWindow()
    app.mainloop()
