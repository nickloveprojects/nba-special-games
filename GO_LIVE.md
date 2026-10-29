# Put the site online (about 10 minutes, no coding)

You will end up with a free website like `https://YOUR-NAME.github.io/nba-special-games/` that updates itself every morning.

## 1. Make a free GitHub account
Go to github.com and sign up. Skip this if you already have one.

## 2. Create an empty project
1. Click the **+** at the top right, then **New repository**.
2. Name it `nba-special-games`.
3. Choose **Public** (free sites need a public project).
4. Do not tick any boxes. Click **Create repository**.

## 3. Upload the files
1. Unzip `nba-special-games.zip` on your computer.
2. On Mac, press **Cmd + Shift + .** in the unzipped folder so hidden folders show. On Windows, open the View menu and tick **Hidden items**.
3. On your new GitHub page, click **uploading an existing file**.
4. Open the unzipped folder, select everything inside it (not the folder itself), and drag it into the GitHub page.
5. Wait for the upload to finish, then click **Commit changes**.

## 4. Check the daily-update file made it
In your project, look for a folder named `.github`. If you do not see it:
1. Click **Add file**, then **Create new file**.
2. In the name box, type exactly `.github/workflows/daily.yml`
3. Open `deploy/daily.yml` from your project, copy everything in it, and paste it into the big box.
4. Click **Commit changes**.

## 5. Turn on the website
1. Click **Settings**, then **Pages** in the left menu.
2. Under **Source**, choose **GitHub Actions**.

## 6. Run the first update
1. Click the **Actions** tab. If asked, click the green button to enable workflows.
2. Click **Update site every morning** on the left, then **Run workflow**, then the green **Run workflow** button.
3. Wait a few minutes until the run shows a green check.
4. Go back to **Settings**, then **Pages**. Your website address is shown at the top.

After that it refreshes by itself every morning. To refresh sooner, repeat step 6.

## Optional: phone or Discord alerts
In **Settings**, then **Secrets and variables**, then **Actions**, add `DISCORD_WEBHOOK_URL` (or `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`). The morning list is then sent to you automatically.

## If something looks wrong
- A red X on the Actions run: open it, copy the error text, and send it to me.
- The site shows an old day: the data providers may have been down. Run the workflow again later.

## Edit the website by chatting with Claude
1. In Claude, open **Settings, then Connectors**, and connect **GitHub**. Give it access to the `nba-special-games` project.
2. Start a new Claude Code chat on the web, choose your `nba-special-games` project, and ask for changes in plain words ("make the History box green", "add this rivalry"). Claude edits the files and saves them to GitHub.
3. Saving to GitHub republishes the site automatically (a minute or two).
Rivalries and hometown fixes live in `config/rivalries.yaml` and `config/overrides.yaml`, so you can also just ask Claude to add a line there.
