Feature: Cadastro de cliente
  Como usuário da API
  Quero cadastrar um novo cliente
  Para que ele seja salvo no sistema

  Scenario: Cadastro de cliente com sucesso
    Given que o payload do cliente é válido
    When eu envio uma requisição de cadastro
    Then o cliente é criado com sucesso
