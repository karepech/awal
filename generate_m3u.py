import requests
import re

API_URL = "https://boti.my.id/index.php?api=playlist&email=mbkidriss9%40gmail.com&password=12345678"

def generate_playlist():
    print("Mengambil data Series & Movies dari API...")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        content = response.text.strip().lstrip('\ufeff')
        
        # MENGINTIP APA YANG DIKIRIM SERVER
        print("HASIL DARI SERVER:", content[:300])
        
        all_series = ["#EXTM3U\n"]
        series_100 = ["#EXTM3U\n"]
        movies = ["#EXTM3U\n"]
        seen_series = set()
        
        c_all = c_s100 = c_mov = 0
        
        blocks = content.split("#EXTINF")
        
        for block in blocks[1:]:
            full_block = "#EXTINF" + block
            lines = full_block.strip().split('\n')
            
            extinf_line = lines[0].strip()
            other_tags = [l.strip() for l in lines[1:] if l.strip().startswith("#")]
            url_line = next((l.strip() for l in lines if l.strip().startswith("http")), None)
            
            m_group = re.search(r'group-title="([^"]+)"', extinf_line, re.IGNORECASE)
            group = m_group.group(1).strip() if m_group else "Uncategorized"
            group_lower = group.lower()
            
            if any(x in group_lower for x in ["live", "tv", "nasional", "sport", "upcoming"]):
                continue
                
            if not url_line:
                continue
            
            out_block = extinf_line + "\n"
            if other_tags:
                out_block += "\n".join(other_tags) + "\n"
            out_block += url_line + "\n\n"
            
            is_series = any(x in group_lower for x in ["series", "drama", "episode", "season"])
            
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
        print(f"Error saat memproses: {e}")

if __name__ == "__main__":
    generate_playlist()
