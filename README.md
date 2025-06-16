# Como criar e usar um ambiente virtual (venv) para este projeto

1. Crie o ambiente virtual:
```bash
python3 -m venv .venv
```

2. Ative o ambiente virtual:
- No Linux/macOS:
    ```bash
    source .venv/bin/activate
    ```
- No Windows:
    ```cmd
    .venv\Scripts\activate
    ```

3. Instale as dependências necessárias:
```bash
pip install pandas scikit-learn websocket-client pynput
```

4. (Opcional) Gere um arquivo requirements.txt para facilitar futuras instalações:
```bash
pip freeze > requirements.txt
```

5. Para sair do ambiente virtual:
```bash
deactivate
```
