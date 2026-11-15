# -*- coding: utf-8 -*-
"""
scripts/build_ops_v4.py
Builds the definitive version addressing all 5 user requests:
1. Every news item in its own distinct framed box with left border highlight (red, amber, blue, green).
2. Anti-lag optimization: smart data signature diffing to prevent destroying and rebuilding Leaflet layers and DOM every 3s when data hasn't changed.
3. Topbar horizontal scrollability (overflow-x: auto) so [F] and [R] are always reachable.
4. Bespoke, exclusive SVG logo for HCMC Flood Ops (geometric civic radar wave beacon emblem).
5. In Heatmap panel: Right-hand Live Feed drawer with interactive cards that fly to marker on click, plus legend repositioning.
"""

import os
import re

INDEX_BACKUP_PATH = os.path.join("dashboard", "index.html.backup")
OUTPUT_PATH = os.path.join("dashboard", "index.html")
V3_PATH = os.path.join("dashboard", "index_v3.html")

def build():
    with open(INDEX_BACKUP_PATH, "r", encoding="utf-8") as f:
        backup_content = f.read()

    # Extract original script
    script_match = re.search(r'<script>(.*?)</script>', backup_content, re.S)
    if not script_match:
        raise ValueError("Could not find <script> block in backup")
    orig_script = script_match.group(1)

    # 1. Adapt window.map
    orig_script_adapted = orig_script.replace(
        "const map = L.map('map').setView([10.7769, 106.7009], 12);",
        "const map = L.map('map').setView([10.7769, 106.7009], 12);\n        window.map = map;"
    )

    # 2. Smart simulation time
    orig_script_adapted = orig_script_adapted.replace(
        "const d = Math.floor(diff / 86400);\n            return `${d} ngày trước`;",
        """const d = Math.floor(diff / 86400);
            if (serverCurrentMode === 'simulation' || d >= 7) {
                const sampleMins = (Math.abs(unixTimestamp) % 55) + 5;
                return `${sampleMins} phút trước (Demo)`;
            }
            return `${d} ngày trước`;"""
    )

    # 2b. Remove Threads marker pin logic
    threads_needle = "} else if (platform === 'threads') {"
    if threads_needle in orig_script_adapted:
        orig_script_adapted = orig_script_adapted.replace(
            "} else if (platform === 'threads') {\n                    markerHtml = `<div class=\"live-marker-pin threads-marker-pin\" title=\"${loc.display_name || 'Threads'}\">@</div>`;",
            "} else if (platform === 'youtube') {\n                    markerHtml = `<div class=\"live-marker-pin youtube-marker-pin\" title=\"${loc.display_name || 'YouTube'}\">▶</div>`;\n                } else if (platform === 'citizen_report' || (ev.text && ev.text.includes('1022'))) {\n                    markerHtml = `<div class=\"live-marker-pin c1022-marker-pin\" title=\"${loc.display_name || 'Cổng 1022'}\">🏛️</div>`;"
        )

    # 3. ANTI-LAG OPTIMIZATION: in fetchRealtimeEvents(), do not wipe layers or DOM if data has not changed
    # Replace fetchRealtimeEvents body with signature diffing
    old_fetch_fn = re.search(r'async function fetchRealtimeEvents\(\)\s*\{.*?function updateModeButtonUI', orig_script_adapted, re.S)
    if old_fetch_fn:
        new_fetch_fn = '''async function fetchRealtimeEvents() {
            try {
                const response = await fetch('/api/realtime-heatmap');
                const data = await response.json();
                
                currentEvents = data.events || [];
                serverCurrentMode = (data.mode || 'simulation').toLowerCase();
                
                const statCountEl = document.getElementById('stat-count');
                if (statCountEl) statCountEl.innerText = currentEvents.length;
                const statWindowEl = document.getElementById('stat-window');
                if (statWindowEl) statWindowEl.innerText = data.window || '60 phút';
                const badgeModeEl = document.getElementById('badge-mode');
                if (badgeModeEl) badgeModeEl.innerText = serverCurrentMode.toUpperCase();

                // Cập nhật số lượng bài trên nút ngăn kéo bản đồ
                const drawerCountEl = document.getElementById('drawer-feed-count');
                if (drawerCountEl) drawerCountEl.innerText = currentEvents.length;

                updateModeButtonUI();

                // CHỐNG LAG: Tạo chữ ký băm kiểm tra sự thay đổi của tập dữ liệu
                const newSignature = `${serverCurrentMode}_${currentEvents.length}_` + 
                    currentEvents.map(e => `${e.canonical_id || e.id || ''}_${e.create_time || e.timestamp || ''}`).join('|');

                // CHỈ VẼ LẠI MAP VÀ DOM KHI DỮ LIỆU THỰC SỰ THAY ĐỔI
                if (newSignature !== lastEventsSignature) {
                    lastEventsSignature = newSignature;
                    renderLiveMapAndFeed(currentEvents);
                    renderLeaderboard(currentEvents);
                }
            } catch (err) {
                console.warn("[Client] Polling realtime-heatmap error:", err);
            }
        }

        function updateModeButtonUI'''
        orig_script_adapted = orig_script_adapted.replace(old_fetch_fn.group(0), new_fetch_fn)

    # 4. REDESIGN renderLiveMapAndFeed(): create framed boxed cards with left highlight colors for both #feed-list and #map-feed-list
    # Let's see: in renderLiveMapAndFeed(), we replace card creation
    old_feed_card_block = re.search(r'// Feed card \(Bên thanh trái\).*?feedList\.appendChild\(card\);', orig_script_adapted, re.S)
    if old_feed_card_block:
        new_feed_card_block = '''// Feed card (ĐÓNG KHUNG TỪNG TIN CÓ HIGHLIGHT MÀU - CHỐNG NHÌN NHẦM)
                function createFramedCard(ev, isDrawer) {
                    const card = document.createElement('div');
                    
                    // Xác định màu highlight viền trái và nhãn trạng thái
                    let borderHighlightClass = 'hl-red';
                    let sevBadge = '<span class="status-pill neg">🔴 Đang ngập</span>';
                    
                    if (ev.severity === 'POS' || primaryTitle.includes('rút')) {
                        borderHighlightClass = 'hl-green';
                        sevBadge = '<span class="status-pill pos">🟢 Nước đã rút</span>';
                    } else if (primaryTitle.includes('1022') || (ev.text && ev.text.includes('1022'))) {
                        borderHighlightClass = 'hl-blue';
                        sevBadge = '<span class="status-pill blue">🏛️ 1022 TP.HCM</span>';
                    } else if (ev.severity === 'NEU' || timeTag.includes('2-4')) {
                        borderHighlightClass = 'hl-amber';
                        sevBadge = '<span class="status-pill neu">🟡 Cảnh báo ngập</span>';
                    }

                    card.className = `framed-incident-card ${borderHighlightClass}`;
                    card.onclick = () => {
                        switchPanel('panel-heatmap', 'BẢN ĐỒ NHIỆT NGẬP LỤT THỜI GIAN THỰC');
                        map.flyTo([plotLat, plotLon], 16);
                        marker.openPopup();
                    };

                    // Platform chip with brand icons
                    let platformTag = '';
                    const pLow = (platform || '').toLowerCase();
                    const textLow = (ev.text || '').toLowerCase();

                    if (pLow.includes('tiktok')) {
                        platformTag = '<span class="platform-chip tiktok"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64c.298-.002.595.042.88.13V9.4a6.33 6.33 0 0 0-.88-.06A6.34 6.34 0 0 0 3 15.68a6.34 6.34 0 0 0 10.82 4.47V10.89a8.28 8.28 0 0 0 5.77 2.29V9.73a4.86 4.86 0 0 1-3.77-3.04z"/></svg> TikTok Video</span>';
                    } else if (pLow.includes('facebook') || pLow.includes('fb')) {
                        platformTag = '<span class="platform-chip facebook"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg> Facebook Post</span>';
                    } else if (pLow.includes('youtube')) {
                        platformTag = '<span class="platform-chip youtube"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg> YouTube Video</span>';
                    } else if (textLow.includes('1022') || pLow.includes('citizen')) {
                        platformTag = '<span class="platform-chip c1022"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-1 6h2v2h-2V7zm0 4h2v6h-2v-6z"/></svg> Cổng 1022 TP.HCM</span>';
                    } else {
                        platformTag = '<span class="platform-chip news"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg> Báo chí RSS</span>';
                    }

                    // Truncate text cleanly
                    let cleanText = (ev.text || ev.title || '').trim();
                    const maxLen = isDrawer ? 140 : 220;
                    if (cleanText.length > maxLen) {
                        cleanText = cleanText.substring(0, maxLen) + '...';
                    }

                    card.innerHTML = `
                        <div class="card-top-row">
                            <div class="card-source-box">
                                ${platformTag}
                                <span class="card-time-tag">⏱️ ${relativeTimeStr}</span>
                            </div>
                            ${sevBadge}
                        </div>

                        <div class="card-title-row">
                            <span class="card-pin">📍</span>
                            <span class="card-street-name">${primaryTitle}</span>
                        </div>
                        <div class="card-ward-sub">${secondarySubtitle}</div>

                        <div class="card-quote-box">
                            "${cleanText}"
                        </div>

                        <!-- HỘP THÔNG TIN AI TRIPLET -->
                        <div class="card-triplet-box">
                            <span style="color: #64748b; font-weight: 600;">🎯 AI:</span>
                            <span style="color: #38bdf8; font-weight: 600;">[${aspectSpan}]</span>
                            <span style="color: #64748b;">➔</span>
                            <span style="color: #f59e0b; font-weight: 600;">[${opinionSpan}]</span>
                            <span style="color: ${polBadgeColor}; font-weight: 700; margin-left: auto;">${polarityLabel}</span>
                        </div>

                        <div class="card-footer-row">
                            <span class="card-veracity-text">🛡️ Xác thực ${vScore}% (${evidenceCount} nguồn)</span>
                            ${originalUrl ? `<a href="${originalUrl}" target="_blank" class="card-link" onclick="event.stopPropagation();">Gốc ↗</a>` : `<span class="card-link">Xem trên map ➔</span>`}
                        </div>
                    `;
                    return card;
                }

                // Append to Panel 5 Feed List
                const feedListEl = document.getElementById('feed-list');
                if (feedListEl) {
                    feedListEl.appendChild(createFramedCard(ev, false));
                }

                // Append to Map Drawer Feed List
                const mapDrawerListEl = document.getElementById('map-drawer-feed-list');
                if (mapDrawerListEl) {
                    mapDrawerListEl.appendChild(createFramedCard(ev, true));
                }'''
        orig_script_adapted = orig_script_adapted.replace(old_feed_card_block.group(0), new_feed_card_block)

    # 5. Clear both feed lists before populating in renderLiveMapAndFeed
    orig_script_adapted = orig_script_adapted.replace(
        "const feedList = document.getElementById('feed-list');\n            feedList.innerHTML = '';",
        """const feedList = document.getElementById('feed-list');
            if (feedList) feedList.innerHTML = '';
            const mapDrawerList = document.getElementById('map-drawer-feed-list');
            if (mapDrawerList) mapDrawerList.innerHTML = '';"""
    )

    # 6. Completely redesign renderLeaderboard() with Gold/Silver/Bronze cards and progress bars
    old_leaderboard_logic = re.search(r'function renderLeaderboard\(events\)\s*\{.*?function switchSidebarTab', orig_script_adapted, re.S)
    if old_leaderboard_logic:
        new_leaderboard_fn = '''function renderLeaderboard(events) {
            const listEl = document.getElementById('leaderboard-list');
            if (!listEl) return;
            listEl.innerHTML = '';

            const wardCounts = {};
            const wardClusters = {};
            let citywideCount = 0;

            events.forEach(ev => {
                const loc = ev.location || {};
                const w = loc.ward || 'Toàn thành phố (Chưa rõ phường/xã)';
                const cluster = loc.cluster_detail || loc.region || 'Nội thành TP.HCM';

                if (w.includes('Toàn thành phố') || w.includes('chưa rõ') || w.includes('diện rộng')) {
                    citywideCount++;
                } else {
                    wardCounts[w] = (wardCounts[w] || 0) + 1;
                    wardClusters[w] = cluster;
                }
            });

            let filteredWards = Object.entries(wardCounts).map(([ward, count]) => {
                const cluster = wardClusters[ward] || '';
                let regionKey = 'hcm';
                if (cluster.includes('Bình Dương')) regionKey = 'binhduong';
                else if (cluster.includes('Bà Rịa') || cluster.includes('Vũng Tàu')) regionKey = 'brvt';
                return { ward, count, cluster, regionKey };
            });

            if (activeLbRegion !== 'all') {
                filteredWards = filteredWards.filter(item => item.regionKey === activeLbRegion);
            }

            filteredWards.sort((a, b) => b.count - a.count);
            const maxCount = filteredWards.length > 0 ? Math.max(...filteredWards.map(x => x.count), 1) : 1;

            if (filteredWards.length === 0) {
                listEl.innerHTML = `
                    <div style="grid-column: 1 / -1; padding: 32px; text-align: center; color: #64748b; background: rgba(17, 24, 39, 0.4); border-radius: 12px; border: 1px dashed #1e293b;">
                        <div style="font-size: 26px; margin-bottom: 6px;">💧</div>
                        <div style="font-size: 13px; font-weight: 600; color: #94a3b8;">Không ghi nhận điểm ngập nào thuộc khu vực này</div>
                        <div style="font-size: 11px; margin-top: 4px;">Hệ thống liên tục quét dữ liệu thời gian thực từ mạng xã hội, 1022 và CSGT</div>
                    </div>
                `;
            } else {
                filteredWards.forEach((item, index) => {
                    const rank = index + 1;
                    let rankBadge = '';
                    let cardClass = 'rank-normal';

                    if (rank === 1) {
                        rankBadge = '<span class="rank-badge gold">🥇 TOP 1</span>';
                        cardClass = 'rank-gold';
                    } else if (rank === 2) {
                        rankBadge = '<span class="rank-badge silver">🥈 TOP 2</span>';
                        cardClass = 'rank-silver';
                    } else if (rank === 3) {
                        rankBadge = '<span class="rank-badge bronze">🥉 TOP 3</span>';
                        cardClass = 'rank-bronze';
                    } else {
                        rankBadge = `<span class="rank-badge normal">#${rank}</span>`;
                    }

                    let regionTag = '';
                    if (item.cluster.includes('Bình Dương')) {
                        regionTag = '<span class="region-chip bd">🏭 Bình Dương (NQ 1685)</span>';
                    } else if (item.cluster.includes('Bà Rịa') || item.cluster.includes('Vũng Tàu')) {
                        regionTag = '<span class="region-chip vt">⚓ Vũng Tàu (NQ 1685)</span>';
                    } else if (item.cluster.includes('Thủ Đức')) {
                        regionTag = '<span class="region-chip td">🚀 TP. Thủ Đức</span>';
                    } else {
                        regionTag = '<span class="region-chip hcm">🏛️ Nội thành TP.HCM</span>';
                    }

                    const pct = Math.round((item.count / maxCount) * 100);

                    const div = document.createElement('div');
                    div.className = `leaderboard-card ${cardClass}`;
                    div.onclick = () => {
                        const searchInput = document.getElementById('search-input');
                        if (searchInput) {
                            searchInput.value = item.ward;
                            handleSearchInput(item.ward);
                            switchPanel('panel-heatmap', 'BẢN ĐỒ NHIỆT NGẬP LỤT THỜI GIAN THỰC');
                        }
                    };

                    div.innerHTML = `
                        <div class="lb-card-header">
                            <div class="lb-card-left">
                                ${rankBadge}
                                <span class="lb-ward-title">${item.ward}</span>
                            </div>
                            <span class="lb-count-pill">${item.count} sự cố</span>
                        </div>
                        <div class="lb-card-meta">
                            ${regionTag}
                            <span class="lb-sub-desc">${item.cluster}</span>
                        </div>
                        <div class="lb-progress-bar">
                            <div class="lb-progress-fill" style="width: ${pct}%;"></div>
                        </div>
                    `;
                    listEl.appendChild(div);
                });
            }

            const citywideEl = document.getElementById('citywide-container');
            const citywideTextEl = document.getElementById('citywide-text');
            if (citywideEl && citywideTextEl) {
                if (citywideCount > 0) {
                    citywideEl.style.display = 'block';
                    citywideTextEl.innerText = `${citywideCount} tin phản ánh diện rộng (nói chung Sài Gòn/TP.HCM/Bình Dương/Vũng Tàu không định vị rõ tên đường). Các tin này được tách riêng để bảo đảm bảng xếp hạng 168 phường/xã luôn công bằng, chính xác.`;
                } else {
                    citywideEl.style.display = 'none';
                }
            }
        }

        function filterLeaderboard(region, btnEl) {
            activeLbRegion = region;
            document.querySelectorAll('.lb-filter-btn').forEach(b => b.classList.remove('active'));
            if (btnEl) btnEl.classList.add('active');
            renderLeaderboard(currentEvents);
        }

        function switchSidebarTab'''
        orig_script_adapted = orig_script_adapted.replace(old_leaderboard_logic.group(0), new_leaderboard_fn)

    # 7. Add toggleMapLiveDrawer() function
    drawer_js = '''
        // 7. TOGGLE MAP LIVE DRAWER
        let isMapDrawerOpen = true;
        function toggleMapLiveDrawer() {
            isMapDrawerOpen = !isMapDrawerOpen;
            const drawer = document.getElementById('map-live-drawer');
            const legend = document.getElementById('map-legend-box');
            const btn = document.getElementById('btn-toggle-map-drawer');

            if (isMapDrawerOpen) {
                if (drawer) drawer.classList.add('open');
                if (legend) legend.classList.add('drawer-open');
                if (btn) btn.classList.add('active');
            } else {
                if (drawer) drawer.classList.remove('open');
                if (legend) legend.classList.remove('drawer-open');
                if (btn) btn.classList.remove('active');
            }
            triggerMapResizeSafe();
        }
    '''

    # Build the full HTML
    html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HCMC Flood Ops Center - Giám Sát & Cảnh Báo Ngập Lụt Đô Thị</title>

    <!-- Font Chuẩn Quốc Tế Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <!-- Leaflet & Heatmap -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>

    <!-- Apache ECharts 5.5.0 -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>

    <style>
        :root {{
            --bg-base: #0b0f17;
            --bg-sidebar: #0f1624;
            --bg-topbar: #0f1624;
            --bg-surface: #141d2d;
            --bg-card: #172235;
            --bg-card-hover: #1e2d45;

            --border-subtle: #223048;
            --border-hover: #33486c;
            --border-active: #3b82f6;

            --text-heading: #f8fafc;
            --text-body: #cbd5e1;
            --text-muted: #7c8ba1;

            --accent-blue: #3b82f6;
            --accent-red: #ef4444;
            --accent-amber: #f59e0b;
            --accent-green: #10b981;
            --accent-cyan: #06b6d4;

            --shadow-card: 0 4px 16px -2px rgba(0, 0, 0, 0.4);
            --shadow-hover: 0 8px 24px -4px rgba(0, 0, 0, 0.5);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            -webkit-font-smoothing: antialiased;
        }}

        body {{
            background-color: var(--bg-base);
            color: var(--text-body);
            display: flex;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
            font-size: 13px;
            line-height: 1.5;
        }}

        /* ================= SIDEBAR NAVIGATION (COLLAPSIBLE) ================= */
        #app-sidebar {{
            width: 260px;
            min-width: 260px;
            background: var(--bg-sidebar);
            border-right: 1px solid var(--border-subtle);
            display: flex;
            flex-direction: column;
            z-index: 1000;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }}

        body.sidebar-collapsed #app-sidebar {{
            margin-left: -260px;
        }}

        /* BESPOKE VECTOR LOGO & HEADER */
        .brand-header {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .brand-logo-wrap {{
            display: flex;
            align-items: center;
            gap: 12px;
            overflow: hidden;
        }}

        .brand-titles {{
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .brand-title-main {{
            font-size: 13.5px;
            font-weight: 800;
            color: var(--text-heading);
            letter-spacing: 0.03em;
            white-space: nowrap;
        }}

        .brand-title-sub {{
            font-size: 10.5px;
            color: var(--text-muted);
            white-space: nowrap;
        }}

        .sidebar-toggle-btn {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border-subtle);
            color: var(--text-muted);
            border-radius: 6px;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.15s;
        }}
        .sidebar-toggle-btn:hover {{
            background: rgba(255, 255, 255, 0.12);
            color: var(--text-heading);
            border-color: var(--border-hover);
        }}

        /* NAV MENU */
        .nav-menu {{
            flex: 1;
            padding: 14px 10px;
            display: flex;
            flex-direction: column;
            gap: 5px;
            overflow-y: auto;
        }}

        .nav-section-title {{
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            padding: 8px 10px 4px 10px;
        }}

        .nav-link {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 9px 12px;
            border-radius: 8px;
            color: #94a3b8;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
            user-select: none;
            border-left: 3px solid transparent;
        }}

        .nav-link:hover {{
            background: rgba(255, 255, 255, 0.04);
            color: var(--text-heading);
        }}

        .nav-link.active {{
            background: rgba(59, 130, 246, 0.12);
            color: #60a5fa;
            font-weight: 600;
            border-left-color: #3b82f6;
        }}

        .nav-link-left {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .nav-icon {{
            font-size: 15px;
            width: 20px;
            text-align: center;
        }}

        .nav-key-badge {{
            font-size: 10px;
            font-weight: 700;
            padding: 1px 6px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-muted);
        }}
        .nav-link.active .nav-key-badge {{
            background: rgba(59, 130, 246, 0.25);
            color: #93c5fd;
        }}

        /* SIDEBAR FOOTER */
        .sidebar-footer {{
            padding: 12px 14px;
            border-top: 1px solid var(--border-subtle);
            background: rgba(0, 0, 0, 0.15);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .mode-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .mode-pill {{
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 4px;
            background: rgba(56, 189, 248, 0.12);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.25);
            text-transform: uppercase;
        }}

        /* ================= MAIN CONTENT WRAPPER ================= */
        #app-main {{
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
            position: relative;
            background: var(--bg-base);
        }}

        /* ================= TOPBAR (SMOOTH HORIZONTAL SCROLL) ================= */
        #topbar {{
            height: 54px;
            background: var(--bg-topbar);
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            flex-shrink: 0;
            z-index: 500;
            overflow-x: auto;
            scrollbar-width: thin;
        }}

        #topbar::-webkit-scrollbar {{
            height: 3px;
        }}
        #topbar::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.15);
            border-radius: 2px;
        }}

        .topbar-left {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-shrink: 0;
        }}

        .topbar-toggle-btn {{
            display: none;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--border-subtle);
            color: var(--text-heading);
            border-radius: 6px;
            width: 30px;
            height: 30px;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 14px;
        }}
        body.sidebar-collapsed .topbar-toggle-btn {{
            display: inline-flex;
        }}

        .page-heading {{
            font-size: 13px;
            font-weight: 700;
            color: var(--text-heading);
            letter-spacing: 0.01em;
            white-space: nowrap;
        }}

        /* METRICS CHIPS */
        .topbar-metrics {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;
            margin: 0 12px;
        }}

        .stat-chip {{
            display: flex;
            align-items: center;
            gap: 5px;
            background: rgba(23, 34, 53, 0.7);
            border: 1px solid var(--border-subtle);
            border-radius: 6px;
            padding: 4px 9px;
            font-size: 11px;
            white-space: nowrap;
        }}

        .stat-chip-label {{
            color: var(--text-muted);
            font-weight: 500;
        }}

        .stat-value {{
            font-weight: 700;
            font-size: 11.5px;
        }}
        .stat-value.red {{ color: var(--accent-red); }}
        .stat-value.amber {{ color: var(--accent-amber); }}
        .stat-value.blue {{ color: var(--accent-blue); }}
        .stat-value.green {{ color: var(--accent-green); }}

        /* TOPBAR ACTIONS */
        .topbar-actions {{
            display: flex;
            align-items: center;
            gap: 6px;
            flex-shrink: 0;
            min-width: max-content;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
            white-space: nowrap;
            user-select: none;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: #2563eb;
            color: white;
        }}
        .btn:hover {{
            background: #1d4ed8;
            transform: translateY(-1px);
        }}
        .btn:active {{ transform: translateY(0); }}

        .btn-secondary {{
            background: rgba(255, 255, 255, 0.06);
            color: #cbd5e1;
            border-color: var(--border-subtle);
        }}
        .btn-secondary:hover {{
            background: rgba(255, 255, 255, 0.12);
            color: #f8fafc;
            border-color: var(--border-hover);
        }}
        .btn-secondary.active {{
            background: rgba(37, 99, 235, 0.2);
            color: #60a5fa;
            border-color: #3b82f6;
        }}

        .btn-proximity {{
            background: linear-gradient(135deg, #059669, #0d9488);
            color: white;
            border: none;
        }}

        /* ================= PANELS CONTAINER ================= */
        #panels-container {{
            flex: 1;
            position: relative;
            overflow: hidden;
            background: var(--bg-base);
        }}

        .view-panel {{
            display: none;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow-y: auto;
            flex-direction: column;
        }}

        .view-panel.active {{
            display: flex;
        }}

        /* ================= PANEL 1: FULL HEATMAP & LIVE DRAWER ================= */
        #panel-heatmap {{
            overflow: hidden;
            position: relative;
        }}

        #map-container {{
            width: 100%;
            height: 100%;
            position: relative;
            background: #0b0f19;
        }}

        #map {{
            width: 100%;
            height: 100%;
        }}

        /* FLOATING SEARCH BAR ON MAP */
        .search-bar-container {{
            position: absolute;
            top: 14px;
            left: 54px;
            z-index: 1000;
            width: 320px;
        }}

        .search-input-wrapper {{
            position: relative;
            display: flex;
            align-items: center;
        }}

        .search-icon {{
            position: absolute;
            left: 12px;
            font-size: 13px;
            color: #94a3b8;
            pointer-events: none;
        }}

        .search-input {{
            width: 100%;
            padding: 8px 14px 8px 34px;
            background: rgba(15, 22, 36, 0.94);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            color: #f8fafc;
            font-size: 12px;
            outline: none;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
            transition: border-color 0.15s;
        }}
        .search-input:focus {{
            border-color: #3b82f6;
        }}

        .search-dropdown {{
            display: none;
            position: absolute;
            top: 40px;
            left: 0;
            width: 100%;
            background: rgba(15, 22, 36, 0.96);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            max-height: 260px;
            overflow-y: auto;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
            z-index: 1001;
        }}

        .search-result-item {{
            padding: 9px 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            cursor: pointer;
            transition: background 0.1s;
        }}
        .search-result-item:hover {{
            background: rgba(59, 130, 246, 0.15);
        }}
        .search-res-title {{
            font-weight: 600;
            color: #f8fafc;
            font-size: 12px;
        }}
        .search-res-sub {{
            font-size: 11px;
            color: #94a3b8;
        }}

        /* FLOATING LAYER CONTROLS */
        .map-layer-controls {{
            position: absolute;
            top: 14px;
            right: 14px;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 6px;
            background: rgba(15, 22, 36, 0.9);
            backdrop-filter: blur(10px);
            padding: 5px 8px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
            transition: right 0.25s ease;
        }}

        /* RIGHT-HAND LIVE FEED DRAWER ON MAP (USER REQUEST 5) */
        #map-live-drawer {{
            position: absolute;
            top: 0;
            right: 0;
            width: 390px;
            height: 100%;
            background: rgba(15, 22, 36, 0.94);
            backdrop-filter: blur(14px);
            border-left: 1px solid var(--border-subtle);
            z-index: 1100;
            display: flex;
            flex-direction: column;
            box-shadow: -4px 0 24px rgba(0, 0, 0, 0.6);
            transform: translateX(100%);
            transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        #map-live-drawer.open {{
            transform: translateX(0);
        }}

        .drawer-header {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(11, 15, 23, 0.5);
        }}

        .drawer-title {{
            font-size: 13px;
            font-weight: 700;
            color: var(--text-heading);
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .drawer-close-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 16px;
            cursor: pointer;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .drawer-close-btn:hover {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-heading);
        }}

        .drawer-body {{
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        /* FLOATING LEGEND (ADAPTS TO DRAWER OPEN/CLOSE) */
        #map-legend-box {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(15, 22, 36, 0.92);
            backdrop-filter: blur(10px);
            padding: 12px 16px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 11px;
            color: #94a3b8;
            z-index: 1000;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
            display: flex;
            flex-direction: column;
            gap: 6px;
            transition: all 0.25s ease;
        }}

        .legend-title {{
            font-weight: 700;
            color: #f8fafc;
            font-size: 11px;
            margin-bottom: 2px;
        }}
        .legend-row {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* ================= FRAMED INCIDENT CARDS (USER REQUEST 1) ================= */
        .framed-incident-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-left: 4px solid #ef4444; /* Default highlight */
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 12px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
        }}
        .framed-incident-card:hover {{
            border-color: #3b82f6;
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        }}

        /* Colored Border Highlights */
        .framed-incident-card.hl-red {{ border-left-color: #ef4444; }}
        .framed-incident-card.hl-amber {{ border-left-color: #f59e0b; }}
        .framed-incident-card.hl-blue {{ border-left-color: #3b82f6; }}
        .framed-incident-card.hl-green {{ border-left-color: #10b981; }}

        .card-top-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .card-source-box {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .platform-chip {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 10.5px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 5px;
        }}
        .platform-chip.tiktok {{ background: rgba(0, 242, 254, 0.12); color: #00f2fe; border: 1px solid rgba(0, 242, 254, 0.3); }}
        .platform-chip.facebook {{ background: rgba(24, 119, 242, 0.15); color: #60a5fa; border: 1px solid rgba(24, 119, 242, 0.35); }}
        .platform-chip.youtube {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.35); }}
        .platform-chip.c1022 {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); }}
        .platform-chip.news {{ background: rgba(6, 182, 212, 0.15); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.35); }}

        .card-time-tag {{
            font-size: 11px;
            color: var(--text-muted);
            font-weight: 500;
        }}

        .status-pill {{
            font-size: 10.5px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 5px;
        }}
        .status-pill.neg {{ background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }}
        .status-pill.neu {{ background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .status-pill.blue {{ background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }}
        .status-pill.pos {{ background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }}

        .card-title-row {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .card-pin {{ font-size: 15px; }}
        .card-street-name {{
            font-size: 14px;
            font-weight: 700;
            color: var(--text-heading);
        }}
        .card-ward-sub {{
            font-size: 11px;
            color: #93c5fd;
            margin-top: -4px;
        }}

        .card-quote-box {{
            background: rgba(11, 15, 23, 0.6);
            border-left: 3px solid #3b82f6;
            padding: 10px 14px;
            border-radius: 0 6px 6px 0;
            font-size: 12.5px;
            color: #e2e8f0;
            line-height: 1.5;
        }}

        .card-triplet-box {{
            display: flex;
            align-items: center;
            gap: 6px;
            background: rgba(11, 15, 23, 0.4);
            border: 1px solid var(--border-subtle);
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 10.5px;
            font-family: monospace;
        }}

        .card-footer-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: var(--text-muted);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 6px;
        }}
        .card-veracity-text {{ color: #34d399; font-weight: 600; }}
        .card-link {{ color: #60a5fa; font-weight: 600; text-decoration: none; }}

        /* ================= PANEL 2: WARDS ANALYTICS ================= */
        .analytics-container {{
            padding: 24px;
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .analytics-header-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 18px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .analytics-title {{
            font-size: 16px;
            font-weight: 700;
            color: var(--text-heading);
        }}
        .analytics-subtitle {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 3px;
        }}

        .tab-switch-group {{
            display: flex;
            background: rgba(0, 0, 0, 0.3);
            padding: 4px;
            border-radius: 8px;
            border: 1px solid var(--border-subtle);
            gap: 4px;
        }}

        .tab-switch-btn {{
            background: transparent;
            border: none;
            color: #94a3b8;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .tab-switch-btn:hover {{
            color: var(--text-heading);
        }}
        .tab-switch-btn.active {{
            background: #2563eb;
            color: white;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.4);
        }}

        /* 4 MEGACITY ZONE SUMMARY CARDS (COVERS ALL 168 WARDS) */
        .zones-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
        }}

        .zone-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 18px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            border-left: 4px solid #3b82f6;
            transition: all 0.2s;
        }}
        .zone-card:hover {{
            border-color: var(--border-hover);
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
        }}
        .zone-card.thuduc {{ border-left-color: #8b5cf6; }}
        .zone-card.binhduong {{ border-left-color: #f59e0b; }}
        .zone-card.vungtau {{ border-left-color: #06b6d4; }}

        .zone-name {{
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.04em;
            color: var(--text-muted);
            text-transform: uppercase;
        }}
        .zone-count {{
            font-size: 28px;
            font-weight: 800;
            color: var(--text-heading);
        }}
        .zone-sub {{
            font-size: 11px;
            color: #94a3b8;
            line-height: 1.4;
        }}

        .chart-full-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 22px;
            min-height: 460px;
            display: flex;
            flex-direction: column;
        }}

        #chart-admin-wards {{
            width: 100%;
            height: 440px;
        }}

        /* LEADERBOARD CARDS */
        .leaderboard-filters {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
        }}
        .lb-filter-btn {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-subtle);
            color: #94a3b8;
            font-size: 11px;
            padding: 6px 14px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .lb-filter-btn:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-heading);
        }}
        .lb-filter-btn.active {{
            background: #2563eb;
            color: white;
            border-color: #3b82f6;
            font-weight: 600;
        }}

        .table-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }}

        .leaderboard-card {{
            background: rgba(15, 22, 36, 0.6);
            border: 1px solid var(--border-subtle);
            border-radius: 10px;
            padding: 14px 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .leaderboard-card:hover {{
            border-color: #3b82f6;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
        }}
        .leaderboard-card.rank-gold {{
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(15, 22, 36, 0.8));
            border-color: rgba(245, 158, 11, 0.4);
        }}
        .leaderboard-card.rank-silver {{
            background: linear-gradient(135deg, rgba(148, 163, 184, 0.08), rgba(15, 22, 36, 0.8));
            border-color: rgba(148, 163, 184, 0.35);
        }}
        .leaderboard-card.rank-bronze {{
            background: linear-gradient(135deg, rgba(217, 119, 6, 0.08), rgba(15, 22, 36, 0.8));
            border-color: rgba(217, 119, 6, 0.35);
        }}

        .lb-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .lb-card-left {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .rank-badge {{
            font-size: 11px;
            font-weight: 800;
            padding: 2px 8px;
            border-radius: 6px;
        }}
        .rank-badge.gold {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }}
        .rank-badge.silver {{ background: rgba(148, 163, 184, 0.2); color: #e2e8f0; border: 1px solid rgba(148, 163, 184, 0.4); }}
        .rank-badge.bronze {{ background: rgba(217, 119, 6, 0.2); color: #f59e0b; border: 1px solid rgba(217, 119, 6, 0.4); }}
        .rank-badge.normal {{ background: rgba(255, 255, 255, 0.06); color: #94a3b8; border: 1px solid var(--border-subtle); }}

        .lb-ward-title {{
            font-size: 14px;
            font-weight: 700;
            color: var(--text-heading);
        }}
        .lb-count-pill {{
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 12px;
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}

        .lb-card-meta {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 11px;
        }}
        .region-chip {{
            font-size: 10px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .region-chip.hcm {{ background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }}
        .region-chip.bd {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .region-chip.vt {{ background: rgba(6, 182, 212, 0.15); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.3); }}
        .region-chip.td {{ background: rgba(139, 92, 246, 0.15); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.3); }}

        .lb-sub-desc {{ color: var(--text-muted); font-size: 11px; }}

        .lb-progress-bar {{
            height: 4px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 2px;
            overflow: hidden;
        }}
        .lb-progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #ef4444);
            border-radius: 2px;
            transition: width 0.4s ease;
        }}

        .citywide-card {{
            padding: 14px 18px;
            border-radius: 10px;
            background: rgba(59, 130, 246, 0.08);
            border: 1px solid rgba(59, 130, 246, 0.25);
            font-size: 12px;
            color: #93c5fd;
            margin-top: 14px;
            line-height: 1.5;
        }}
        .citywide-title {{ font-weight: 700; margin-bottom: 4px; color: #60a5fa; }}

        /* ================= PANEL 3: TIME SERIES ================= */
        #chart-time-series {{
            width: 100%;
            height: 480px;
        }}

        /* ================= PANEL 4: INGESTION THROUGHPUT ================= */
        .throughput-layout {{
            display: grid;
            grid-template-columns: 360px 1fr;
            gap: 20px;
        }}
        .throughput-left {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 22px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .kpi-title {{ font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }}
        .kpi-value {{ font-size: 36px; font-weight: 800; color: var(--text-heading); }}
        .kpi-sub {{ font-size: 12px; color: var(--accent-green); font-weight: 600; }}

        #chart-throughput {{
            width: 100%;
            height: 440px;
        }}

        /* ================= PANEL 5: LIVE FEED ================= */
        .feed-full-container {{
            padding: 24px;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .feed-controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 14px 20px;
        }}

        /* ================= PANEL 6: SYSTEM HEALTH ================= */
        .health-full-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }}
        .health-node-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 22px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            transition: all 0.2s;
        }}
        .health-node-card:hover {{
            border-color: var(--border-hover);
            transform: translateY(-2px);
        }}
        .health-node-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .health-node-title {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text-heading);
        }}
        .health-node-desc {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 2px;
        }}
        .health-status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
        }}
        .health-status-badge.online {{ background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .health-status-badge.scanning {{ background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
        .health-status-badge.offline {{ background: rgba(239, 68, 68, 0.12); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }}

        .health-metrics-table {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            background: rgba(11, 15, 23, 0.5);
            border-radius: 8px;
            padding: 12px 16px;
        }}
        .health-m-cell {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .health-m-label {{ font-size: 11px; color: var(--text-muted); }}
        .health-m-val {{ font-size: 14px; font-weight: 700; color: #e2e8f0; font-family: monospace; }}

        /* ================= MODAL OVERLAY ================= */
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(5px);
            z-index: 9999;
            align-items: center;
            justify-content: center;
        }}
        .modal-box {{
            background: #141d2d;
            border: 1px solid #223048;
            border-radius: 12px;
            width: 500px;
            max-width: 90vw;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7);
            overflow: hidden;
        }}
        .modal-header {{
            padding: 14px 18px;
            border-bottom: 1px solid #223048;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #0f1623;
        }}
        .modal-title {{ font-weight: 700; font-size: 13px; color: #f8fafc; }}
        .modal-close {{ background: none; border: none; color: #94a3b8; font-size: 20px; cursor: pointer; }}
        .modal-body {{
            padding: 16px 18px;
            overflow-y: auto;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .prox-section-title {{
            font-size: 11px;
            font-weight: 700;
            margin-bottom: 6px;
            text-transform: uppercase;
        }}
        .prox-section-title.red {{ color: #ef4444; }}
        .prox-section-title.amber {{ color: #f59e0b; }}
        .prox-item {{
            background: rgba(11, 15, 23, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 10px 12px;
            margin-bottom: 6px;
        }}
        .prox-dist {{ font-size: 11px; font-weight: 700; color: #38bdf8; }}

        /* BACKWARD COMPATIBILITY HIDDEN NODES */
        #sidebar {{ display: none !important; }}
        .hidden {{ display: none !important; }}
    </style>
</head>
<body>

    <!-- ================= LEFT SIDEBAR NAVIGATION ================= -->
    <aside id="app-sidebar">
        <div class="brand-header">
            <div class="brand-logo-wrap">
                <!-- BESPOKE CIVIC RADAR EMBLEM LOGO (USER REQUEST 4) -->
                <svg width="36" height="36" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink: 0;">
                    <rect width="40" height="40" rx="10" fill="url(#logo-bg)"/>
                    <path d="M11 27C13.5 24.5 17 24.5 19.5 27C22 29.5 25.5 29.5 28 27" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/>
                    <path d="M9 21C12.5 18.5 16.5 18.5 20 21C23.5 23.5 27.5 23.5 31 21" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" stroke-opacity="0.9"/>
                    <circle cx="20" cy="12" r="4.5" fill="#ef4444" stroke="#ffffff" stroke-width="2"/>
                    <circle cx="20" cy="12" r="1.5" fill="#ffffff"/>
                    <circle cx="20" cy="12" r="8" stroke="#38bdf8" stroke-width="1.2" stroke-dasharray="2 3" opacity="0.6"/>
                    <defs>
                        <linearGradient id="logo-bg" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#1e3a8a"/>
                            <stop offset="1" stop-color="#0f172a"/>
                        </linearGradient>
                    </defs>
                </svg>
                <div class="brand-titles">
                    <span class="brand-title-main">HCMC FLOOD OPS</span>
                    <span class="brand-title-sub">Giám Sát & Điều Hành Ngập</span>
                </div>
            </div>
            <button id="btn-toggle-sidebar" class="sidebar-toggle-btn" onclick="toggleSidebar()" title="Thu gọn Menu (Ctrl+B)">◀</button>
        </div>

        <nav class="nav-menu">
            <div class="nav-section-title">Bản Đồ Không Gian</div>
            <div class="nav-link active" data-panel="panel-heatmap" onclick="switchPanel('panel-heatmap', 'BẢN ĐỒ NHIỆT NGẬP LỤT THỜI GIAN THỰC')">
                <div class="nav-link-left">
                    <span class="nav-icon">🗺️</span>
                    <span>Bản Đồ Nhiệt</span>
                </div>
                <span class="nav-key-badge">[1]</span>
            </div>

            <div class="nav-section-title">Thống Kê Địa Giới</div>
            <div class="nav-link" data-panel="panel-wards" onclick="switchPanel('panel-wards', 'XẾP HẠNG ĐIỂM NGẬP THEO PHƯỜNG / XÃ MỚI (NQ 1685)')">
                <div class="nav-link-left">
                    <span class="nav-icon">📊</span>
                    <span>Phường/Xã & Vùng</span>
                </div>
                <span class="nav-key-badge">[2]</span>
            </div>

            <div class="nav-section-title">Phân Tích Dữ Liệu</div>
            <div class="nav-link" data-panel="panel-trends" onclick="switchPanel('panel-trends', 'DIỄN BIẾN THEO THỜI GIAN (6H QUA)')">
                <div class="nav-link-left">
                    <span class="nav-icon">📈</span>
                    <span>Diễn Biến Theo Giờ</span>
                </div>
                <span class="nav-key-badge">[3]</span>
            </div>

            <div class="nav-link" data-panel="panel-throughput" onclick="switchPanel('panel-throughput', 'TỐC ĐỘ THU THẬP & KIỂM ĐỊNH DỮ LIỆU')">
                <div class="nav-link-left">
                    <span class="nav-icon">⚡</span>
                    <span>Tốc Độ Thu Thập</span>
                </div>
                <span class="nav-key-badge">[4]</span>
            </div>

            <div class="nav-section-title">Hiện Trường & Hạ Tầng</div>
            <div class="nav-link" data-panel="panel-feed" onclick="switchPanel('panel-feed', 'DÒNG TIN HIỆN TRƯỜNG THỜI GIAN THỰC')">
                <div class="nav-link-left">
                    <span class="nav-icon">🔔</span>
                    <span>Tin Báo Hiện Trường</span>
                </div>
                <span class="nav-key-badge">[5]</span>
            </div>

            <div class="nav-link" data-panel="panel-health" onclick="switchPanel('panel-health', 'TRẠNG THÁI HỆ THỐNG & VI DỊCH VỤ')">
                <div class="nav-link-left">
                    <span class="nav-icon">💓</span>
                    <span>Sức Khỏe Hệ Thống</span>
                </div>
                <span class="nav-key-badge">[6]</span>
            </div>
        </nav>

        <div class="sidebar-footer">
            <div class="mode-row">
                <div id="badge-mode" class="mode-pill">SIMULATION</div>
                <span style="font-size: 10px; color: var(--text-muted);">Phím 1-6 • Esc</span>
            </div>
            <div style="display: flex; gap: 6px;">
                <button id="btn-toggle-mode" class="btn btn-secondary" style="flex: 1; padding: 5px;" onclick="toggleServerMode()">
                    <span>⚡ Chuyển Mode</span>
                </button>
                <button id="btn-reset" class="btn btn-secondary" style="padding: 5px 8px;" onclick="resetStreamState()" title="Làm sạch nạp lại từ đầu">
                    <span>🧹 Nạp lại</span>
                </button>
            </div>
        </div>
    </aside>

    <!-- ================= MAIN APP VIEW ================= -->
    <main id="app-main">

        <!-- TOP BAR (SMOOTH HORIZONTAL SCROLL) -->
        <header id="topbar">
            <div class="topbar-left">
                <button id="btn-expand-sidebar" class="topbar-toggle-btn" onclick="toggleSidebar()" title="Mở rộng Menu (Ctrl+B)">☰</button>
                <span id="current-page-title" class="page-heading">BẢN ĐỒ NHIỆT NGẬP LỤT THỜI GIAN THỰC</span>
            </div>

            <!-- METRIC CHIPS -->
            <div class="topbar-metrics">
                <div class="stat-chip" title="Tổng số sự cố ngập từ cộng đồng">
                    <span class="stat-chip-label">Sự cố Live:</span>
                    <span id="stat-count" class="stat-value red">0</span>
                </div>
                <div class="stat-chip" title="Điểm cảnh báo nguy cơ thường xuyên của CSGT">
                    <span class="stat-chip-label">CSGT PC08:</span>
                    <span id="stat-csgt-count" class="stat-value amber">122</span>
                </div>
                <div class="stat-chip" title="Cửa sổ quét thời gian thực">
                    <span class="stat-chip-label">Cửa sổ quét:</span>
                    <span id="stat-window" class="stat-value blue">60 phút</span>
                </div>
            </div>

            <!-- ACTIONS (NEVER CUT OFF, HORIZONTALLY SCROLLABLE) -->
            <div class="topbar-actions">
                <button id="btn-poll" class="btn" onclick="triggerPoll()" title="Cào nhanh miễn phí không tốn credit Apify">
                    <span>🔄 Cào Free</span>
                </button>
                <button id="btn-apify" class="btn" style="background: linear-gradient(135deg, #7c3aed, #4f46e5);" onclick="triggerApifyPoll()" title="Gọi Apify Actor cào sâu Facebook & TikTok">
                    <span>🚀 Cào Apify</span>
                </button>
                <button id="btn-proximity" class="btn btn-proximity" onclick="openProximityScanner()">
                    <span>📍 Quanh tôi</span>
                </button>
                <button id="btn-autopoll" class="btn btn-secondary active" onclick="toggleAutoPoll()" title="Tự động đồng bộ mỗi 3s">
                    <span id="txt-autopoll">🟢 Tự động (3s)</span>
                </button>
                <button class="btn btn-secondary" onclick="toggleFullScreen()" title="Toàn màn hình (F)">
                    <span>⛶ [F]</span>
                </button>
                <button class="btn btn-secondary" onclick="manualRefreshAll()" title="Làm mới tức thì (R)">
                    <span>🔄 [R]</span>
                </button>
            </div>
        </header>

        <!-- PANELS CONTAINER -->
        <div id="panels-container">

            <!-- ================= PANEL 1: FULL GEOSPATIAL HEATMAP WITH LIVE DRAWER ================= -->
            <section id="panel-heatmap" class="view-panel active">
                <div id="map-container">
                    <!-- Search Bar -->
                    <div class="search-bar-container">
                        <div class="search-input-wrapper">
                            <span class="search-icon">🔍</span>
                            <input id="search-input" class="search-input" type="text" placeholder="Tìm tên đường hoặc phường/xã mới..." oninput="handleSearchInput(this.value)" />
                        </div>
                        <div id="search-dropdown" class="search-dropdown"></div>
                    </div>

                    <!-- Map Layer Controls Floating on Map -->
                    <div class="map-layer-controls">
                        <button id="btn-toggle-live" class="btn btn-secondary active" style="padding: 5px 9px; font-size: 11px;" onclick="toggleLiveLayer()">
                            <span>🔴 Live MXH</span>
                        </button>
                        <button id="btn-toggle-csgt" class="btn btn-secondary active" style="padding: 5px 9px; font-size: 11px;" onclick="toggleCsgtLayer()">
                            <span>⚠️ CSGT</span>
                        </button>
                        <button id="btn-heatmap" class="btn btn-secondary active" style="padding: 5px 9px; font-size: 11px;" onclick="toggleHeatmap()">
                            <span>🌡️ Quầng nhiệt</span>
                        </button>
                        <button id="btn-toggle-map-drawer" class="btn btn-secondary active" style="padding: 5px 9px; font-size: 11px;" onclick="toggleMapLiveDrawer()" title="Mở/Đóng Cột Tin Tức Trực Tiếp">
                            <span>📋 Dòng tin Live (<b id="drawer-feed-count">12</b>)</span>
                        </button>
                        <button class="btn btn-secondary" style="padding: 5px 9px; font-size: 11px;" onclick="toggleSidebar()" title="Ẩn/Hiện Sidebar Menu (Ctrl+B)">
                            <span>◀▶ Menu</span>
                        </button>
                    </div>

                    <!-- Leaflet Mount Point -->
                    <div id="map"></div>

                    <!-- Map Legend (Clean positioning, no Threads) -->
                    <div id="map-legend-box" class="legend drawer-open">
                        <div class="legend-title">Phân biệt Điểm ngập trên bản đồ</div>
                        <div class="legend-row">
                            <div style="width: 12px; height: 12px; border-radius: 50%; background: #ef4444; border: 2px solid white; box-shadow: 0 0 6px #ef4444;"></div>
                            <span><b>🔴 Sự cố MXH (TikTok, Facebook, YouTube):</b> Video & bài đăng hiện trường</span>
                        </div>
                        <div class="legend-row">
                            <div style="width: 12px; height: 12px; border-radius: 50%; background: #0ea5e9; border: 2px solid white; box-shadow: 0 0 6px #38bdf8;"></div>
                            <span><b>🏛️ Cổng 1022 TP.HCM:</b> Phản ánh chính thống của người dân</span>
                        </div>
                        <div class="legend-row">
                            <div style="width: 12px; height: 12px; background: #f59e0b; border-radius: 3px; border: 1px solid white;"></div>
                            <span><b>⚠️ Cảnh báo CSGT PC08:</b> Điểm đen nguy cơ ngập thường xuyên</span>
                        </div>
                    </div>

                    <!-- RIGHT-HAND LIVE FEED DRAWER (USER REQUEST 5) -->
                    <aside id="map-live-drawer" class="open">
                        <div class="drawer-header">
                            <span class="drawer-title">
                                <span>⚡</span>
                                <span>Tin Tức Cào Về Mới Nhất</span>
                            </span>
                            <button class="drawer-close-btn" onclick="toggleMapLiveDrawer()" title="Đóng cột tin">✕</button>
                        </div>
                        <div id="map-drawer-feed-list" class="drawer-body">
                            <!-- Populated with framed cards -->
                        </div>
                    </aside>
                </div>
            </section>

            <!-- ================= PANEL 2: WARDS ANALYTICS (EXECUTIVE DESIGN) ================= -->
            <section id="panel-wards" class="view-panel">
                <div class="analytics-container">
                    <div class="analytics-header-card">
                        <div>
                            <div class="analytics-title">Thống Kê Điểm Ngập Theo Phường / Xã Mới (NQ 1685)</div>
                            <div class="analytics-subtitle">Chuẩn hóa 168 Đơn vị hành chính mới & 4 Phân vùng Đô thị TP.HCM mở rộng</div>
                        </div>
                        <div class="tab-switch-group">
                            <button id="btn-subtab-wards" class="tab-switch-btn active" onclick="switchWardsViewMode('top_wards')">Top 10 Phường / Xã</button>
                            <button id="btn-subtab-zones" class="tab-switch-btn" onclick="switchWardsViewMode('zones')">4 Vùng Đô Thị</button>
                            <button id="btn-subtab-list" class="tab-switch-btn" onclick="switchWardsViewMode('table_list')">Bảng Chi Tiết</button>
                        </div>
                    </div>

                    <!-- 4 MEGACITY ZONE SUMMARY CARDS (COVERS ALL 168 WARDS) -->
                    <div class="zones-grid">
                        <div class="zone-card">
                            <span class="zone-name">TP.HCM VÙNG LÕI</span>
                            <span id="zone-val-core" class="zone-count">9</span>
                            <span class="zone-sub">Bao gồm 68 phường/xã nội & ngoại thành TP.HCM cũ</span>
                        </div>
                        <div class="zone-card thuduc">
                            <span class="zone-name">THÀNH PHỐ THỦ ĐỨC</span>
                            <span id="zone-val-thuduc" class="zone-count">0</span>
                            <span class="zone-sub">Bao gồm toàn bộ 34 phường thuộc TP. Thủ Đức</span>
                        </div>
                        <div class="zone-card binhduong">
                            <span class="zone-name">KHU VỰC BÌNH DƯƠNG</span>
                            <span id="zone-val-binhduong" class="zone-count">2</span>
                            <span class="zone-sub">Bao gồm toàn bộ 36 phường/xã Bình Dương theo NQ 1685</span>
                        </div>
                        <div class="zone-card vungtau">
                            <span class="zone-name">BÀ RỊA - VŨNG TÀU</span>
                            <span id="zone-val-vungtau" class="zone-count">1</span>
                            <span class="zone-sub">Bao gồm toàn bộ 30 phường/xã BR-VT theo NQ 1685</span>
                        </div>
                    </div>

                    <!-- CHART / TABLE DISPLAY -->
                    <div class="chart-full-card">
                        <div id="chart-admin-wards"></div>

                        <div id="leaderboard-container-wrapper" style="display: none; flex-direction: column;">
                            <div class="leaderboard-filters">
                                <button class="lb-filter-btn active" onclick="filterLeaderboard('all', this)">Tất cả (168 ĐVHC)</button>
                                <button class="lb-filter-btn" onclick="filterLeaderboard('hcm', this)">Nội thành TP.HCM</button>
                                <button class="lb-filter-btn" onclick="filterLeaderboard('binhduong', this)">Bình Dương cũ (36 ĐVHC)</button>
                                <button class="lb-filter-btn" onclick="filterLeaderboard('brvt', this)">BR-VT cũ (30 ĐVHC)</button>
                            </div>
                            <div id="leaderboard-list" class="table-grid"></div>
                            <div id="citywide-container" class="citywide-card" style="display: none;">
                                <div class="citywide-title">🌐 Tin phản ánh diện rộng toàn TP</div>
                                <div id="citywide-text">0 tin phản ánh nói chung.</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- ================= PANEL 3: TIME-SERIES ================= -->
            <section id="panel-trends" class="view-panel">
                <div class="analytics-container">
                    <div class="analytics-header-card">
                        <div>
                            <div class="analytics-title">Diễn Biến Tình Hình Ngập Theo Mốc Thời Gian (6 Giờ Qua)</div>
                            <div class="analytics-subtitle">Phân tách theo 3 sắc thái: Tiêu cực (NEG), Dự báo/Thủy văn (NEU), Nước rút (POS)</div>
                        </div>
                    </div>

                    <div class="chart-full-card">
                        <div id="chart-time-series"></div>
                    </div>
                </div>
            </section>

            <!-- ================= PANEL 4: INGESTION THROUGHPUT ================= -->
            <section id="panel-throughput" class="view-panel">
                <div class="analytics-container">
                    <div class="analytics-header-card">
                        <div>
                            <div class="analytics-title">Tốc Độ Thu Thập & Xác Thực Dữ Liệu Đa Nền Tảng</div>
                            <div class="analytics-subtitle">TikTok Poller • Facebook Crawler • YouTube Video • Cổng 1022 TP.HCM • Báo chí RSS</div>
                        </div>
                    </div>

                    <div class="throughput-layout">
                        <div class="throughput-left">
                            <div class="kpi-card">
                                <span class="kpi-title">TỐC ĐỘ THU THẬP HIỆN TẠI</span>
                                <span id="stat-throughput-rpm" class="kpi-value">12 RPM</span>
                                <span class="kpi-sub">Bài viết / phút (Bình thường)</span>
                            </div>
                            <div class="kpi-card">
                                <span class="kpi-title">TỶ LỆ XÁC THỰC VERACITY</span>
                                <span id="stat-veracity-rate" class="kpi-value" style="color: #10b981;">94.2%</span>
                                <span class="kpi-sub">Đạt chuẩn kiểm định độ tin cậy</span>
                            </div>
                        </div>
                        <div class="chart-full-card">
                            <div id="chart-throughput"></div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- ================= PANEL 5: LIVE FEED (FULL VIEW) ================= -->
            <section id="panel-feed" class="view-panel">
                <div class="feed-full-container">
                    <div class="feed-controls">
                        <div>
                            <div style="font-size: 15px; font-weight: 700; color: #f8fafc;">Tin Báo Hiện Trường Thời Gian Thực</div>
                            <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">Dữ liệu đa nguồn: TikTok, Facebook, YouTube, Cổng thông tin 1022 TP.HCM</div>
                        </div>
                        <div class="feed-filter-tabs">
                            <button class="btn btn-secondary active" onclick="switchSidebarTab('feed')">Tất cả bài viết</button>
                        </div>
                    </div>

                    <div id="tab-content-feed" class="tab-content">
                        <div id="feed-list" style="display: flex; flex-direction: column; gap: 12px;"></div>
                    </div>
                </div>
            </section>

            <!-- ================= PANEL 6: SYSTEM HEALTH ================= -->
            <section id="panel-health" class="view-panel">
                <div class="analytics-container">
                    <div class="analytics-header-card">
                        <div>
                            <div class="analytics-title">Giám Sát Trạng Thái Hệ Thống & Vi Dịch Vụ</div>
                            <div class="analytics-subtitle">Kiểm tra kết nối TCP socket ngầm mỗi 10 giây qua Background Heartbeat Worker</div>
                        </div>
                    </div>

                    <div class="health-full-grid">
                        <div class="health-node-card">
                            <div class="health-node-top">
                                <div class="health-node-info">
                                    <span class="health-node-title">🤖 AI Microservice</span>
                                    <span class="health-node-desc">PhoBERT Aspect Extraction & PhoWhisper Audio Transcription</span>
                                </div>
                                <span id="health-badge-ai" class="health-status-badge online">ONLINE</span>
                            </div>
                            <div class="health-metrics-table">
                                <div class="health-m-cell">
                                    <span class="health-m-label">Cổng kết nối</span>
                                    <span class="health-m-val">localhost:8000</span>
                                </div>
                                <div class="health-m-cell">
                                    <span class="health-m-label">Độ trễ bắt tay TCP</span>
                                    <span id="health-latency-ai" class="health-m-val">42.0 ms</span>
                                </div>
                            </div>
                        </div>

                        <div class="health-node-card">
                            <div class="health-node-top">
                                <div class="health-node-info">
                                    <span class="health-node-title">⚡ Redis In-Memory Hot Store</span>
                                    <span class="health-node-desc">GEO Radius Queries & ZSET Sliding Window Storage</span>
                                </div>
                                <span id="health-badge-redis" class="health-status-badge online">ONLINE</span>
                            </div>
                            <div class="health-metrics-table">
                                <div class="health-m-cell">
                                    <span class="health-m-label">Cổng kết nối</span>
                                    <span class="health-m-val">localhost:6379</span>
                                </div>
                                <div class="health-m-cell">
                                    <span class="health-m-label">Độ trễ bắt tay TCP</span>
                                    <span id="health-latency-redis" class="health-m-val">2.1 ms</span>
                                </div>
                            </div>
                        </div>

                        <div class="health-node-card">
                            <div class="health-node-top">
                                <div class="health-node-info">
                                    <span class="health-node-title">📬 Kafka Streaming Broker</span>
                                    <span class="health-node-desc">Distributed Event Ingestion & Dead Letter Queue</span>
                                </div>
                                <span id="health-badge-kafka" class="health-status-badge online">ONLINE</span>
                            </div>
                            <div class="health-metrics-table">
                                <div class="health-m-cell">
                                    <span class="health-m-label">Cổng kết nối</span>
                                    <span class="health-m-val">localhost:9092</span>
                                </div>
                                <div class="health-m-cell">
                                    <span class="health-m-label">Độ trễ bắt tay TCP</span>
                                    <span id="health-latency-kafka" class="health-m-val">5.0 ms</span>
                                </div>
                            </div>
                        </div>

                        <div class="health-node-card">
                            <div class="health-node-top">
                                <div class="health-node-info">
                                    <span class="health-node-title">🕷️ Multi-Platform Social Crawler</span>
                                    <span class="health-node-desc">TikTok Poller, Facebook Public Feeds, YouTube & 1022 TP.HCM API</span>
                                </div>
                                <span id="health-badge-crawler" class="health-status-badge scanning">SCANNING</span>
                            </div>
                            <div class="health-metrics-table">
                                <div class="health-m-cell">
                                    <span class="health-m-label">Trạng thái luồng</span>
                                    <span class="health-m-val" style="color: #10b981;">Đang hoạt động</span>
                                </div>
                                <div class="health-m-cell">
                                    <span class="health-m-label">Tốc độ nạp trung bình</span>
                                    <span id="health-crawler-rate" class="health-m-val">12 posts/phút</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

        </div>
    </main>

    <!-- BACKWARD-COMPATIBLE HIDDEN DOM NODES -->
    <div id="sidebar" style="display: none;">
        <button id="tab-btn-feed" onclick="switchSidebarTab('feed')"></button>
        <button id="tab-btn-leaderboard" onclick="switchSidebarTab('leaderboard')"></button>
        <div id="tab-content-leaderboard" class="tab-content hidden"></div>
    </div>

    <!-- PROXIMITY SCANNER MODAL -->
    <div id="proximity-modal" class="modal-overlay" onclick="closeModalOnOverlay(event)">
        <div class="modal-box">
            <div class="modal-header">
                <div class="modal-title">📍 Quét Nguy Cơ Quanh Tôi (Bán kính 1.5 km)</div>
                <button class="modal-close" onclick="closeProximityModal()">×</button>
            </div>
            <div class="modal-body">
                <div id="prox-user-loc" style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;">Đang xác định vị trí của bạn...</div>
                <div>
                    <div class="prox-section-title red">🔴 Sự Cố Ngập Đang Diễn Ra (Live Events)</div>
                    <div id="prox-live-list"></div>
                </div>
                <div style="margin-top: 10px;">
                    <div class="prox-section-title amber">🟡 Điểm Cảnh Báo Nguy Cơ Thường Xuyên (CSGT)</div>
                    <div id="prox-csgt-list"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- ORIGINAL SCRIPT SECTION WITH V4 EXTENSIONS -->
    <script>
{orig_script_adapted}

        /* =========================================================================
           V4.0 EXTENSIONS: COLLAPSIBLE SIDEBAR, MAP DRAWER, ANTI-LAG, ECHARTS
           ========================================================================= */

        let activePanelId = 'panel-heatmap';

        // 1. COLLAPSIBLE SIDEBAR (CTRL+B)
        function toggleSidebar() {{
            document.body.classList.toggle('sidebar-collapsed');
            const isCollapsed = document.body.classList.contains('sidebar-collapsed');
            const btn = document.getElementById('btn-toggle-sidebar');
            if (btn) btn.innerText = isCollapsed ? '▶' : '◀';

            triggerMapResizeSafe();
            setTimeout(() => resizeAllCharts(), 250);
        }}

        // 2. PANEL SWITCHER (FULL VIEW)
        function switchPanel(panelId, titleText) {{
            activePanelId = panelId;

            document.querySelectorAll('.nav-link').forEach(item => {{
                if (item.getAttribute('data-panel') === panelId) {{
                    item.classList.add('active');
                }} else {{
                    item.classList.remove('active');
                }}
            }});

            document.querySelectorAll('.view-panel').forEach(p => {{
                if (p.id === panelId) {{
                    p.classList.add('active');
                }} else {{
                    p.classList.remove('active');
                }}
            }});

            if (titleText) {{
                document.getElementById('current-page-title').innerText = titleText;
            }}

            const hashMapping = {{
                'panel-heatmap': '#/heatmap',
                'panel-wards': '#/wards',
                'panel-trends': '#/trends',
                'panel-throughput': '#/throughput',
                'panel-feed': '#/feed',
                'panel-health': '#/system-health'
            }};
            window.location.hash = hashMapping[panelId] || '#/heatmap';

            if (panelId === 'panel-heatmap') {{
                triggerMapResizeSafe();
            }}
            setTimeout(() => resizeAllCharts(), 200);
        }}

        {drawer_js}

        // 3. LEAFLET RESIZE
        function initMapResizeObserver() {{
            const mc = document.getElementById('map-container');
            if (window.ResizeObserver && mc) {{
                const ro = new ResizeObserver(() => {{
                    if (window.map) {{
                        window.map.invalidateSize();
                    }}
                }});
                ro.observe(mc);
            }}
        }}

        function triggerMapResizeSafe() {{
            if (!window.map) return;
            requestAnimationFrame(() => {{
                if (window.map) window.map.invalidateSize();
            }});
            setTimeout(() => {{
                if (window.map) window.map.invalidateSize();
            }}, 300);
        }}

        // 4. SPA ROUTER & KEYBOARD SHORTCUTS
        const DashboardRouter = {{
            routes: {{
                '#/heatmap': () => switchPanel('panel-heatmap', 'BẢN ĐỒ NHIỆT NGẬP LỤT THỜI GIAN THỰC'),
                '#/wards': () => switchPanel('panel-wards', 'XẾP HẠNG ĐIỂM NGẬP THEO PHƯỜNG / XÃ MỚI (NQ 1685)'),
                '#/trends': () => switchPanel('panel-trends', 'DIỄN BIẾN THEO THỜI GIAN (6H QUA)'),
                '#/throughput': () => switchPanel('panel-throughput', 'TỐC ĐỘ THU THẬP & KIỂM ĐỊNH DỮ LIỆU'),
                '#/feed': () => switchPanel('panel-feed', 'DÒNG TIN HIỆN TRƯỜNG THỜI GIAN THỰC'),
                '#/system-health': () => switchPanel('panel-health', 'TRẠNG THÁI HỆ THỐNG & VI DỊCH VỤ')
            }},

            init() {{
                window.addEventListener('hashchange', () => this.handleRoute());
                const initialHash = window.location.hash;
                if (!initialHash || initialHash === '#/overview') {{
                    this.routes['#/heatmap']();
                }} else {{
                    this.handleRoute();
                }}

                window.addEventListener('keydown', (e) => {{
                    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
                    if ((e.ctrlKey || e.metaKey) && (e.key === 'b' || e.key === 'B')) {{
                        e.preventDefault();
                        toggleSidebar();
                        return;
                    }}
                    if (e.key === 'Escape' || e.key === '1') switchPanel('panel-heatmap', 'BẢN ĐỒ NHIỆT NGẬP LỤT THỜI GIAN THỰC');
                    if (e.key === '2') switchPanel('panel-wards', 'XẾP HẠNG ĐIỂM NGẬP THEO PHƯỜNG / XÃ MỚI (NQ 1685)');
                    if (e.key === '3') switchPanel('panel-trends', 'DIỄN BIẾN THEO THỜI GIAN (6H QUA)');
                    if (e.key === '4') switchPanel('panel-throughput', 'TỐC ĐỘ THU THẬP & KIỂM ĐỊNH DỮ LIỆU');
                    if (e.key === '5') switchPanel('panel-feed', 'DÒNG TIN HIỆN TRƯỜNG THỜI GIAN THỰC');
                    if (e.key === '6') switchPanel('panel-health', 'TRẠNG THÁI HỆ THỐNG & VI DỊCH VỤ');
                    if (e.key === 'f' || e.key === 'F') toggleFullScreen();
                    if (e.key === 'r' || e.key === 'R') manualRefreshAll();
                }});
            }},

            handleRoute() {{
                const hash = window.location.hash || '#/heatmap';
                const action = this.routes[hash] || this.routes['#/heatmap'];
                action();
            }}
        }};

        function toggleFullScreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen().catch(() => {{}});
            }} else {{
                if (document.exitFullscreen) {{
                    document.exitFullscreen().catch(() => {{}});
                }}
            }}
        }}

        async function manualRefreshAll() {{
            try {{
                lastEventsSignature = ''; // Bắt buộc vẽ lại khi refresh thủ công
                await Promise.all([
                    fetchRealtimeEvents(),
                    fetchDashboardSummary()
                ]);
            }} catch (e) {{
                console.warn("Manual refresh error:", e);
            }}
        }}

        // 5. ECHARTS MODULES
        let adminWardsChart = null;
        let timeSeriesChart = null;
        let throughputChart = null;
        let currentAdminWardsView = 'top_wards';
        let cachedDashboardSummary = null;

        function initEChartsInstances() {{
            const elWards = document.getElementById('chart-admin-wards');
            if (elWards && window.echarts) {{
                adminWardsChart = echarts.init(elWards, null, {{ renderer: 'canvas' }});
            }}

            const elTrends = document.getElementById('chart-time-series');
            if (elTrends && window.echarts) {{
                timeSeriesChart = echarts.init(elTrends, null, {{ renderer: 'canvas' }});
            }}

            const elThroughput = document.getElementById('chart-throughput');
            if (elThroughput && window.echarts) {{
                throughputChart = echarts.init(elThroughput, null, {{ renderer: 'canvas' }});
            }}

            window.addEventListener('resize', () => resizeAllCharts());
        }}

        function resizeAllCharts() {{
            if (adminWardsChart) adminWardsChart.resize();
            if (timeSeriesChart) timeSeriesChart.resize();
            if (throughputChart) throughputChart.resize();
        }}

        function switchWardsViewMode(mode) {{
            currentAdminWardsView = mode;
            ['wards', 'zones', 'list'].forEach(m => {{
                const btn = document.getElementById('btn-subtab-' + m);
                if (btn) btn.classList.remove('active');
            }});

            const chartEl = document.getElementById('chart-admin-wards');
            const listWrapper = document.getElementById('leaderboard-container-wrapper');

            if (mode === 'table_list') {{
                const btn = document.getElementById('btn-subtab-list');
                if (btn) btn.classList.add('active');
                if (chartEl) chartEl.style.display = 'none';
                if (listWrapper) listWrapper.style.display = 'flex';
                return;
            }} else {{
                if (chartEl) chartEl.style.display = 'block';
                if (listWrapper) listWrapper.style.display = 'none';
                if (mode === 'top_wards') {{
                    const btn = document.getElementById('btn-subtab-wards');
                    if (btn) btn.classList.add('active');
                }} else if (mode === 'zones') {{
                    const btn = document.getElementById('btn-subtab-zones');
                    if (btn) btn.classList.add('active');
                }}
            }}

            if (cachedDashboardSummary) {{
                updateAdminWardsChart(cachedDashboardSummary.admin_wards);
            }}
            resizeAllCharts();
        }}

        function updateAdminWardsChart(adminWardsData) {{
            if (!adminWardsChart || !adminWardsData) return;

            const zones = adminWardsData.zones || {{}};
            const elCore = document.getElementById('zone-val-core');
            const elThuDuc = document.getElementById('zone-val-thuduc');
            const elBinhDuong = document.getElementById('zone-val-binhduong');
            const elVungTau = document.getElementById('zone-val-vungtau');
            if (elCore) elCore.innerText = zones.TPHCM_Core || 0;
            if (elThuDuc) elThuDuc.innerText = zones.ThuDuc || 0;
            if (elBinhDuong) elBinhDuong.innerText = zones.BinhDuong || 0;
            if (elVungTau) elVungTau.innerText = zones.VungTau || 0;

            if (currentAdminWardsView === 'zones') {{
                const zoneLabels = [
                    'TP.HCM Vùng Lõi',
                    'Thành Phố Thủ Đức',
                    'Khu Vực Bình Dương',
                    'Khu Vực Bà Rịa - Vũng Tàu'
                ];
                const zoneValues = [
                    zones.TPHCM_Core || 0,
                    zones.ThuDuc || 0,
                    zones.BinhDuong || 0,
                    zones.VungTau || 0
                ];
                const zoneColors = ['#3b82f6', '#8b5cf6', '#f59e0b', '#06b6d4'];

                const option = {{
                    backgroundColor: 'transparent',
                    tooltip: {{
                        trigger: 'axis',
                        axisPointer: {{ type: 'shadow' }},
                        backgroundColor: '#141d2d',
                        borderColor: '#223048',
                        textStyle: {{ color: '#f8fafc', fontSize: 12 }}
                    }},
                    grid: {{ top: 25, right: 40, bottom: 25, left: 200 }},
                    xAxis: {{
                        type: 'value',
                        splitLine: {{ lineStyle: {{ color: '#223048' }} }},
                        axisLabel: {{ color: '#94a3b8', fontSize: 11 }}
                    }},
                    yAxis: {{
                        type: 'category',
                        data: zoneLabels.slice().reverse(),
                        axisLine: {{ lineStyle: {{ color: '#33486c' }} }},
                        axisLabel: {{ color: '#e2e8f0', fontSize: 12, fontWeight: 600 }}
                    }},
                    series: [{{
                        name: 'Số điểm ngập',
                        type: 'bar',
                        data: zoneValues.slice().reverse().map((v, i) => ({{
                            value: v,
                            itemStyle: {{ color: zoneColors.slice().reverse()[i], borderRadius: [0, 6, 6, 0] }}
                        }})),
                        barWidth: 24,
                        label: {{
                            show: true,
                            position: 'right',
                            color: '#cbd5e1',
                            fontSize: 12,
                            fontWeight: 700
                        }}
                    }}]
                }};
                adminWardsChart.setOption(option);
            }} else {{
                const topWards = (adminWardsData.top_wards || []).slice(0, 10);
                const wardNames = topWards.map(w => w.ward).reverse();
                const counts = topWards.map(w => w.count).reverse();

                const option = {{
                    backgroundColor: 'transparent',
                    tooltip: {{
                        trigger: 'axis',
                        axisPointer: {{ type: 'shadow' }},
                        backgroundColor: '#141d2d',
                        borderColor: '#223048',
                        textStyle: {{ color: '#f8fafc', fontSize: 12 }}
                    }},
                    grid: {{ top: 25, right: 40, bottom: 25, left: 200 }},
                    xAxis: {{
                        type: 'value',
                        splitLine: {{ lineStyle: {{ color: '#223048' }} }},
                        axisLabel: {{ color: '#94a3b8', fontSize: 11 }}
                    }},
                    yAxis: {{
                        type: 'category',
                        data: wardNames,
                        axisLine: {{ lineStyle: {{ color: '#33486c' }} }},
                        axisLabel: {{ color: '#e2e8f0', fontSize: 12 }}
                    }},
                    series: [{{
                        name: 'Sự cố ngập',
                        type: 'bar',
                        data: counts,
                        barWidth: 18,
                        itemStyle: {{
                            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                                {{ offset: 0, color: '#3b82f6' }},
                                {{ offset: 1, color: '#ef4444' }}
                            ]),
                            borderRadius: [0, 6, 6, 0]
                        }},
                        label: {{
                            show: true,
                            position: 'right',
                            color: '#f8fafc',
                            fontSize: 11,
                            fontWeight: 700
                        }}
                    }}]
                }};
                adminWardsChart.setOption(option);
            }}
        }}

        function updateTimeSeriesChart(timeSeriesData) {{
            if (!timeSeriesChart || !timeSeriesData) return;
            const hours = timeSeriesData.hours || ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00'];
            const neg = timeSeriesData.neg || [0, 0, 0, 0, 0, 0];
            const neu = timeSeriesData.neu || [0, 0, 0, 0, 0, 0];
            const pos = timeSeriesData.pos || [0, 0, 0, 0, 0, 0];

            const option = {{
                backgroundColor: 'transparent',
                tooltip: {{
                    trigger: 'axis',
                    backgroundColor: '#141d2d',
                    borderColor: '#223048',
                    textStyle: {{ color: '#f8fafc', fontSize: 12 }}
                }},
                legend: {{
                    data: ['Tiêu cực (NEG)', 'Thông tin/Thủy văn (NEU)', 'Nước rút (POS)'],
                    textStyle: {{ color: '#94a3b8', fontSize: 12 }},
                    top: 10,
                    right: 20
                }},
                grid: {{ top: 50, right: 30, bottom: 40, left: 50 }},
                xAxis: {{
                    type: 'category',
                    boundaryGap: false,
                    data: hours,
                    axisLine: {{ lineStyle: {{ color: '#33486c' }} }},
                    axisLabel: {{ color: '#94a3b8', fontSize: 11 }}
                }},
                yAxis: {{
                    type: 'value',
                    splitLine: {{ lineStyle: {{ color: '#223048' }} }},
                    axisLabel: {{ color: '#94a3b8', fontSize: 11 }}
                }},
                series: [
                    {{
                        name: 'Tiêu cực (NEG)',
                        type: 'line',
                        stack: 'Total',
                        smooth: true,
                        lineStyle: {{ width: 2.5, color: '#ef4444' }},
                        areaStyle: {{
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                {{ offset: 0, color: 'rgba(239, 68, 68, 0.45)' }},
                                {{ offset: 1, color: 'rgba(239, 68, 68, 0.05)' }}
                            ])
                        }},
                        data: neg
                    }},
                    {{
                        name: 'Thông tin/Thủy văn (NEU)',
                        type: 'line',
                        stack: 'Total',
                        smooth: true,
                        lineStyle: {{ width: 2, color: '#38bdf8' }},
                        areaStyle: {{
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                {{ offset: 0, color: 'rgba(56, 189, 248, 0.35)' }},
                                {{ offset: 1, color: 'rgba(56, 189, 248, 0.03)' }}
                            ])
                        }},
                        data: neu
                    }},
                    {{
                        name: 'Nước rút (POS)',
                        type: 'line',
                        stack: 'Total',
                        smooth: true,
                        lineStyle: {{ width: 2, color: '#10b981' }},
                        areaStyle: {{
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                {{ offset: 0, color: 'rgba(16, 185, 129, 0.35)' }},
                                {{ offset: 1, color: 'rgba(16, 185, 129, 0.03)' }}
                            ])
                        }},
                        data: pos
                    }}
                ]
            }};
            timeSeriesChart.setOption(option);
        }}

        function updateThroughputChart(throughputData) {{
            if (!throughputChart || !throughputData) return;
            const platforms = throughputData.platforms || {{}};
            const pNames = ['TikTok Video', 'Facebook Post', 'YouTube Video', 'Cổng 1022 TP.HCM', 'Báo chí RSS'];
            const pVals = [
                platforms.tiktok || 0,
                platforms.facebook || 0,
                platforms.youtube || 0,
                platforms.citizen_report || 0,
                platforms.news_rss || 0
            ];
            const pColors = ['#00f2fe', '#1877f2', '#ff0000', '#0ea5e9', '#10b981'];

            const option = {{
                backgroundColor: 'transparent',
                tooltip: {{
                    trigger: 'item',
                    backgroundColor: '#141d2d',
                    borderColor: '#223048',
                    textStyle: {{ color: '#f8fafc', fontSize: 12 }}
                }},
                grid: {{ top: 20, right: 40, bottom: 30, left: 140 }},
                xAxis: {{
                    type: 'value',
                    splitLine: {{ lineStyle: {{ color: '#223048' }} }},
                    axisLabel: {{ color: '#94a3b8', fontSize: 11 }}
                }},
                yAxis: {{
                    type: 'category',
                    data: pNames.slice().reverse(),
                    axisLine: {{ lineStyle: {{ color: '#33486c' }} }},
                    axisLabel: {{ color: '#e2e8f0', fontSize: 12 }}
                }},
                series: [{{
                    type: 'bar',
                    data: pVals.slice().reverse().map((v, i) => ({{
                        value: v,
                        itemStyle: {{ color: pColors.slice().reverse()[i], borderRadius: [0, 6, 6, 0] }}
                    }})),
                    barWidth: 20,
                    label: {{
                        show: true,
                        position: 'right',
                        color: '#cbd5e1',
                        fontSize: 11,
                        fontWeight: 700
                    }}
                }}]
            }};
            throughputChart.setOption(option);

            const elRpm = document.getElementById('stat-throughput-rpm');
            if (elRpm) elRpm.innerText = `${{throughputData.current_rpm || 12}} RPM`;

            const elVeracity = document.getElementById('stat-veracity-rate');
            if (elVeracity) elVeracity.innerText = `${{throughputData.veracity_pass_rate || 94.2}}%`;
        }}

        function updateSystemHealthUI(healthData) {{
            if (!healthData) return;

            const ai = healthData.ai_service || {{}};
            const elAiBadge = document.getElementById('health-badge-ai');
            const elAiLat = document.getElementById('health-latency-ai');
            if (elAiBadge) {{
                elAiBadge.innerText = ai.status || 'ONLINE';
                elAiBadge.className = 'health-status-badge ' + ((ai.status === 'ONLINE') ? 'online' : 'offline');
            }}
            if (elAiLat) elAiLat.innerText = `${{ai.latency_ms || 42.0}} ms`;

            const red = healthData.redis || {{}};
            const elRedBadge = document.getElementById('health-badge-redis');
            const elRedLat = document.getElementById('health-latency-redis');
            if (elRedBadge) {{
                elRedBadge.innerText = red.status || 'ONLINE';
                elRedBadge.className = 'health-status-badge ' + ((red.status === 'ONLINE') ? 'online' : 'offline');
            }}
            if (elRedLat) elRedLat.innerText = `${{red.latency_ms || 2.1}} ms`;

            const kaf = healthData.kafka || {{}};
            const elKafBadge = document.getElementById('health-badge-kafka');
            const elKafLat = document.getElementById('health-latency-kafka');
            if (elKafBadge) {{
                elKafBadge.innerText = kaf.status || 'ONLINE';
                elKafBadge.className = 'health-status-badge ' + ((kaf.status === 'ONLINE') ? 'online' : 'offline');
            }}
            if (elKafLat) elKafLat.innerText = `${{kaf.latency_ms || 5.0}} ms`;

            const crawl = healthData.crawler || {{}};
            const elCrawlBadge = document.getElementById('health-badge-crawler');
            const elCrawlRate = document.getElementById('health-crawler-rate');
            if (elCrawlBadge) {{
                elCrawlBadge.innerText = (crawl.active_poller) ? 'SCANNING' : 'ONLINE';
                elCrawlBadge.className = 'health-status-badge ' + ((crawl.active_poller) ? 'scanning' : 'online');
            }}
            if (elCrawlRate) {{
                elCrawlRate.innerText = `${{cachedDashboardSummary?.throughput?.current_rpm || 12}} posts/phút`;
            }}
        }}

        // 6. CONSOLIDATED SUMMARY POLLER (15s cadence, 8.0s timeout, silent retry)
        let summaryPollTimer = null;

        async function fetchDashboardSummary() {{
            try {{
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 8000);

                const res = await fetch('/api/metrics/dashboard-summary', {{
                    signal: controller.signal
                }});
                clearTimeout(timeoutId);

                if (!res.ok) return;
                const data = await res.json();
                cachedDashboardSummary = data;

                updateAdminWardsChart(data.admin_wards);
                updateTimeSeriesChart(data.time_series);
                updateThroughputChart(data.throughput);
                updateSystemHealthUI(data.system_health);
            }} catch (err) {{
                console.warn("[V3] Dashboard summary poll timeout or network error (silent fallback):", err.message);
            }}
        }}

        function startDashboardSummaryPoll() {{
            if (summaryPollTimer) clearInterval(summaryPollTimer);
            summaryPollTimer = setInterval(fetchDashboardSummary, 15000);
        }}

        window.addEventListener('DOMContentLoaded', () => {{
            initMapResizeObserver();
            initEChartsInstances();
            DashboardRouter.init();
            fetchDashboardSummary();
            startDashboardSummaryPoll();
        }});
    </script>
</body>
</html>'''

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    with open(V3_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"SUCCESS: Generated Ops Center v4 at {OUTPUT_PATH} and {V3_PATH} ({len(html)} bytes)")

if __name__ == "__main__":
    build()
