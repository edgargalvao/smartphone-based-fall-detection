import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

print("--- Iniciando: Carregamento e Pré-processamento ---")

# --- 1. Carregar o Dataset ---
try:
    df = pd.read_csv('sensor_data.csv')
    print("Dataset carregado com sucesso.")
except FileNotFoundError:
    print("Erro: sensor_data.csv não encontrado.")
    exit()

print(f"Formato original: {df.shape}")

# --- 2. Pré-processamento ---
# Remover colunas (se existirem)
cols_to_drop = [col for col in df.columns if 'norm' in col or 'svm_acc' in col or 'svm_linacc' in col]
df = df.drop(columns=cols_to_drop, errors='ignore')
# Identificar colunas de features
feature_cols = [col for col in df.columns if col not in ['timestamp', 'falling']]

# Converter e tratar NaNs
print("Tratando valores ausentes...")
for col in feature_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df[feature_cols] = df[feature_cols].ffill()
df[feature_cols] = df[feature_cols].bfill()
df = df.dropna()
df['falling'] = df['falling'].astype(int)

print("Pré-processamento concluído.")
print(f"Formato dos dados após limpeza: {df.shape}")

print("\n--- Iniciando: Engenharia de Características (Janela Reduzida) ---")

# --- 3. Engenharia de Características ---
WINDOW_SIZE = 30  # !! JANELA REDUZIDA !!
STEP_SIZE = 15    # !! PASSO REDUZIDO !!
print(f"AVISO: Usando WINDOW_SIZE={WINDOW_SIZE} e STEP_SIZE={STEP_SIZE} devido ao dataset pequeno.")

features = []
labels = []
feature_names_list = []

# Checar se temos linhas suficientes
if len(df) < WINDOW_SIZE:
    print(f"\n--- ERRO CRÍTICO ---")
    print(f"Dataset tem apenas {len(df)} linhas, menos que a WINDOW_SIZE de {WINDOW_SIZE}.")
    print("Não é possível criar janelas. Por favor, use um dataset maior.")
    exit()

# Iterar sobre o DataFrame
for i in range(0, len(df) - WINDOW_SIZE, STEP_SIZE):
    window = df[feature_cols].iloc[i : i + WINDOW_SIZE]
    label_window = df['falling'].iloc[i : i + WINDOW_SIZE]

    window_features = []
    current_feature_names = []
    for col in feature_cols:
        series = window[col]
        window_features.append(series.mean())
        window_features.append(series.std())
        window_features.append(series.min())
        window_features.append(series.max())
        window_features.append(series.median())
        window_features.append(series.max() - series.min())

        if i == 0:
            current_feature_names.extend([
                f'{col}_mean', f'{col}_std', f'{col}_min',
                f'{col}_max', f'{col}_median', f'{col}_range'
            ])

    features.append(window_features)
    labels.append(1 if label_window.sum() > 0 else 0)
    if i == 0:
        feature_names_list = current_feature_names

# Criar DataFrame com as características
X = pd.DataFrame(features, columns=feature_names_list)
y = pd.Series(labels, name='is_fall')

print(f"Engenharia de características concluída. Criadas {len(X)} janelas.")
print(f"Distribuição das labels nas janelas: \n{y.value_counts()}")

# --- Verificar se há dados suficientes para treinar ---
if len(X) < 4 or y.value_counts().min() < 2: # Precisa de pelo menos 2 na minoria para 'stratify'
    print("\n--- ERRO CRÍTICO ---")
    print("Não há janelas suficientes ou amostras suficientes na classe minoritária para treinar/testar o modelo.")
    print("É fundamental coletar mais dados.")
else:
    print("\n--- Iniciando: Implementação do Random Forest ---")
    print("AVISO: Treinando com POUQUÍSSIMAS janelas. Resultados NÃO SERÃO CONFIÁVEIS.")

    # --- 4. Dividir os Dados ---
    # Tentar 50% para teste para maximizar a chance de ter uma queda no teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42, stratify=y)
    print(f"Dados divididos: Treino={len(X_train)}, Teste={len(X_test)}")
    print(f"Labels de Treino: \n{y_train.value_counts()}")
    print(f"Labels de Teste: \n{y_test.value_counts()}")

    # --- 5. Instanciar e Treinar o Modelo ---
    rf_model = RandomForestClassifier(n_estimators=50, random_state=42, class_weight='balanced', n_jobs=-1)

    print("\nTreinando o modelo Random Forest...")
    rf_model.fit(X_train, y_train)
    print("Treinamento concluído.")

    # --- 6. Fazer Previsões ---
    y_pred = rf_model.predict(X_test)

    # --- 7. Avaliar o Modelo ---
    print("\n--- Resultados da Avaliação (NÃO CONFIÁVEIS) ---")
    print("\nMatriz de Confusão:")
    print(confusion_matrix(y_test, y_pred))
    print("\nRelatório de Classificação:")
    print(classification_report(y_test, y_pred, zero_division=0))