# SolarSense AI - DSE Team Repository

Welcome to the SolarSense AI Data Science & Engineering team repository! This is where we'll track all our model development work for the next 2-3 weeks.

---

## 📋 Table of Contents

1. [Repository Structure](#repository-structure)
2. [Getting Started](#getting-started)
3. [Daily Workflow - Beginner Method (Recommended)](#daily-workflow---beginner-method-recommended)
4. [How to Create a Pull Request](#how-to-create-a-pull-request)
5. [Rules & Best Practices](#rules--best-practices)
6. [Alternative: Colab + Git Integration](#alternative-colab--git-integration)
7. [Need Help?](#need-help)

---

## 📁 Repository Structure

```
solarsense-ai/
├── README.md                    # This file - read it first!
├── models/
│   ├── energy_consumption/      # Model 1: Evelyn & Abishag's work
│   │   ├── notebooks/           # Your Jupyter/Colab notebooks (.ipynb files)
│   │   ├── data/                # Datasets (Kaggle downloads, CSV files)
│   │   └── src/                 # Final Python scripts (.py files) - Week 2
│   ├── solar_generation/        # Model 2: Tessa & Bella's work
│   │   ├── notebooks/
│   │   ├── data/
│   │   └── src/
│   ├── roi_calculation/         # Model 3: Zainabu & Brandy's work
│   │   ├── notebooks/
│   │   ├── data/
│   │   └── src/
│   └── recommendation/          # Model 4: Bella & Abishag's work
│       ├── notebooks/
│       └── src/
├── api/                         # Flask/FastAPI code (Week 2)
└── docs/                        # API documentation
```

**What each folder is for:**

- **`notebooks/`** - Save your Jupyter/Colab notebooks here (`.ipynb` files). This is where you'll do most of your work in Week 1.
- **`data/`** - Store datasets, CSV files, or downloaded data here. Keep datasets under 100MB if possible.
- **`src/`** - Final production code (`.py` files). You'll convert your notebooks to Python scripts here at the end of Week 1.
- **`api/`** - Backend API code (Flask/FastAPI). We'll work on this in Week 2.
- **`docs/`** - API documentation and guides.

**Your work location:** You should upload your work to the folder that matches your assigned model. For example:
- Evelyn & Abishag → `models/energy_consumption/notebooks/`
- Tessa & Bella → `models/solar_generation/notebooks/`
- Zainabu & Brandy → `models/roi_calculation/notebooks/`
- Bella & Abishag (Model 4) → `models/recommendation/notebooks/`

---

## 🚀 Getting Started

### Step 1: Create a GitHub Account (If You Don't Have One)

1. Go to https://github.com/signup
2. Create your account with your email
3. Verify your email address
4. Done! ✅

### Step 2: Know Your Branch Name

**IMPORTANT:** Everyone works on their own branch. DO NOT work on the `main` branch or someone else's branch.

**Your branch names:**
- Evelyn: `evelyn-energy-consumption`
- Abishag: `abishag-data-pipeline`
- Tessa: `tessa-solar-generation`
- Bella: `bella-orchestration`
- Zainabu: `zainabu-roi-model`
- Brandy: `brandy-data-engineering`

**You will ONLY upload files to your own branch.**

---

## 📤 Daily Workflow - Beginner Method (Recommended)

This method requires NO command line or Git knowledge. You'll upload files directly through the GitHub website.

### **Step 1: Work in Colab/Kaggle/Jupyter**

- Do your work as normal in Colab, Kaggle, or local Jupyter notebook
- Save your notebook with a clear name: `energy_consumption_day1.ipynb` or `solar_generation_exploration.ipynb`

### **Step 2: Download Your Notebook**

**In Colab:**
- Click `File` → `Download` → `Download .ipynb`

**In Kaggle:**
- Click the three dots (⋮) at the top → `Download Notebook`

**In Jupyter:**
- Click `File` → `Download as` → `Notebook (.ipynb)`

Your notebook will download to your computer (usually in `Downloads` folder).

### **Step 3: Go to Your Branch on GitHub**

1. Open the repository link: [INSERT REPO LINK HERE]
2. At the top left, click the dropdown that says `main`
3. Select **YOUR branch name** from the list (e.g., `evelyn-energy-consumption`)
4. You should now see your branch name displayed where it previously said `main`

### **Step 4: Navigate to Your Folder**

Click through the folders to get to where you should upload:

**Example for Evelyn:**
1. Click `models/`
2. Click `energy_consumption/`
3. Click `notebooks/`

You're now in the right place to upload! ✅

### **Step 5: Upload Your Notebook**

1. Click the **"Add file"** button (top right)
2. Select **"Upload files"**
3. Drag your `.ipynb` file from your Downloads folder OR click "choose your files" to browse
4. Scroll down to the **"Commit changes"** section
5. In the text box, write a clear message about what you did:
   - Good: `"Day 1: Initial data exploration and XGBoost model testing"`
   - Bad: `"Update"` or `"changes"`
6. Make sure the radio button says **"Commit directly to the `[your-branch-name]` branch"**
7. Click **"Commit changes"**

Done! Your work is now saved to GitHub. ✅

### **Step 6: Verify Your Upload**

- Refresh the page
- You should see your file in the `notebooks/` folder
- Click on it to make sure it uploaded correctly

### **Step 7: Repeat Daily**

Upload your work **every day by 8:00 PM WAT**. Even if your code doesn't fully work yet, upload it. We want to track progress daily.

---

## 🔄 How to Create a Pull Request

Once your model is working and you're ready to merge your code into the main codebase:

### **Step 1: Go to the Main Repository Page**

1. Navigate to the repository home page: [INSERT REPO LINK]
2. You should see a yellow banner that says **"[Your branch] had recent pushes"** with a green **"Compare & pull request"** button
3. Click **"Compare & pull request"**

**If you don't see the banner:**
1. Click the **"Pull requests"** tab at the top
2. Click the green **"New pull request"** button
3. Set **base:** to `dev` and **compare:** to your branch name
4. Click **"Create pull request"**

### **Step 2: Fill Out the Pull Request Form**

1. **Title:** Write a clear title (e.g., "Energy Consumption Model - Ready for Integration")
2. **Description:** Explain what you built:
   ```
   ## What I Built
   - Energy consumption estimation model using XGBoost
   - Trained on Kaggle commercial building dataset
   - API endpoint returns kWh estimates
   
   ## Testing Done
   - Tested with 5 different SME profiles
   - Accuracy: 85% on validation set
   
   ## Ready for Review
   @[your-partner-name] please review before merging
   ```
3. Click **"Create pull request"**

### **Step 3: Code Review (Pair Reviews Partner's Code)**

**If you're the reviewer:**
1. Click on the **"Files changed"** tab
2. Review your partner's code
3. If everything looks good, click **"Review changes"** → **"Approve"** → **"Submit review"**
4. If you have questions, leave comments on specific lines

**If you're waiting for review:**
1. Wait for your partner to approve
2. Once approved, you can merge (but check with Tessa first)

### **Step 4: Merging (WAIT FOR TESSA'S APPROVAL)**

**Do NOT merge to `main` on your own.** After your partner approves:
1. Notify Tessa in the team channel: "Model X PR ready for final review"
2. Tessa will review and approve merge to `dev` branch
3. At end of Week 1, Tessa will merge all working models from `dev` to `main`

---

## ⚠️ Rules & Best Practices

### **DO:**

✅ **Upload your work daily by 8:00 PM WAT** - This is mandatory. Even if your code is broken or incomplete, upload it. We need to track progress.

✅ **Work ONLY on your own branch** - Never upload to someone else's branch or the `main` branch.

✅ **Write clear commit messages** - Explain what you did: "Day 2: Built feature engineering pipeline" not "updates"

✅ **Save notebooks in the `notebooks/` folder** - Keep your work organized in the right location.

✅ **Convert to `.py` files at the end of Week 1** - Once your notebook is working, export the code as a Python script and save it in `src/`

✅ **Ask for help if stuck** - GitHub is widely used, so AI assistants (ChatGPT, Claude) can help you troubleshoot. Just describe what you're trying to do and paste any error messages.

### **DON'T:**

❌ **Don't commit to the `main` branch** - Always work on your own branch

❌ **Don't work on someone else's branch** - You might overwrite their work

❌ **Don't upload files larger than 100MB** - GitHub has file size limits. For large datasets, share via Google Drive and add a link in a text file.

❌ **Don't forget to upload for multiple days** - Daily uploads keep everyone aligned and make it easier to track progress

❌ **Don't merge Pull Requests without review** - Your partner must review your code, and Tessa must approve before merging

---

## 💼 Workflow Summary

**Week 1: Notebook Development**

```
Day-to-day:
1. Work in Colab/Kaggle/Jupyter
2. Download your notebook
3. Upload to GitHub (your branch, correct folder)
4. Write clear commit message
5. Upload by 8:00 PM WAT
6. Post daily update in team channel
```

**End of Week 1: Code Conversion**

```
When model is working:
1. Export notebook code to .py file
2. Upload .py file to src/ folder
3. Create Pull Request
4. Partner reviews your code
5. Wait for Tessa's approval
6. Tessa merges to dev branch
```

**Week 2: Integration**

```
All models merged:
1. Work with Sarah (Backend) to integrate API
2. Test end-to-end
3. Final deployment
```

---

## 🔧 Alternative: Colab + Git Integration

**For those comfortable with Git commands:** You can commit directly from Google Colab instead of manually downloading and uploading.

### **One-Time Setup:**

```python
# Run this in your first Colab cell

# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Navigate to your project folder (create this folder in your Drive first)
%cd /content/drive/MyDrive/SolarSense-DSE

# Clone the repository (first time only)
!git clone https://github.com/[YOUR-ORG]/solarsense-ai.git
%cd solarsense-ai

# Set your Git identity (replace with your info)
!git config user.email "your-email@example.com"
!git config user.name "Your Name"

# Switch to your branch
!git checkout [your-branch-name]
# Example: !git checkout evelyn-energy-consumption
```

### **Daily Workflow in Colab:**

```python
# At the start of your session:

# Pull latest changes
!git pull origin [your-branch-name]

# Work on your notebook...

# At the end of your session (before 8 PM WAT):

# Add your changes
!git add .

# Commit with a message
!git commit -m "Day 2: Built feature engineering pipeline"

# Push to your branch
!git push origin [your-branch-name]
```

**Note:** You'll need to authenticate with GitHub. The first time you push, Colab will ask for your GitHub username and a Personal Access Token (PAT). GitHub has guides on creating a PAT.

---

## 🆘 Need Help?

### **GitHub Troubleshooting:**

GitHub is one of the most widely used tools in tech, which means AI assistants are very good at helping with it. If you're stuck:

1. **Ask ChatGPT or Claude:**
   - "How do I upload a file to a specific branch on GitHub?"
   - "I'm getting an error when trying to commit: [paste error]. How do I fix it?"
   - "How do I find my branch on GitHub?"

2. **Search GitHub Docs:** https://docs.github.com/

3. **Ask in the Team Channel:** Post your question with a screenshot if possible

4. **DM Tessa:** For urgent issues or if you're completely stuck

### **Common Issues:**

**"I can't find my branch"**
- Make sure you're clicking the branch dropdown at the top left of the page
- Your branch should be in the list. If not, ask Tessa to create it.

**"My file didn't upload"**
- Check that you selected the right branch before uploading
- Check that you clicked "Commit changes" at the bottom
- Refresh the page to see if it appears

**"I accidentally uploaded to the wrong branch"**
- Don't panic! Just delete the file from the wrong branch and re-upload to the correct one
- Or ask Tessa for help

---

## 📌 Note for Experienced Users

**If you're already familiar with Git or have your own preferred workflows** (e.g., using Git CLI, GitHub Desktop, VS Code integration, etc.), feel free to use those methods instead. The important things are:

1. You work on your own branch
2. You commit daily by 8:00 PM WAT
3. You keep files organized in the correct folders
4. You create Pull Requests before merging

**Just make sure your workflow doesn't clash with the team's** - if you're using advanced Git features (rebasing, force pushing, etc.), check with Tessa first to avoid conflicts.

---

## 🎯 Quick Reference

**Daily Deadline:** Upload by 8:00 PM WAT  
**Your Branch:** [Check list above - use ONLY your branch]  
**Upload Location:** `models/[your-model]/notebooks/`  
**Commit Message Format:** "Day X: [what you did]"  
**Pull Request:** Only when model is working + partner has reviewed  

---

**Questions? Ask in the DSE team channel or DM Tessa**

Let's build something great! 
