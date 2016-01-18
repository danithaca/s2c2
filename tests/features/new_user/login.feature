Feature: user login
  In order to use servuno
  As anonymous user
  I need to be able to login and logout

  @core
  Scenario: Login on login page and logout
    Given I am on "/account/login/"
    When I fill in the following:
      | Email    | test@servuno.com |
      | Password | password         |
    And I press "Log in"
    Then the response status code should be 200
    And the response should contain "<!-- logged in as test@servuno.com -->"

    Given I am on "/account/logout/"
    Then the response status code should be 200
    Then I should be on ":ANONYMOUS_LANDING"
    And the response status code should be 200
    And the response should not contain "<!-- logged in as test@servuno.com -->"
