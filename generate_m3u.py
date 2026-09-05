import requests
import re

API_URL = "https://boti.my.id/index.php?api=playlist&email=mbkidriss9%40gmail.com&password=12345678"

def generate_playlist():
    print("Mengambil data Series & Movies dari API (Khusus HLS)...")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(API_URL, headers=headers, timeout=20)
        # Menghapus karakter enter (\r) agar pemotongan blok sempurna
        content = response.text.replace('\r', '').strip()
        
        all_series = ["#EXTM3U\n"]
        series_100 = ["#EXTM3U\n"]
        movies = ["#EXTM3U\n"]
        seen_series = set()
        
        c_all = c_s100 = c_mov = 0
        
        # Memotong data tepat di setiap awalan channel (#EXTINF)
        raw_blocks = re.split(r'\n(?=#EXTINF)', content)
        
        for block in raw_blocks:
            if not block.startswith("#EXTINF"): continue
            
            # Ekstrak Grup
            m_group = re.search(r'group-title="([^"]+)"', block, re.IGNORECASE)
            group = m_group.group(1).strip() if m_group else "Uncategorized"
            group_lower = group.lower()
            
            # Lewati jika ini Live / Upcoming (akan diproses oleh generate_live.py)
            if any(x in group_lower for x in ["live", "tv", "nasional", "sport", "upcoming"]):
                continue
                
            # Pisahkan baris dalam 1 blok
            lines = block.strip().split('\n')
            extinf_line = lines[0]
            other_tags = [l for l in lines[1:] if l.startswith("#")]
            
            # Cari baris URL (Baris yang tidak berawalan #)
            url_line = next((l for l in lines if l.startswith("http")), None)
            if not url_line: continue
            
            # Cek apakah tayangan ini masuk kategori Series
            is_series = any(x in group_lower for x in ["series", "drama", "episode", "season"])
            
            # --- MERAKIT URL MURNI HLS UNTUK SEMUA VOD ---
            out_block = extinf_line + "\n"
            if other_tags: out_block += "\n".join(other_tags) + "\n"
            out_block += url_line + "\n\n"
            
            # --- DISTRIBUSI KE FILE ---
            if is_series:
                all_series.append(out_block)
                c_all += 1
                if group in seen_series:
                    series_100.append(out_block)
                    c_s100 += 1
                elif len(seen_series) < 100:
                    seen_series.add(group)
                    series_100.append(out_block)
                    c_s100 += 1
            else:
                movies.append(out_block)
                c_mov += 1
                
        with open("all_series.m3u", "w", encoding="utf-8") as f: f.writelines(all_series)
        with open("series_100.m3u", "w", encoding="utf-8") as f: f.writelines(series_100)
        with open("movies.m3u", "w", encoding="utf-8") as f: f.writelines(movies)
        print(f"Sukses! All Series: {c_all} | Series 100: {c_s100} | Movies: {c_mov}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_playlist()
