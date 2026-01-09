Feature: Gestão de cliente
  Scenario: Criar, consultar, atualizar e deletar um cliente
    Given que o payload do cliente é válido
    When eu crio o cliente
    Then o cliente é criado com sucesso
    When eu consulto o cliente
    Then os dados do cliente estão corretos
    When eu atualizo o cliente
    Then o cliente é atualizado com sucesso
    When eu deleto o cliente
    Then o cliente é deletado com sucesso
