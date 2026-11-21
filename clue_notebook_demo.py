"""
DEMO: XEM DỮ LIỆU MANH MỐI TỪ DATABASE
========================================
Hiển thị tất cả manh mối và thông tin chi tiết
"""
import sqlite3
from pathlib import Path

def get_all_clues_with_details():
    """Lấy tất cả manh mối với thông tin đầy đủ"""
    db_path = Path('c:/Users/tum/Desktop/PythonProject16/game.db')
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            mm.ma_manh_moi,
            mm.tieu_de_manh_moi,
            mm.loai_manh_moi,
            mm.noi_dung_chi_tiet,
            mm.thu_tu_timeline_dung,
            sk.ten_su_kien,
            sk.nam_dien_ra,
            sk.ma_dia_diem,
            nv.ten_nhan_vat,
            dd.ten_dia_diem,
            dd.khu_vuc
        FROM manh_moi mm
        LEFT JOIN su_kien_lich_su sk ON mm.ma_su_kien = sk.ma_su_kien
        LEFT JOIN nhan_vat nv ON mm.ma_nhan_vat = nv.ma_nhan_vat
        LEFT JOIN dia_diem dd ON sk.ma_dia_diem = dd.ma_dia_diem
        ORDER BY sk.nam_dien_ra, mm.thu_tu_timeline_dung
    """)
    
    clues = []
    for row in cur.fetchall():
        clues.append(dict(row))
    
    conn.close()
    return clues

def print_clue_details(clue):
    """In thông tin chi tiết của một manh mối"""
    print(f"\n{'='*80}")
    print(f"🔍 MANH MỐI #{clue['ma_manh_moi']}: {clue['tieu_de_manh_moi']}")
    print(f"{'='*80}")
    
    if clue['ten_su_kien']:
        print(f"📖 Sự kiện: {clue['ten_su_kien']}")
    if clue['nam_dien_ra']:
        print(f"📅 Năm: {clue['nam_dien_ra']}")
    if clue['ten_dia_diem']:
        print(f"📍 Địa điểm: {clue['ten_dia_diem']} ({clue['khu_vuc']})")
    if clue['ten_nhan_vat']:
        print(f"🎭 Nhân vật: {clue['ten_nhan_vat']}")
    if clue['loai_manh_moi']:
        print(f"📚 Loại: {clue['loai_manh_moi']}")
    if clue['thu_tu_timeline_dung']:
        print(f"⏰ Thứ tự timeline: {clue['thu_tu_timeline_dung']}")
    
    print(f"\n📝 NỘI DUNG CHI TIẾT:")
    print("-" * 80)
    
    # Tách nội dung thành từng đoạn cho dễ đọc
    content = clue['noi_dung_chi_tiet']
    if content:
        paragraphs = content.split('. ')
        for i, para in enumerate(paragraphs[:5]):  # Giới hạn 5 đoạn đầu
            if para.strip():
                print(f"{i+1}. {para.strip()}.")
        if len(paragraphs) > 5:
            print(f"... và {len(paragraphs)-5} đoạn nữa ...")
    else:
        print("(Không có nội dung chi tiết)")
    
    print("-" * 80)

def print_clue_summary_table(clues):
    """In bảng tổng hợp các manh mối"""
    print(f"\n{'='*80}")
    print(f"📊 TỔNG HỢP {len(clues)} MANH MỐI TRONG DATABASE")
    print(f"{'='*80}")
    
    print(f"\n{'ID':^4} | {'LOẠI':^12} | {'NHÂN VẬT':^20} | {'NĂM':^6} | {'TIÊU ĐỀ'}")
    print(f"{'-'*4}-+-{'-'*12}-+-{'-'*20}-+-{'-'*6}-+-{'-'*50}")
    
    for clue in clues[:20]:  # Giới hạn 20 manh mối đầu tiên
        clue_id = clue['ma_manh_moi']
        clue_type = clue['loai_manh_moi'] or "N/A"
        character = clue['ten_nhan_vat'] or "N/A"
        year = clue['nam_dien_ra'] or "N/A"
        title = clue['tieu_de_manh_moi'][:50] + "..." if len(clue['tieu_de_manh_moi']) > 50 else clue['tieu_de_manh_moi']
        
        print(f"{clue_id:^4} | {clue_type:^12} | {character:^20} | {year:^6} | {title}")
    
    if len(clues) > 20:
        print(f"\n... và {len(clues)-20} manh mối khác ...")

def main():
    """Chạy demo"""
    print("\n" + "🎮 "*40)
    print("DEMO: NHẬT KÝ MANH MỐI - GAME LỊCH SỬ VIỆT NAM")
    print("🎮 "*40)
    
    # Lấy dữ liệu
    clues = get_all_clues_with_details()
    
    # Tổng hợp
    print_clue_summary_table(clues)
    
    # Hiển thị chi tiết 3 manh mối đầu tiên
    print(f"\n{'='*80}")
    print("📖 CHI TIẾT 3 MANH MỐI ĐẦU TIÊN")
    print(f"{'='*80}")
    
    for i, clue in enumerate(clues[:3]):
        print_clue_details(clue)
    
    # Thống kê
    print(f"\n{'='*80}")
    print("📈 THỐNG KÊ MANH MỐI")
    print(f"{'='*80}")
    
    # Phân loại theo loại
    type_counts = {}
    for clue in clues:
        clue_type = clue['loai_manh_moi'] or "Unknown"
        type_counts[clue_type] = type_counts.get(clue_type, 0) + 1
    
    print("\n📊 PHÂN LOẠI THEO LOẠI:")
    for clue_type, count in type_counts.items():
        percentage = (count / len(clues)) * 100
        print(f"  {clue_type:15}: {count:3} manh mối ({percentage:.1f}%)")
    
    # Phân bổ theo năm
    year_counts = {}
    for clue in clues:
        year = clue['nam_dien_ra']
        if year:
            year_counts[year] = year_counts.get(year, 0) + 1
    
    print(f"\n📊 PHÂN BỔ THEO NĂM:")
    for year, count in sorted(year_counts.items())[:5]:  # 5 năm đầu
        print(f"  Năm {year}: {count} manh mối")
    
    print(f"\n✅ TỔNG CỘNG: {len(clues)} manh mối sẵn sàng cho nhật ký game!")

if __name__ == '__main__':
    main()
