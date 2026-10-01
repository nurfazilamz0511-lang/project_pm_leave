# PM Leave - Approval Foreman

Alur approval:
Employee -> Foreman -> Manager -> HR -> Disetujui

## Akun demo
- Employee: nurfazila / password123
- Foreman: foreman / foreman123
- Manager: manager / manager123
- HR: hr / hr123

## Menjalankan
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```
Buka http://127.0.0.1:5000

Foreman, Manager, dan HR memiliki menu Approval sesuai status masing-masing.
