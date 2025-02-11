# Projeto Frequência - Momento Áureo

Aplicativo Streamlit para gerenciamento de frequência e livros do Momento Áureo.

## Funcionalidades

- Controle de frequência dos participantes
- Análise de dados e visualizações
- Gerenciamento de livros para estudo
- Interface intuitiva e responsiva

## Requisitos

- Python 3.12+
- Streamlit 1.31.0
- Pandas 1.5.3
- Outras dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/projeto_frequencia.git
cd projeto_frequencia
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o aplicativo:
```bash
streamlit run streamlit_app.py
```

## Estrutura do Projeto

```
projeto_frequencia/
├── streamlit_app.py     # Aplicativo principal
├── requirements.txt     # Dependências
├── .streamlit/         # Configurações do Streamlit
│   └── config.toml
└── data/              # Diretório de dados
    ├── livros.xlsx    # Banco de dados de livros
    └── capas/         # Imagens das capas dos livros
```

## Contribuindo

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
