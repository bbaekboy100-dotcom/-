"""
세출예산 성질별 분류 프로그램 GUI
의정부시 버스정책과
"""
import sys, os, threading, io, contextlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# PyInstaller 실행 시 경로 처리
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from 세출_성질별_분류 import main as run_classification, URBAN_INFRA_NAMES


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("세출예산 성질별 분류 프로그램 (의정부시)")
        self.geometry("700x500")
        self.resizable(False, False)
        self.configure(bg="#F0F4F8")
        self._build()

    def _build(self):
        # 헤더
        hdr = tk.Frame(self, bg="#1F3864", height=64)
        hdr.pack(fill="x")
        tk.Label(hdr, text="세출예산 성질별 분류 프로그램",
                 font=("맑은 고딕", 15, "bold"),
                 fg="white", bg="#1F3864").pack(pady=18)

        # 입력 영역
        frm = tk.Frame(self, bg="#F0F4F8", padx=30, pady=20)
        frm.pack(fill="x")

        # 입력 파일
        tk.Label(frm, text="입력 파일 (세출예산 .xlsx)",
                 font=("맑은 고딕", 10, "bold"),
                 bg="#F0F4F8").grid(row=0, column=0, sticky="w")
        self.v_input = tk.StringVar()
        tk.Entry(frm, textvariable=self.v_input,
                 width=48, font=("맑은 고딕", 9)
                 ).grid(row=0, column=1, padx=8)
        tk.Button(frm, text="찾아보기", command=self._browse_in,
                  bg="#2E75B6", fg="white", font=("맑은 고딕", 9),
                  relief="flat", padx=10
                  ).grid(row=0, column=2)

        # 출력 파일
        tk.Label(frm, text="결과 파일 저장 위치",
                 font=("맑은 고딕", 10, "bold"),
                 bg="#F0F4F8").grid(row=1, column=0, sticky="w", pady=(12,0))
        self.v_output = tk.StringVar()
        tk.Entry(frm, textvariable=self.v_output,
                 width=48, font=("맑은 고딕", 9)
                 ).grid(row=1, column=1, padx=8, pady=(12,0))
        tk.Button(frm, text="찾아보기", command=self._browse_out,
                  bg="#2E75B6", fg="white", font=("맑은 고딕", 9),
                  relief="flat", padx=10
                  ).grid(row=1, column=2, pady=(12,0))

        # 연도
        tk.Label(frm, text="회계연도",
                 font=("맑은 고딕", 10, "bold"),
                 bg="#F0F4F8").grid(row=2, column=0, sticky="w", pady=(12,0))
        self.v_year = tk.StringVar(value="2026")
        tk.Entry(frm, textvariable=self.v_year,
                 width=10, font=("맑은 고딕", 9)
                 ).grid(row=2, column=1, sticky="w", padx=8, pady=(12,0))

        # 실행 버튼
        tk.Button(self, text="▶   분류 실행",
                  command=self._run,
                  bg="#1F3864", fg="white",
                  font=("맑은 고딕", 12, "bold"),
                  relief="flat", padx=30, pady=10
                  ).pack(pady=12)

        # 진행바
        self.progress = ttk.Progressbar(self, mode="indeterminate", length=600)
        self.progress.pack()

        # 로그창
        lf = tk.Frame(self, bg="#F0F4F8", padx=30)
        lf.pack(fill="both", expand=True)
        tk.Label(lf, text="실행 로그",
                 font=("맑은 고딕", 9, "bold"),
                 bg="#F0F4F8", anchor="w").pack(fill="x")
        self.log = tk.Text(lf, height=9,
                           font=("Consolas", 9),
                           bg="#1E1E1E", fg="#D4D4D4",
                           relief="flat", state="disabled")
        self.log.pack(fill="both", expand=True, pady=(4,0))

        # 하단 안내
        tk.Label(self,
                 text=f"도시기본기능유지 기준 목록 {len(URBAN_INFRA_NAMES)}개 등록됨  |  2026년 통계목 체계 기준",
                 font=("맑은 고딕", 8), fg="#888", bg="#F0F4F8"
                 ).pack(pady=6)

    def _browse_in(self):
        p = filedialog.askopenfilename(
            title="세출예산 파일 선택",
            filetypes=[("Excel", "*.xlsx *.xls"), ("모든 파일", "*.*")])
        if p:
            self.v_input.set(p)
            if not self.v_output.get():
                yr = self.v_year.get() or "result"
                self.v_output.set(
                    os.path.join(os.path.dirname(p),
                                 f"세출_성질별_분류_{yr}.xlsx"))

    def _browse_out(self):
        yr = self.v_year.get() or "result"
        p = filedialog.asksaveasfilename(
            title="결과 파일 저장",
            defaultextension=".xlsx",
            initialfile=f"세출_성질별_분류_{yr}.xlsx",
            filetypes=[("Excel", "*.xlsx")])
        if p:
            self.v_output.set(p)

    def _log(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _run(self):
        inp = self.v_input.get().strip()
        out = self.v_output.get().strip()
        yr  = self.v_year.get().strip()

        if not inp or not os.path.exists(inp):
            messagebox.showerror("오류", "입력 파일을 선택해 주세요.")
            return
        if not out:
            messagebox.showerror("오류", "출력 파일 경로를 지정해 주세요.")
            return
        try:
            year = int(yr)
        except ValueError:
            messagebox.showerror("오류", "회계연도는 숫자로 입력해 주세요.")
            return

        self.progress.start(10)
        self._log(f"[{year}년] 분류 시작: {os.path.basename(inp)}")

        def worker():
            try:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    run_classification(
                        input_file=inp,
                        output_file=out,
                        year=year)
                for line in buf.getvalue().splitlines():
                    self.after(0, self._log, line)
                self.after(0, self._done, out)
            except Exception as e:
                self.after(0, self._error, str(e))

        threading.Thread(target=worker, daemon=True).start()

    def _done(self, out):
        self.progress.stop()
        self._log(f"\n✔ 완료: {out}")
        messagebox.showinfo("완료",
            f"분류가 완료됐습니다.\n\n{out}")

    def _error(self, msg):
        self.progress.stop()
        self._log(f"\n✘ 오류: {msg}")
        messagebox.showerror("오류", msg)


if __name__ == "__main__":
    App().mainloop()
