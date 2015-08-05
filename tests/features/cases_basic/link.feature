Feature: Check link
  In order to view the information on the site
  As an anonymous user
  I need to view the links correctly

  Scenario: check help link
    Given I am at the homepage
    Then I should see "Help"
    When I click "Help"
    Then I should be at "/help"
    And I should see "Care.com"
