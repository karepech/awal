import requests
import json
import re

API_URL = "https://boti.my.id/index.php?api=playlist&email=mbkidriss9%40gmail.com&password=12345678"
OUTPUT_LIVE = "live.m3u"
OUTPUT_UPCOMING = "upcoming.m3u"
FALLBACK_MP4 = "http://127.0.0.1/dummy.mp4"

def generate_live_playlist():
    print(f"Mengambil data Live & Upcoming dari API...")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(API_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        live_lines = ["#EXTM3U\n"]
        upcoming_lines = ["#EXTM3U\n"]
        
        try:
            data = response.json()
            channels_to_process = []
            
            if isinstance(data, list):
                for item in data:
                    if "channels" in item and isinstance(item["channels"], list):
                        cat_name = item.get("category", item.get("group", item.get("name", "Uncategorized")))
                        for ch in item["channels"]:
                            if isinstance(ch, dict):
                                ch["_auto_group"] = cat_name
                                channels_to_process.append(ch)
                    elif isinstance(item, dict): channels_to_process.append(item)
            elif isinstance(data, dict):
                global_u = data.get("u", "mbkidriss9@gmail.com")
                global_x = data.get("x", "")
                global_a = data.get("a", "")
                for key, value in data.items():
                    if isinstance(value, list):
                        cat_name = "Vidio" if key.lower() in ["data", "channels", "list"] else key
                        for item in value:
                            if isinstance(item, dict):
                                item["_auto_group"] = cat_name
                                item["_global_u"] = global_u
                                item["_global_x"] = global_x
                                item["_global_a"] = global_a
                                channels_to_process.append(item)
            
            for ch in channels_to_process:
                name = ch.get("name", ch.get("title", ch.get("channel", "Unknown")))
                logo = ch.get("logo", ch.get("image", ""))
                group = ch.get("group", ch.get("category", ch.get("category_name", ch.get("_auto_group", "Vidio"))))
                group_title_original = str(group).strip()
                group_lower = group_title_original.lower()
                
                is_upcoming = "upcoming" in group_lower or "mendatang" in group_lower
                is_live = any(x in group_lower for x in ["live", "tv", "nasional", "sport"])
                
                if not is_upcoming and not is_live:
                    continue
                
                if "id" in ch:
                    u = ch.get("u", ch.get("_global_u", "mbkidriss9@gmail.com"))
                    x = ch.get("x", ch.get("_global_x", "644_SrZsWczYRmp5J7Xx"))
                    a = ch.get("a", ch.get("_global_a", "eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7InR5cGUiOiJhY2Nlc3NfdG9rZW4iLCJ1aWQiOjIyMjMzNzE5NH0sImV4cCI6MTc4ODY3NzAzOH0.UHImVkHT2jujFUpPlo_vfULpyt1lZArjsLgw-CX7lVc"))
                    ch_id = ch['id']
                    
                    # Mempertahankan format raw blok tanpa mengubah judul channel
                    if is_upcoming:
                        # Fallback MP4 untuk Upcoming
                        block = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_title_original}", {name}\n{FALLBACK_MP4}\n\n'
                        upcoming_lines.append(block)
                    else:
                        hls_url = f"https://boti.my.id/index.m3u8?u={u}&x={x}&a={a}&id={ch_id}&type=hls"
                        dash_url = f"https://boti.my.id/index.mpd?u={u}&x={x}&a={a}&id={ch_id}&type=dash"
                        drm_url = f"https://boti.my.id/index.php?u={u}&x={x}&a={a}&id={ch_id}&type=drm"
                        
                        block = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_title_original}", {name} (HLS)\n{hls_url}\n'
                        block += f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_title_original}", {name} (DASH)\n'
                        block += '#KODIPROP:inputstream=inputstream.adaptive\n'
                        block += '#KODIPROP:inputstream.adaptive.manifest_type=mpd\n'
                        block += '#KODIPROP:inputstream.adaptive.license_type=com.widevine.alpha\n'
                        block += f'#KODIPROP:inputstream.adaptive.license_key={drm_url}\n{dash_url}\n\n'
                        live_lines.append(block)

            with open(OUTPUT_LIVE, "w", encoding="utf-8") as f: f.writelines(live_lines)
            with open(OUTPUT_UPCOMING, "w", encoding="utf-8") as f: f.writelines(upcoming_lines)
            print("Sukses memproses Live & Upcoming!")
            
        except json.JSONDecodeError:
            print("Error: API tidak merespons JSON yang valid.")
            
    except requests.exceptions.RequestException as e:
        print(f"Koneksi gagal: {e}")

if __name__ == "__main__":
    generate_live_playlist()
