import os
import threading
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox

from ApiModelProperty import convert_api_to_comment as property_conversion
from ApiOperation import convert_java_file as operation_conversion
from ApiModel import convert_api_model_to_javadoc as model_conversion


# ================================
# GUI 应用
# ================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("注解转 JavaDoc 工具")
        self.root.geometry("680x500")

        self.default_path = os.getcwd()
        self.create_widgets()

    def create_widgets(self):
        # 路径输入
        frame = tk.Frame(self.root)
        frame.pack(pady=10, fill="x")

        tk.Label(frame, text="文件路径:").pack(side="left")

        self.path_var = tk.StringVar(value=self.default_path)
        tk.Entry(frame, textvariable=self.path_var, width=55).pack(side="left", padx=5)

        tk.Button(frame, text="选择文件夹", command=self.choose_path).pack(side="left")

        # 多选框
        check_frame = tk.Frame(self.root)
        check_frame.pack(pady=5)

        self.var_api_model_property = tk.BooleanVar(value=True)
        self.var_api_operation = tk.BooleanVar(value=True)
        self.var_api_model = tk.BooleanVar(value=True)

        tk.Checkbutton(check_frame, text="转换 ApiModelProperty", variable=self.var_api_model_property).pack(
            side="left", padx=10)

        tk.Checkbutton(check_frame, text="转换 ApiOperation(只生成注释，没有@param等参数)",
                       variable=self.var_api_operation).pack(side="left", padx=10)
        tk.Checkbutton(check_frame, text="转换 ApiModel", variable=self.var_api_model).pack(side="left", padx=10)

        # 执行按钮
        tk.Button(self.root, text="开始执行", width=20, command=self.start_process).pack(pady=10)

        # 进度条
        self.progress = ttk.Progressbar(self.root, length=600, mode="determinate")
        self.progress.pack()

        # 日志输出
        tk.Label(self.root, text="执行详情:").pack()
        self.log_box = scrolledtext.ScrolledText(self.root, width=80, height=15, state="disabled")
        self.log_box.pack(pady=5)

    def choose_path(self):
        folder = filedialog.askdirectory(initialdir=self.default_path)
        if folder:
            self.path_var.set(folder)

    def log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

    def start_process(self):
        path = self.path_var.get().strip()

        if not os.path.exists(path):
            messagebox.showerror("错误", "路径不存在！")
            return

        self.log_box.config(state="normal")
        self.log_box.delete(1.0, tk.END)
        self.log_box.config(state="disabled")

        t = threading.Thread(target=self.process_task, args=(path,))
        t.daemon = True
        t.start()

    def process_task(self, path):
        java_files = []
        for root, _, files in os.walk(path):
            for f in files:
                if f.endswith(".java"):
                    java_files.append(os.path.join(root, f))

        total = len(java_files)
        self.progress["maximum"] = total

        self.log(f"开始处理，共 {total} 个 Java 文件")

        for i, fp in enumerate(java_files, start=1):
            self.progress["value"] = i
            self.log(f"\n处理文件：{fp}")

            with open(fp, "r", encoding="utf-8") as f:
                content = f.read()

            modified = False

            if self.var_api_model_property.get():
                content, added1 = property_conversion(content)
                if added1:
                    modified = True
                    self.log(f"  ApiModelProperty → JavaDoc 生成 {added1} 条")

            if self.var_api_operation.get():
                content, added2 = operation_conversion(content)
                if added2:
                    modified = True
                    self.log(f"  ApiOperation → JavaDoc 生成 {added2} 条")

            if self.var_api_model.get():
                content, added1 = model_conversion(content)
                if added1:
                    modified = True
                    self.log(f"  ApiModel → JavaDoc 生成 {added1} 条")

            if modified:
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(content)

        self.log("\n🎉 处理完成了！")


# ================================
# 程序主入口
# ================================
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
