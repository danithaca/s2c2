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
      | price       | 20               |
    Then pause 2 seconds
    Then I should see "$20.00/hour, 1 hour"

    When I fill in "event_end" with "12/01/2010 20:00"
    Then pause 2 seconds
    Then I should see "$10.00/hour, 2 hour"

    When I fill in "price" with "10"
    Then pause 2 seconds
    Then I should see "$5.00/hour, 2 hour"

    When I fill in "price" with "0"
    Then pause 2 second
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
