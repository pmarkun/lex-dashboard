
# Dashboard de Usuários e Histórico de Conversas

## Objetivo do Projeto
Este projeto exibe um dashboard para visualizar usuários e o histórico de mensagens, usando dados do Firestore. Ele inclui a capacidade de visualizar detalhes do usuário, sua atividade recente, e o histórico de conversas.

## Requisitos
- Python 3.x
- Bibliotecas listadas no `requirements.txt`

## Configuração
### 1. Instalação de Dependências
Execute o seguinte comando para instalar as dependências:
```bash
pip install -r requirements.txt
```

### 2. Configuração do Firestore
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```dotenv
FIRESTORE_PROJECT_ID=seu_project_id
FIRESTORE_CREDENTIALS_PATH=./caminho_para_serviceAccountKey.json
```

### 3. Executar o Projeto
Execute o projeto usando o comando:
```bash
streamlit run app.py
```

## Estrutura do Código
- **get_users():** Recupera e ordena os usuários por `updatedAt`, colocando aqueles sem `updatedAt` no final.
- **search_users(query):** Permite buscar usuários por `phone` ou `profileName`.
- **get_total_messages():** Conta o número total de mensagens na coleção `sessions->messages`.
- **get_weekly_data():** Recupera dados de usuários e mensagens na última semana.
- **create_whatsapp_link(profile_name, phone):** Cria um link para WhatsApp usando `phone` ou `profileName`.
- **paginate_data(data, page_size, page_number):** Pagina a lista de usuários para exibição.
- **show_user_conversation(user):** Exibe os detalhes e o histórico de conversa de um usuário específico.
- **show_dashboard():** Controla a exibição do dashboard com todos os gráficos e informações.

## Colaboração
- **Adicione novas funcionalidades seguindo a estrutura estabelecida.**
- **Utilize nomes verbosos para variáveis e funções para manter o código claro e compreensível.**
- **Sempre atualize o arquivo `requirements.txt` ao adicionar novas dependências.**

Este código foi estruturado e documentado para facilitar a manutenção e a adição de novas funcionalidades, permitindo que outros colaboradores contribuam de forma eficaz.
