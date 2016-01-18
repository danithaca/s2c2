Feature: Test inactive user (mark as spam)

  Scenario: check login ok
    Given I am on "/account/login/"
    When I fill in the following:
      | Email    | test1@servuno.com |
      | Password | password         |
    And I press "Log in"
    Then the response status code should be 200
    And the response should contain "<!-- logged in as test1@servuno.com -->"

  Scenario: setup, mark as inactive
    Given I am logged in as admin
    And I am on "/admin/auth/user/"
    When I fill in "searchbar" with "test1"
    And I press "Search"
    When I follow "test1"
    Then the "Username" field should contain "test1"
    When I uncheck "Active"
    And I press "Save"
    Then I should be on "/admin/auth/user/"

  Scenario: check login prevented
    Given I am on "/account/login/"
    When I fill in the following:
      | Email    | test1@servuno.com |
      | Password | password         |
    And I press "Log in"
    Then I should see "This account is inactive."
    And I should be on "/account/login/"

  Scenario: tear down, mark as active
    Given I am logged in as admin
    And I am on "/admin/auth/user/"
    When I fill in "searchbar" with "test1"
    And I press "Search"
    When I follow "test1"
    Then the "Username" field should contain "test1"
    When I check "Active"
    And I press "Save"
    Then I should be on "/admin/auth/user/"

  Scenario: make sure login ok
    Given I am on "/account/login/"
    When I fill in the following:
      | Email    | test1@servuno.com |
      | Password | password         |
    And I press "Log in"
    Then the response status code should be 200
    And the response should contain "<!-- logged in as test1@servuno.com -->"