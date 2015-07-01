Feature: check user permission with contract
  In order to use servuno in a secure way
  As anonymous user
  I should not access certain part of the site.

  Scenario: view contract
    Given I am on "/contract/3"
    Then I should be on "/account/login/"

  Scenario: add contract
    Given I am on "/contract/add"
    Then I should be on "/account/login/"

  Scenario: view contract
    Given I am on "/contract/"
    Then I should be on "/account/login/"