import csv

input_path = 'sensor_data.csv'
output_path = 'sensor_data_normalized.csv'

with open(input_path, newline='') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

# Identifique as colunas a serem normalizadas
skip_cols = {'timestamp', 'norm', 'falling', 'android.sensor.rotation_vector_value_4'}
col_indices = [i for i, col in enumerate(header) if col not in skip_cols]

# Pegue os índices das colunas timestamp e falling, se existirem
timestamp_idx = header.index('timestamp') if 'timestamp' in header else None
falling_idx = header.index('falling') if 'falling' in header else None

# Calcule min e max para cada coluna selecionada
mins = [float('inf')] * len(col_indices)
maxs = [float('-inf')] * len(col_indices)
for row in rows:
    for idx, col in enumerate(col_indices):
        try:
            val = float(row[col])
            if val < mins[idx]:
                mins[idx] = val
            if val > maxs[idx]:
                maxs[idx] = val
        except Exception:
            continue

# Normaliza os dados e calcula a norma global min-max para cada linha
normalized_rows = []
new_header = []
if timestamp_idx is not None:
    new_header.append('timestamp')
new_header += [header[i] for i in col_indices]
if falling_idx is not None:
    new_header.append('falling')
new_header.append('global_norm')

for row in rows:
    norm_vals = []
    norm_row = []
    if timestamp_idx is not None:
        norm_row.append(row[timestamp_idx])
    for idx, col in enumerate(col_indices):
        try:
            val = float(row[col])
            min_v = mins[idx]
            max_v = maxs[idx]
            if max_v != min_v:
                norm_val = (val - min_v) / (max_v - min_v)
            else:
                norm_val = 0.0
        except Exception:
            norm_val = 0.0
        norm_row.append(norm_val)
        norm_vals.append(norm_val)
    if falling_idx is not None:
        norm_row.append(row[falling_idx])
    # Norma global min-max
    global_norm = sum(v**2 for v in norm_vals) ** 0.5
    norm_row.append(global_norm)
    normalized_rows.append(norm_row)

with open(output_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(new_header)
    writer.writerows(normalized_rows)
