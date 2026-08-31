import os
import sys
import time
import json
import shutil
import hashlib
import argparse
import threading
from datetime import datetime, timedelta
from pathlib import Path

class BackupManager:
    """
    Enterprise-grade Backup & Version Control Manager for Candidates Master Tracker.
    Implements:
      1. Pre-connection / Startup snapshots (sessions tier).
      2. Grandfather-Father-Son (GFS) Tiered Schedules:
         - Daily (1:00 PM & 6:00 PM) -> 7-day rolling retention.
         - Weekly (Saturday 6:00 PM) -> 8-week retention.
         - Monthly (1st of month at 09:00 AM) -> 12-month retention.
         - Manual / On-Demand snapshots.
      3. SHA-256 content hashing (smart deduplication).
      4. Atomic writes & thread-safe re-entrant locking.
      5. Audit logging in JSON format.
    """

    RETENTION_POLICIES = {
        'sessions': {'max_count': 30, 'max_days': None},
        'daily': {'max_count': None, 'max_days': 7},
        'weekly': {'max_count': None, 'max_days': 56}, # 8 weeks
        'monthly': {'max_count': None, 'max_days': 365}, # 12 months
        'manual': {'max_count': 25, 'max_days': None}
    }

    def __init__(self, source_file: str, backup_base_dir: str = None):
        self.source_file = Path(source_file).resolve()
        if backup_base_dir:
            self.backup_base_dir = Path(backup_base_dir).resolve()
        else:
            self.backup_base_dir = self.source_file.parent / "backups"

        self.lock = threading.RLock()
        self.log_file = self.backup_base_dir / "backup_log.json"
        self._scheduler_thread = None
        self._stop_scheduler_event = threading.Event()

        # Initialize folder hierarchy
        self._init_directories()

    def _init_directories(self):
        """Create all tier directories and ensure log file exists."""
        with self.lock:
            self.backup_base_dir.mkdir(parents=True, exist_ok=True)
            for tier in ['sessions', 'daily', 'weekly', 'monthly', 'manual']:
                (self.backup_base_dir / tier).mkdir(parents=True, exist_ok=True)

            if not self.log_file.exists():
                self._save_log([])

    def _load_log(self) -> list:
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save_log(self, entries: list):
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(entries[-300:], f, indent=2) # Retain last 300 audit entries
        except Exception as e:
            print(f"[BackupManager Log Error] {e}")

    def _calculate_hash(self, filepath: Path) -> str:
        """Calculate SHA-256 hash of a file for change detection."""
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def _prune_tier(self, tier: str):
        """Auto-prune old backup files in a given tier according to retention policy."""
        tier_dir = self.backup_base_dir / tier
        if not tier_dir.exists():
            return

        policy = self.RETENTION_POLICIES.get(tier, {})
        max_days = policy.get('max_days')
        max_count = policy.get('max_count')

        files = sorted(tier_dir.glob("*.xlsx"), key=os.path.getmtime)

        # 1. Prune by age (e.g. 7 days for daily)
        if max_days is not None:
            cutoff = datetime.now() - timedelta(days=max_days)
            for file_path in list(files):
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mtime < cutoff:
                    # Keep at least 2 files regardless of age for safety
                    if len(files) > 2:
                        try:
                            file_path.unlink()
                            files.remove(file_path)
                        except Exception:
                            pass

        # 2. Prune by max file count
        if max_count is not None and len(files) > max_count:
            excess = len(files) - max_count
            for old_file in files[:excess]:
                try:
                    old_file.unlink()
                except Exception:
                    pass

    def create_backup(self, tier: str = 'sessions', prefix: str = 'snapshot', force: bool = False) -> dict:
        """
        Create a new timestamped backup in the designated tier.
        Performs atomic file copy and SHA-256 deduplication.
        """
        if not self.source_file.exists():
            return {"status": "skipped", "reason": "Source file does not exist", "tier": tier}

        tier = tier.lower()
        if tier not in self.RETENTION_POLICIES:
            tier = 'sessions'

        with self.lock:
            current_hash = self._calculate_hash(self.source_file)
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            tier_dir = self.backup_base_dir / tier
            tier_dir.mkdir(parents=True, exist_ok=True)

            # Check if identical backup exists in this tier to prevent unnecessary duplicates
            if not force:
                recent_backups = sorted(tier_dir.glob("*.xlsx"), key=os.path.getmtime, reverse=True)
                if recent_backups:
                    last_hash = self._calculate_hash(recent_backups[0])
                    if last_hash and last_hash == current_hash:
                        # Log the skipped duplicate event
                        log_entries = self._load_log()
                        log_entries.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "tier": tier,
                            "prefix": prefix,
                            "filename": recent_backups[0].name,
                            "hash": current_hash,
                            "status": "unchanged_reused",
                            "size_bytes": recent_backups[0].stat().st_size
                        })
                        self._save_log(log_entries)
                        return {
                            "status": "unchanged",
                            "tier": tier,
                            "filename": recent_backups[0].name,
                            "filepath": str(recent_backups[0]),
                            "hash": current_hash
                        }

            # Create backup filename
            backup_filename = f"candidates_tracker_{prefix}_{timestamp_str}.xlsx"
            target_path = tier_dir / backup_filename
            temp_path = tier_dir / f"{backup_filename}.tmp"

            try:
                # Atomic copy via temp file
                shutil.copy2(self.source_file, temp_path)
                if temp_path.exists():
                    temp_path.replace(target_path)

                file_size = target_path.stat().st_size

                # Auto-prune old files in this tier
                self._prune_tier(tier)

                # Update audit log
                log_entries = self._load_log()
                log_entries.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tier": tier,
                    "prefix": prefix,
                    "filename": backup_filename,
                    "hash": current_hash,
                    "status": "created",
                    "size_bytes": file_size
                })
                self._save_log(log_entries)

                return {
                    "status": "success",
                    "tier": tier,
                    "filename": backup_filename,
                    "filepath": str(target_path),
                    "size_bytes": file_size,
                    "hash": current_hash
                }
            except Exception as e:
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except Exception:
                        pass
                return {"status": "error", "error": str(e), "tier": tier}

    def restore_backup(self, backup_relative_or_abs_path: str) -> dict:
        """
        Restore the master tracker file from a selected backup.
        Takes a safety snapshot of the current state before overwriting.
        """
        with self.lock:
            target_backup = Path(backup_relative_or_abs_path)
            if not target_backup.is_absolute():
                target_backup = (self.backup_base_dir / backup_relative_or_abs_path).resolve()

            if not target_backup.exists() or not target_backup.is_file():
                return {"status": "error", "message": f"Backup file '{target_backup}' not found."}

            try:
                # 1. Take safety pre-restore backup of current state if exists
                if self.source_file.exists():
                    self.create_backup(tier='manual', prefix='pre_restore_safety', force=True)

                # 2. Atomically copy backup over master tracker
                temp_restore = self.source_file.parent / f"{self.source_file.name}.restore.tmp"
                shutil.copy2(target_backup, temp_restore)
                temp_restore.replace(self.source_file)

                # Log restore action
                log_entries = self._load_log()
                log_entries.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tier": "restore",
                    "prefix": "restored_from",
                    "filename": target_backup.name,
                    "hash": self._calculate_hash(self.source_file),
                    "status": "restored",
                    "size_bytes": self.source_file.stat().st_size
                })
                self._save_log(log_entries)

                return {
                    "status": "success",
                    "message": f"Successfully restored from '{target_backup.name}'.",
                    "restored_file": target_backup.name
                }
            except Exception as e:
                return {"status": "error", "message": f"Restore failed: {str(e)}"}

    def get_backup_summary(self) -> dict:
        """
        Retrieve structured summary of all backup tiers, last backup dates,
        and list of recent files for the UI and monitoring API.
        """
        with self.lock:
            summary = {
                "source_file": str(self.source_file),
                "source_exists": self.source_file.exists(),
                "source_size_bytes": self.source_file.stat().st_size if self.source_file.exists() else 0,
                "source_last_modified": datetime.fromtimestamp(self.source_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S") if self.source_file.exists() else None,
                "tiers": {},
                "all_backups": []
            }

            all_files = []
            for tier in ['sessions', 'daily', 'weekly', 'monthly', 'manual']:
                tier_dir = self.backup_base_dir / tier
                tier_files = sorted(tier_dir.glob("*.xlsx"), key=os.path.getmtime, reverse=True)
                
                last_backup_time = None
                if tier_files:
                    last_backup_time = datetime.fromtimestamp(tier_files[0].stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")

                summary["tiers"][tier] = {
                    "count": len(tier_files),
                    "last_backup": last_backup_time,
                    "directory": str(tier_dir)
                }

                for f in tier_files:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    all_files.append({
                        "filename": f.name,
                        "tier": tier,
                        "relative_path": f"{tier}/{f.name}",
                        "size_bytes": f.stat().st_size,
                        "size_formatted": f"{f.stat().st_size / 1024:.1f} KB",
                        "modified_time": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                        "timestamp_raw": f.stat().st_mtime
                    })

            # Sort all files by most recent first
            all_files.sort(key=lambda x: x["timestamp_raw"], reverse=True)
            summary["all_backups"] = all_files[:60] # Top 60 most recent files
            return summary

    def check_and_run_scheduled_backups(self) -> dict:
        """
        Check current system time and execute any due scheduled backups:
          - Daily: 13:00 (1:00 PM) and 18:00 (6:00 PM)
          - Weekly: Saturday 18:00 (6:00 PM)
          - Monthly: 1st of month at 09:00 AM
        """
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        weekday = now.weekday() # Monday=0, Saturday=5, Sunday=6
        day_of_month = now.day

        results = {}

        # 1. Monthly Backup: 1st of month at 09:00 AM (checked within window 09:00 - 09:15)
        if day_of_month == 1 and hour == 9 and minute < 15:
            monthly_dir = self.backup_base_dir / "monthly"
            today_str = now.strftime("%Y%m01")
            existing_today = list(monthly_dir.glob(f"*{today_str}*.xlsx"))
            if not existing_today:
                res = self.create_backup(tier='monthly', prefix=f"monthly_{now.strftime('%Y_%m')}", force=False)
                results['monthly'] = res

        # 2. Weekly Backup: Saturday at 18:00 (6:00 PM) (checked within window 18:00 - 18:15)
        if weekday == 5 and hour == 18 and minute < 15:
            weekly_dir = self.backup_base_dir / "weekly"
            today_str = now.strftime("%Y%m%d")
            existing_today = list(weekly_dir.glob(f"*{today_str}*.xlsx"))
            if not existing_today:
                res = self.create_backup(tier='weekly', prefix=f"weekly_sat_{today_str}", force=False)
                results['weekly'] = res

        # 3. Daily Backup Slot 1: 13:00 (1:00 PM) (checked within window 13:00 - 13:15)
        if hour == 13 and minute < 15:
            daily_dir = self.backup_base_dir / "daily"
            slot_str = now.strftime("%Y%m%d_13")
            existing_slot = list(daily_dir.glob(f"*{slot_str}*.xlsx"))
            if not existing_slot:
                res = self.create_backup(tier='daily', prefix=f"daily_1300_{now.strftime('%Y%m%d')}", force=False)
                results['daily_1300'] = res

        # 4. Daily Backup Slot 2: 18:00 (6:00 PM) (checked within window 18:00 - 18:15)
        if hour == 18 and minute < 15:
            daily_dir = self.backup_base_dir / "daily"
            slot_str = now.strftime("%Y%m%d_18")
            existing_slot = list(daily_dir.glob(f"*{slot_str}*.xlsx"))
            if not existing_slot:
                res = self.create_backup(tier='daily', prefix=f"daily_1800_{now.strftime('%Y%m%d')}", force=False)
                results['daily_1800'] = res

        return results

    def start_scheduler_daemon(self, interval_seconds: int = 60):
        """Starts a background daemon thread that checks schedules every interval_seconds."""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return

        self._stop_scheduler_event.clear()

        def _worker():
            while not self._stop_scheduler_event.is_set():
                try:
                    self.check_and_run_scheduled_backups()
                except Exception as e:
                    print(f"[Backup Scheduler Worker Error] {e}")
                self._stop_scheduler_event.wait(interval_seconds)

        self._scheduler_thread = threading.Thread(target=_worker, name="BackupSchedulerDaemon", daemon=True)
        self._scheduler_thread.start()

    def stop_scheduler_daemon(self):
        """Stops the background scheduler daemon."""
        self._stop_scheduler_event.set()
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=2.0)


def main():
    """CLI Entry point for standalone manual invocation and Windows Task Scheduler."""
    parser = argparse.ArgumentParser(description="Candidate Master Tracker Backup Manager")
    parser.add_argument("--trigger", choices=['auto', 'session', 'daily', 'weekly', 'monthly', 'manual', 'status', 'restore'], default='status', help="Action or backup tier to trigger")
    parser.add_argument("--source", default=r"C:\Users\Raj\Projects\Employee-Finder\candidates_tracker.xlsx", help="Master tracker file path")
    parser.add_argument("--restore-file", default=None, help="Relative or absolute path of backup file to restore")

    args = parser.parse_args()
    mgr = BackupManager(args.source)

    if args.trigger == 'status':
        summary = mgr.get_backup_summary()
        print("\n=======================================================")
        print(" 📦 CANDIDATE TRACKER BACKUP SYSTEM STATUS")
        print("=======================================================")
        print(f"Master File: {summary['source_file']}")
        print(f"File Exists: {summary['source_exists']} ({summary['source_size_bytes']} bytes)")
        print(f"Last Modified: {summary['source_last_modified']}")
        print("\n--- BACKUP TIERS ---")
        for tier, data in summary['tiers'].items():
            print(f"• [{tier.upper()}]: {data['count']} snapshots | Last Backup: {data['last_backup'] or 'None'}")
        print(f"\nTotal Recent Snapshots: {len(summary['all_backups'])}")
        print("=======================================================\n")

    elif args.trigger == 'auto':
        print(f"[{datetime.now()}] Checking scheduled backups (Daily 1PM/6PM, Weekly Sat 6PM, Monthly 1st 9AM)...")
        res = mgr.check_and_run_scheduled_backups()
        print(f"Result: {json.dumps(res, indent=2)}")

    elif args.trigger in ['session', 'daily', 'weekly', 'monthly', 'manual']:
        prefix_map = {
            'session': 'cli_session',
            'daily': f"daily_{datetime.now().strftime('%Y%m%d_%H%M')}",
            'weekly': f"weekly_sat_{datetime.now().strftime('%Y%m%d')}",
            'monthly': f"monthly_{datetime.now().strftime('%Y_%m')}",
            'manual': 'manual_checkpoint'
        }
        res = mgr.create_backup(tier=args.trigger, prefix=prefix_map[args.trigger], force=True)
        print(f"Created [{args.trigger}] backup:")
        print(json.dumps(res, indent=2))

    elif args.trigger == 'restore':
        if not args.restore_file:
            print("Error: Please provide --restore-file <path_to_backup_file>")
            sys.exit(1)
        res = mgr.restore_backup(args.restore_file)
        print(f"Restore Result: {json.dumps(res, indent=2)}")


if __name__ == "__main__":
    main()
