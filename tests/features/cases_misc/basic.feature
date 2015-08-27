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
  Scenario: check calendar
    Given I am logged in as user "test@servuno.com" with password "password"
    Then I should be on "/calendar/"
    And I should see "Find a Babysitter"
    And I should see "Recent Activities"
    And I should see a "div.fc-view" element
    And I should see a "button.fc-agendaDay-button" element
    And I should see a "button.fc-agendaWeek-button" element
    And I should see a "button.fc-month-button" element
    And I should see a "button.fc-prev-button" element
    And I should see a "button.fc-next-button" element

  @core @javascript
  Scenario: check jotform
    Given I am on the homepage
    Then pause 5 seconds
    And I should see a ".jotform-feedback-link" element
    And I should see "Send Feedback"
