Feature: user login
  In order to use servuno
  As anonymous user
  I need to be able to login

  Scenario: login and logout
    Given I am on the homepage
    Then I should see "Servuno"
    When I fill in the following:
      | Email    | mrzhou@umich.edu |
      | Password | g0blue!!         |
    And I press "Log in"
    Then the response status code should be 200
    And I should see "Please override"
    When I go to "/account/logout"
    Then I should see "Servuno"