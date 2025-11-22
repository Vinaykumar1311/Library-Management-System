import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# =====================================================
# DATABASE CONNECTION
# =====================================================
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",        
            password="1234",     
            database="LibraryDB"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Database Connection Failed!\n{err}")
        return None

# =====================================================
# LOGIN WINDOW
# =====================================================
def login_window():
    login = tk.Tk()
    login.title("Library Management System - Login")
    login.geometry("420x300")
    login.configure(bg="#ecf0f1")

    tk.Label(login, text=" Library Management Login", bg="#2980b9", fg="white",
             font=("Arial", 16, "bold"), pady=12).pack(fill="x")

    frame = tk.Frame(login, bg="#ecf0f1", pady=30)
    frame.pack()

    tk.Label(frame, text="Username:", bg="#ecf0f1", font=("Arial", 12)).grid(row=0, column=0, pady=5)
    tk.Label(frame, text="Password:", bg="#ecf0f1", font=("Arial", 12)).grid(row=1, column=0, pady=5)

    username_var = tk.StringVar()
    password_var = tk.StringVar()

    username_entry = tk.Entry(frame, textvariable=username_var, width=25)
    password_entry = tk.Entry(frame, textvariable=password_var, width=25, show="*")

    username_entry.grid(row=0, column=1, pady=5, padx=5)
    password_entry.grid(row=1, column=1, pady=5, padx=5)

    def validate_login():
        uname = username_var.get().strip()
        pword = password_var.get().strip()
        if not uname or not pword:
            messagebox.showwarning("Missing Info", "Please enter both username and password.")
            return

        conn = connect_db()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT role FROM Users WHERE username=%s AND password=%s", (uname, pword))
            result = cur.fetchone()
            conn.close()

            if result:
                role = result[0]
                login.destroy()
                open_dashboard(uname, role)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")

    tk.Button(login, text="Login", bg="#27ae60", fg="white",
              font=("Arial", 12), width=12, command=validate_login).pack(pady=20)

    tk.Button(login, text="Exit", bg="#c0392b", fg="white",
              font=("Arial", 12), width=12, command=login.destroy).pack()

    login.mainloop()

# =====================================================
# MAIN DASHBOARD
# =====================================================
def open_dashboard(username, role):
    root = tk.Tk()
    root.title(f"Library Management System - Logged in as {username} ({role})")
    root.geometry("1300x800")
    root.configure(bg="#f7f9fb")

    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 10), rowheight=25)
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    header = tk.Label(root, text=f"Library Management System Dashboard ({role})", 
                      bg="#2c3e50", fg="white", font=("Arial", 20, "bold"), pady=10)
    header.pack(fill="x")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # ===========================================
    # COMMON HELPER FUNCTIONS
    # ===========================================
    def load_table(treeview, query):
        for row in treeview.get_children():
            treeview.delete(row)
        conn = connect_db()
        if conn:
            cur = conn.cursor()
            cur.execute(query)
            for row in cur.fetchall():
                treeview.insert("", tk.END, values=row)
            conn.close()

    def delete_selected(treeview, table, key):
        if role != 'Admin':
            messagebox.showwarning("Access Denied", "Only Admin can delete records.")
            return
        selected = treeview.focus()
        if not selected:
            return
        key_val = treeview.item(selected)["values"][0]
        conn = connect_db()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE {key}=%s", (key_val,))
        conn.commit()
        conn.close()
        load_table(treeview, f"SELECT * FROM {table}")

    # =====================================================
    # TAB 1: PUBLISHERS
    # =====================================================
    pub_tab = ttk.Frame(notebook)
    notebook.add(pub_tab, text="Publishers")

    pub_table = ttk.Treeview(pub_tab, columns=("publisher_id","name","address"), show="headings")
    for c in ("publisher_id","name","address"):
        pub_table.heading(c, text=c.title())
        pub_table.column(c, width=250)
    pub_table.pack(fill="x", pady=10)

    form = tk.LabelFrame(pub_tab, text="Add Publisher")
    form.pack(fill="x", pady=10)
    pname, paddr = tk.Entry(form, width=25), tk.Entry(form, width=35)
    tk.Label(form, text="Name:").grid(row=0, column=0)
    pname.grid(row=0, column=1)
    tk.Label(form, text="Address:").grid(row=0, column=2)
    paddr.grid(row=0, column=3)

    def add_publisher():
        if role == "Viewer": 
            messagebox.showwarning("Access Denied", "Viewers cannot add data.")
            return
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO Publishers (name, address) VALUES (%s,%s)", (pname.get(), paddr.get()))
        conn.commit()
        conn.close()
        load_table(pub_table, "SELECT * FROM Publishers")

    ttk.Button(form, text="Add Publisher", command=add_publisher).grid(row=0, column=4, padx=10)
    ttk.Button(pub_tab, text="Delete", command=lambda: delete_selected(pub_table, "Publishers", "publisher_id")).pack(pady=5)
    load_table(pub_table, "SELECT * FROM Publishers")

    # =====================================================
    # TAB 2: BOOKS
    # =====================================================
    book_tab = ttk.Frame(notebook)
    notebook.add(book_tab, text="Books")

    book_table = ttk.Treeview(book_tab, columns=("book_id","title","author","publisher_id","year_published","available_copies"), show="headings")
    for c in ("book_id","title","author","publisher_id","year_published","available_copies"):
        book_table.heading(c, text=c.replace("_"," ").title())
        book_table.column(c, width=180)
    book_table.pack(fill="x", pady=10)

    form = tk.LabelFrame(book_tab, text="Add Book")
    form.pack(fill="x", pady=10)
    b_title,b_author,b_pubid,b_year,b_copies=[tk.Entry(form,width=20) for _ in range(5)]
    labels=["Title:","Author:","Publisher ID:","Year:","Copies:"]
    for i,l in enumerate(labels):
        tk.Label(form,text=l).grid(row=i//2,column=(i%2)*2)
        [b_title,b_author,b_pubid,b_year,b_copies][i].grid(row=i//2,column=(i%2)*2+1)
    def add_book():
        if role == "Viewer": return messagebox.showwarning("Access Denied","Viewers cannot add data.")
        conn=connect_db()
        cur=conn.cursor()
        cur.callproc("AddNewBook",(b_title.get(),b_author.get(),b_pubid.get(),b_year.get(),b_copies.get()))
        conn.commit();conn.close()
        load_table(book_table,"SELECT * FROM Books")
    ttk.Button(form,text="Add Book",command=add_book).grid(row=3,column=1,pady=10)
    ttk.Button(book_tab,text="Delete",command=lambda:delete_selected(book_table,"Books","book_id")).pack(pady=5)
    load_table(book_table,"SELECT * FROM Books")

    # =====================================================
    # TAB 3: MEMBERS
    # =====================================================
    mem_tab = ttk.Frame(notebook)
    notebook.add(mem_tab, text="Members")

    mem_table = ttk.Treeview(mem_tab, columns=("member_id","name","email","phone","join_date"), show="headings")
    for c in ("member_id","name","email","phone","join_date"):
        mem_table.heading(c,text=c.title());mem_table.column(c,width=200)
    mem_table.pack(fill="x",pady=10)
    form=tk.LabelFrame(mem_tab,text="Add Member");form.pack(fill="x",pady=10)
    m_name,m_email,m_phone=[tk.Entry(form,width=25) for _ in range(3)]
    for i,t in enumerate(["Name:","Email:","Phone:"]):
        tk.Label(form,text=t).grid(row=0,column=i*2);[m_name,m_email,m_phone][i].grid(row=0,column=i*2+1)
    def add_member():
        if role=="Viewer": return messagebox.showwarning("Access Denied","Viewers cannot add data.")
        conn=connect_db();cur=conn.cursor()
        cur.callproc("AddNewMember",(m_name.get(),m_email.get(),m_phone.get()));conn.commit();conn.close()
        load_table(mem_table,"SELECT * FROM Members")
    ttk.Button(form,text="Add Member",command=add_member).grid(row=0,column=6,padx=10)
    ttk.Button(mem_tab,text="Delete",command=lambda:delete_selected(mem_table,"Members","member_id")).pack(pady=5)
    load_table(mem_table,"SELECT * FROM Members")

    # =====================================================
    # TAB 4: LIBRARIANS
    # =====================================================
    lib_tab=ttk.Frame(notebook)
    notebook.add(lib_tab,text="Librarians")
    lib_table=ttk.Treeview(lib_tab,columns=("librarian_id","name","email","phone"),show="headings")
    for c in ("librarian_id","name","email","phone"):
        lib_table.heading(c,text=c.title());lib_table.column(c,width=200)
    lib_table.pack(fill="x",pady=10)
    form=tk.LabelFrame(lib_tab,text="Add Librarian");form.pack(fill="x",pady=10)
    l_name,l_email,l_phone=[tk.Entry(form,width=25) for _ in range(3)]
    for i,t in enumerate(["Name:","Email:","Phone:"]):
        tk.Label(form,text=t).grid(row=0,column=i*2);[l_name,l_email,l_phone][i].grid(row=0,column=i*2+1)
    def add_librarian():
        if role=="Viewer":return messagebox.showwarning("Access Denied","Viewers cannot add data.")
        conn=connect_db();cur=conn.cursor()
        cur.execute("INSERT INTO Librarian (name,email,phone) VALUES (%s,%s,%s)",(l_name.get(),l_email.get(),l_phone.get()))
        conn.commit();conn.close()
        load_table(lib_table,"SELECT * FROM Librarian")
    ttk.Button(form,text="Add Librarian",command=add_librarian).grid(row=0,column=6,padx=10)
    ttk.Button(lib_tab,text="Delete",command=lambda:delete_selected(lib_table,"Librarian","librarian_id")).pack(pady=5)
    load_table(lib_table,"SELECT * FROM Librarian")

    # =====================================================
    # TAB 5: ISSUE
    # =====================================================
    issue_tab=ttk.Frame(notebook)
    notebook.add(issue_tab,text="Issue")
    issue_table=ttk.Treeview(issue_tab,columns=("issue_id","book_id","member_id","librarian_id","issue_date","return_date"),show="headings")
    for c in ("issue_id","book_id","member_id","librarian_id","issue_date","return_date"):
        issue_table.heading(c,text=c.replace("_"," ").title());issue_table.column(c,width=180)
    issue_table.pack(fill="x",pady=10)
    form=tk.LabelFrame(issue_tab,text="Add Issue");form.pack(fill="x",pady=10)
    i_book,i_member,i_lib,i_issue,i_return=[tk.Entry(form,width=20) for _ in range(5)]
    labels=["Book ID:","Member ID:","Librarian ID:","Issue Date:","Return Date:"]
    for i,t in enumerate(labels):
        tk.Label(form,text=t).grid(row=i//2,column=(i%2)*2);[i_book,i_member,i_lib,i_issue,i_return][i].grid(row=i//2,column=(i%2)*2+1)
    def add_issue():
        if role=="Viewer":return messagebox.showwarning("Access Denied","Viewers cannot add data.")
        conn=connect_db();cur=conn.cursor()
        cur.execute("INSERT INTO Issue (book_id,member_id,librarian_id,issue_date,return_date) VALUES (%s,%s,%s,%s,%s)",(i_book.get(),i_member.get(),i_lib.get(),i_issue.get(),i_return.get()))
        conn.commit();conn.close();load_table(issue_table,"SELECT * FROM Issue")
    ttk.Button(form,text="Add Issue",command=add_issue).grid(row=3,column=1,pady=10)
    load_table(issue_table,"SELECT * FROM Issue")

    # =====================================================
    # TAB 6: FINE
    # =====================================================
    fine_tab=ttk.Frame(notebook)
    notebook.add(fine_tab,text="Fine")
    fine_table=ttk.Treeview(fine_tab,columns=("fine_id","issue_id","amount","status"),show="headings")
    for c in ("fine_id","issue_id","amount","status"):
        fine_table.heading(c,text=c.title());fine_table.column(c,width=200)
    fine_table.pack(fill="x",pady=10)
    form=tk.LabelFrame(fine_tab,text="Add Fine");form.pack(fill="x",pady=10)
    f_issue,f_amt,f_status=[tk.Entry(form,width=20) for _ in range(3)]
    for i,t in enumerate(["Issue ID:","Amount:","Status:"]):
        tk.Label(form,text=t).grid(row=0,column=i*2);[f_issue,f_amt,f_status][i].grid(row=0,column=i*2+1)
    def add_fine():
        if role=="Viewer":return messagebox.showwarning("Access Denied","Viewers cannot add data.")
        conn=connect_db();cur=conn.cursor()
        cur.execute("INSERT INTO Fine (issue_id,amount,status) VALUES (%s,%s,%s)",(f_issue.get(),f_amt.get(),f_status.get()))
        conn.commit();conn.close();load_table(fine_table,"SELECT * FROM Fine")
    ttk.Button(form,text="Add Fine",command=add_fine).grid(row=0,column=6,padx=10)
    load_table(fine_table,"SELECT * FROM Fine")

    # =====================================================
    # TAB 7: REPORTS (FUNCTIONS + QUERIES)
    # =====================================================
    report_tab=ttk.Frame(notebook)
    notebook.add(report_tab,text="Reports")
    report_frame=tk.Frame(report_tab,padx=20,pady=20)
    report_frame.pack(fill="both",expand=True)
    tree=ttk.Treeview(report_frame,columns=("col1","col2","col3"),show="headings",height=20)
    tree.pack(fill="both",expand=True)

    def show_functions():
        conn=connect_db();cur=conn.cursor()
        cur.execute("SELECT GetAvailableBooks(),GetMemberCount();")
        result=cur.fetchone()
        tree.delete(*tree.get_children())
        tree["columns"]=("Metric","Value")
        for c in tree["columns"]:
            tree.heading(c,text=c);tree.column(c,width=250)
        tree.insert("", "end", values=("Total Available Books", result[0]))
        tree.insert("", "end", values=("Total Members", result[1]))
        conn.close()

    def show_queries():
        conn=connect_db();cur=conn.cursor()
        cur.execute("SELECT p.name, COUNT(b.book_id) FROM Publishers p LEFT JOIN Books b ON p.publisher_id=b.publisher_id GROUP BY p.name;")
        agg=cur.fetchall()
        cur.execute("SELECT m.name, b.title, i.issue_date FROM Members m JOIN Issue i ON m.member_id=i.member_id JOIN Books b ON i.book_id=b.book_id;")
        join=cur.fetchall()
        cur.execute("SELECT title FROM Books WHERE publisher_id IN (SELECT publisher_id FROM Publishers WHERE name='McGraw Hill');")
        nested=cur.fetchall()
        tree.delete(*tree.get_children())
        tree["columns"]=("Col1","Col2","Col3")
        for c in tree["columns"]:
            tree.heading(c,text=c);tree.column(c,width=300)
        tree.insert("", "end", values=("---- Aggregate: Books per Publisher ----", "", ""))
        for r in agg: tree.insert("", "end", values=(r[0], f"{r[1]} Books", ""))
        tree.insert("", "end", values=("","", ""))
        tree.insert("", "end", values=("---- Join: Member & Book Issued ----","", ""))
        for r in join: tree.insert("", "end", values=(r[0],r[1],r[2]))
        tree.insert("", "end", values=("","", ""))
        tree.insert("", "end", values=("---- Nested: Books by McGraw Hill ----","", ""))
        for r in nested: tree.insert("", "end", values=(r[0],"",""))
        conn.close()

    ttk.Button(report_frame,text="Show Functions",command=show_functions,width=25).pack(pady=8)
    ttk.Button(report_frame,text="Show SQL Queries",command=show_queries,width=25).pack(pady=8)

    root.mainloop()

# =====================================================
# RUN APP
# =====================================================
if __name__=="__main__":
    login_window()
