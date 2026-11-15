# -*- coding: utf-8 -*-
"""
core/apify_pool.py - Bộ Quản lý Pool API Key Đa Tài khoản Apify & Tự động Xoay Key (Smart Key Rotation)
Dành cho Hệ thống Cảnh báo Ngập lụt Đa nền tảng SE363.

Đặc tính kỹ thuật:
1. Hỗ trợ gộp nhiều tài khoản Apify Free ($5.00 USD/tháng/tài khoản).
2. Tự động kiểm tra hạn mức qua Apify REST API (/v2/users/me/limits) mà không cần đăng nhập thủ công.
3. Chế độ kép (Dual Mode):
   - AUTO-ROTATE: Tự động xoay sang tài khoản có số dư khả dụng cao nhất hoặc khi tài khoản hiện tại hết hạn mức.
   - MANUAL PIN: Cho phép Admin chọn cố định một tài khoản cụ thể để cào.
4. Auto-Failover: Tự động bắt lỗi HTTP 402 (Payment Required / Hết $5) hoặc 429 khi đang cào để đổi key tức thì.
5. Thread-safe, bảo mật (file token được đưa vào .gitignore), có cơ chế Fallback an toàn về APIFY_TOKEN gốc.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import threading
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.config import APIFY_TOKEN

POOL_FILE = os.path.join(ROOT_DIR, "data", "apify_token_pool.json")
_LOCK = threading.RLock()


def mask_token(token: str) -> str:
    """Ẩn bớt ký tự nhạy cảm của API Token để hiển thị an toàn trên giao diện."""
    if not token or not isinstance(token, str):
        return ""
    token = token.strip()
    if len(token) <= 12:
        return token[:3] + "..." + token[-2:]
    return f"{token[:12]}...{token[-4:]}"


def query_apify_token_info(token: str, timeout_sec: float = 3.5) -> Dict[str, Any]:
    """
    Truy vấn trực tiếp số dư và thông tin người dùng từ Apify Cloud REST API.
    Endpoints:
      - GET https://api.apify.com/v2/users/me (Lấy tên, email, gói cước)
      - GET https://api.apify.com/v2/users/me/limits (Lấy hạn mức $ và số tiền đã tiêu)
    """
    token = token.strip()
    if not token:
        return {
            "status": "INVALID",
            "error": "Token rỗng",
            "monthly_usage_usd": 0.0,
            "monthly_limit_usd": 5.0,
            "remaining_usd": 0.0,
            "usage_percent": 100.0,
            "last_checked_iso": datetime.now(timezone.utc).isoformat()
        }

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "SE363-UrbanFloodMonitor/1.0"
    }

    user_info = {}
    limits_info = {}
    status = "ACTIVE"
    error_msg = ""

    # 1. Gọi /v2/users/me
    try:
        req_me = urllib.request.Request("https://api.apify.com/v2/users/me", headers=headers)
        with urllib.request.urlopen(req_me, timeout=timeout_sec) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            user_info = data.get("data", {})
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return {
                "status": "INVALID",
                "error": "Token không hợp lệ hoặc đã bị thu hồi (HTTP 401)",
                "monthly_usage_usd": 0.0,
                "monthly_limit_usd": 5.0,
                "remaining_usd": 0.0,
                "usage_percent": 100.0,
                "last_checked_iso": datetime.now(timezone.utc).isoformat()
            }
        error_msg = f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        error_msg = str(e)

    # 2. Gọi /v2/users/me/limits
    try:
        req_limits = urllib.request.Request("https://api.apify.com/v2/users/me/limits", headers=headers)
        with urllib.request.urlopen(req_limits, timeout=timeout_sec) as resp:
            data_limits = json.loads(resp.read().decode("utf-8"))
            limits_info = data_limits.get("data", {})
    except urllib.error.HTTPError as e:
        if e.code == 401:
            status = "INVALID"
            error_msg = "Token không hợp lệ (HTTP 401)"
        elif e.code == 402:
            status = "EXHAUSTED"
            error_msg = "Hết hạn mức chi tiêu (HTTP 402 Quota Exceeded)"
        else:
            error_msg = f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        if not error_msg:
            error_msg = str(e)

    # Bóc tách hạn mức
    limits = limits_info.get("limits") or {}
    current = limits_info.get("current") or {}
    cycle = limits_info.get("cycle") or {}

    max_monthly_usd = float(limits.get("maxMonthlyUsageUsd") or 5.0)
    current_monthly_usd = float(current.get("monthlyUsageUsd") or 0.0)
    remaining_usd = max(0.0, round(max_monthly_usd - current_monthly_usd, 3))
    usage_percent = round((current_monthly_usd / max_monthly_usd * 100), 1) if max_monthly_usd > 0 else 0.0

    if status == "ACTIVE":
        if remaining_usd <= 0.05 or usage_percent >= 99.0:
            status = "EXHAUSTED"
            error_msg = "Đã dùng hết 100% hạn mức $5/tháng"

    username = user_info.get("username") or user_info.get("name") or "Apify User"
    email = user_info.get("email") or ""
    plan = user_info.get("plan") or {}
    plan_name = plan.get("id") or "FREE"

    return {
        "status": status,
        "username": username,
        "email": email,
        "plan": str(plan_name).upper(),
        "monthly_usage_usd": round(current_monthly_usd, 3),
        "monthly_limit_usd": round(max_monthly_usd, 2),
        "remaining_usd": remaining_usd,
        "usage_percent": usage_percent,
        "cycle_end": cycle.get("endAt"),
        "error": error_msg,
        "last_checked_iso": datetime.now(timezone.utc).isoformat()
    }


class ApifyPoolManager:
    """Bộ điều phối Pool Token Apify Singleton hỗ trợ Auto-Rotate và Manual-Pin."""

    _instance: Optional['ApifyPoolManager'] = None

    def __init__(self):
        self.mode: str = "auto"  # 'auto' hoac 'manual'
        self.active_token: Optional[str] = None
        self.tokens: List[Dict[str, Any]] = []
        self._load_pool()

    @classmethod
    def get_instance(cls) -> 'ApifyPoolManager':
        if cls._instance is None:
            with _LOCK:
                if cls._instance is None:
                    cls._instance = ApifyPoolManager()
        return cls._instance

    def _load_pool(self):
        """Nạp danh sách token từ file đệm cục bộ an toàn."""
        with _LOCK:
            if os.path.exists(POOL_FILE):
                try:
                    with open(POOL_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.mode = data.get("mode", "auto")
                        self.active_token = data.get("active_token")
                        self.tokens = data.get("tokens", [])
                except Exception as e:
                    print(f"[ApifyPool] Lỗi đọc file pool {POOL_FILE}: {e}")
                    self.tokens = []

            # Nếu pool rỗng, tự động khởi tạo với APIFY_TOKEN mặc định từ config
            if not self.tokens and APIFY_TOKEN:
                clean_tok = APIFY_TOKEN.strip()
                if clean_tok:
                    self.tokens = [{
                        "token": clean_tok,
                        "label": "Tài khoản mặc định (core/config.py)",
                        "username": "Default Apify",
                        "email": "",
                        "plan": "FREE",
                        "monthly_usage_usd": 0.0,
                        "monthly_limit_usd": 5.0,
                        "remaining_usd": 5.0,
                        "usage_percent": 0.0,
                        "status": "UNCHECKED",
                        "error": "",
                        "last_checked_iso": datetime.now(timezone.utc).isoformat()
                    }]
                    self.active_token = clean_tok
                    self._save_pool()

    def _save_pool(self):
        """Ghi đè danh sách an toàn qua file tạm để chống race-condition."""
        with _LOCK:
            try:
                os.makedirs(os.path.dirname(POOL_FILE), exist_ok=True)
                tmp_file = f"{POOL_FILE}.tmp"
                payload = {
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "mode": self.mode,
                    "active_token": self.active_token,
                    "tokens": self.tokens
                }
                with open(tmp_file, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                os.replace(tmp_file, POOL_FILE)
            except Exception as e:
                print(f"[ApifyPool] Lỗi ghi file pool {POOL_FILE}: {e}")

    def get_active_token(self) -> str:
        """
        Lấy Token đang kích hoạt để thực hiện cào dữ liệu.
        - Chế độ Manual: Dùng key do Admin chỉ định.
        - Chế độ Auto: Tự động chọn key ACTIVE có số dư cao nhất.
        - Fallback: Trả về APIFY_TOKEN gốc nếu pool không có key nào khả dụng.
        """
        with _LOCK:
            if not self.tokens:
                return APIFY_TOKEN

            # 1. Chế độ Thủ công (Manual Pin)
            if self.mode == "manual" and self.active_token:
                for acc in self.tokens:
                    if acc.get("token") == self.active_token:
                        if acc.get("status") != "EXHAUSTED":
                            return self.active_token
                        else:
                            print(f"[ApifyPool] Key thủ công ({mask_token(self.active_token)}) đã hết hạn ngạch. Tạm thời xoay tự động...")
                            break

            # 2. Chế độ Tự động (Auto-Rotate)
            active_candidates = [
                acc for acc in self.tokens
                if acc.get("status") in ["ACTIVE", "UNCHECKED"]
            ]

            if active_candidates:
                # Ưu tiên tài khoản còn nhiều tiền nhất (remaining_usd cao nhất)
                best_acc = max(active_candidates, key=lambda x: x.get("remaining_usd", 0.0))
                best_tok = best_acc.get("token")
                if self.active_token != best_tok:
                    self.active_token = best_tok
                    self._save_pool()
                return best_tok

            # 3. Nếu toàn bộ đều EXHAUSTED hoặc INVALID, dùng fallback đầu tiên
            if self.active_token:
                return self.active_token
            return APIFY_TOKEN

    def rotate_next(self, reason: str = "manual") -> Tuple[Optional[str], str]:
        """Xoay sang Token kế tiếp trong pool (vòng tròn)."""
        with _LOCK:
            if len(self.tokens) <= 1:
                return self.active_token, "Pool chỉ có 1 token hoặc rỗng, không thể xoay."

            current_idx = -1
            for idx, acc in enumerate(self.tokens):
                if acc.get("token") == self.active_token:
                    current_idx = idx
                    break

            # Tìm token ACTIVE kế tiếp
            n = len(self.tokens)
            next_acc = None
            for step in range(1, n + 1):
                cand = self.tokens[(current_idx + step) % n]
                if cand.get("status") in ["ACTIVE", "UNCHECKED"]:
                    next_acc = cand
                    break

            if not next_acc:
                # Nếu không có active nào, xoay đại sang tài khoản kế tiếp
                next_acc = self.tokens[(current_idx + 1) % n]

            old_masked = mask_token(self.active_token or "")
            self.active_token = next_acc.get("token")
            self._save_pool()
            new_masked = mask_token(self.active_token)

            msg = f"Đã xoay Token ({reason}): {old_masked} -> {new_masked} ({next_acc.get('label') or next_acc.get('username')})"
            print(f"[ApifyPool] {msg}")
            return self.active_token, msg

    def set_manual_active(self, token: str) -> bool:
        """Admin chỉ định thủ công một Key cụ thể làm Key kích hoạt."""
        with _LOCK:
            token = token.strip()
            found = False
            for acc in self.tokens:
                if acc.get("token") == token:
                    found = True
                    break
            if not found:
                return False

            self.mode = "manual"
            self.active_token = token
            self._save_pool()
            print(f"[ApifyPool] Admin đã ghim thủ công Token: {mask_token(token)}")
            return True

    def set_mode(self, mode: str) -> bool:
        """Đổi chế độ hoạt động: 'auto' hoặc 'manual'."""
        with _LOCK:
            if mode not in ["auto", "manual"]:
                return False
            self.mode = mode
            if mode == "auto":
                # Lập tức chọn lại token tốt nhất
                self.get_active_token()
            self._save_pool()
            print(f"[ApifyPool] Chuyển chế độ hoạt động sang: {mode.upper()}")
            return True

    def mark_exhausted(self, token: str, reason: str = "Hết hạn mức $5 (HTTP 402)"):
        """Đánh dấu một token bị cạn hạn mức trong lúc cào và lập tức xoay key kế tiếp."""
        with _LOCK:
            token = token.strip()
            for acc in self.tokens:
                if acc.get("token") == token:
                    acc["status"] = "EXHAUSTED"
                    acc["remaining_usd"] = 0.0
                    acc["usage_percent"] = 100.0
                    acc["error"] = reason
                    acc["last_checked_iso"] = datetime.now(timezone.utc).isoformat()
                    break

            print(f"[ApifyPool] ⚠️ Token {mask_token(token)} đã bị đánh dấu EXHAUSTED ({reason})!")
            self.rotate_next(reason=f"failover_{reason}")

    def add_token(self, token: str, label: Optional[str] = None, check_now: bool = True) -> Dict[str, Any]:
        """Thêm tài khoản mới vào Pool và tự động ping kiểm tra số dư."""
        with _LOCK:
            token = token.strip()
            if not token.startswith("apify_api_"):
                return {"status": "error", "message": "Token Apify phải bắt đầu bằng 'apify_api_'"}

            # Kiểm tra xem token đã có trong pool chưa
            for acc in self.tokens:
                if acc.get("token") == token:
                    if label:
                        acc["label"] = label
                    if check_now:
                        info = query_apify_token_info(token)
                        acc.update(info)
                    self._save_pool()
                    return {"status": "success", "message": "Đã cập nhật thông tin Token sẵn có trong Pool", "account": acc}

            # Tạo bản ghi mới
            acc = {
                "token": token,
                "label": label or f"Tài khoản {len(self.tokens) + 1}",
                "username": "",
                "email": "",
                "plan": "FREE",
                "monthly_usage_usd": 0.0,
                "monthly_limit_usd": 5.0,
                "remaining_usd": 5.0,
                "usage_percent": 0.0,
                "status": "UNCHECKED",
                "error": "",
                "last_checked_iso": datetime.now(timezone.utc).isoformat()
            }

            if check_now:
                info = query_apify_token_info(token)
                acc.update(info)

            self.tokens.append(acc)
            if not self.active_token or self.active_token == APIFY_TOKEN:
                self.active_token = token

            self._save_pool()
            print(f"[ApifyPool] Đã thêm thành công Token mới: {mask_token(token)} ({acc.get('label')})")
            return {"status": "success", "message": "Đã thêm thành công Token vào Pool", "account": acc}

    def remove_token(self, token: str) -> bool:
        """Xóa một Token ra khỏi Pool."""
        with _LOCK:
            token = token.strip()
            orig_len = len(self.tokens)
            self.tokens = [acc for acc in self.tokens if acc.get("token") != token]
            if len(self.tokens) == orig_len:
                return False

            if self.active_token == token:
                self.active_token = self.tokens[0]["token"] if self.tokens else None

            self._save_pool()
            print(f"[ApifyPool] Đã xóa Token: {mask_token(token)}")
            return True

    def refresh_all(self, timeout_sec: float = 3.5) -> Dict[str, Any]:
        """Ping đồng thời tất cả các Token trong pool để lấy Usage thời gian thực."""
        with _LOCK:
            tokens_to_check = [acc.get("token") for acc in self.tokens if acc.get("token")]

        if not tokens_to_check:
            return {"status": "empty", "message": "Pool hiện chưa có token nào."}

        results = {}
        with ThreadPoolExecutor(max_workers=min(len(tokens_to_check), 8)) as executor:
            futures = {
                executor.submit(query_apify_token_info, tok, timeout_sec): tok
                for tok in tokens_to_check
            }
            for fut in futures:
                tok = futures[fut]
                try:
                    results[tok] = fut.result()
                except Exception as e:
                    results[tok] = {"status": "ERROR", "error": str(e)}

        with _LOCK:
            for acc in self.tokens:
                tok = acc.get("token")
                if tok in results:
                    acc.update(results[tok])
            self._save_pool()

        return self.get_pool_status()

    def get_pool_status(self, mask_tokens: bool = True) -> Dict[str, Any]:
        """Tổng hợp thông số toàn bộ Pool phục vụ API và Dashboard."""
        with _LOCK:
            total_accounts = len(self.tokens)
            active_count = 0
            exhausted_count = 0
            invalid_count = 0
            total_limit = 0.0
            total_used = 0.0
            active_label = "Chưa kích hoạt"

            accounts_view = []
            for acc in self.tokens:
                tok = acc.get("token", "")
                is_active = (tok == self.active_token)
                st = acc.get("status", "UNCHECKED")

                if is_active:
                    active_label = acc.get("label") or acc.get("username") or mask_token(tok)

                if st == "ACTIVE":
                    active_count += 1
                elif st == "EXHAUSTED":
                    exhausted_count += 1
                elif st == "INVALID":
                    invalid_count += 1

                lim = float(acc.get("monthly_limit_usd", 5.0))
                used = float(acc.get("monthly_usage_usd", 0.0))
                total_limit += lim
                total_used += used

                item = dict(acc)
                item["is_active"] = is_active
                if mask_tokens:
                    item["masked_token"] = mask_token(tok)
                    item["token_id"] = tok[:10] + tok[-4:] if len(tok) >= 14 else tok
                    item.pop("token", None)  # Ẩn token nguyên bản khi gửi về Client
                accounts_view.append(item)

            total_remaining = max(0.0, round(total_limit - total_used, 2))
            overall_pct = round((total_used / total_limit * 100), 1) if total_limit > 0 else 0.0

            return {
                "status": "success",
                "mode": self.mode,
                "active_token_masked": mask_token(self.active_token or ""),
                "active_account_label": active_label,
                "total_accounts": total_accounts,
                "active_accounts": active_count,
                "exhausted_accounts": exhausted_count,
                "invalid_accounts": invalid_count,
                "total_quota_usd": round(total_limit, 2),
                "total_used_usd": round(total_used, 2),
                "total_remaining_usd": total_remaining,
                "overall_usage_percent": overall_pct,
                "accounts": accounts_view,
                "last_synced_iso": datetime.now(timezone.utc).isoformat()
            }
