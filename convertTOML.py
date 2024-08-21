import json
import toml
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Caminho para os arquivos
json_file_path = 'serviceAccountKey.json'
toml_file_path = os.path.join('.streamlit', 'secrets.toml')

# Certifique-se de que o diretório .streamlit existe
os.makedirs('.streamlit', exist_ok=True)

# Ler o arquivo JSON
with open(json_file_path, 'r') as json_file:
    json_data = json.load(json_file)

# Cria um dicionário para as variáveis do JSON
data = {
    "FIRESTORE_CREDENTIALS": json_data,
    "FIRESTORE_PROJECT_ID": os.getenv('FIRESTORE_PROJECT_ID'),
    "FIRESTORE_DATABASE": os.getenv('FIRESTORE_DATABASE')
}

# Converter para TOML e salvar no arquivo
with open(toml_file_path, 'w') as toml_file:
    toml.dump(data, toml_file)

print(f'Dados convertidos para TOML e salvos em {toml_file_path}')