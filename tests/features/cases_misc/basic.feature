Feature: Check link
  In order to view the information on the site
  As an anonymous user
  I need to view the links correctly

#  @core
#  Scenario: check help link
#    Given I am on the homepage
#    Then I should see "Help"
#    When I follow "Help"
#    Then I should be on "/help/"
#    And I should see "Care.com"

  @core
  Scenario: check about link
    Given I am on the homepage
    Then I should see "About"
    When I follow "About"
    Then I should be on "/about/"
    And I should see "Key Features"


  @core @javascript
  Scenario: check jotform
    Given I am on the homepage
    Then pause 5 seconds
    And I should see a ".jotform-feedback-link" element
    And I should see "Send Feedback"

  @core
  Scenario: check navbar
    Given I am logged in as user "test@servuno.com" with password "password"
    Then I should see "John"
    When I follow "Edit account"
    Then I should be on "/account/edit/"
    When I follow "Dashboard"
    Then I should be on "/dashboard/"
    Then I should see "Logout"
