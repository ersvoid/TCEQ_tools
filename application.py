import tkinter as tk
import tkinter.scrolledtext
import base64
import datetime
import os
from data_pull import data_pull, schedule_monitoring, compliance_pull, summary_pull, violation_pull, \
    summary_pull_by_schedule, time_in_range, sampling_export, find_samples, testing
from connection import auto_connect
from math import floor
import ctypes
from tkintertable import TableCanvas, TableModel
from sample_sites_excel_output import sample_sites_excel_write
from sample_sites_word_doc import export_to_word
import random
import csv
# from table_app import TablesApp

# SCREEN SIZE

user32 = ctypes.windll.user32
screensize = (str(user32.GetSystemMetrics(0)) + "x" + str(user32.GetSystemMetrics(1)))

# COLORS
antique = "AntiqueWhite3"
olive = "DarkOliveGreen3"
color_text = antique
color_main = olive

icon = """
AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAABILAAASCwAAAAAA
AAAAAAD///////////7+/f//////6evC/8zQcP/Fyl//0NR+//Lz2v///////v79////////////
//////////////////////7+/f//////3eCh/8jMZv/Gy2L/rbQe/661IP+0ui//6OrB///////+
/v3///////////////////////7+/f//////7/DU/8vPbf/p68T/trs0/7O5LP+1uzH/sLYj/7e9
Of/6+vH//////////v/////////////////+/vz//////9jclv/l57b/xcti/6yzG/+0ui//s7ks
/7W6MP+utR//5ui5///////+/vz//////////////////v78///////Z3Jb/5ui6/7zCRv+xtyf/
s7kt/7O5LP+0ui//rrQe/+LlsP///////v78//7///////////////7+/P//////5Oe2/97hpP/K
zm3/rrQe/7S6Lv+zuSz/s7ks/7K4K//x8tn///////39+v////7///////////////7///////r7
8//FymD/z9N8/7K4Kf+zuS3/tLou/6+2Iv/DyFr//////////v/////////+////////////////
//7+/P//////19uS/6yzGv+1uzL/s7kr/7S6L/+utB7/5Oa1//Dy2P/Y3JX/4OOs//z8+P//////
//////////////7///////j57f+3vTn/srgo/7S6L/+vtiL/wsdW/+PmtP/Q03z/vcJI/6mwEP/K
zm3//////////v////////////39+v//////1tqQ/620HP+1uzP/rrQe/+Djqf/Y25L/1tmN/7C2
JP+1uzL/rrUg/+7w0f/////////////////+/v3//v79//r68f+6v0D/rrQe/8DFUf/8/Pf/2dyW
/8/Te/+utR7/tbsx/7C3Jv/u8NL///////7+/f//////4+a0/8LHVf/d4KL/4eOs/6ivDv/m6Lr/
/////97hpf/IzWf/trw0/7C2JP++xE3//v/+////////////+/v0/9HVgf+5vz7/srgr//T14P/Y
25T//P35///////4+ez/t704/7O5Lv+ttB7/3eCj///////+/vz////+///////c357/srkr/8PI
Wf///////v79//7+/f/+/vz//////9jclf+qsRT/vMJH//v89f/////////+//7+/f//////7vDR
/661H//l6Ln///////3++//////////+///////7+/T/t7w3/97hpv///////v78////////////
//////7+/f/e4aP/+/v0//////////////////////////7//////+vsx//4+e7/////////////
////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAA=="""

icondata = base64.b64decode(icon)
# The temp file is icon.ico
tempFile = "icon.ico"
iconfile = open(tempFile, "wb")
# Extract the icon
iconfile.write(icondata)
iconfile.close()


def login():
    global login_screen
    login_screen = tk.Toplevel(root)
    login_screen.title("Login")
    login_screen.geometry("300x250")
    tk.Label(login_screen, text="Please enter details below to login").pack()
    tk.Label(login_screen, text="").pack()

    global username_verify
    global password_verify

    username_verify = tk.StringVar()
    password_verify = tk.StringVar()

    global username_login_entry
    global password_login_entry

    tk.Label(login_screen, text="Username * ").pack()
    username_login_entry = tk.Entry(login_screen, textvariable=username_verify)
    username_login_entry.pack()
    tk.Label(login_screen, text="").pack()
    tk.Label(login_screen, text="Password * ").pack()
    password_login_entry = tk.Entry(login_screen, textvariable=password_verify, show='*')
    password_login_entry.pack()
    tk.Label(login_screen, text="").pack()
    tk.Button(login_screen, text="Login", width=10, height=1, command=login_verify).pack()


def login_verify():
    username1 = username_verify.get()
    password1 = password_verify.get()
    username_login_entry.delete(0, tk.END)
    password_login_entry.delete(0, tk.END)
    live_connection = auto_connect(username1, password1)
    if live_connection:
        main.username.set(username1)
        main.password.set(password1)
        login_success()
    else:
        user_not_found()


def login_success():
    global login_success_screen
    login_success_screen = tk.Toplevel(login_screen)
    login_success_screen.title("Success")
    login_success_screen.geometry("150x100")
    tk.Label(login_success_screen, text="Login Success").pack()
    tk.Button(login_success_screen, text="OK", command=delete_login_success).pack()


def user_not_found():
    global user_not_found_screen
    user_not_found_screen = tk.Toplevel(login_screen)
    user_not_found_screen.title("Success")
    user_not_found_screen.geometry("150x100")
    tk.Label(user_not_found_screen, text="User Not Found").pack()
    tk.Button(user_not_found_screen, text="OK", command=delete_user_not_found_screen).pack()


def no_results():
    global no_results_screen
    no_results_screen = tk.Toplevel(root)
    no_results_screen.title("Results")
    no_results_screen.geometry("150x100")
    tk.Label(no_results_screen, text="No Results Found").pack()
    tk.Button(no_results_screen, text="OK", command=no_results_screen.destroy).pack()


def delete_login_success():
    login_success_screen.destroy()
    login_screen.destroy()


def delete_user_not_found_screen():
    user_not_found_screen.destroy()


def export_sample_sites():
    global export_sample_sites_screen
    global pws_entry
    export_sample_sites_screen = tk.Toplevel(root)
    export_sample_sites_screen.title("Export Sample Sites")
    export_sample_sites_screen.geometry("400x100")

    entry_frame = tk.LabelFrame(export_sample_sites_screen, text="Enter PWS ID:")
    entry_frame.pack()

    pws_entry = tk.Entry(entry_frame)
    pws_entry.pack(padx=10, pady=10, side="left")

    word_export = tk.Button(entry_frame, text="Export to Word", command=word_push)
    word_export.pack(padx=10, pady=10, side="left")

    excel_export = tk.Button(entry_frame, text="Export to Excel", command=excel_push)
    excel_export.pack(padx=10, pady=10, side="left")

    tk.Button(export_sample_sites_screen, text="CLOSE", command=export_sample_sites_screen.destroy).pack()


def excel_push():
    pws_id = pws_entry.get()
    sampling_info = sampling_export(main.username.get(), main.password.get(), pws_id)
    sample_sites_excel_write(sampling_info)


def word_push():
    pws_id = pws_entry.get()
    sampling_info = sampling_export(main.username.get(), main.password.get(), pws_id)
    path = r"sample_sites_" + pws_id + ".docx"
    export_to_word(sampling_info[1], path)


class Page(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()


class Home(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        tk.Label(self).pack()
        label = tk.Label(self, text="LEAD AND COPPER PROGRAM", font=("Times", 22))
        label.pack(side="top")
        tk.Label(self).pack()
        self.date_frame = tk.LabelFrame(self, text="Today's Date", font=("Times", 18))
        self.date_frame.pack()
        today = datetime.date.today()
        date_string = str(today.month) + " - " + str(today.day) + " - " + str(today.year)
        self.date_label = tk.Label(self.date_frame, text=date_string, font=("Times", 16)).pack(padx=10, pady=10)
        tk.Label(self).pack()
        self.period_frame = tk.LabelFrame(self, text="Current Monitoring Period", font=("Times", 18))
        self.period_frame.pack()
        period_string = ""
        if time_in_range(datetime.date(today.year, 1, 1), datetime.date(today.year, 5, 31), today):
            period_string = period_string + "6M1 Routine Monitoring"
        elif time_in_range(datetime.date(today.year, 6, 1), datetime.date(today.year, 6, 30), today):
            period_string = period_string + "6M1 Routine Monitoring \n YR/3Y/9Y Reduced Monitoring"
        elif time_in_range(datetime.date(today.year, 7, 1), datetime.date(today.year, 9, 30), today):
            period_string = period_string + "YR/3Y/9Y Reduced Monitoring \n 6M2 Routine Monitoring"
        elif time_in_range(datetime.date(today.year, 10, 1), datetime.date(today.year, 12, 30), today):
            period_string = period_string + "6M2 Routine Monitoring"
        self.period_label = tk.Label(self.period_frame, text=period_string, font=("Times", 16)).pack(padx=10, pady=10)

        tk.Label(self, text="Created by Eric Stinson 2019").pack(side="bottom")


class Display(Page):

    def __init__(self, *args, **kwargs):

        Page.__init__(self, *args, **kwargs)

        self.margin10 = "10"
        self.margin20 = "20"
        self.margin30 = "30"

        self.pws_frame = tk.LabelFrame(self, text="Enter PWS ID:")
        self.pws_frame.pack()

        self.pws_entry_text = tk.StringVar()
        self.pws_entry = tk.Entry(self.pws_frame, textvariable=self.pws_entry_text)
        self.pws_entry.pack(padx=10, pady=10, side="left")

        self.pws_enter = tk.Button(self.pws_frame, text="DISPLAY", command=self.return_info)
        self.pws_enter.pack(padx=10, pady=10, side="left")

        tk.Label(self).pack()

        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill='both', expand=1)

        self.frame = tk.Frame(self.canvas)

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame, anchor='nw', tags="self.frame")

        self.pws_info = tkinter.scrolledtext.ScrolledText(self.frame, font="Consolas 12")
        self.pws_info.pack(fill="both", expand=1)

        tk.Label(self.frame).pack()
        tk.Label(self.frame).pack(side="left", fill="x", expand=1)
        tk.Label(self.frame).pack(side="left", fill="x", expand=1)
        tk.Label(self.frame).pack(side="left", fill="x", expand=1)
        tk.Label(self, text="Created by Eric Stinson 2019").pack()

        # self.indicators = tkinter.scrolledtext.Text(self.frame, bg=color_text, font="Consolas 12")
        # self.indicators.pack()
        #
        # self.milestones = tkinter.scrolledtext.Text(self.frame, bg=color_text, font="Consolas 12")
        # self.milestones.pack()
        #
        # self.closed = tkinter.scrolledtext.Text(self.frame, bg=color_text, font="Consolas 12")
        # self.closed.pack()
        #
        # self.open = tkinter.scrolledtext.Text(self.frame, bg=color_text, font="Consolas 12")
        # self.open.pack()
        #
        # self.compliance = tkinter.scrolledtext.Text(self.frame, bg=color_text, font="Consolas 12")
        # self.compliance.pack()
        #
        # self.schedules = tkinter.scrolledtext.Text(self.frame, bg=color_text, font="Consolas 12")
        # self.schedules.pack()
        #
        # self.summaries = tkinter.scrolledtext.Text(self.frame, bg=color_text, font="Consolas 12")
        # self.summaries.pack()
        #
        # self.wqps = tkinter.scrolledtext.Text(self.frame, bg=color_text, font="Consolas 12")
        # self.wqps.pack()
        #
        # self.sample_sites = tkinter.scrolledtext.Text(self.frame, bg=color_text, font="Consolas 12")
        # self.sample_sites.pack()

        # self.vsb = tk.Scrollbar(self.canvas, orient="vertical", command=self.canvas.yview)
        # self.vsb.pack(side="right", fill='y')
        #
        # self.canvas.configure(yscrollcommand=self.vsb.set)

        # self.frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind('<Configure>', self.frame_width)
        # self.master.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(floor(-1*(event.delta/120)), "units")

    def frame_width(self, event):
        canvas_width = event.width
        canvas_height = event.height
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width, height=canvas_height)

    def on_frame_configure(self, event):
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def return_info(self, c=None):
        if c is None:
            pws_id = self.pws_entry.get()
            pws_id = pws_id.strip().replace(" ", "")
            information = data_pull(main.username.get(), main.password.get(), pws_id)
        else:
            pws_id = self.pws_entry.get()
            pws_id = pws_id.strip().replace(" ", "")
            information = data_pull("username", "password", pws_id)

        self.pws_info.config(state="normal")
        self.pws_info.delete(1.0, tk.END)

        inv_info = information[0]
        self.return_inventory(inv_info)
        if inv_info[5] == "NC":
            return

        scheds = information[6]
        self.return_schedules(scheds)

        summaries = information[7]
        self.return_summaries(summaries)

        plan = information[10]
        self.return_plan(plan)

        sites = information[9]
        self.return_sites(sites)

        closed = information[3]
        open_vios = information[4]
        self.return_violations([closed, open_vios])

        compliance = information[5]
        self.returns_compliance(compliance)

        indicators = information[1]
        self.return_indicators(indicators)

        milestones = information[2]
        self.return_milestones(milestones)

        wqps = information[8]
        self.return_wqps(wqps)

        self.pws_info.config(state="disabled")

        # self.indicators.delete(1.0, tk.END)
        # self.milestones.delete(1.0, tk.END)
        # self.closed.delete(1.0, tk.END)
        # self.open.delete(1.0, tk.END)
        # self.compliance.delete(1.0, tk.END)
        # self.schedules.delete(1.0, tk.END)
        # self.summaries.delete(1.0, tk.END)
        # self.wqps.delete(1.0, tk.END)
        # self.sample_sites.delete(1.0, tk.END)
        # for group in information:
        #     try:
        #         for item in group:
        #             self.pws_info.insert(tk.END, item)
        #             self.pws_info.insert(tk.END, "\n")
        #     except:
        #         self.pws_info.insert(tk.END, group)
        #         self.pws_info.insert(tk.END, "\n")
        # for group in information[1]:
        #     self.indicators.insert(tk.END, group)
        #     self.indicators.insert(tk.END, "\n")
        # for group in information[2]:
        #     self.milestones.insert(tk.END, group)
        #     self.milestones.insert(tk.END, "\n")
        # for group in information[3]:
        #     self.closed.insert(tk.END, group)
        #     self.closed.insert(tk.END, "\n")
        # for group in information[4]:
        #     self.open.insert(tk.END, group)
        #     self.open.insert(tk.END, "\n")
        # for group in information[5]:
        #     self.compliance.insert(tk.END, group)
        #     self.compliance.insert(tk.END, "\n")
        # for group in information[6]:
        #     self.schedules.insert(tk.END, group)
        #     self.schedules.insert(tk.END, "\n")
        # for group in information[7]:
        #     self.summaries.insert(tk.END, group)
        #     self.summaries.insert(tk.END, "\n")
        # for group in information[8]:
        #     self.wqps.insert(tk.END, group)
        #     self.wqps.insert(tk.END, "\n")
        # for group in information[9]:
        #     self.sample_sites.insert(tk.END, group)
        #     self.sample_sites.insert(tk.END, "\n")

    def return_inventory(self, container):

        number0 = container[0]
        number0 = "{} {}".format(number0[:2], number0[2:])
        name = container[1]
        activity = container[2]
        source = container[3]
        pop = container[4]
        pws_type = container[5]
        pbcu_points = container[9]

        self.pws_info.tag_config("title", font="Consolas 18 bold", justify="center", underline=1)
        self.pws_info.tag_config("h", font="Consolas 14 bold", lmargin1="10")
        self.pws_info.tag_config("i", font="Consolas 12", lmargin1="20")

        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "{} - {}".format(name, container[0]), "title")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "INVENTORY INFORMATION", "h")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "PWS ID: {}".format(number0), "i")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "PWS NAME: {}".format(name), "i")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "ACTIVITY: {}".format(activity), "i")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "SOURCE: {}".format(source), "i")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "POPULATION: {}".format(pop), "i")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "PWS TYPE: {}".format(pws_type), "i")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "PBCU Points: {}".format(pbcu_points), "i")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")

    def return_schedules(self, container):
        self.pws_info.tag_config("h", font="Consolas 14 bold", lmargin1="10")
        self.pws_info.tag_config("i", font="Consolas 12", lmargin1="20", lmargin2="20", rmargin="20")
        self.pws_info.tag_config("s", font="Consolas 12 bold", lmargin1="15")

        self.pws_info.insert(tk.END, "LCR TAP MONITORING SCHEDULES", "h")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")

        if container:
            self.pws_info.insert(tk.END, "CURRENT SCHEDULE", "s")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "SCHEDULE: {}".format(container[0][0]), "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "SAMPLES: {} {}".format(container[0][4], container[0][5]), "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "COMMENT: {}".format(container[0][1]), "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "HISTORIC SCHEDULES", "s")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "\n")
            for group in container[1]:
                self.pws_info.insert(tk.END, "{} {} {}".format(group[0], group[4], group[5]), "i")
                self.pws_info.insert(tk.END, "\n")
                self.pws_info.insert(tk.END, "{}".format(group[1]), "i")
                self.pws_info.insert(tk.END, "\n")
                self.pws_info.insert(tk.END, "\n")

    def return_summaries(self, container):
        self.pws_info.tag_config("h", font="Consolas 14 bold", lmargin1="10")
        self.pws_info.tag_config("i", font="Consolas 12", lmargin1="20")
        self.pws_info.tag_config("j", font="Consolas 12", lmargin1="25")
        self.pws_info.insert(tk.END, "LCR TAP MONITORING SUMMARIES", "h")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")
        if container:
            for period in container:
                self.pws_info.insert(tk.END, "{} - {}".format(period[1][0][1].date(), period[1][0][2].date()), "i")
                self.pws_info.insert(tk.END, "\n")
                self.pws_info.insert(tk.END, "{} - {} samples {} {} {}""".format(period[1][0][4], period[1][0][8],
                                                                                 period[1][0][9], period[1][0][10],
                                                                                 period[1][0][11]), "j")
                self.pws_info.insert(tk.END, "\n")
                self.pws_info.insert(tk.END, "{} - {} samples {} {} {}""".format(period[1][1][4], period[1][1][8],
                                                                                 period[1][1][9], period[1][1][10],
                                                                                 period[1][1][11]), "j")
                self.pws_info.insert(tk.END, "\n")
                self.pws_info.insert(tk.END, "\n")
        if not container:
            self.pws_info.insert(tk.END, "NO SUMMARIES FOUND", "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "\n")

    def return_plan(self, container):
        self.pws_info.tag_config("h", font="Consolas 14 bold", lmargin1="10")
        self.pws_info.tag_config("i", font="Consolas 12", lmargin1="20")
        self.pws_info.insert(tk.END, "LCR TAP MONITORING SAMPLE PLAN", "h")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")
        if container:
            self.pws_info.insert(tk.END, "Approval: {} Begin: {}".format(container[0][0], container[0][1]), "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "\n")

        else:
            self.pws_info.insert(tk.END, "NO PLAN FOUND", "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "\n")

    def return_sites(self, container):
        self.pws_info.tag_config("h", font="Consolas 14 bold", lmargin1="10")
        self.pws_info.tag_config("i", font="Consolas 12", lmargin1="20")
        self.pws_info.insert(tk.END, "LCR TAP MONITORING SAMPLE SITES", "h")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")
        a = 0
        i = 0
        if container:
            for group in container:
                if group[6] == "A":
                    a += 1
                else:
                    i += 1
                self.pws_info.insert(tk.END,  "{}{} - {} - {} - {} - {} - {}".format(group[0], group[1], group[2],
                                                                                     group[3], group[4], group[5],
                                                                                     group[6]), "i")
                self.pws_info.insert(tk.END, "\n")
        else:
            self.pws_info.insert(tk.END, "NO SITES FOUND", "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "Active: {} Inactive: {}".format(a, i), "i")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")

    def return_closed(self, container):
        self.pws_info.tag_config("s", font="Consolas 12 bold", lmargin1="15")
        self.pws_info.tag_config("i", font="Consolas 12", lmargin1="20")
        self.pws_info.tag_config("j", font="Consolas 12", lmargin1="25")
        self.pws_info.insert(tk.END, "CLOSED VIOLATIONS", "s")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")

        if container:
            for group in container:
                self.pws_info.insert(tk.END, "{} {} {} - {}".format(container[group][0][0], container[group][0][1],
                                                                    container[group][0][2],
                                                                    container[group][0][3]), "i")
                self.pws_info.insert(tk.END, "\n")
                actions = container[group][1]
                for action in actions:
                    self.pws_info.insert(tk.END, "- {} {} {} {} {}".format(action[1], action[2], action[3], action[4],
                                                                           action[5]), "j")
                    self.pws_info.insert(tk.END, "\n")
                self.pws_info.insert(tk.END, "\n")

        else:
            self.pws_info.insert(tk.END, "NONE FOUND", "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "\n")

    def return_open(self, container):
        self.pws_info.tag_config("s", font="Consolas 12 bold", lmargin1="15")
        self.pws_info.tag_config("i", font="Consolas 12", lmargin1="20")
        self.pws_info.tag_config("j", font="Consolas 12", lmargin1="25")
        self.pws_info.insert(tk.END, "OPEN VIOLATIONS", "s")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")

        if container:
            for group in container:
                self.pws_info.insert(tk.END, "{} {} {} - {}".format(container[group][0][0], container[group][0][1],
                                                                    container[group][0][2],
                                                                    container[group][0][3]), "i")
                self.pws_info.insert(tk.END, "\n")
                actions = container[group][1]
                for action in actions:
                    self.pws_info.insert(tk.END, "- {} {} {} {} {}".format(action[1], action[2], action[3], action[4],
                                                                           action[5]), "j")
                    self.pws_info.insert(tk.END, "\n")
                self.pws_info.insert(tk.END, "\n")

        else:
            self.pws_info.insert(tk.END, "NONE FOUND", "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "\n")

    def return_violations(self, container):
        self.pws_info.tag_config("h", font="Consolas 14 bold", lmargin1="10")
        self.pws_info.insert(tk.END, "VIOLATIONS", "h")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")
        self.return_open(container[1])
        self.return_closed(container[0])

    def returns_compliance(self, container):
        self.pws_info.tag_config("h", font="Consolas 14 bold", lmargin1="10")
        self.pws_info.tag_config("i", font="Consolas 12", lmargin1="20")

        self.pws_info.insert(tk.END, "COMPLIANCE SCHEDULES", "h")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")
        if container:
            for group in container:
                self.pws_info.insert(tk.END, "{} Effective: {} Due: {} Closed: {}".format(group[3], group[1], group[4],
                                                                                          group[2]), "i")
                self.pws_info.insert(tk.END, "\n")
        else:
            self.pws_info.insert(tk.END, "NONE FOUND", "i")
            self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")

    def return_indicators(self, container):
        self.pws_info.tag_config("h", font="Consolas 14 bold", lmargin1="10")
        self.pws_info.tag_config("i", font="Consolas 12", lmargin1="20")

        self.pws_info.insert(tk.END, "INDICATORS", "h")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")

        if container:
            indicator = container[-1]
            if indicator[3] is None:
                indicator[3] = "OPEN"
            self.pws_info.insert(tk.END, "{} - {}".format(indicator[0], indicator[1]), "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "Begin: {} - Close: {}".format(indicator[2], indicator[3]), "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "\n")

        else:
            self.pws_info.insert(tk.END, "NONE FOUND", "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "\n")

    def return_milestones(self, container):
        self.pws_info.tag_config("h", font="Consolas 14 bold", lmargin1="10")
        self.pws_info.tag_config("i", font="Consolas 12", lmargin1="20")

        self.pws_info.insert(tk.END, "MILESTONES", "h")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")

        if container:
            for item in container:
                self.pws_info.insert(tk.END, "{} {} {}".format(item[0], item[1], item[2]), "i")
                self.pws_info.insert(tk.END, "\n")
                self.pws_info.insert(tk.END, "\n")
        else:
            self.pws_info.insert(tk.END, "NONE FOUND", "i")
            self.pws_info.insert(tk.END, "\n")
            self.pws_info.insert(tk.END, "\n")

    def return_wqps(self, container):
        self.pws_info.tag_config("h", font="Consolas 14 bold", lmargin1="10")
        self.pws_info.tag_config("i", font="Consolas 12", lmargin1="20")
        self.pws_info.insert(tk.END, "WATER QUALITY PARAMETER SCHEDULES", "h")
        self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")
        if container:
            for group in container:
                self.pws_info.insert(tk.END, "Begin: {} End: {} Sample Count: {}/{} Schedule: {}".format(group[0],
                                                                                                         group[1],
                                                                                                         group[2],
                                                                                                         group[3],
                                                                                                         group[4]), "i")
                self.pws_info.insert(tk.END, "\n")
        else:
            self.pws_info.insert(tk.END, "NONE FOUND", "i")
            self.pws_info.insert(tk.END, "\n")
        self.pws_info.insert(tk.END, "\n")


class Monitoring(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.entry_frame = tk.Frame(self)
        self.entry_frame.grid()

        self.schedule_label = tk.LabelFrame(self.entry_frame, text="Schedule Type:")
        self.schedule_label.grid(row=0, column=0, padx=5, pady=5)

        self.year_label = tk.LabelFrame(self.entry_frame, text="Year:")
        self.year_label.grid(row=0, column=1, padx=5, pady=5)

        self.option_label = tk.LabelFrame(self.entry_frame, text="Options:")
        self.option_label.grid(row=1, column=0, padx=5, pady=5)

        schedule_list = ['6M1', '6M2', 'YR', '3Y', '9Y']
        self.schedule = tk.StringVar()
        self.schedule.set(schedule_list[0])
        self.schedule_list = tk.OptionMenu(self.schedule_label, self.schedule, '6M1', '6M2', 'YR', '3Y', '9Y')
        self.schedule_list.grid(row=0, column=0, padx=5, pady=5)

        self.year = tk.StringVar()
        self.year_lst = tk.Entry(self.year_label, textvariable=self.year)
        self.year_lst.grid(row=0, column=1, padx=5, pady=5)

        options = ['ALL SCHEDULES', "OPEN SCHEDULES", "CLOSED SCHEDULES"]
        self.options_var = tk.StringVar()
        self.options_var.set(options[0])
        self.options = tk.OptionMenu(self.option_label, self.options_var, 'ALL SCHEDULES', "OPEN SCHEDULES",
                                     "CLOSED SCHEDULES")
        self.options.grid(row=0, column=0, padx=5, pady=5)

        self.create_table_btn = tk.Button(self.entry_frame, text="DISPLAY", command=self.create_table)
        self.create_table_btn.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(self).grid()

        tk.Label(self, text="Created by Eric Stinson 2019").grid()

    def create_table(self):
        try:
            self.table.destroy()
        except:
            pass
        print("Button pushed")
        schedule = self.schedule.get()
        year = self.year.get()
        if year == "":
            no_results()
            return
        option = self.options_var.get()
        print("Selections Captured")
        schedule_lst = schedule_monitoring(main.username.get(), main.password.get(), schedule, year, option)
        if not schedule_lst:
            no_results()
        print("List of Schedules Generated")

        dct = {}
        for pws in schedule_lst:
            pws_id = pws[0]
            name = pws[2]
            activity = pws[3]
            source = pws[4]
            pop = pws[5]
            samples = pws[9]
            dct[pws_id] = {'PWS ID': pws_id, 'NAME': name, 'ACTIVITY': activity, 'SOURCE': source, 'POPULATION': pop,
                           'SAMPLES': samples}

        print("table values generated")
        model = TableModel()
        self.table = TableCanvas(self, model=model, data=dct, read_only=True)
        self.table.show()


class Compliance(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.entry_frame = tk.Frame(self)
        self.entry_frame.grid()

        self.schedule_label = tk.LabelFrame(self.entry_frame, text="Compliance Schedule Type:")
        self.schedule_label.grid(row=0, column=0, padx=10, pady=10)

        self.year_label = tk.LabelFrame(self.entry_frame, text="Year:")
        self.year_label.grid(row=0, column=1, padx=10, pady=10)

        self.option_label = tk.LabelFrame(self.entry_frame, text="Options:")
        self.option_label.grid(row=1, column=0, padx=5, pady=5)

        schedule_list = ['LCNT', 'CCST', 'CCTI', 'LCTS']
        self.schedule = tk.StringVar()
        self.schedule.set(schedule_list[0])
        self.schedule_list = tk.OptionMenu(self.schedule_label, self.schedule, 'LCNT', 'CCST', 'CCTI', 'LCTS')
        self.schedule_list.grid(row=0, column=0, padx=10, pady=10)

        self.year = tk.StringVar()
        self.year_lst = tk.Entry(self.year_label, textvariable=self.year)
        self.year_lst.grid(row=0, column=1, padx=5, pady=5)

        options = ['ALL SCHEDULES', "OPEN SCHEDULES", "CLOSED SCHEDULES"]
        self.options_var = tk.StringVar()
        self.options_var.set(options[0])
        self.options = tk.OptionMenu(self.option_label, self.options_var, 'ALL SCHEDULES', "OPEN SCHEDULES",
                                     "CLOSED SCHEDULES")
        self.options.grid(row=0, column=0, padx=5, pady=5)

        self.create_table_btn = tk.Button(self.entry_frame, text="DISPLAY", command=self.create_table)
        self.create_table_btn.grid(row=0, column=3, padx=10, pady=10)

        tk.Label(self).grid()

        tk.Label(self, text="Created by Eric Stinson 2019").grid()

    def create_table(self):
        print("Button pushed")
        schedule = self.schedule.get()
        year = self.year.get()
        option = self.options_var.get()
        if year == "":
            if option == "OPEN SCHEDULES":
                year = None
            else:
                no_results()
                return
        print("Selections Captured")
        schedule_lst = compliance_pull(main.username.get(), main.password.get(), schedule, year, option)
        if not schedule_lst:
            no_results()
        print("List of Schedules Generated")

        dct = {}
        for pws in schedule_lst:
            pws_id = pws[0]
            name = pws[2]
            activity = pws[3]
            pop = pws[4]
            begin = pws[7]
            if begin is not None:
                begin = str(begin.date())
            due = pws[10]
            if due is not None:
                due = str(due.date())
            close = pws[8]
            if close is not None:
                close = str(close.date())
            dct[pws_id] = {'PWS ID': pws_id, 'NAME': name, 'ACTIVITY': activity, 'POPULATION': pop, 'BEGIN DATE': begin,
                           'DUE DATE': due, 'CLOSE DATE': close}
        print(len(dct))
        print("table values generated")
        model = TableModel()
        self.table = TableCanvas(self, model=model, data=dct, read_only=True)
        self.table.show()


class ActionLevelExceed(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.entry_frame = tk.Frame(self)
        self.entry_frame.grid()

        self.schedule_label = tk.LabelFrame(self.entry_frame, text="Summary Results:")
        self.schedule_label.grid(row=0, column=0, padx=10, pady=10)

        self.year_label = tk.LabelFrame(self.entry_frame, text="Year:")
        self.year_label.grid(row=0, column=1, padx=10, pady=10)

        schedule_list = ['PB ALE', 'CU ALE', 'PB>RML', 'CU>RML']
        self.schedule = tk.StringVar()
        self.schedule.set(schedule_list[0])
        self.schedule_list = tk.OptionMenu(self.schedule_label, self.schedule, 'PB ALE', 'CU ALE', 'PB>RML', 'CU>RML')
        self.schedule_list.grid(row=0, column=0, padx=10, pady=10)

        self.year = tk.StringVar()
        self.year_lst = tk.Entry(self.year_label, textvariable=self.year)
        self.year_lst.grid(row=0, column=1, padx=5, pady=5)

        self.create_table_btn = tk.Button(self.entry_frame, text="DISPLAY", command=self.create_table)
        self.create_table_btn.grid(row=0, column=3, padx=10, pady=10)

        tk.Label(self).grid()

        tk.Label(self, text="Created by Eric Stinson 2019").grid()

    def create_table(self):
        print("Button pushed")
        schedule = self.schedule.get()
        year = self.year.get()
        if year == "":
            year = None
        print("Selections Captured")
        schedule_lst = summary_pull(main.username.get(), main.password.get(), schedule, year)
        if not schedule_lst:
            no_results()
        print("List of Schedules Generated")

        dct = {}
        for pws in schedule_lst:
            pws_id = pws[0]
            name = pws[1]
            activity = pws[2]
            pop = pws[3]
            date = pws[4]
            measure = pws[5]
            dct[pws_id] = {'PWS ID': pws_id, 'NAME': name, 'ACTIVITY': activity, 'POPULATION': pop, 'DATE': date,
                           'MEASURE': measure}

        print("table values generated")
        model = TableModel()
        self.table = TableCanvas(self, model=model, data=dct, read_only=True)
        self.table.show()


class Violations(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.entry_frame = tk.Frame(self)
        self.entry_frame.grid()

        self.schedule_label = tk.LabelFrame(self.entry_frame, text="Violations:")
        self.schedule_label.grid(row=0, column=0, padx=10, pady=10)

        self.year_label = tk.LabelFrame(self.entry_frame, text="Year:")
        self.year_label.grid(row=0, column=1, padx=10, pady=10)

        self.option_label = tk.LabelFrame(self.entry_frame, text="Options:")
        self.option_label.grid(row=1, column=0, padx=5, pady=5)

        schedule_list = [51, 52, 53, 56, 57, 58, 59, 63, 64, 65, 66]
        self.schedule = tk.StringVar()
        self.schedule.set(schedule_list[0])
        self.schedule_list = tk.OptionMenu(self.schedule_label, self.schedule, 51, 52, 53, 56, 57, 58, 59, 63, 64, 65,
                                           66)
        self.schedule_list.grid(row=0, column=0, padx=10, pady=10)

        self.year = tk.StringVar()
        self.year_lst = tk.Entry(self.year_label, textvariable=self.year)
        self.year_lst.grid(row=0, column=1, padx=5, pady=5)

        options = ['ALL VIOLATIONS', "OPEN VIOLATIONS",
                                     "CLOSED VIOLATIONS"]
        self.options_var = tk.StringVar()
        self.options_var.set(options[0])
        self.options = tk.OptionMenu(self.option_label, self.options_var, 'ALL VIOLATIONS', "OPEN VIOLATIONS",
                                     "CLOSED VIOLATIONS")
        self.options.grid(row=0, column=0, padx=5, pady=5)

        self.create_table_btn = tk.Button(self.entry_frame, text="DISPLAY", command=self.create_table)
        self.create_table_btn.grid(row=0, column=3, padx=10, pady=10)

        tk.Label(self).grid()

        tk.Label(self, text="Created by Eric Stinson 2019").grid()

    def create_table(self):
        print("Button pushed")
        schedule = self.schedule.get()
        year = self.year.get()
        option = self.options_var.get()
        if year == "":
            if option == "OPEN VIOLATIONS":
                year = None
            else:
                no_results()
                return
        print("Selections Captured")
        violation_dct = violation_pull(main.username.get(), main.password.get(), schedule, year, option)
        if not violation_dct:
            no_results()
            return
        print("List of Schedules Generated")

        dct = {}
        for viol in violation_dct:
            viol_info = violation_dct[viol]
            pws = viol_info[0]
            vio = viol_info[1]
            pws_id = pws[0]
            name = pws[2]
            activity = pws[3]
            pop = pws[4]
            begin = vio[3]
            close = vio[4]
            # actions = []
            dct[pws_id] = {'PWS ID': pws_id, 'NAME': name, 'ACTIVITY': activity, 'POPULATION': pop, 'BEGIN DATE': begin,
                           'CLOSE DATE': close}

        print("table values generated")
        self.table = TableCanvas(self, data=dct, read_only=True)
        self.table.show()


class Scheduling(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Display Selected",
                                    command=self.display)
        self.popup_menu.add_command(label="Get Sample Results", command=self.show_samples)

        self.entry_frame = tk.Frame(self)
        self.entry_frame.grid()

        self.schedule_label = tk.LabelFrame(self.entry_frame, text="Schedule Type:")
        self.schedule_label.grid(row=0, column=0, padx=5, pady=5)

        self.year_label = tk.LabelFrame(self.entry_frame, text="Year:")
        self.year_label.grid(row=0, column=1, padx=5, pady=5)

        schedule_list = ['6M1', '6M2', 'YR', '3Y', '9Y']
        self.schedule = tk.StringVar()
        self.schedule.set(schedule_list[0])
        self.schedule_list = tk.OptionMenu(self.schedule_label, self.schedule, '6M1', '6M2', 'YR', '3Y', '9Y')
        self.schedule_list.grid(row=0, column=0, padx=5, pady=5)

        self.year = tk.StringVar()
        self.year_lst = tk.Entry(self.year_label, textvariable=self.year)
        self.year_lst.grid(row=0, column=1, padx=5, pady=5)

        self.create_table_btn = tk.Button(self.entry_frame, text="DISPLAY", command=self.create_table)
        self.create_table_btn.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(self).grid()

        tk.Label(self, text="Created by Eric Stinson 2019").grid()

        self.bind("<Button-3>", self.popup)
        self.entry_frame.bind("<Button-3>", self.popup)

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def display(self):
        val = self.table.get_currentRecord()
        main.create_display_page(val)

    def show_samples(self):
        val = self.table.get_currentRecord()
        main.create_sample_page(val)

    def create_table(self):
        try:
            self.table.destroy()
        except:
            pass
        schedule = self.schedule.get()
        year = self.year.get()
        if year == "":
            no_results()
            return
        schedule_lst = schedule_monitoring(main.username.get(), main.password.get(), schedule, year,
                                           option="OPEN SCHEDULES")
        open_scheds_with_summs = summary_pull_by_schedule(main.username.get(), main.password.get(), schedule_lst)
        if not open_scheds_with_summs:
            no_results()
            return
        dct = {}
        for key in open_scheds_with_summs:
            pws = open_scheds_with_summs[key]
            inv_info = pws[0]
            lead = pws[1]
            copper = pws[2]
            pws_id = inv_info[0]
            name = inv_info[1]
            activity = inv_info[2]
            pop = inv_info[3]
            samples_required = inv_info[4]
            date = str(lead[2])
            samples_collected = lead[8]
            cu_summary = copper[9]
            pb_summary = lead[9]
            dct[pws_id] = {'PWS ID': pws_id, 'NAME': name, 'ACTIVITY': activity, 'POPULATION': pop, 'SAMPLES REQUIRED':
                           samples_required, 'SAMPLES COLLECTED': samples_collected, 'CU SUMMARY': cu_summary,
                           'PB SUMMARY': pb_summary, "DATE": date}
        self.table = TableCanvas(self, data=dct)
        self.table.show()
        self.table.bind("<Button-3>", self.popup)
        self.export_table_btn = tk.Button(self, text="EXPORT", command=self.table.exportTable(filename="sample"))


class SampleSummaries(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        self.entry_frame = tk.Frame(self)
        self.entry_frame.grid()

        self.entry_label = tk.LabelFrame(self.entry_frame, text="PWS ID:")
        self.entry_label.grid(row=0, column=0, padx=10, pady=10)

        self.entry_text = tk.StringVar()
        self.entry = tk.Entry(self.entry_label, textvariable=self.entry_text)
        self.entry.grid(row=0, column=0, padx=5, pady=5)

        self.create_table_btn = tk.Button(self.entry_frame, text="DISPLAY", command=self.create_table)
        self.create_table_btn.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self).grid()

        tk.Label(self, text="Created by Eric Stinson 2019").grid()

    def create_table(self):
        print("Button pushed")
        pws_id = self.entry.get()
        if pws_id == "":
            no_results()
            return
        print("Selections Captured")
        container = find_samples(main.username.get(), main.password.get(), pws_id)
        if not container:
            no_results()
            return
        print("Samples Returned")

        dct = {}
        for item in container:
            tsasampl = item[0]
            lcr_id = item[1]
            description_text = item[2]
            collection_address = item[3]
            date = str(item[4])
            reject = item[5]
            dct[tsasampl] = {"SAMPLE ID": tsasampl, "LCR ID": lcr_id, "DESCRIPTION": description_text,
                             "ADDRESS": collection_address, "DATE": date, "REJECTION": reject}

        print("table values generated")
        self.table = TableCanvas(self, data=dct)
        self.table.show()


class MainView(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.p2_btn = tk.StringVar()
        self.p2_btn.set("LCR Display")
        p1 = Home(self)
        p2 = Display(self)
        p3 = Monitoring(self)
        p4 = Compliance(self)
        p5 = ActionLevelExceed(self)
        p6 = Violations(self)
        p7 = Scheduling(self)
        p8 = SampleSummaries(self)

        self.buttonframe = tk.Frame(self)
        self.container = tk.Frame(self)
        self.buttonframe.pack(side="top", fill="x", expand=False)
        self.container.pack(side="top", fill="both", expand=True)

        p1.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        p3.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        p8.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        p4.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        p5.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        p6.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        p7.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tk.Button(self.buttonframe, text="Home", command=p1.lift)
        b2 = tk.Button(self.buttonframe, textvariable=self.p2_btn, command=p2.lift)
        b3 = tk.Button(self.buttonframe, text="Monitoring", command=p3.lift)
        b8 = tk.Button(self.buttonframe, text="Samples", command=p8.lift)
        b4 = tk.Button(self.buttonframe, text="Compliance", command=p4.lift)
        b5 = tk.Button(self.buttonframe, text="ALEs", command=p5.lift)
        b6 = tk.Button(self.buttonframe, text="Violations", command=p6.lift)
        b7 = tk.Button(self.buttonframe, text="Scheduling", command=p7.lift)

        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")
        b8.pack(side="left")
        b4.pack(side="left")
        b5.pack(side="left")
        b6.pack(side="left")
        b7.pack(side="left")

        p1.show()

    def create_display_page(self, val=None):
        p = Display(self)
        self.display_btn = tk.StringVar()
        self.display_btn.set("LCR Display")
        p.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        insideframe = tk.Frame(self.buttonframe)
        insideframe.pack(side="left")
        buttonlabel = tk.Button(insideframe, textvariable=self.display_btn, command=p.lift)
        buttonlabel.pack(side="left")

        def x_marks_the_spot():
            insideframe.destroy()
            p.destroy()

        close = tk.Button(insideframe, text="x", command=x_marks_the_spot)
        close.pack(side="right")
        try:
            p.pws_entry_text.set(val['PWS ID'])
            p.return_info()
        except:
            pass

    # def create_test_page(self, val="TX2460013"):
    #     p = Display(self)
    #     self.display_btn = tk.StringVar()
    #     self.display_btn.set("LCR Display")
    #     p.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
    #     insideframe = tk.Frame(self.buttonframe)
    #     insideframe.pack(side="left")
    #     buttonlabel = tk.Button(insideframe, textvariable=self.display_btn, command=p.lift)
    #     buttonlabel.pack(side="left")
    #
    #     def x_marks_the_spot():
    #         insideframe.destroy()
    #         p.destroy()
    #
    #     close = tk.Button(insideframe, text="x", command=x_marks_the_spot)
    #     close.pack(side="right")
    #     try:
    #         p.pws_entry_text.set(val)
    #         p.return_info(c=1)
    #     except:
    #         pass

    def create_sample_page(self, val=None):
        p = SampleSummaries(self)
        self.display_btn = tk.StringVar()
        self.display_btn.set("Samples")
        p.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        insideframe = tk.Frame(self.buttonframe)
        insideframe.pack(side="left")
        buttonlabel = tk.Button(insideframe, textvariable=self.display_btn, command=p.lift)
        buttonlabel.pack(side="left")

        def x_marks_the_spot():
            insideframe.destroy()
            p.destroy()

        close = tk.Button(insideframe, text="x", command=x_marks_the_spot)
        close.pack(side="right")
        try:
            p.entry_text.set(val['PWS ID'])
            p.create_table()
        except:
            pass

    # def create_test(self, val=None):
    #     print("Starting Testing")
    #     lst = testing()
    #     count = 0
    #     values = [x * 50 for x in range(141)]
    #     container = []
    #     for sys in lst:
    #         count += 1
    #         if count < 4500:
    #             pass
    #         else:
    #             if count == 5260:
    #                 print(container)
    #                 return
    #
    #             _id = sys[0]
    #             p = Display(self)
    #             self.display_btn = tk.StringVar()
    #             self.display_btn.set("LCR Display")
    #             p.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
    #             insideframe = tk.Frame(self.buttonframe)
    #             insideframe.pack(side="left")
    #             buttonlabel = tk.Button(insideframe, textvariable=self.display_btn, command=p.lift)
    #             buttonlabel.pack(side="left")
    #
    #             def x_marks_the_spot():
    #                 insideframe.destroy()
    #                 p.destroy()
    #
    #             close = tk.Button(insideframe, text="x", command=x_marks_the_spot)
    #             close.pack(side="right")
    #
    #             try:
    #                 if count in values:
    #                     print("Completed Count # ", count)
    #                 p.pws_entry_text.set(_id)
    #                 p.return_info(c=1)
    #                 insideframe.destroy()
    #                 p.destroy()
    #             except:
    #                 print("Count # {} failed".format(count))
    #                 insideframe.destroy()
    #                 p.destroy()
    #                 container.append(_id)


if __name__ == "__main__":
    root = tk.Tk()
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    menubar = tk.Menu(root)
    # create a pulldown menu, and add it to the menu bar
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Login", command=login)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    pagemenu = tk.Menu(menubar, tearoff=0)
    pagemenu.add_command(label="Display PWS", command=main.create_display_page)
    pagemenu.add_command(label="Samples", command=main.create_sample_page)
    menubar.add_cascade(label="Create Pages", menu=pagemenu)
    exportmenu = tk.Menu(menubar, tearoff=0)
    exportmenu.add_command(label="Sample Sites", command=export_sample_sites)
    menubar.add_cascade(label="Export", menu=exportmenu)
    # test = tk.Menu(menubar, tearoff=0)
    # test.add_command(label="Test Page", command=main.create_test_page)
    # test.add_command(label="Testing", command=main.create_test)
    # menubar.add_cascade(label="Test", menu=test)
    root.wm_geometry(screensize)
    root.wm_iconbitmap(tempFile)
    root.config(menu=menubar)
    root.title("WATER You Looking For?")
    root.mainloop()
