# PDFjin 🚀

> **All-in-one PDF toolkit** — Convert, merge, split, compress, protect and edit PDFs online. Hosted on Google Cloud.

---

## 📁 Project Structure

```
pdfjin/
├── frontend/              ← Static website (HTML/CSS/JS)
│   ├── index.html         ← Landing page
│   ├── css/style.css      ← Main stylesheet
│   ├── js/main.js         ← JavaScript
│   └── pages/             ← Individual tool pages (Step 2)
│
├── backend/               ← Python API (Step 3 — coming soon)
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
└── deploy/                ← GCP deployment scripts
    ├── setup-gcp.ps1      ← Run ONCE to create everything on GCP
    ├── update.ps1         ← Run every time you make changes
    ├── add-custom-domain.ps1  ← Run when you have a domain name
    └── teardown.ps1       ← Clean up GCP resources
```

---

## 🚀 Deploy to Google Cloud — Step by Step

### Prerequisites
1. ✅ **Google Account** — [accounts.google.com](https://accounts.google.com)
2. ✅ **gcloud CLI** — [Download here](https://cloud.google.com/sdk/docs/install)
3. ✅ **Billing enabled** — Required to serve public traffic

### 1️⃣ Install gcloud CLI (Windows)
Download and run the installer from:
👉 https://cloud.google.com/sdk/docs/install-sdk#windows

After install, open PowerShell and run:
```powershell
gcloud --version   # Should show version number
```

### 2️⃣ Edit the Config (Required!)
Open `deploy\setup-gcp.ps1` and change:
```powershell
$PROJECT_ID   = "pdfjin-site"       # ← Must be globally unique on GCP
$BUCKET_NAME  = "pdfjin-website"    # ← Must be globally unique
$REGION       = "asia-southeast1"   # ← Keep for Southeast Asia
```
> ⚠️ If the name is already taken, just add numbers: `pdfjin-site-2025`

### 3️⃣ Run the Frontend Setup Script
Open PowerShell **as Administrator** in the project folder:
```powershell
cd C:\Users\ADMIN\Desktop\pdfjin
.\deploy\setup-gcp.ps1
```

### 4️⃣ Deploy the Backend (Python API)
To make the tools actually work, you need to deploy the backend engine to Cloud Run:
```powershell
.\deploy\deploy-backend.ps1
```
This will:
- ✅ Build a Docker image of the Python app
- ✅ Deploy it to **Google Cloud Run**
- ✅ Print your API URL (e.g., `https://pdfjin-api-xyz.a.run.app`)

### 5️⃣ Your Site is Live! 🎉
After both scripts complete, your site will be at:
```
https://storage.googleapis.com/pdfjin.com/index.html
```

---

## 🔄 Deploying Updates

**For Frontend (HTML/CSS/JS):**
```powershell
.\deploy\update.ps1
```

**For Backend (Python Engine):**
```powershell
.\deploy\deploy-backend.ps1
```

---

## 🌐 Add Custom Domain + HTTPS + CDN (Optional)

Once you have a domain name (e.g., from Namecheap, GoDaddy, Google Domains):

1. Edit `deploy\add-custom-domain.ps1`:
```powershell
$DOMAIN = "www.yourdomain.com"   # ← Your actual domain
```

2. Run:
```powershell
.\deploy\add-custom-domain.ps1
```

3. The script will print an **IP address** — add it as an **A Record** in your domain's DNS settings.

4. Wait 5-30 minutes → your site is live at `https://www.yourdomain.com` 🎉

---

## 💰 Cost Estimate

| Scenario | Monthly Cost |
|----------|-------------|
| Low traffic (< 10GB/month) | ~**Free** (within GCP free tier) |
| With Load Balancer + CDN | ~$18/month |
| New GCP account | **$300 free credit** for 90 days |

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3 (Vanilla), JavaScript |
| **Hosting** | Google Cloud Storage |
| **CDN** | Google Cloud CDN |
| **SSL** | Google-managed certificates (auto-renew) |
| **Backend** *(Step 3)* | Python FastAPI + Docker |
| **Backend Hosting** *(Step 3)* | Google Cloud Run |
| **PDF Engine** | LibreOffice, pypdf, Ghostscript, img2pdf |

---

## 📋 Services Offered

| # | Tool | Engine |
|---|------|--------|
| 1 | PDF to Word | `pdf2docx` |
| 2 | Word to PDF | LibreOffice |
| 3 | PDF to JPG | `pdf2image` (Poppler) |
| 4 | JPG to PDF | `img2pdf` |
| 5 | PDF to PowerPoint | LibreOffice |
| 6 | Excel to PDF | LibreOffice |
| 7 | HTML to PDF | WeasyPrint |
| 8 | Merge PDF | `pypdf` |
| 9 | Split PDF | `pypdf` |
| 10 | Rotate PDF | `pypdf` |
| 11 | Reorder Pages | `pypdf` |
| 12 | Compress PDF | Ghostscript |
| 13 | Protect PDF | `pikepdf` |
| 14 | Unlock PDF | `pikepdf` |
| 15 | Watermark PDF | `reportlab` + `pypdf` |
| 16 | Add Page Numbers | `reportlab` + `pypdf` |
| 17 | Repair PDF | `pikepdf` |
