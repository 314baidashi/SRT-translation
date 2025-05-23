import os
import srt
import tkinter as tk
from tkinter import ttk
import argostranslate.package
import argostranslate.translate
from srt import parse, compose
import tkinter.messagebox as messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

class SRTTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SRT字幕翻译工具-Sky繁星")
        self.root.geometry("600x400")

        # 拖放区域
        self.drop_frame = tk.Frame(root, bd=2, relief="groove")
        self.drop_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.drop_label = tk.Label(self.drop_frame, text="将SRT文件拖放到此处", font=('微软雅黑', 12))
        self.drop_label.pack(expand=True, fill="both")
        # 绑定拖放事件
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)

        # 语言选择框架
        self.lang_frame = tk.Frame(root)
        self.lang_frame.pack(pady=15, padx=20, fill="x")

        # 原语言下拉框
        self.src_lang_label = ttk.Label(self.lang_frame, text="原语言：")
        self.src_lang_label.grid(row=0, column=0, padx=5, sticky="w")
        self.src_lang = ttk.Combobox(self.lang_frame, values=["简体中文", "英语", "日语", "韩语", "俄语"], state="readonly")
        self.src_lang.grid(row=0, column=1, padx=5, sticky="ew")
        self.src_lang.current(1)  # 默认英语

        # 目标语言下拉框
        self.dest_lang_label = ttk.Label(self.lang_frame, text="目标语言：")
        self.dest_lang_label.grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.dest_lang = ttk.Combobox(self.lang_frame, values=["简体中文", "英语", "日语", "韩语", "俄语"], state="readonly")
        self.dest_lang.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        self.dest_lang.current(0)  # 默认简体中文

        self.lang_frame.grid_columnconfigure(1, weight=1)

        # 开始按钮
        self.start_btn = ttk.Button(root, text="开始翻译", command=self.translate_srt)
        self.start_btn.pack(pady=25, ipadx=20)

        # 进度条
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=10)

    def on_drag_enter(self, event):
        self.drop_label.config(text="释放文件以导入")
        return "break"

    def on_drag_leave(self, event):
        self.drop_label.config(text="将SRT文件拖放到此处")
        return "break"

    def on_drop(self, event):
        # 获取拖放文件列表
        file_path = os.path.normpath(event.data.strip('{}').replace('{', '').replace('}', ''))
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件路径不存在")
            return
        self.input_file = file_path
        self.drop_label.config(text=f"已选择文件：{os.path.basename(file_path)}")

    def translate_srt(self):
        if not hasattr(self, 'input_file'):
            messagebox.showerror("错误", "请先拖放SRT文件")
            return
        src_lang = self.src_lang.get()
        dest_lang = self.dest_lang.get()
        try:
            subs = self.parse_srt(self.input_file)
            self.progress_bar["maximum"] = len(subs)
            self.progress_bar["value"] = 0
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            lang_map = {'简体中文': 'zh', '英语': 'en', '日语': 'ja', '韩语': 'ko', '俄语': 'ru'}
            from_code = lang_map[src_lang]
            to_code = lang_map[dest_lang]
            package_to_install = next(
                (x for x in available_packages if x.from_code == from_code and x.to_code == to_code), None
            )
            if package_to_install:
                argostranslate.package.install_from_path(package_to_install.download())
            translated_subs = self.translate_subs(subs, from_code, to_code)
            self.write_srt(translated_subs, self.input_file)
            messagebox.showinfo("完成", "翻译已完成")
        except Exception as e:
            messagebox.showerror("错误", f"翻译失败：{str(e)}")

    def parse_srt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return list(parse(content))

    def translate_subs(self, subs, from_code, to_code):
        translated_subs = []
        for sub in subs:
            translated_text = argostranslate.translate.translate(sub.content, from_code, to_code)
            translated_sub = srt.Subtitle(
                sub.index,
                sub.start,
                sub.end,
                translated_text
            )
            translated_subs.append(translated_sub)
            self.progress_bar["value"] += 1
            self.root.update_idletasks()
        return translated_subs

    def write_srt(self, translated_subs, input_path):
        output_path = input_path.rsplit('.', 1)[0] + '_translated.srt'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(compose(translated_subs))

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = SRTTranslatorApp(root)
    root.mainloop()
