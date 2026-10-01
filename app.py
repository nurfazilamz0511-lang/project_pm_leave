from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "pm-leave-dev-secret-key")


users = {
    "nurfazila": {
        "username": "nurfazila",
        "password": generate_password_hash("password123"),
        "name": "Nur Fazila",
        "email": "nurfazila@palma.local",
        "department": "Human Resources",
        "position": "Staff",
        "role": "Employee",
        "phone": "08xxxxxxxxxx"
    },
    "foreman": {
        "username": "foreman",
        "password": generate_password_hash("foreman123"),
        "name": "Budi Foreman",
        "email": "foreman@palma.local",
        "department": "Operational",
        "position": "Foreman",
        "role": "Foreman",
        "phone": "08xxxxxxxx11"
    },
    "manager": {
        "username": "manager",
        "password": generate_password_hash("manager123"),
        "name": "Andi Manager",
        "email": "manager@palma.local",
        "department": "Operational",
        "position": "Manager",
        "role": "Manager",
        "phone": "08xxxxxxxx22"
    },
    "hr": {
        "username": "hr",
        "password": generate_password_hash("hr123"),
        "name": "Siti HR",
        "email": "hr@palma.local",
        "department": "Human Resources",
        "position": "HR",
        "role": "HR",
        "phone": "08xxxxxxxx33"
    }
}

# -----------------------------------------------------------------------------
# DEMO LEAVE DATA
# Alur: Diajukan -> Menunggu Foreman -> Menunggu Manager -> Menunggu HR -> Disetujui
# -----------------------------------------------------------------------------
leave_requests = [
    {
        "id": 1,
        "employee": "nurfazila",
        "employee_name": "Nur Fazila",
        "type": "Cuti Tahunan",
        "start": "2026-10-05",
        "end": "2026-10-07",
        "days": 3,
        "reason": "Keperluan keluarga",
        "status": "Menunggu Foreman",
        "created": "25 Sep 2026",
        "approved_by": [],
        "history": []
    },
    {
        "id": 2,
        "employee": "nurfazila",
        "employee_name": "Nur Fazila",
        "type": "Cuti Pribadi",
        "start": "2026-11-12",
        "end": "2026-11-12",
        "days": 1,
        "reason": "Urusan pribadi",
        "status": "Menunggu Manager",
        "created": "25 Sep 2026",
        "approved_by": ["Foreman - Budi Foreman"],
        "history": [
            {"role": "Foreman", "action": "Disetujui", "by": "Budi Foreman", "at": "25 Sep 2026 10:30"}
        ]
    },
    {
        "id": 3,
        "employee": "nurfazila",
        "employee_name": "Nur Fazila",
        "type": "Cuti Khusus",
        "start": "2026-12-01",
        "end": "2026-12-02",
        "days": 2,
        "reason": "Keperluan keluarga",
        "status": "Disetujui",
        "created": "20 Sep 2026",
        "approved_by": ["Foreman - Budi Foreman", "Manager - Andi Manager", "HR - Siti HR"],
        "history": [
            {"role": "Foreman", "action": "Disetujui", "by": "Budi Foreman", "at": "20 Sep 2026 09:00"},
            {"role": "Manager", "action": "Disetujui", "by": "Andi Manager", "at": "20 Sep 2026 11:00"},
            {"role": "HR", "action": "Disetujui", "by": "Siti HR", "at": "20 Sep 2026 14:00"}
        ]
    }
]

ROLE_STATUS = {
    "Foreman": "Menunggu Foreman",
    "Manager": "Menunggu Manager",
    "HR": "Menunggu HR"
}

NEXT_STATUS = {
    "Foreman": "Menunggu Manager",
    "Manager": "Menunggu HR",
    "HR": "Disetujui"
}

REJECTION_STATUS = {
    "Foreman": "Ditolak Foreman",
    "Manager": "Ditolak Manager",
    "HR": "Ditolak HR"
}


def current_user():
    username = session.get("user")
    return users.get(username)


def is_logged_in():
    return current_user() is not None


def can_approve(role):
    return role in ROLE_STATUS


def get_user_requests(username):
    return [x for x in leave_requests if x["employee"] == username]


@app.context_processor
def inject_globals():
    user = current_user()
    return {
        "account": user or users["nurfazila"],
        "current_year": datetime.now().year,
        "current_role": user["role"] if user else None,
        "can_approve": can_approve(user["role"]) if user else False
    }


@app.route("/")
def index():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = users.get(username)

        if user and check_password_hash(user["password"], password):
            session["user"] = username
            flash(f"Selamat datang, {user['name']}.", "success")
            return redirect(url_for("dashboard"))

        flash("Username atau password salah.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Anda telah keluar dari PM Leave.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))

    user = current_user()
    mine = get_user_requests(user["username"])

    approved = sum(1 for x in mine if x["status"] == "Disetujui")
    pending_statuses = {"Diajukan", "Menunggu Foreman", "Menunggu Manager", "Menunggu HR"}
    pending = sum(1 for x in mine if x["status"] in pending_statuses)
    rejected = sum(1 for x in mine if x["status"].startswith("Ditolak"))
    total = len(mine)
    used_days = sum(x["days"] for x in mine if x["status"] == "Disetujui")
    remaining = max(12 - used_days, 0)

    # Statistik untuk approver.
    approval_queue = [x for x in leave_requests if user["role"] in ROLE_STATUS and x["status"] == ROLE_STATUS[user["role"]]]

    return render_template(
        "dashboard.html",
        active="dashboard",
        total=total,
        approved=approved,
        pending=pending,
        rejected=rejected,
        remaining=remaining,
        recent=mine[:5],
        approval_queue=approval_queue
    )


@app.route("/cuti", methods=["GET", "POST"])
def cuti():
    if not is_logged_in():
        return redirect(url_for("login"))

    user = current_user()
    if user["role"] != "Employee":
        flash("Menu pengajuan cuti hanya tersedia untuk Employee.", "error")
        return redirect(url_for("approval"))

    if request.method == "POST":
        leave_type = request.form.get("type", "Cuti Tahunan")
        start = request.form.get("start", "")
        end = request.form.get("end", "")
        reason = request.form.get("reason", "").strip()

        try:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            days = (end_date - start_date).days + 1
        except ValueError:
            flash("Tanggal cuti belum valid.", "error")
            return redirect(url_for("cuti"))

        if days <= 0:
            flash("Tanggal selesai harus sama atau setelah tanggal mulai.", "error")
            return redirect(url_for("cuti"))

        if not reason:
            flash("Alasan cuti wajib diisi.", "error")
            return redirect(url_for("cuti"))

        new_id = max((x["id"] for x in leave_requests), default=0) + 1
        leave_requests.insert(0, {
            "id": new_id,
            "employee": user["username"],
            "employee_name": user["name"],
            "type": leave_type,
            "start": start,
            "end": end,
            "days": days,
            "reason": reason,
            "status": "Menunggu Foreman",
            "created": datetime.now().strftime("%d %b %Y"),
            "approved_by": [],
            "history": []
        })
        flash("Pengajuan cuti berhasil dikirim dan menunggu persetujuan Foreman.", "success")
        return redirect(url_for("cuti"))

    mine = get_user_requests(user["username"])
    used_days = sum(x["days"] for x in mine if x["status"] == "Disetujui")
    remaining = max(12 - used_days, 0)

    return render_template(
        "leave.html",
        active="leave",
        requests=mine,
        used_days=used_days,
        remaining=remaining
    )


@app.route("/approval")
def approval():
    if not is_logged_in():
        return redirect(url_for("login"))

    user = current_user()
    if not can_approve(user["role"]):
        flash("Anda tidak memiliki akses ke halaman approval.", "error")
        return redirect(url_for("dashboard"))

    required_status = ROLE_STATUS[user["role"]]
    queue = [x for x in leave_requests if x["status"] == required_status]

    return render_template(
        "approval.html",
        active="approval",
        queue=queue,
        role=user["role"],
        required_status=required_status
    )


@app.route("/approval/<int:request_id>/<action>", methods=["POST"])
def process_approval(request_id, action):
    if not is_logged_in():
        return redirect(url_for("login"))

    user = current_user()
    role = user["role"]

    if not can_approve(role):
        flash("Anda tidak memiliki hak approval.", "error")
        return redirect(url_for("dashboard"))

    item = next((x for x in leave_requests if x["id"] == request_id), None)
    if not item:
        flash("Data pengajuan tidak ditemukan.", "error")
        return redirect(url_for("approval"))

    required_status = ROLE_STATUS[role]
    if item["status"] != required_status:
        flash("Pengajuan ini belum atau sudah diproses oleh role lain.", "error")
        return redirect(url_for("approval"))

    if action not in {"approve", "reject"}:
        flash("Aksi approval tidak valid.", "error")
        return redirect(url_for("approval"))

    now = datetime.now().strftime("%d %b %Y %H:%M")
    if action == "approve":
        item["status"] = NEXT_STATUS[role]
        item["approved_by"].append(f"{role} - {user['name']}")
        item["history"].append({
            "role": role,
            "action": "Disetujui",
            "by": user["name"],
            "at": now
        })
        if role == "HR":
            message = "Pengajuan cuti disetujui. Proses approval selesai."
        else:
            message = f"Pengajuan disetujui oleh {role} dan diteruskan ke {NEXT_STATUS[role].replace('Menunggu ', '')}."
        flash(message, "success")
    else:
        item["status"] = REJECTION_STATUS[role]
        item["history"].append({
            "role": role,
            "action": "Ditolak",
            "by": user["name"],
            "at": now
        })
        flash(f"Pengajuan ditolak oleh {role}.", "success")

    return redirect(url_for("approval"))


@app.route("/approval/<int:request_id>")
def approval_detail(request_id):
    if not is_logged_in():
        return redirect(url_for("login"))

    user = current_user()
    if not can_approve(user["role"]):
        return redirect(url_for("dashboard"))

    item = next((x for x in leave_requests if x["id"] == request_id), None)
    if not item:
        flash("Data pengajuan tidak ditemukan.", "error")
        return redirect(url_for("approval"))

    return render_template("approval_detail.html", active="approval", item=item, role=user["role"])


@app.route("/pengaturan", methods=["GET", "POST"])
def settings():
    if not is_logged_in():
        return redirect(url_for("login"))

    user = current_user()
    if request.method == "POST":
        user["name"] = request.form.get("name", user["name"]).strip() or user["name"]
        user["email"] = request.form.get("email", user["email"]).strip() or user["email"]
        user["phone"] = request.form.get("phone", user["phone"]).strip() or user["phone"]
        flash("Pengaturan akun berhasil diperbarui.", "success")
        return redirect(url_for("settings"))

    return render_template("settings.html", active="settings")


if __name__ == "__main__":
    app.run(debug=True)
