# Deploying the DRP ABM on Fly.io

## What you need before starting

- A computer with a terminal (Mac Terminal, Windows PowerShell, or Linux terminal)
- A credit card (Fly.io requires one on signup but has a free tier that covers this app)
- The complete project folder containing all .py, .xlsx, .json, and static/index.html files, plus the four deployment files (requirements.txt, Dockerfile, fly.toml, .dockerignore)

## Step 1: Install Fly.io CLI

**Mac:**
```
brew install flyctl
```

**Windows (PowerShell):**
```
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Linux:**
```
curl -L https://fly.io/install.sh | sh
```

Verify it installed:
```
fly version
```

## Step 2: Create a Fly.io account

```
fly auth signup
```

This opens your browser. Create an account and add a payment method. The free tier includes 3 shared-CPU VMs and 256MB RAM each, which is more than enough for this app.

If you already have an account:
```
fly auth login
```

## Step 3: Organize your project folder

Create a folder (e.g., `drp-abm`) and place all files in this structure:

```
drp-abm/
  app.py
  agent.py
  analytical_engine.py
  config.py
  data_loader.py
  primary_model.py
  relational_engine.py
  appendix3_enrichment.json
  Phase_1A_Master_final.xlsx
  Phase_3A_Condition_Mapping.xlsx
  Phase_3A_Outcome_Mapping.xlsx
  Phase_3A_Quantitative_Matrix_VERIFIED.xlsx
  Phase_3B_Qualitative_Matrix_FINAL.xlsx
  Phase_4B_Complete.xlsx
  Phase_4D_Outcome_Positioning.xlsx
  Relational_Density.xlsx
  requirements.txt
  Dockerfile
  fly.toml
  .dockerignore
  static/
    index.html
```

The test files (test_loading.py, test_analytical.py, test_relational.py) are optional for deployment. They won't cause issues if included, but they're not needed in production.

## Step 4: Navigate to your project folder

```
cd /path/to/drp-abm
```

## Step 5: Launch the app on Fly.io

```
fly launch
```

Fly will detect the Dockerfile and fly.toml. It will ask:

- **Would you like to copy its configuration to the new app?** Yes
- **App name:** Choose something like `drp-abm` (must be globally unique; if taken, try `drp-abm-2025` or similar)
- **Region:** Pick the closest to you (e.g., `iad` for US East, `lhr` for London)
- **Would you like to set up a PostgreSQL database?** No
- **Would you like to set up an Upstash Redis database?** No
- **Would you like to deploy now?** Yes

The first deploy takes 2-3 minutes. You'll see Docker building the image, installing Python packages, and pushing to Fly.io.

## Step 6: Verify the deployment

Once complete, Fly prints your app URL:

```
Visit your newly deployed app at https://drp-abm.fly.dev/
```

Open that URL in your browser. The model takes 5-10 seconds to initialize on first request (loading Excel files into memory). After that, all interactions are fast.

You can also open it from the terminal:
```
fly apps open
```

## Step 7: Check logs if anything goes wrong

```
fly logs
```

You should see the familiar startup output:
```
Initializing ABM...
Loading Phase_4B (condition positioning)...
  -> 43 agents created with condition scores
...
Ready: 43 agents loaded.
```

## Ongoing management

**Redeploy after code changes:**
```
fly deploy
```

**Check app status:**
```
fly status
```

**Scale memory if needed** (unlikely, but if the app runs out of memory):
```
fly scale memory 512
```

**View the Fly.io dashboard:**
```
fly dashboard
```

**Stop the app** (to avoid any charges):
```
fly scale count 0
```

**Restart the app:**
```
fly scale count 1
```

**Delete the app entirely:**
```
fly apps destroy drp-abm
```

## Custom domain (optional)

If you want to serve the app at a custom URL like `abm.yourdomain.com`:

```
fly certs add abm.yourdomain.com
```

Fly will give you a CNAME record to add to your DNS. Point `abm.yourdomain.com` to `drp-abm.fly.dev` and Fly provisions an SSL certificate automatically.

## Cost

This app fits comfortably within Fly.io's free tier. The `auto_stop_machines` setting in fly.toml means the machine stops when idle and restarts on the next request (with a ~10 second cold start). If you want the app always warm for instant responses, set `min_machines_running = 1` in fly.toml and redeploy. That uses your free allowance continuously but avoids cold starts.

## Troubleshooting

**"Error: could not find Dockerfile"**
Make sure you're in the correct directory and the Dockerfile exists.

**App deploys but shows 502 error**
Check `fly logs`. Most likely the Excel files are missing from the Docker image. Verify they're not excluded by .dockerignore and that they're in the same directory as the Python files.

**Timeout on first request**
Normal. The model loads 8 Excel files at startup. Subsequent requests are fast. If it persists, increase the timeout: edit Dockerfile and change `--timeout 120` to `--timeout 180`.

**"No machines running"**
The app auto-stopped. Just refresh the page and wait 10 seconds for it to restart.
