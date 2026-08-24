# Universal Privacy & GitHub Pre-Commit Sync Script for all Raj's Projects
$ErrorActionPreference = "Continue"

$sourceRule = "c:\Users\Raj\Projects\Employee-Finder\.agents\rules\data_privacy_git_hygiene.md"
$sourceSkillDir = "c:\Users\Raj\Projects\Employee-Finder\.agents\skills\git-privacy-sanitizer"
$sourceGemini = "c:\Users\Raj\Projects\Employee-Finder\GEMINI.md"

$targetProjects = @(
    "GmailReader",
    "CareerOS",
    "3D-Sub-Agent-Tracker",
    "CareerOS-Blueprint",
    "GitHub-Auto-Update"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  UNIVERSAL DATA PRIVACY & GITHUB HYGIENE PROPAGATION" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

foreach ($proj in $targetProjects) {
    $projPath = "c:\Users\Raj\Projects\$proj"
    if (Test-Path $projPath) {
        Write-Host "`n[+] Processing Project: $proj" -ForegroundColor Green
        
        # 1. Ensure .agents directory structure
        $targetRulesDir = "$projPath\.agents\rules"
        $targetSkillDir = "$projPath\.agents\skills\git-privacy-sanitizer"
        New-Item -ItemType Directory -Force -Path $targetRulesDir | Out-Null
        New-Item -ItemType Directory -Force -Path $targetSkillDir | Out-Null
        
        # 2. Copy Rule and Skill
        Copy-Item -Force $sourceRule "$targetRulesDir\data_privacy_git_hygiene.md"
        Copy-Item -Force -Recurse "$sourceSkillDir\*" $targetSkillDir
        
        # 3. Create or Update GEMINI.md in target project
        $targetGemini = "$projPath\GEMINI.md"
        if (-not (Test-Path $targetGemini)) {
            $geminiContent = @"
# Project Rules: $proj

## Mandatory Data Privacy & GitHub Zero-PII Policy
- **Zero Real PII in Git**: Real resumes, personal phone numbers, real emails, addresses, .env, tokens, credentials.json, token.json, or personal endpoint URLs must NEVER be committed to Git or pushed to GitHub.
- **Automatic Masking & Anonymization**: All tracked sample data files must strictly use realistic mock/dummy data.
- **Local Backup Protection**: Real user data must be backed up exclusively to local_private_backup/ or private_data/ (both enforced in .gitignore).
- **Mandatory Pre-Commit Sanitization**: Follow the git-privacy-sanitizer skill before every git commit or git push.
"@
            Set-Content -Path $targetGemini -Value $geminiContent
        }

        # 4. Check .gitignore for critical privacy tokens
        $gitignorePath = "$projPath\.gitignore"
        $privacyEntries = @(
            ".env",
            "*.env",
            ".secure_config.bin",
            "credentials.json",
            "token.json",
            "local_private_backup/",
            "private_data/",
            "*.db",
            "*.pdf",
            "*.docx",
            "resumes/",
            "**/candidate_data/"
        )
        
        if (Test-Path $gitignorePath) {
            $existingGitignore = Get-Content $gitignorePath -Raw
            foreach ($entry in $privacyEntries) {
                if ($existingGitignore -notmatch [regex]::Escape($entry)) {
                    Add-Content -Path $gitignorePath -Value "`n$entry"
                }
            }
        } else {
            Set-Content -Path $gitignorePath -Value ($privacyEntries -join "`n")
        }

        # 5. If it's a Git repo with a remote, stage and commit the privacy additions
        if (Test-Path "$projPath\.git") {
            Write-Host "  -> Git repository detected. Checking remote and staging privacy rules..." -ForegroundColor Yellow
            $status = git -C $projPath status -s
            Write-Host "  Status in ${proj}:"
            Write-Host $status
            
            git -C $projPath add .agents GEMINI.md .gitignore
            $commitCheck = git -C $projPath status --porcelain
            if ($commitCheck) {
                git -C $projPath commit -m "feat(security): enforce mandatory zero-PII data privacy rules, skill, and git hygiene policy"
                $currentBranch = (git -C $projPath branch --show-current).Trim()
                if ($currentBranch) {
                    Write-Host "  -> Pushing to origin $currentBranch..." -ForegroundColor Cyan
                    git -C $projPath push origin $currentBranch
                }
            } else {
                Write-Host "  -> All privacy files already cleanly committed in $proj." -ForegroundColor Gray
            }
        }
    }
}

Write-Host "`n[✓] Universal propagation completed successfully across all projects!" -ForegroundColor Green
