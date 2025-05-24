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
        self.src_lang = ttk.Combobox(self.lang_frame, values=["英语", "日语", "韩语"], state="readonly")
        self.src_lang.grid(row=0, column=1, padx=5, sticky="ew")
        self.src_lang.current(0)  # 默认英语
        self.src_lang.bind('<<ComboboxSelected>>', self.update_dest_lang)

        # 目标语言下拉框
        self.dest_lang_label = ttk.Label(self.lang_frame, text="目标语言：")
        self.dest_lang_label.grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.dest_lang = ttk.Combobox(self.lang_frame, values=["简体中文"], state="readonly")
        self.dest_lang.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        self.update_dest_lang()

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
            lang_map = {'简体中文': 'zh', '英语': 'en', '日语': 'ja', '韩语': 'ko'}
            from_code = lang_map[src_lang]
            to_code = lang_map[dest_lang]
            if src_lang in ['日语', '韩语'] and dest_lang == '简体中文':
                # 先从源语言翻译到英语
                en_package_to_install = next(
                    (x for x in available_packages if x.from_code == lang_map[src_lang] and x.to_code == 'en'), None
                )
                if en_package_to_install:
                    argostranslate.package.install_from_path(en_package_to_install.download())
                else:
                    messagebox.showerror("错误", f"未找到从 {src_lang} 到 英语 的翻译包。")
                    return
                # 执行第一次翻译到英语
                try:
                    en_translated_subs = self.translate_subs(subs, lang_map[src_lang], 'en')
                except AttributeError as ae:
                    logging.error(f"翻译到英语时出现 AttributeError: {ae}")
                    raise
                
                # 再从英语翻译到中文
                zh_package_to_install = next(
                    (x for x in available_packages if x.from_code == 'en' and x.to_code == lang_map[dest_lang]), None
                )
                if zh_package_to_install:
                    argostranslate.package.install_from_path(zh_package_to_install.download())
                else:
                    messagebox.showerror("错误", f"未找到从 英语 到 {dest_lang} 的翻译包。")
                    return
                
                try:
                    translated_subs = self.translate_subs(en_translated_subs, 'en', lang_map[dest_lang])
                except AttributeError as ae:
                    logging.error(f"翻译到 {dest_lang} 时出现 AttributeError: {ae}")
                    raise
            else:
                package_to_install = next(
                    (x for x in available_packages if x.from_code == from_code and x.to_code == to_code), None
                )
                if package_to_install:
                    argostranslate.package.install_from_path(package_to_install.download())
                else:
                    messagebox.showerror("错误", f"未找到从 {src_lang} 到 {dest_lang} 的翻译包。")
                    return
                
                try:
                    translated_subs = self.translate_subs(subs, from_code, to_code)
                except AttributeError as ae:
                    logging.error(f"翻译时出现 AttributeError: {ae}")
                    raise
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
            # 记录原始时间轴信息
            original_start = sub.start
            original_end = sub.end
            translated_text = argostranslate.translate.translate(sub.content, from_code, to_code)
            # 确保序号正确
            new_index = sub.index if len(translated_subs) == 0 else len(translated_subs) + 1
            translated_sub = srt.Subtitle(
                new_index,
                original_start,
                original_end,
                translated_text
            )
            translated_subs.append(translated_sub)
            self.progress_bar["value"] += 1
            self.root.update_idletasks()
        return translated_subs

    def write_srt(self, translated_subs, input_path):
        src_lang = self.src_lang.get()
        dest_lang = self.dest_lang.get()
        lang_map = {'简体中文': 'zh', '英语': 'en', '日语': 'ja', '韩语': 'ko'}
        from_code = lang_map[src_lang]
        to_code = lang_map[dest_lang]
        file_name, file_ext = os.path.splitext(input_path)
        # 从名称尾部查找原语言映射词并删除
        if file_name.endswith(from_code):
            file_name = file_name[:-(len(from_code))]
        # 加上目标语言映射词
        output_path = file_name + to_code + file_ext
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(compose(translated_subs))

    def update_dest_lang(self, event=None):
        src_lang = self.src_lang.get()
        lang_map = {
            "英语": ["简体中文"],
            "日语": ["简体中文", "英语"],
            "韩语": ["简体中文", "英语"]
        }
        self.dest_lang['values'] = lang_map.get(src_lang, ["简体中文"])
        self.dest_lang.current(0)

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = SRTTranslatorApp(root)
    root.mainloop()
