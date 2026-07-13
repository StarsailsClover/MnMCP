#!/usr/bin/env python3
"""
MnMCP 控制面板 v2
现代化GUI - 基于 customtkinter

三种用户角色:
  1. 玩家 (Player)   — 连接到已有房间，最简单
  2. 房主 (Host)      — 创建房间让别人加入
  3. 服务器 (Server)  — 部署中继服务器

版本: v0.3.1_26w09b_Phase 7
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import subprocess
import time
import json
import sys
import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent


def _find_python() -> str:
    """Find a Python interpreter that has the required packages."""
    # 1) The Python that is running this GUI already works
    current = sys.executable
    # 2) But if it was launched via a wrapper (StepFun embeds a stripped
    #    Python), the child process may lack packages.  Prefer the full
    #    Python314 install when available.
    candidates = [
        Path(r"C:\Users\Sails\AppData\Local\Programs\Python\Python314\python.exe"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return current


PYTHON_EXE = _find_python()

# ── 主题 ─────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 品牌色
C_BG        = "#0F0F17"
C_CARD      = "#1A1A2E"
C_CARD_HI   = "#222240"
C_BORDER    = "#2A2A4A"
C_ACCENT    = "#6C63FF"
C_ACCENT_HI = "#8B83FF"
C_GREEN     = "#4ADE80"
C_RED       = "#F87171"
C_YELLOW    = "#FBBF24"
C_TEXT      = "#E2E8F0"
C_TEXT_DIM  = "#64748B"
C_INPUT_BG  = "#16162A"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_H2     = ("Segoe UI", 15, "bold")
FONT_H3     = ("Segoe UI", 12, "bold")
FONT_BODY   = ("Segoe UI", 12)
FONT_SMALL  = ("Segoe UI", 10)
FONT_MONO   = ("Cascadia Code", 10)


# ═══════════════════════════════════════════════════════════
#  可复用组件
# ═══════════════════════════════════════════════════════════

class StatusDot(ctk.CTkFrame):
    """状态指示灯"""
    def __init__(self, master, size=10, color=C_RED, **kw):
        super().__init__(master, width=size, height=size,
                         corner_radius=size//2, fg_color=color, **kw)
        self._color = color
    def set(self, color):
        self._color = color
        self.configure(fg_color=color)


class StatCard(ctk.CTkFrame):
    """统计卡片"""
    def __init__(self, master, title, value="0", accent=C_ACCENT, **kw):
        super().__init__(master, fg_color=C_CARD, corner_radius=12,
                         border_width=1, border_color=C_BORDER, **kw)
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=title, font=FONT_SMALL,
                     text_color=C_TEXT_DIM).grid(row=0, padx=14, pady=(12,0), sticky="w")
        self._val = ctk.CTkLabel(self, text=value, font=("Segoe UI", 28, "bold"),
                                 text_color=accent)
        self._val.grid(row=1, padx=14, pady=(0,12), sticky="w")
    def set(self, v):
        self._val.configure(text=str(v))


class LogConsole(ctk.CTkFrame):
    """日志控制台"""
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=C_CARD, corner_radius=12,
                         border_width=1, border_color=C_BORDER, **kw)
        # 工具栏
        bar = ctk.CTkFrame(self, fg_color="transparent", height=36)
        bar.pack(fill="x", padx=12, pady=(10,0))
        ctk.CTkLabel(bar, text="日志", font=FONT_H3,
                     text_color=C_TEXT).pack(side="left")
        ctk.CTkButton(bar, text="清空", width=56, height=28,
                      fg_color=C_CARD_HI, hover_color=C_BORDER,
                      font=FONT_SMALL, command=self.clear).pack(side="right", padx=4)
        ctk.CTkButton(bar, text="导出", width=56, height=28,
                      fg_color=C_CARD_HI, hover_color=C_BORDER,
                      font=FONT_SMALL, command=self.export).pack(side="right", padx=4)
        # 文本区
        self._text = ctk.CTkTextbox(self, font=FONT_MONO, fg_color=C_INPUT_BG,
                                     text_color=C_TEXT, corner_radius=8,
                                     border_width=0, state="disabled",
                                     wrap="word")
        self._text.pack(fill="both", expand=True, padx=12, pady=(8,12))
        # 颜色标签
        for tag, color in [("INFO", "#94A3B8"), ("WARN", C_YELLOW),
                           ("ERROR", C_RED), ("OK", C_GREEN),
                           ("DIM", C_TEXT_DIM), ("ACCENT", C_ACCENT)]:
            self._text.tag_config(tag, foreground=color)

    def append(self, text, tag="INFO"):
        self._text.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self._text.insert("end", f"[{ts}] ", "DIM")
        self._text.insert("end", text + "\n", tag)
        self._text.configure(state="disabled")
        self._text.see("end")

    def append_raw(self, line):
        tag = "INFO"
        ll = line.upper()
        if "ERROR" in ll or "FAIL" in ll:
            tag = "ERROR"
        elif "WARN" in ll:
            tag = "WARN"
        elif "OK" in ll or "SUCCESS" in ll or "PASS" in ll:
            tag = "OK"
        self.append(line, tag)

    def clear(self):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")

    def export(self):
        p = filedialog.asksaveasfilename(defaultextension=".log",
                                         filetypes=[("Log","*.log"),("Text","*.txt")])
        if p:
            with open(p, "w", encoding="utf-8") as f:
                f.write(self._text.get("1.0", "end"))


# ═══════════════════════════════════════════════════════════
#  页面: 欢迎 / 角色选择
# ═══════════════════════════════════════════════════════════

class WelcomePage(ctk.CTkFrame):
    """首页 — 选择你是谁"""
    def __init__(self, master, on_select):
        super().__init__(master, fg_color="transparent")
        self._on_select = on_select
        self.grid_columnconfigure(0, weight=1)

        # 标题
        ctk.CTkLabel(self, text="MnMCP", font=("Segoe UI", 42, "bold"),
                     text_color=C_ACCENT).grid(row=0, pady=(60,4))
        ctk.CTkLabel(self, text="Minecraft  ↔  迷你世界  跨平台联机",
                     font=FONT_BODY, text_color=C_TEXT_DIM).grid(row=1, pady=(0,40))

        ctk.CTkLabel(self, text="选择你的角色", font=FONT_H2,
                     text_color=C_TEXT).grid(row=2, pady=(0,20))

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=3, pady=10)

        roles = [
            ("🎮", "玩家", "连接到已有房间\n最简单的方式开始游戏", "player"),
            ("🏠", "房主", "创建房间邀请好友\n支持MC或迷你世界开房", "host"),
            ("🖥️", "服务器", "部署中继服务器\n为玩家提供联机服务", "server"),
        ]
        for i, (icon, title, desc, role) in enumerate(roles):
            self._role_card(cards, i, icon, title, desc, role)

    def _role_card(self, parent, col, icon, title, desc, role):
        card = ctk.CTkFrame(parent, fg_color=C_CARD, corner_radius=16,
                            border_width=1, border_color=C_BORDER,
                            width=240, height=220)
        card.grid(row=0, column=col, padx=12, pady=4)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=icon, font=("Segoe UI", 36)).grid(
            row=0, pady=(24,4))
        ctk.CTkLabel(card, text=title, font=FONT_H2,
                     text_color=C_TEXT).grid(row=1, pady=(0,4))
        ctk.CTkLabel(card, text=desc, font=FONT_SMALL,
                     text_color=C_TEXT_DIM, justify="center").grid(row=2, pady=(0,12))
        ctk.CTkButton(card, text="选择", font=FONT_BODY, height=36,
                      fg_color=C_ACCENT, hover_color=C_ACCENT_HI,
                      corner_radius=8,
                      command=lambda r=role: self._on_select(r)).grid(
            row=3, padx=30, pady=(0,20), sticky="ew")


# ═══════════════════════════════════════════════════════════
#  页面: 玩家 (Player)
# ═══════════════════════════════════════════════════════════

class PlayerPage(ctk.CTkFrame):
    """玩家页 — 输入地址即可连接"""
    def __init__(self, master, app: "MnMCPApp"):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        # 顶部导航
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.grid(row=0, sticky="ew", padx=20, pady=(16,0))
        ctk.CTkButton(nav, text="← 返回", width=80, height=32,
                      fg_color="transparent", hover_color=C_CARD,
                      font=FONT_SMALL, text_color=C_TEXT_DIM,
                      command=app.go_home).pack(side="left")
        self._status_dot = StatusDot(nav, size=12, color=C_RED)
        self._status_dot.pack(side="right", padx=(0,8))
        self._status_lbl = ctk.CTkLabel(nav, text="未连接", font=FONT_SMALL,
                                        text_color=C_TEXT_DIM)
        self._status_lbl.pack(side="right")

        # 主内容
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, sticky="nsew", padx=20, pady=10)
        body.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── 连接卡片 ──
        conn_card = ctk.CTkFrame(body, fg_color=C_CARD, corner_radius=14,
                                 border_width=1, border_color=C_BORDER)
        conn_card.grid(row=0, sticky="ew", pady=(0,10))
        conn_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(conn_card, text="🎮  快速连接", font=FONT_H2,
                     text_color=C_TEXT).grid(row=0, column=0, columnspan=3,
                                             padx=20, pady=(16,12), sticky="w")

        ctk.CTkLabel(conn_card, text="服务器地址", font=FONT_SMALL,
                     text_color=C_TEXT_DIM).grid(row=1, column=0, padx=(20,8), sticky="w")
        self.addr_entry = ctk.CTkEntry(conn_card, placeholder_text="例: play.example.com",
                                       font=FONT_BODY, height=40,
                                       fg_color=C_INPUT_BG, border_color=C_BORDER,
                                       corner_radius=8)
        self.addr_entry.grid(row=1, column=1, padx=4, sticky="ew")
        self.addr_entry.insert(0, "127.0.0.1")

        ctk.CTkLabel(conn_card, text="端口", font=FONT_SMALL,
                     text_color=C_TEXT_DIM).grid(row=1, column=2, padx=(12,4), sticky="w")
        self.port_entry = ctk.CTkEntry(conn_card, width=90, placeholder_text="25565",
                                       font=FONT_BODY, height=40,
                                       fg_color=C_INPUT_BG, border_color=C_BORDER,
                                       corner_radius=8)
        self.port_entry.grid(row=1, column=3, padx=(0,20), sticky="w")
        self.port_entry.insert(0, "25565")

        # 游戏选择
        ctk.CTkLabel(conn_card, text="我使用的游戏", font=FONT_SMALL,
                     text_color=C_TEXT_DIM).grid(row=2, column=0, padx=(20,8),
                                                  pady=(12,0), sticky="w")
        self.game_var = ctk.StringVar(value="mc")
        game_frame = ctk.CTkFrame(conn_card, fg_color="transparent")
        game_frame.grid(row=2, column=1, columnspan=3, padx=4, pady=(12,0), sticky="w")
        ctk.CTkRadioButton(game_frame, text="Minecraft", variable=self.game_var,
                           value="mc", font=FONT_BODY,
                           fg_color=C_ACCENT, hover_color=C_ACCENT_HI).pack(
            side="left", padx=(0,20))
        ctk.CTkRadioButton(game_frame, text="迷你世界", variable=self.game_var,
                           value="mnw", font=FONT_BODY,
                           fg_color=C_ACCENT, hover_color=C_ACCENT_HI).pack(side="left")

        # 连接按钮
        btn_frame = ctk.CTkFrame(conn_card, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=4, padx=20, pady=16, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)

        self.connect_btn = ctk.CTkButton(
            btn_frame, text="连  接", font=("Segoe UI", 14, "bold"),
            height=44, corner_radius=10,
            fg_color=C_GREEN, hover_color="#22C55E", text_color="#0F0F17",
            command=self._connect)
        self.connect_btn.grid(row=0, column=0, sticky="ew")
        self.disconnect_btn = ctk.CTkButton(
            btn_frame, text="断开连接", font=FONT_BODY,
            height=44, corner_radius=10, width=120,
            fg_color=C_RED, hover_color="#EF4444", text_color="#fff",
            command=self._disconnect, state="disabled")
        self.disconnect_btn.grid(row=0, column=1, padx=(10,0))

        # 提示
        tip = ctk.CTkFrame(body, fg_color=C_CARD, corner_radius=10,
                           border_width=1, border_color=C_BORDER)
        tip.grid(row=1, sticky="ew", pady=(0,10))
        ctk.CTkLabel(tip, text="💡 使用说明", font=FONT_H3,
                     text_color=C_ACCENT).pack(anchor="w", padx=16, pady=(12,4))
        tips_text = (
            "• Minecraft 玩家: 直接在游戏「多人游戏」中添加上面的服务器地址即可\n"
            "• 迷你世界玩家: 需要以管理员权限运行本程序，程序会自动配置VPN来连接\n"
            "• 如果服务器在远程，请填写服务器的公网IP或域名"
        )
        ctk.CTkLabel(tip, text=tips_text, font=FONT_SMALL,
                     text_color=C_TEXT_DIM, justify="left").pack(
            anchor="w", padx=16, pady=(0,12))

        # 日志
        self.log = LogConsole(body)
        self.log.grid(row=2, sticky="nsew", pady=(0,4))
        body.grid_rowconfigure(2, weight=1)

    def _connect(self):
        addr = self.addr_entry.get().strip()
        port = self.port_entry.get().strip()
        game = self.game_var.get()
        if not addr:
            self.log.append("请输入服务器地址", "ERROR")
            return
        game_name = "Minecraft" if game == "mc" else "迷你世界"
        self.log.append(f"正在连接 {addr}:{port} ({game_name})...", "ACCENT")

        self.connect_btn.configure(state="disabled")
        self.disconnect_btn.configure(state="normal")
        self._status_dot.set(C_YELLOW)
        self._status_lbl.configure(text="连接中...", text_color=C_YELLOW)

        # 构建命令
        scenario = "C"  # 玩家连接到中继服务器
        cmd = [
            PYTHON_EXE,
            str(PROJECT_ROOT / "start_multiplayer.py"),
            "personal", "--scenario", scenario,
            "--relay-host", addr,
        ]
        if game == "mnw":
            self.log.append("迷你世界模式: 将启动VPN捕获模块", "WARN")

        self.app.start_process(cmd, self.log, self._on_started, self._on_stopped)

    def _on_started(self):
        self._status_dot.set(C_GREEN)
        self._status_lbl.configure(text="已连接", text_color=C_GREEN)

    def _on_stopped(self):
        self.connect_btn.configure(state="normal")
        self.disconnect_btn.configure(state="disabled")
        self._status_dot.set(C_RED)
        self._status_lbl.configure(text="未连接", text_color=C_TEXT_DIM)

    def _disconnect(self):
        self.app.stop_process()


# ═══════════════════════════════════════════════════════════
#  页面: 房主 (Host)
# ═══════════════════════════════════════════════════════════

class HostPage(ctk.CTkFrame):
    """房主页 — 创建房间"""
    def __init__(self, master, app: "MnMCPApp"):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 导航
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.grid(row=0, sticky="ew", padx=20, pady=(16,0))
        ctk.CTkButton(nav, text="← 返回", width=80, height=32,
                      fg_color="transparent", hover_color=C_CARD,
                      font=FONT_SMALL, text_color=C_TEXT_DIM,
                      command=app.go_home).pack(side="left")
        self._status_dot = StatusDot(nav, size=12, color=C_RED)
        self._status_dot.pack(side="right", padx=(0,8))
        self._status_lbl = ctk.CTkLabel(nav, text="未运行", font=FONT_SMALL,
                                        text_color=C_TEXT_DIM)
        self._status_lbl.pack(side="right")

        # ── 配置区 ──
        cfg = ctk.CTkFrame(self, fg_color=C_CARD, corner_radius=14,
                           border_width=1, border_color=C_BORDER)
        cfg.grid(row=1, sticky="ew", padx=20, pady=10)
        cfg.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(cfg, text="🏠  创建房间", font=FONT_H2,
                     text_color=C_TEXT).grid(row=0, column=0, columnspan=4,
                                             padx=20, pady=(16,14), sticky="w")

        # 房主类型
        ctk.CTkLabel(cfg, text="我用什么开房", font=FONT_SMALL,
                     text_color=C_TEXT_DIM).grid(row=1, column=0, padx=(20,8), sticky="w")
        self.host_type = ctk.StringVar(value="mc")
        ht_frame = ctk.CTkFrame(cfg, fg_color="transparent")
        ht_frame.grid(row=1, column=1, columnspan=3, padx=4, sticky="w")
        ctk.CTkRadioButton(ht_frame, text="Minecraft 开服", variable=self.host_type,
                           value="mc", font=FONT_BODY,
                           fg_color=C_ACCENT, hover_color=C_ACCENT_HI,
                           command=self._on_type_change).pack(side="left", padx=(0,16))
        ctk.CTkRadioButton(ht_frame, text="迷你世界 创建房间", variable=self.host_type,
                           value="mnw", font=FONT_BODY,
                           fg_color=C_ACCENT, hover_color=C_ACCENT_HI,
                           command=self._on_type_change).pack(side="left")

        # 中继服务器
        ctk.CTkLabel(cfg, text="中继服务器", font=FONT_SMALL,
                     text_color=C_TEXT_DIM).grid(row=2, column=0, padx=(20,8),
                                                  pady=(12,0), sticky="w")
        self.relay_entry = ctk.CTkEntry(cfg, placeholder_text="127.0.0.1",
                                        font=FONT_BODY, height=38,
                                        fg_color=C_INPUT_BG, border_color=C_BORDER,
                                        corner_radius=8)
        self.relay_entry.grid(row=2, column=1, padx=4, pady=(12,0), sticky="ew")
        self.relay_entry.insert(0, "127.0.0.1")

        # MC服务器地址 (场景B)
        self.mc_lbl = ctk.CTkLabel(cfg, text="MC服务器", font=FONT_SMALL,
                                   text_color=C_TEXT_DIM)
        self.mc_lbl.grid(row=3, column=0, padx=(20,8), pady=(8,0), sticky="w")
        self.mc_entry = ctk.CTkEntry(cfg, placeholder_text="127.0.0.1:25565",
                                     font=FONT_BODY, height=38,
                                     fg_color=C_INPUT_BG, border_color=C_BORDER,
                                     corner_radius=8)
        self.mc_entry.grid(row=3, column=1, padx=4, pady=(8,0), sticky="ew")
        self.mc_entry.insert(0, "127.0.0.1:25565")

        # 按钮
        btn_frame = ctk.CTkFrame(cfg, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=4, padx=20, pady=16, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        self.start_btn = ctk.CTkButton(
            btn_frame, text="▶  开始", font=("Segoe UI", 14, "bold"),
            height=44, corner_radius=10,
            fg_color=C_GREEN, hover_color="#22C55E", text_color="#0F0F17",
            command=self._start)
        self.start_btn.grid(row=0, column=0, sticky="ew")
        self.stop_btn = ctk.CTkButton(
            btn_frame, text="■  停止", font=FONT_BODY,
            height=44, corner_radius=10, width=100,
            fg_color=C_RED, hover_color="#EF4444", text_color="#fff",
            command=self._stop, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=(10,0))

        self._on_type_change()

        # 日志
        self.log = LogConsole(self)
        self.log.grid(row=2, sticky="nsew", padx=20, pady=(0,10))

    def _on_type_change(self):
        if self.host_type.get() == "mc":
            self.mc_lbl.grid()
            self.mc_entry.grid()
        else:
            self.mc_lbl.grid_remove()
            self.mc_entry.grid_remove()

    def _start(self):
        ht = self.host_type.get()
        relay = self.relay_entry.get().strip() or "127.0.0.1"
        scenario = "B" if ht == "mc" else "A"
        label = "MC房主 (场景B)" if ht == "mc" else "迷你世界房主 (场景A)"

        self.log.append(f"启动 {label}，中继: {relay}", "ACCENT")

        cmd = [
            PYTHON_EXE,
            str(PROJECT_ROOT / "start_multiplayer.py"),
            "personal", "--scenario", scenario,
            "--relay-host", relay,
        ]
        if scenario == "B":
            mc_full = self.mc_entry.get().strip() or "127.0.0.1:25565"
            parts = mc_full.split(":")
            mc_h = parts[0]
            mc_p = parts[1] if len(parts) > 1 else "25565"
            cmd.extend(["--mc-host", mc_h, "--mc-port", mc_p])

        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self._status_dot.set(C_YELLOW)
        self._status_lbl.configure(text="启动中...", text_color=C_YELLOW)

        self.app.start_process(cmd, self.log,
                               lambda: self._set_running(True),
                               lambda: self._set_running(False))

    def _set_running(self, on):
        if on:
            self._status_dot.set(C_GREEN)
            self._status_lbl.configure(text="运行中", text_color=C_GREEN)
        else:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self._status_dot.set(C_RED)
            self._status_lbl.configure(text="已停止", text_color=C_TEXT_DIM)

    def _stop(self):
        self.app.stop_process()


# ═══════════════════════════════════════════════════════════
#  页面: 服务器 (Server)
# ═══════════════════════════════════════════════════════════

class ServerPage(ctk.CTkFrame):
    """服务器页 — 部署中继"""
    def __init__(self, master, app: "MnMCPApp"):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 导航
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.grid(row=0, sticky="ew", padx=20, pady=(16,0))
        ctk.CTkButton(nav, text="← 返回", width=80, height=32,
                      fg_color="transparent", hover_color=C_CARD,
                      font=FONT_SMALL, text_color=C_TEXT_DIM,
                      command=app.go_home).pack(side="left")
        self._status_dot = StatusDot(nav, size=12, color=C_RED)
        self._status_dot.pack(side="right", padx=(0,8))
        self._status_lbl = ctk.CTkLabel(nav, text="未运行", font=FONT_SMALL,
                                        text_color=C_TEXT_DIM)
        self._status_lbl.pack(side="right")

        # ── 配置 + 统计 ──
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=1, sticky="ew", padx=20, pady=10)
        top.grid_columnconfigure(0, weight=3)
        top.grid_columnconfigure(1, weight=2)

        # 左: 配置
        cfg = ctk.CTkFrame(top, fg_color=C_CARD, corner_radius=14,
                           border_width=1, border_color=C_BORDER)
        cfg.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        cfg.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(cfg, text="🖥️  中继服务器", font=FONT_H2,
                     text_color=C_TEXT).grid(row=0, column=0, columnspan=2,
                                             padx=20, pady=(16,14), sticky="w")

        labels = ["监听地址", "MC 端口", "MNW 端口", "最大连接"]
        defaults = ["0.0.0.0", "25565", "19132", "40"]
        self.srv_entries = []
        for i, (lbl, dflt) in enumerate(zip(labels, defaults)):
            ctk.CTkLabel(cfg, text=lbl, font=FONT_SMALL,
                         text_color=C_TEXT_DIM).grid(row=i+1, column=0,
                                                      padx=(20,8), pady=4, sticky="w")
            e = ctk.CTkEntry(cfg, font=FONT_BODY, height=36,
                             fg_color=C_INPUT_BG, border_color=C_BORDER,
                             corner_radius=8, width=160)
            e.grid(row=i+1, column=1, padx=(0,20), pady=4, sticky="w")
            e.insert(0, dflt)
            self.srv_entries.append(e)

        btn_frame = ctk.CTkFrame(cfg, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, padx=20, pady=14, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)
        self.start_btn = ctk.CTkButton(
            btn_frame, text="▶  启动服务器", font=("Segoe UI", 13, "bold"),
            height=42, corner_radius=10,
            fg_color=C_GREEN, hover_color="#22C55E", text_color="#0F0F17",
            command=self._start)
        self.start_btn.grid(row=0, column=0, sticky="ew")
        self.stop_btn = ctk.CTkButton(
            btn_frame, text="■", font=FONT_H2,
            height=42, width=50, corner_radius=10,
            fg_color=C_RED, hover_color="#EF4444", text_color="#fff",
            command=self._stop, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=(8,0))

        # 右: 统计
        stats_frame = ctk.CTkFrame(top, fg_color="transparent")
        stats_frame.grid(row=0, column=1, sticky="nsew")
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)

        self.card_mc  = StatCard(stats_frame, "MC 在线", accent=C_ACCENT)
        self.card_mc.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self.card_mnw = StatCard(stats_frame, "MNW 在线", accent=C_YELLOW)
        self.card_mnw.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        self.card_pkt = StatCard(stats_frame, "已翻译", accent=C_GREEN)
        self.card_pkt.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        self.card_err = StatCard(stats_frame, "错误", accent=C_RED)
        self.card_err.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        # 运行时间
        self.uptime_lbl = ctk.CTkLabel(stats_frame, text="运行时间: --:--:--",
                                       font=FONT_SMALL, text_color=C_TEXT_DIM)
        self.uptime_lbl.grid(row=2, column=0, columnspan=2, pady=(8,0))

        # 日志
        self.log = LogConsole(self)
        self.log.grid(row=2, sticky="nsew", padx=20, pady=(0,10))

        self._uptime_start = 0
        self._tick()

    def _tick(self):
        if self._uptime_start > 0:
            s = int(time.time() - self._uptime_start)
            self.uptime_lbl.configure(
                text=f"运行时间: {s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}")
        self.after(1000, self._tick)

    def _start(self):
        host = self.srv_entries[0].get().strip() or "0.0.0.0"
        mc_port = self.srv_entries[1].get().strip() or "25565"
        mnw_port = self.srv_entries[2].get().strip() or "19132"
        max_c = self.srv_entries[3].get().strip() or "40"

        self.log.append(f"启动中继服务器 {host} MC:{mc_port} MNW:{mnw_port}", "ACCENT")

        cmd = [
            PYTHON_EXE,
            str(PROJECT_ROOT / "start_multiplayer.py"),
            "streamer",
            "--host", host,
            "--mc-port", mc_port,
            "--mnw-port", mnw_port,
            "--max-clients", max_c,
        ]

        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self._status_dot.set(C_YELLOW)
        self._status_lbl.configure(text="启动中...", text_color=C_YELLOW)
        self._uptime_start = time.time()

        self.app.start_process(cmd, self.log,
                               lambda: self._set_state(True),
                               lambda: self._set_state(False))

    def _set_state(self, on):
        if on:
            self._status_dot.set(C_GREEN)
            self._status_lbl.configure(text="运行中", text_color=C_GREEN)
        else:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self._status_dot.set(C_RED)
            self._status_lbl.configure(text="已停止", text_color=C_TEXT_DIM)
            self._uptime_start = 0

    def _stop(self):
        self.app.stop_process()


# ═══════════════════════════════════════════════════════════
#  主应用
# ═══════════════════════════════════════════════════════════

class MnMCPApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MnMCP")
        self.geometry("960x680")
        self.minsize(800, 560)
        self.configure(fg_color=C_BG)

        # 进程管理
        self._proc: subprocess.Popen = None
        self._proc_thread: threading.Thread = None
        self._active_log: LogConsole = None
        self._on_started_cb = None
        self._on_stopped_cb = None

        # 页面容器
        self._container = ctk.CTkFrame(self, fg_color="transparent")
        self._container.pack(fill="both", expand=True)
        self._container.grid_columnconfigure(0, weight=1)
        self._container.grid_rowconfigure(0, weight=1)

        # 创建所有页面
        self._pages = {}
        self._create_pages()
        self._show("welcome")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_pages(self):
        for PageClass, name in [
            (lambda m: WelcomePage(m, self._on_role_select), "welcome"),
            (lambda m: PlayerPage(m, self), "player"),
            (lambda m: HostPage(m, self), "host"),
            (lambda m: ServerPage(m, self), "server"),
        ]:
            page = PageClass(self._container)
            page.grid(row=0, column=0, sticky="nsew")
            self._pages[name] = page

    def _show(self, name):
        self._pages[name].tkraise()

    def _on_role_select(self, role):
        self._show(role)

    def go_home(self):
        if self._proc and self._proc.poll() is None:
            if not messagebox.askyesno("确认", "服务正在运行，返回会停止它，确定吗？"):
                return
            self.stop_process()
        self._show("welcome")

    # ── 进程管理 ──

    def start_process(self, cmd, log: LogConsole, on_started=None, on_stopped=None):
        """启动子进程并将输出重定向到日志"""
        self._active_log = log
        self._on_started_cb = on_started
        self._on_stopped_cb = on_stopped

        log.append(f"命令: {' '.join(cmd)}", "DIM")

        self._proc_thread = threading.Thread(
            target=self._run_proc, args=(cmd,), daemon=True)
        self._proc_thread.start()

    def _run_proc(self, cmd):
        try:
            creation = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, cwd=str(PROJECT_ROOT),
                creationflags=creation)

            if self._on_started_cb:
                self.after(0, self._on_started_cb)

            for line in iter(self._proc.stdout.readline, ""):
                line = line.rstrip()
                if line and self._active_log:
                    self.after(0, lambda l=line: self._active_log.append_raw(l))

            self._proc.wait()
        except Exception as e:
            if self._active_log:
                self.after(0, lambda: self._active_log.append(f"进程异常: {e}", "ERROR"))
        finally:
            self._proc = None
            if self._on_stopped_cb:
                self.after(0, self._on_stopped_cb)

    def stop_process(self):
        if self._proc:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
            except Exception:
                pass

    def _on_close(self):
        if self._proc and self._proc.poll() is None:
            if not messagebox.askyesno("退出", "服务正在运行，确定退出？"):
                return
            self.stop_process()
        self.destroy()


def main():
    app = MnMCPApp()
    app.mainloop()


if __name__ == "__main__":
    main()
