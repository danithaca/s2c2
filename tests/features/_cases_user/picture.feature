Feature: Test picture

  @core
  Scenario: basic picture page
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "Edit account"
    Then I should see "Picture"
    When I follow "Picture"
    Then I should see "Picture upload"

  # todo: add more advanced picture upload test.