# Setup Guide - Complete in 30 Minutes

## What You Need

| Item | Cost | Where |
|---|---|---|
| Domain | ~$1 first year | Sav.com (use `.xyz` or `.fun` promo) |
| GitHub account | Free | github.com |
| Cloudflare account | Free | cloudflare.com |
| OpenRouter API keys | Free | openrouter.ai (create 4 accounts) |
| NVIDIA API key | Free | build.nvidia.com |
| Unsplash API key | Free | unsplash.com/developers |
| NewsAPI key | Free | newsapi.org |

---

## Step 1: Domain (`~$1`)

1. Go to **Sav.com** (or Namecheap)
2. Search for a cheap domain (`.xyz`, `.fun`, `.click` - usually $0.50-$1 first year)
3. Buy it
4. Go to your domain's DNS settings, delete all existing nameservers
5. Add Cloudflare nameservers (you'll get these in Step 2)

---

## Step 2: Cloudflare (Free)

1. Create account at **cloudflare.com**
2. Add your domain
3. Copy the two Cloudflare nameservers (e.g., `nora.ns.cloudflare.com`)
4. Go back to Sav.com → paste these as your domain's nameservers
5. Wait 5-10 minutes for DNS to propagate
6. In Cloudflare → DNS → Add these records:
   - Type: `A`, Name: `@`, Value: `185.199.108.153`
   - Type: `A`, Name: `@`, Value: `185.199.109.153`
   - Type: `A`, Name: `@`, Value: `185.199.110.153`
   - Type: `A`, Name: `@`, Value: `185.199.111.153`
   - Type: `CNAME`, Name: `www`, Value: `yourgithubusername.github.io`
7. Enable the orange proxy (Proxied) toggle

---

## Step 3: GitHub Repo (Free)

1. Go to **github.com** and log in
2. Click **New repository**
3. Name it: `yourgithubusername.github.io` (replace with your actual username)
4. Set it to **Public**
5. Do NOT initialize with README (we'll push files)
6. Click **Create repository**

---

## Step 4: Push Files to GitHub

Open terminal / PowerShell on your computer (you have Python installed):

```powershell
# Go to the Ads folder
cd C:\Users\Shiva\Desktop\Ads

# Initialize git
git init
git add .
git commit -m "Initial setup"

# Connect to your GitHub repo
git remote add origin https://github.com/YOURUSERNAME/YOURUSERNAME.github.io.git
git branch -M main
git push -u origin main
```

---

## Step 5: Enable GitHub Pages

1. Go to your repo on GitHub → **Settings** → **Pages**
2. Under "Branch": select `main` and `/ (root)`, click **Save**
3. Under "Custom domain": enter `yourdomain.com` (not .github.io)
4. Click **Save** → wait for DNS check
5. Check "Enforce HTTPS"

Your site is live at `https://yourdomain.com` within 5 minutes.

---

## Step 6: Update Site Config

Edit `_config.yml` in the Ads folder - change `YOURDOMAIN.com` to your actual domain.

Then commit and push:
```powershell
git add .
git commit -m "Updated domain config"
git push
```

---

## Step 7: Get API Keys (5 minutes)

### OpenRouter (4 keys - 4 accounts)
1. Go to **openrouter.ai**
2. Sign up with email, Google, or GitHub
3. Go to **Keys** → **Create Key**
4. Copy the key
5. Repeat for 3 more accounts (use different emails)
6. You get $1 free credit per account (enough for ~50 articles each)

### NVIDIA
1. Go to **build.nvidia.com**
2. Sign up
3. Go to **API** → **Generate API Key**
4. Copy the key

### Unsplash
1. Go to **unsplash.com/developers**
2. Click **Register as a developer** → **Create app**
3. Name it anything → **Accept terms**
4. Copy the **Access Key**

### NewsAPI
1. Go to **newsapi.org**
2. Click **Get API Key** → sign up
3. Copy the key (free tier: 100 requests/day)

---

## Step 8: Add Secrets to GitHub

1. Go to your repo on GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each one:

| Secret Name | Value |
|---|---|
| `OPENROUTER_API_KEY_1` | Your first OpenRouter key |
| `OPENROUTER_API_KEY_2` | Your second OpenRouter key |
| `OPENROUTER_API_KEY_3` | Your third OpenRouter key |
| `OPENROUTER_API_KEY_4` | Your fourth OpenRouter key |
| `NVIDIA_API_KEY_1` | Your NVIDIA key |
| `UNSPLASH_ACCESS_KEY` | Your Unsplash key |
| `NEWSAPI_KEY` | Your NewsAPI key |

---

## Step 9: Enable Workflow Permissions

1. Go to your repo → **Settings** → **Actions** → **General**
2. Under "Workflow permissions":
   - Select **"Read and write permissions"**
   - Check **"Allow GitHub Actions to create and approve pull requests"**
3. Click **Save**

---

## Step 10: Test It

1. Go to your repo → **Actions** tab
2. Click **"Daily Content Generator"** on the left
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait 2-3 minutes
5. If it turns green ✓ → check your site at `https://yourdomain.com`
6. You should see your first article!

---

## Step 11: AdSense (After ~30 articles)

**Do NOT apply too early.** Wait until you have:
- ✅ 25+ published articles (the script creates 1/day → 3.5 weeks)
- ✅ All pages working (Home, About, Contact, Privacy, Terms)
- ✅ Custom domain with SSL (green lock in browser)

Then:
1. Go to **adsense.google.com**
2. Click **"Get started"** → enter your site URL
3. Paste the ad code into `_config.yml`:
   ```yaml
   google_adsense_id: "ca-pub-XXXXXXXXXXXXXXXX"
   ```
4. Commit and push:
   ```powershell
   git add .
   git commit -m "Added AdSense"
   git push
   ```
5. Submit for approval in AdSense
6. Wait 1-7 days for approval

---

## Step 12: You're Done

The system now:
- Runs daily at 6 AM UTC automatically
- Finds trending topics
- Generates articles
- Publishes to your site
- Shows ads (once approved)

**You never need to touch it again.**

---

## Monitoring

- Check **GitHub Actions** tab → see daily run logs
- Check **Google Search Console** (free) → see which articles rank
- Check **AdSense dashboard** → see earnings

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Workflow fails | Go to Actions tab → click failed run → read logs |
| "No non-duplicate topic found" | Normal - check back tomorrow when new trends appear |
| LLM API fails | Make sure all 5 API keys are added as GitHub Secrets |
| Site shows 404 | GitHub Pages takes 1-2 minutes to deploy after push |
| Domain not loading | Check Cloudflare DNS settings - must have A records pointing to GitHub IPs |
