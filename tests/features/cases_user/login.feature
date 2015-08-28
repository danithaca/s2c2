Feature: user login
  In order to use servuno
  As anonymous user
  I need to be able to login and logout

  @core
  Scenario: Login on login page and logout
    Given I am on "/account/login"
    When I fill in the following:
      | Email    | test@servuno.com |
      | Password | password         |
    And I press "Log in"
    Then the response status code should be 200
    And the response should contain "<!-- logged in as test@servuno.com -->"
    When I follow "Logout"
    Then I should be on "/account/login/"
    And the response should not contain "<!-- logged in as test@servuno.com -->"

  @core
  Scenario: login from homepage
    Given I am on the homepage
    Then I should see "Servuno"
    When I fill in the following:
      | Email    | test@servuno.com |
      | Password | password         |
    And I press "Log in"
    Then the response status code should be 200
    And the response should contain "<!-- logged in as test@servuno.com -->"

  @core
  Scenario: logout
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "Logout"
    Then the response status code should be 200
    And the response should not contain "<!-- logged in as test@servuno.com -->"