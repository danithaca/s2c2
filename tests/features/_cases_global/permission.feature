Feature: check user permission with contract
  In order to use servuno in a secure way
  As anonymous user
  I should not access certain part of the site.

  @core
  Scenario: view contract
    Given I am on "/job/3"
    Then I should be on "/account/login/"

  @core
  Scenario: add contract
    Given I am on "/job/post/favor"
    Then I should be on "/account/login/"
    Given I am on "/job/post/paid"
    Then I should be on "/account/login/"

  @core
  Scenario: view contract
    Given I am on "/job/"
    Then I should be on "/account/login/"

  @core
  Scenario: dashboard
    Given I am on "/dashboard/"
    Then I should be on "/account/login/"
