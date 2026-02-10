import pandas as pd
import numpy as np
import os

# Membaca data dari Excel
try:
    df = pd.read_excel('data_kuesioner.xlsx')
except Exception as e:
    raise SystemExit(f"Error reading 'data_kuesioner.xlsx': {e}")

# Mengambil hanya kolom Q1 sampai Q17 (exclude Partisipan)
questions = [col for col in df.columns if col.startswith('Q')]
data = df[questions]

# Baca input dan normalisasi
target_question = input().strip().lower()

if target_question == "q1":
    # Pada kusioner dari keseluruhan data, skala mana yang paling banyak dipilih oleh partisipan? sertakan jumlah dan persen
    # Contoh Jawaban: CS|500|70.1
    all_values = pd.Series(data.values.flatten()).dropna()
    value_counts = all_values.value_counts()
    most_common = value_counts.index[0]
    count = int(value_counts.iloc[0])
    percentage = (count / len(all_values)) * 100
    print(f"{most_common}|{count}|{percentage:.1f}")

elif target_question == "q2":
    # Pada kusioner dari keseluruhan data, skala mana yang paling sedikit dipilih oleh partisipan? sertakan jumlah dan persen
    # Contoh Jawaban: TS|1|1.1
    all_values = pd.Series(data.values.flatten()).dropna()
    value_counts = all_values.value_counts()
    least_common = value_counts.index[-1]
    count = int(value_counts.iloc[-1])
    percentage = (count / len(all_values)) * 100
    print(f"{least_common}|{count}|{percentage:.1f}")

elif target_question == "q3":
    # Pada kusioner dari pertanyaan Q1 sampai Q17, pertanyaan mana yang pilihan skala SS (Sangat Setuju) paling banyak? sertakan jumlah dan persen
    # Contoh Jawaban: Q2|30|34.4
    ss_counts = (data == 'SS').sum()
    max_q = ss_counts.idxmax()
    count = ss_counts[max_q]
    total = len(df)
    percentage = (count / total) * 100
    print(f"{max_q}|{count}|{percentage:.1f}")

elif target_question == "q4":
    # Pada kusioner dari pertanyaan Q1 sampai Q17, pertanyaan mana yang pilihan skala S (Setuju) paling banyak? sertakan jumlah dan persen
    # Contoh Jawaban: Q2|30|34.4
    s_counts = (data == 'S').sum()
    max_q = s_counts.idxmax()
    count = s_counts[max_q]
    total = len(df)
    percentage = (count / total) * 100
    print(f"{max_q}|{count}|{percentage:.1f}")

elif target_question == "q5":
    # Pada kusioner dari pertanyaan Q1 sampai Q17, pertanyaan mana yang pilihan skala CS (Cukup Setuju) paling banyak? sertakan jumlah dan persen
    # Contoh Jawaban: Q2|30|34.4
    cs_counts = (data == 'CS').sum()
    max_q = cs_counts.idxmax()
    count = cs_counts[max_q]
    total = len(df)
    percentage = (count / total) * 100
    print(f"{max_q}|{count}|{percentage:.1f}")

elif target_question == "q6":
    # Pada kusioner dari pertanyaan Q1 sampai Q17, pertanyaan mana yang pilihan skala CTS (Cukup Tidak Setuju) paling banyak? sertakan jumlah dan persen
    # Contoh Jawaban: Q2|30|34.4
    cts_counts = (data == 'CTS').sum()
    max_q = cts_counts.idxmax()
    count = cts_counts[max_q]
    total = len(df)
    percentage = (count / total) * 100
    print(f"{max_q}|{count}|{percentage:.1f}")

elif target_question == "q7":
    # Pada kusioner dari pertanyaan Q1 sampai Q17, pertanyaan mana yang pilihan skala TS (Tidak Setuju) paling banyak? sertakan jumlah dan persen
    # Contoh Jawaban: Q2|30|34.4
    ts_counts = (data == 'TS').sum()
    max_q = ts_counts.idxmax()
    count = ts_counts[max_q]
    total = len(df)
    percentage = (count / total) * 100
    print(f"{max_q}|{count}|{percentage:.1f}")

elif target_question == "q8":
    # Pada kusioner dari pertanyaan Q1 sampai Q17, pertanyaan mana yang pilihan skala TS (Tidak Setuju) paling banyak? sertakan jumlah dan persen
    # Contoh Jawaban: Q2|30|34.4
    ts_counts = (data == 'TS').sum()
    # jika tidak ada TS di seluruh dataset, cetak string kosong
    if ts_counts.sum() == 0:
        print("")
    else:
        max_q = ts_counts.idxmax()
        count = int(ts_counts[max_q])
        # persentase dihitung terhadap seluruh responden
        total = len(df)
        percentage = (count / total) * 100 if total else 0.0
        print(f"{max_q}|{count}|{percentage:.1f}")

elif target_question == "q9":
    # Pada kusioner dari pertanyaan Q1 sampai Q17, pertanyaan mana saja yang terdapat memilih skala STS (Sangat Tidak Setuju)? sertakan jumlah dan persen
    # Contoh Jawaban: Q1:0.1|Q2:0.2|Q3:0.1
    sts_counts = (data == 'STS').sum()
    total = len(df)
    result_parts = []
    for q in questions:
        count = int(sts_counts[q])
        # hanya tambahkan jika terdapat STS untuk pertanyaan ini
        if count > 0:
            percentage = (count / total) * 100 if total else 0.0
            result_parts.append(f"{q}:{percentage:.1f}")
    print("|".join(result_parts))

elif target_question == "q10":
    # Jika skala skor untuk masing masing skala adalah 6, 5, 4, 3, 2, 1 untuk SS, S, CS, CTS, TS, STS
    # Berapa skor rata-rata keseluruhan pertanyaan?
    # Contoh Jawaban: 5.60
    score_map = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
    # Replace text scales with numeric scores and coerce non-mapped to NaN
    scores = data.replace(score_map).apply(pd.to_numeric, errors='coerce')
    # Stack drops NaN and returns a Series of all numeric answers
    avg_score = scores.stack().mean()
    print(f"{avg_score:.2f}")

elif target_question == "q11":
    # Jika skala skor untuk masing masing skala adalah 6, 5, 4, 3, 2, 1 untuk SS, S, CS, CTS, TS, STS
    # Maka pada kusioner dari pertanyaan Q1 sampai Q17, pertanyaan mana yang memiliki skor rata-rata tertinggi?
    # Contoh Jawaban: Q1:5.60
    score_map = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
    scores = data.replace(score_map).apply(pd.to_numeric, errors='coerce')
    avg_per_q = scores.mean(skipna=True)
    max_q = avg_per_q.idxmax()
    max_score = avg_per_q[max_q]
    print(f"{max_q}:{max_score:.2f}")

elif target_question == "q12":
    # Jika skala skor untuk masing masing skala adalah 6, 5, 4, 3, 2, 1 untuk SS, S, CS, CTS, TS, STS
    # Maka pada kusioner dari pertanyaan Q1 sampai Q17, pertanyaan mana yang memiliki skor rata-rata terendah?
    # Contoh Jawaban: Q2:3.60
    score_map = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
    scores = data.replace(score_map).apply(pd.to_numeric, errors='coerce')
    avg_per_q = scores.mean(skipna=True)
    min_q = avg_per_q.idxmin()
    min_score = avg_per_q[min_q]
    print(f"{min_q}:{min_score:.2f}")

elif target_question == "q13":
    # Jika skala di kategorikan menjadi positif (SS dan S), netral (CS) dan negatif (CTS, TS dan STS)
    # Maka hitung jumlah responden dan persentase masing-masing kategori
    # Contoh Jawaban: positif=1000:80.1|netral=200:10.1|negatif=200:100.2
    all_values = pd.Series(data.values.flatten()).dropna()
    total = len(all_values)

    positif = int(((all_values == 'SS') | (all_values == 'S')).sum())
    netral = int((all_values == 'CS').sum())
    negatif = int(((all_values == 'CTS') | (all_values == 'TS') | (all_values == 'STS')).sum())

    pct_positif = (positif / total) * 100 if total else 0.0
    pct_netral = (netral / total) * 100 if total else 0.0
    pct_negatif = (negatif / total) * 100 if total else 0.0

    print(f"positif={positif}:{pct_positif:.1f}|netral={netral}:{pct_netral:.1f}|negatif={negatif}:{pct_negatif:.1f}")