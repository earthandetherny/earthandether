# Earth + Ether — Website

earthandetherny.com · GitHub Pages deployment

---

## 📁 Files

| File | Purpose |
|------|---------|
| `index.html` | Main website (all images embedded) |
| `listings.json` | Current Chairish listings (auto-updated weekly) |
| `scripts/scrape.py` | Scraper that runs in GitHub Actions |
| `.github/workflows/update-listings.yml` | Weekly auto-update schedule |

---

## 🚀 First-Time Setup (one-time, ~10 minutes)

### 1. Create a GitHub account
Go to [github.com](https://github.com) and sign up (free).

### 2. Create a new repository
- Click **+** → **New repository**
- Name it: `earthandether-site` (or anything you like)
- Set to **Public**
- Click **Create repository**

### 3. Upload all files
- On the repo page click **uploading an existing file**
- Drag in ALL files: `index.html`, `listings.json`, `README.md`
- Also upload the folders: `.github/` and `scripts/`
- Click **Commit changes**

### 4. Enable GitHub Pages
- Go to **Settings** → **Pages**
- Under *Source*, select **Deploy from a branch**
- Branch: `main` · Folder: `/ (root)`
- Click **Save**
- Your site will be live at `https://YOUR-USERNAME.github.io/earthandether-site/`

### 5. Connect your domain
- In GitHub Pages settings, enter `earthandetherny.com` under *Custom domain*
- GitHub gives you 4 DNS records to add at your registrar (GoDaddy/Namecheap/etc.)
- Add the 4 `A` records and one `CNAME` record as shown
- HTTPS is automatic and free

---

## 🔄 How Auto-Updates Work

Every **Monday at 7 AM UTC**, GitHub Actions automatically:

1. Launches a headless Chrome browser
2. Visits your Chairish shop: `chairish.com/shop/earthandether`
3. Extracts the 10 most recent active listings
4. Checks each listing URL — removes any that are sold
5. Writes the results to `listings.json`
6. Commits and deploys automatically

**The website fetches `listings.json` on every page load** — so visitors always see the current listings without you doing anything.

### Trigger an update manually
Go to **Actions** tab → **Update Chairish Listings** → **Run workflow** → **Run workflow**

---

## ✏️ Updating Listings Manually

If you want to add or remove specific items without waiting for Monday:

1. Open `listings.json` in GitHub (click the file → pencil icon ✏️)
2. Edit the JSON array — each item is:
   ```json
   {
     "url":   "https://www.chairish.com/product/XXXXXX",
     "img":   "https://chairish-prod.freetls.fastly.net/image/...",
     "title": "Item Name"
   }
   ```
3. To get an image URL: open the product on Chairish → right-click the photo → **Copy image address**
4. Click **Commit changes** — site updates in ~30 seconds

---

## 📧 Contact
earthandetherny@gmail.com
