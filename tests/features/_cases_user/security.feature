Feature: test security

  @core
  Scenario: security check
    Given I am on "/account/1/"
    Then I should be on "/account/login/"

    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/account/1/"
    Then the response status code should be 403
