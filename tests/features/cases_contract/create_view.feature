Feature: Test Find (contract add)

  @core
  Scenario: access the link
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "Find a Babysitter"
    Then I should be on "/contract/add/"


  @core @javascript
  Scenario: UI without submission
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/contract/add/"
    When I fill in the following:
      | event_start | 12/01/2010 18:00 |
      | event_end   | 12/01/2010 19:00 |
      | price       | 8                |
    # need 10+ seconds for javascript to catch up
    Then pause 3 seconds
    Then I should see "$8.00/hour, 1 hour"

    When I fill in "event_end" with "12/01/2010 20:00"
    Then pause 3 seconds
    Then I should see "$4.00/hour, 2 hour"

    When I fill in "price" with "2"
    Then pause 3 seconds
    Then I should see "$1.00/hour, 2 hour"

    When I fill in "price" with "0"
    Then pause 3 second
    Then I should see "favor exchange, 2 hour"


  @core @javascript
  Scenario: form submission
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on the homepage
    When I run the following Javascript:
      """
      var start = moment().add({days: 1, hours: 1});
      var end = moment(start).add({hours: 1});
      $('#calendar').fullCalendar('select', start, end);
      """
    Then pause 2 seconds
    Then I should be on "/contract/add/"
    And I should see "1 hour"

    When I press "submit"
    Then the URL should match "/contract/\d+/"
    And I should see a ".match-summary" element
    And I should see "successfully"

    Given I am on the homepage
    Then I should see "Upcoming"
    And I should see a ".fc-event" element
    And I should see an ".engagement" element
    And I should see "$10"

  @core @javascript
  Scenario: view contract
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on the homepage
    When I run the following Javascript:
      """
      $('.engagement.engagement-headline').click();
      """
    Then the URL should match "/contract/\d+/"
    And I should see "Edit"
    And I should see "Active"
    And I should see "Cancel"
    And I should see "Last updated"
    And I should see "test1"
    And I should see "John Smith's List"

  Scenario: check email
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email subject contains "John Smith needs your help"
    And check email contains "Compensation: $10"
    And check email contains "Please respond here"
    And check email contains "/contract/match/"
