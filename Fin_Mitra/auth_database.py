# auth_database.py
import sqlite3
import shutil
import os
from pathlib import Path
from datetime import datetime
import bcrypt
from typing import Tuple, Dict, Optional, List
import pandas as pd

from app_context import get_base_data_dir

DB_PATH = Path("/var/Data/App_Login_DB.db")   # 🔒 HARD-WIRED


class AuthDatabase:

    def __init__(self):
        if not DB_PATH.exists():
            raise RuntimeError(
                f"Auth DB missing at {DB_PATH}. "
                f"Create it once and redeploy."
            )

        self.db_path = str(DB_PATH)
        self.init_database()

    # --------------------------------------------------
    # CONNECTION
    # --------------------------------------------------
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # --------------------------------------------------
    # INIT TABLES (SAFE / IDEMPOTENT)
    # --------------------------------------------------
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AuditTrail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_user_id INTEGER,
                target_username TEXT,
                action TEXT,
                performed_by_user_id INTEGER,
                performed_by_username TEXT,
                new_value TEXT,
                timestamp TEXT
            )
            """)
    
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS UserDetails (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT UNIQUE NOT NULL,
                Password_Encrypted TEXT NOT NULL,
                Email TEXT UNIQUE NOT NULL,
                Role TEXT NOT NULL,
                Created_At TEXT NOT NULL,
                Updated_At TEXT NOT NULL,
                Is_Active INTEGER DEFAULT 1
            )
        """)
    
        # ✅ ADD THIS BLOCK
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS SubAdminUsers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                SubAdmin_Username TEXT NOT NULL,
                User_Username TEXT NOT NULL,
                Created_At TEXT NOT NULL,
                UNIQUE(SubAdmin_Username, User_Username)
            )
        """)
    
        conn.commit()
        conn.close()


    # --------------------------------------------------
    # PASSWORD
    # --------------------------------------------------
    def encrypt_password(self, password: str) -> str:
        return bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    # --------------------------------------------------
    # CREATE USER (DB + FILESYSTEM)
    # --------------------------------------------------
    def create_user(
        self,
        username: str,
        password: str,
        email: str,
        role: str = "User"
    ) -> Tuple[bool, str]:

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT 1 FROM UserDetails WHERE Username=? OR Email=?",
                (username, email)
            )
            if cursor.fetchone():
                return False, "Username or email already exists"

            now = datetime.now().isoformat()
            hashed = self.encrypt_password(password)

            cursor.execute("""
                INSERT INTO UserDetails
                (Username, Password_Encrypted, Email, Role,
                 Created_At, Updated_At, Is_Active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (username, hashed, email, role, now, now))

            conn.commit()

        except Exception as e:
            conn.rollback()
            return False, f"DB error: {e}"

        finally:
            conn.close()

        # --------------------------------------------------
        # FILESYSTEM PROVISIONING (AFTER DB SUCCESS)
        # --------------------------------------------------
        try:
            base_dir = get_base_data_dir()
            user_dir = os.path.join(base_dir, username)
            os.makedirs(user_dir, exist_ok=True)

            template_dir = Path(__file__).parent / "data"
            if not template_dir.is_dir():
                raise RuntimeError(f"Template dir missing: {template_dir}")

            for item in template_dir.iterdir():
                dst = Path(user_dir) / item.name
                if item.is_dir():
                    if not dst.exists():
                        shutil.copytree(item, dst)
                else:
                    if not dst.exists():
                        shutil.copy2(item, dst)

        except Exception as fs_err:
            # rollback DB user if FS fails
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM UserDetails WHERE Username=?",
                (username,)
            )
            conn.commit()
            conn.close()

            return False, f"Filesystem error: {fs_err}"

        return True, f"User '{username}' created successfully"

    # --------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------
    def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Tuple[bool, Optional[Dict], str]:

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, Username, Password_Encrypted, Email, Role
            FROM UserDetails
            WHERE Username=? AND Is_Active=1
        """, (username,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return False, None, "Invalid credentials"

        if not self.verify_password(password, row["Password_Encrypted"]):
            return False, None, "Invalid credentials"

        return True, {
            "user_id": row["user_id"],
            "username": row["Username"],
            "email": row["Email"],
            "role": row["Role"],
        }, "Login successful"

    def change_password(self, user_id: int, new_password: str) -> Tuple[bool, str]:
        conn = self.get_connection()
        cursor = conn.cursor()
    
        try:
            hashed = self.encrypt_password(new_password)
    
            cursor.execute("""
                UPDATE UserDetails
                SET Password_Encrypted=?, Updated_At=?
                WHERE user_id=?
            """, (hashed, datetime.now().isoformat(), user_id))
    
            if cursor.rowcount == 0:
                return False, "User not found"
    
            conn.commit()
            return True, "Password updated successfully"
    
        except Exception as e:
            conn.rollback()
            return False, str(e)
    
        finally:
            conn.close()

    def get_all_users(self):
        """
        Returns all users for admin / user management UI
        """
        conn = self.get_connection()
        cursor = conn.cursor()
    
        cursor.execute("""
            SELECT
                user_id AS User_ID,
                Username,
                Email,
                Role,
                Is_Active,
                Created_At
            FROM UserDetails
            ORDER BY Created_At DESC
        """)
    
        rows = cursor.fetchall()
        conn.close()
    
        # Convert sqlite rows → list of dicts
        return [dict(row) for row in rows]

    def log_audit_trail(
        self,
        target_user_id,
        target_username,
        action,
        performed_by_user_id,
        performed_by_username,
        new_value=None
    ):
        conn = self.get_connection()
        cursor = conn.cursor()
    
        cursor.execute("""
            INSERT INTO AuditTrail
            (
                target_user_id,
                target_username,
                action,
                performed_by_user_id,
                performed_by_username,
                new_value,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            target_user_id,
            target_username,
            action,
            performed_by_user_id,
            performed_by_username,
            new_value,
            datetime.now().isoformat()
        ))
    
        conn.commit()
        conn.close()

    # --------------------------------------------------
    # UPDATE USER
    # --------------------------------------------------
    def update_user(self, user_id: int, **fields):
        """
        Generic user update function
        Example:
        update_user(5, Is_Active=0)
        """
        if not fields:
            return False, "No fields to update"
    
        conn = self.get_connection()
        cursor = conn.cursor()
    
        try:
            updates = []
            values = []
    
            for k, v in fields.items():
                updates.append(f"{k}=?")
                values.append(v)
    
            values.append(user_id)
    
            sql = f"""
            UPDATE UserDetails
            SET {', '.join(updates)},
                Updated_At=?
            WHERE user_id=?
            """
    
            values.insert(-1, datetime.now().isoformat())
    
            cursor.execute(sql, values)
    
            conn.commit()
            return True, "User updated"
    
        except Exception as e:
            conn.rollback()
            return False, str(e)
    
        finally:
            conn.close()

    def get_user_by_username(self, username: str):
        conn = self.get_connection()
        cursor = conn.cursor()
    
        cursor.execute("""
            SELECT user_id, Username, Email, Role, Is_Active
            FROM UserDetails
            WHERE Username=?
        """, (username,))
    
        row = cursor.fetchone()
        conn.close()
    
        return dict(row) if row else None

    # --------------------------------------------------
    # ADMIN / SUBADMIN MANAGEMENT
    # --------------------------------------------------
    def attach_user_to_subadmin(
        self,
        subadmin_username: str,
        user_username: str
    ) -> Tuple[bool, str]:

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR IGNORE INTO SubAdminUsers
                (SubAdmin_Username, User_Username, Created_At)
                VALUES (?, ?, ?)
            """, (subadmin_username, user_username, datetime.now().isoformat()))

            conn.commit()
            return True, "User attached to Sub-Admin"

        except Exception as e:
            conn.rollback()
            return False, str(e)

        finally:
            conn.close()

    def get_users_for_subadmin(self, subadmin_username: str) -> List[str]:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT User_Username
            FROM SubAdminUsers
            WHERE SubAdmin_Username=?
        """, (subadmin_username,))

        users = [r["User_Username"] for r in cursor.fetchall()]
        conn.close()
        return users

    # --------------------------------------------------
    # FILE ACCESS CONTROL
    # --------------------------------------------------
    def get_accessible_master_ledgers(self, session: Dict) -> List[str]:
        """
        Returns paths to master_ledger.csv files the user can READ
        """
        base_dir = get_base_data_dir()
        role = session["role"]
        username = session["username"]

        if role == "Admin":
            return [
                os.path.join(base_dir, u, "master_ledger.csv")
                for u in os.listdir(base_dir)
                if os.path.exists(os.path.join(base_dir, u, "master_ledger.csv"))
            ]

        if role == "SubAdmin":
            users = self.get_users_for_subadmin(username)
            return [
                os.path.join(base_dir, u, "master_ledger.csv")
                for u in users
                if os.path.exists(os.path.join(base_dir, u, "master_ledger.csv"))
            ]

        # Normal User
        path = os.path.join(base_dir, username, "master_ledger.csv")
        return [path] if os.path.exists(path) else []

    # --------------------------------------------------
    # CONSOLIDATION
    # --------------------------------------------------
    def consolidate_master_ledgers(self, session: Dict) -> pd.DataFrame:
        """
        Admin / SubAdmin only
        """
        paths = self.get_accessible_master_ledgers(session)
        dfs = []

        for p in paths:
            df = pd.read_csv(p)
            df["Source_User"] = Path(p).parent.name
            dfs.append(df)

        if not dfs:
            return pd.DataFrame()

        return pd.concat(dfs, ignore_index=True)

    def get_users_by_role(self, role: str) -> List[str]:
        conn = self.get_connection()
        cursor = conn.cursor()
    
        cursor.execute("""
            SELECT Username
            FROM UserDetails
            WHERE Role=? AND Is_Active=1
        """, (role,))
    
        users = [r["Username"] for r in cursor.fetchall()]
        conn.close()
        return users


    def consolidate_and_write_for_subadmin(self, session: Dict) -> Tuple[bool, str]:
        """
        Creates consolidated:
        - master_ledger.csv
        - journal_book.csv
        - Mapper.xlsx (deduplicated)
        inside /var/Data/<subadmin>/
        """
    
        if session["role"] not in ("Admin", "SubAdmin"):
            return False, "Permission denied"
    
        base_dir = get_base_data_dir()
        subadmin = session["username"]
    
        users = (
            self.get_users_for_subadmin(subadmin)
            if session["role"] == "SubAdmin"
            else [
                u for u in os.listdir(base_dir)
                if os.path.isdir(os.path.join(base_dir, u))
            ]
        )
    
        ml_frames = []
        jb_frames = []
        mapper_frames = []
    
        # --------------------------------------------------
        # COLLECT DATA FROM USERS
        # --------------------------------------------------
        for u in users:
            u_dir = os.path.join(base_dir, u)
    
            ml = os.path.join(u_dir, "master_ledger.csv")
            jb = os.path.join(u_dir, "journal_book.csv")
            mp = os.path.join(u_dir, "Mapper.xlsx")
    
            if os.path.exists(ml):
                df = pd.read_csv(ml)
                df["Source_User"] = u
                ml_frames.append(df)
    
            if os.path.exists(jb):
                df = pd.read_csv(jb)
                df["Source_User"] = u
                jb_frames.append(df)
    
            if os.path.exists(mp):
                df = pd.read_excel(mp)
                df["Source_User"] = u
                mapper_frames.append(df)
    
        if not ml_frames and not jb_frames and not mapper_frames:
            return False, "No ledgers or mappers found to consolidate"
    
        out_dir = os.path.join(base_dir, subadmin)
        os.makedirs(out_dir, exist_ok=True)
    
        # --------------------------------------------------
        # WRITE MASTER LEDGER
        # --------------------------------------------------
        # if ml_frames:
        #     pd.concat(ml_frames, ignore_index=True).to_csv(
        #         os.path.join(out_dir, "master_ledger.csv"),
        #         index=False
        #     )

        if ml_frames:
            consolidated_df = pd.concat(ml_frames, ignore_index=True)
        
            if not consolidated_df.empty:
        
                master_path = os.path.join(out_dir, "master_ledger.csv")
        
                # If file exists, load existing data
                if os.path.exists(master_path):
                    existing_df = pd.read_csv(master_path)
        
                    # Combine existing + new
                    combined_df = pd.concat(
                        [existing_df, consolidated_df],
                        ignore_index=True
                    )
        
                    # Remove full-row duplicates
                    combined_df = combined_df.drop_duplicates(keep="first")
        
                    combined_df.to_csv(master_path, index=False)
        
                else:
                    # First time write
                    consolidated_df = consolidated_df.drop_duplicates(keep="first")
                    consolidated_df.to_csv(master_path, index=False)

    
        # --------------------------------------------------
        # WRITE JOURNAL BOOK
        # --------------------------------------------------
        # if jb_frames:
        #     pd.concat(jb_frames, ignore_index=True).to_csv(
        #         os.path.join(out_dir, "journal_book.csv"),
        #         index=False
        #     )

        if jb_frames:
            consolidated_jb = pd.concat(jb_frames, ignore_index=True)
        
            if not consolidated_jb.empty:
        
                journal_path = os.path.join(out_dir, "journal_book.csv")
        
                if os.path.exists(journal_path):
                    existing_jb = pd.read_csv(journal_path)
        
                    combined_jb = pd.concat(
                        [existing_jb, consolidated_jb],
                        ignore_index=True
                    )
        
                    combined_jb = combined_jb.drop_duplicates(keep="first")
        
                    combined_jb.to_csv(journal_path, index=False)
        
                else:
                    consolidated_jb = consolidated_jb.drop_duplicates(keep="first")
                    consolidated_jb.to_csv(journal_path, index=False)
    
        # --------------------------------------------------
        # WRITE DEDUPLICATED MAPPER
        # --------------------------------------------------
        if mapper_frames:
            mapper_df = pd.concat(mapper_frames, ignore_index=True)
    
            # 🔑 DEFINE BUSINESS KEYS FOR DEDUPLICATION
            DEDUPE_KEYS = [
                "LINE_ITEM",
                "GROUP",
                "FS_Group"
            ]
    
            existing_keys = [c for c in DEDUPE_KEYS if c in mapper_df.columns]
    
            if existing_keys:
                mapper_df = mapper_df.drop_duplicates(
                    subset=existing_keys,
                    keep="first"
                )
            else:
                # fallback: full-row dedupe
                mapper_df = mapper_df.drop_duplicates()
    
            mapper_df.to_excel(
                os.path.join(out_dir, "Mapper.xlsx"),
                index=False
            )
    
        # --------------------------------------------------
        # MARK GENERATED WORKSPACE
        # --------------------------------------------------
        with open(os.path.join(out_dir, ".generated.flag"), "w") as f:
            f.write(datetime.now().isoformat())
    
        return True, "Consolidated ledgers & mapper generated"





# --------------------------------------------------
# SINGLETON
# --------------------------------------------------
_db = None

def get_auth_db():
    global _db
    if _db is None:
        _db = AuthDatabase()
    return _db








